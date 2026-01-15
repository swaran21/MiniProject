from app.models import RecipeRequest, RecipeResponse
from app.utils.data_consts import RECIPE_TEMPLATES
from app.services.nutrition_service import NutritionService
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os
import random
import re
import sqlite3

# CRITICAL FIX: Singleton Pattern to Prevent Memory Leak
# The GPT-2 model is 500MB. Without this, each RecipeService() instantiation 
# loads a new copy into RAM, causing memory exhaustion.
_RECIPE_SERVICE_INSTANCE = None

class RecipeService:
    """
    Recipe Generation Service with Hybrid RAG Architecture
    
    SINGLETON IMPLEMENTATION:
    - Uses __new__ to ensure only ONE instance exists
    - Model is loaded ONCE per application lifecycle
    - Prevents 500MB x N instances memory leak
    """
    
    def __new__(cls):
        """Singleton constructor - returns existing instance if available"""
        global _RECIPE_SERVICE_INSTANCE
        if _RECIPE_SERVICE_INSTANCE is None:
            _RECIPE_SERVICE_INSTANCE = super(RecipeService, cls).__new__(cls)
            _RECIPE_SERVICE_INSTANCE._initialized = False
        return _RECIPE_SERVICE_INSTANCE
    
    def __init__(self):
        """Initialize model and database (only runs once due to Singleton)"""
        # Prevent re-initialization if already loaded
        if self._initialized:
            return
        
        self._initialized = True
        
        # Initialize nutrition service for real calorie calculations
        self.nutrition_service = NutritionService()
        
        model_path = "app/models/recipe_gpt2_improved"
        if os.path.exists(model_path):
            try:
                print(f"🔄 Loading trained recipe model from {model_path}...")
                self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
                self.model = GPT2LMHeadModel.from_pretrained(model_path)
                self.model.eval()  # Set to evaluation mode
                print("✅ Recipe GPT-2 Model Loaded Successfully (ML Powered)")
                self.use_ml = True
            except Exception as e:
                print(f"⚠️  Failed to load model: {e}")
                print("Falling back to template-based generation")
                self.use_ml = False
        else:
            print(f"⚠️  Model not found at {model_path}, using templates")
            self.use_ml = False
            
        # Initialize Database Connection (Hybrid RAG)
        self.db_conn = None
        self.init_database_connection()
    
    def init_database_connection(self):
        """Initialize SQLite database connection"""
        import sqlite3
        db_path = "data/database/recipes.db"
        
        if not os.path.exists(db_path):
            print(f"⚠️ Database not found at {db_path}")
            print(f"💡 Run 'python seed_db.py' to create the database")
            return
        
        try:
            self.db_conn = sqlite3.connect(db_path, check_same_thread=False)
            self.db_conn.row_factory = sqlite3.Row  # Access columns by name
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipes")
            count = cursor.fetchone()[0]
            print(f"✅ Connected to recipe database ({count} recipes loaded)")
        except Exception as e:
            print(f"⚠️ Failed to connect to database: {e}")
            self.db_conn = None
    
    def _generate_with_ml(self, ingredients: str) -> dict:
        """Generate recipe using trained GPT-2 model with improved output quality"""
        # Format input for the model
        input_text = f"INPUT: {ingredients}\nOUTPUT:"
        
        # Tokenize (Ensure we create an attention mask)
        inputs = self.tokenizer(input_text, return_tensors='pt', padding=True, truncation=True)
        
        # IMPROVED GENERATION PARAMETERS (Final Polish)
        outputs = self.model.generate(
            inputs['input_ids'],
            attention_mask=inputs['attention_mask'], # Added mask for stability
            max_length=400,
            num_return_sequences=1,
            temperature=0.1,           # STRICT MODE: Almost deterministic (was 0.5)
            top_p=0.95,                # Focus on top choices
            repetition_penalty=1.5,    # STRICTER: Prevent loops (was 1.3)
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.encode('<END>')[0] if '<END>' in self.tokenizer.get_vocab() else self.tokenizer.eos_token_id
        )
        
        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"DEBUG RAW MODEL OUTPUT: {generated_text}") 
        
        # Robust Parsing Strategy to handle model glitches
        # problem: sometimes model repeats INPUT or formatted oddly
        
        # 1. Strip the Input Prompt ("INPUT: ... OUTPUT:")
        if 'OUTPUT:' in generated_text:
            # Take everything after the last OUTPUT: to avoid repeat hallucinations
            recipe_text = generated_text.split('OUTPUT:')[-1].strip()
        else:
            # Fallback: Model forgot OUTPUT tag, try to remove INPUT manually
            recipe_text = generated_text.replace(input_text, "").strip()
            
        # 2. Cleanup End Tokens
        if '<END>' in recipe_text:
            recipe_text = recipe_text.split('<END>')[0].strip()
            
        # 3. Final safety cleanup
        # If text starts with "TITLE |", it's good. If it looks like ingredients, it's messy.
        if "INPUT:" in recipe_text: # Double check prompt leakage
            recipe_text = recipe_text.split("OUTPUT:")[-1].strip()

        
        # Use centralized parser
        return self._parse_recipe_text(recipe_text)
    
    def _remove_copyright_noise(self, text: str) -> str:
        """Remove copyright notices and licensing text from ML output"""
        if not text:
            return text
        
        # Common copyright patterns to remove
        copyright_patterns = [
            r'Copyright\s*©?\s*\d{4}.*?All rights reserved\.?',
            r'©\s*\d{4}.*?All rights reserved\.?',
            r'This recipe was provided.*?commercial purposes["\']?',
            r'Recipe courtesy of.*?Food Network',
            r'Television Food Network.*?All rights reserved',
            r'Recipe provided under license.*?commercial purposes',
            r'not available.*?commercial purposes',
            r'All rights reserved\.',
            r'Used with permission\.',
        ]
        
        cleaned = text
        for pattern in copyright_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove multiple spaces and empty lines left behind
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
        
        return cleaned.strip()
    
    def _parse_recipe_text(self, recipe_text: str) -> dict:
        """Robustly parse raw recipe text into structured data"""
        recipe_text = self._remove_copyright_noise(recipe_text)
        title = "AI Generated Recipe"
        ingredients_list = []
        instructions = "Mix all ingredients and cook until done."
        
        # Parse with ROBUST FALLBACKS
        title = "AI Generated Recipe"
        ingredients_list = []
        instructions = "Mix all ingredients and cook until done."
        
        # 1. Extract Title
        # Try standard format first
        title_match = re.search(r'TITLE:\s*(.*?)(?:\||INGREDIENTS:|CUISINE:|$)', recipe_text, re.IGNORECASE)
        if title_match and title_match.group(1).strip():
            title = title_match.group(1).strip()
            
        # 2. Extract Ingredients & Instructions (Unified Strategy)
        # Check if we have standard tags
        has_ingredients_tag = bool(re.search(r'INGREDIENTS?:', recipe_text, re.IGNORECASE))
        has_instructions_tag = bool(re.search(r'INSTRUCTIONS?:', recipe_text, re.IGNORECASE))
        
        if has_ingredients_tag and has_instructions_tag:
            # Happy Path: Standard parsing
            ing_match = re.search(r'INGREDIENTS?:?\s*(.+?)(?:\s*\|\s*INSTRUCTIONS?:|$)', recipe_text, re.DOTALL | re.IGNORECASE)
            if ing_match:
                raw_ings = ing_match.group(1)
                ingredients_list = [i.strip() for i in raw_ings.split(';') if i.strip()]
            
            inst_match = re.search(r'INSTRUCTIONS?:\s*(.+?)$', recipe_text, re.DOTALL | re.IGNORECASE)
            if inst_match:
                instructions = inst_match.group(1).strip()
        else:
            # SAD PATH: Model forgot tags (e.g. "TITLE | CUISINE*: Asian; 1/2 cup garlic; 1 tsp salt. Heat oil...")
            # Strategy: Split by semicolons. Everything with semicolons is ingredients.
            # The last part (sentences) is instructions.
            
            # Remove Title/Cuisine preamble
            clean_text = re.sub(r'^.*?CUISINE.*?:.*?;', '', recipe_text, flags=re.DOTALL | re.IGNORECASE)
            if clean_text == recipe_text: # Regex didn't match
                 clean_text = re.sub(r'^.*?OUTPUT:', '', recipe_text, flags=re.DOTALL | re.IGNORECASE)
            
            # Split by semicolons
            segments = clean_text.split(';')
            
            # If we have segments, the first N-1 are likely ingredients
            if len(segments) > 1:
                potential_ingredients = segments[:-1]
                last_segment = segments[-1]
                
                # The last segment might be "1 tsp salt. Cook meat." -> Mixed ingredient + instruction
                # Check if the last segment splits into an instruction
                if '.' in last_segment:
                    parts = last_segment.split('.', 1)
                    potential_ingredients.append(parts[0].strip()) # "1 tsp salt"
                    instructions = parts[1].strip() + "." # "Cook meat."
                else:
                    instructions = last_segment.strip()
                
                ingredients_list = [i.strip() for i in potential_ingredients if i.strip()]
            else:
                # No semicolons? Panic. Just treat it as instructions.
                instructions = clean_text.strip()

        # 3. Clean Ingredients List
        cleaned_ingredients = []
        for ing in ingredients_list:
            # Remove leading numbers/bullets/glitchy chars
            ing = re.sub(r'^[\d\-\•\*\.]+\s*', '', ing)
            ing = re.sub(r'[\(\)]', '', ing) # Remove parens
            ing = re.sub(r'CUISINE.*?:', '', ing, flags=re.IGNORECASE) # Remove stray tags
            
            # Start filter
            if re.match(r'^\s*(cook|heat|add|boil|fry|bake|mix|combine|stir|serve)', ing, re.IGNORECASE):
                # Instruction mixed in?
                if len(ing) > 50 and instructions == "Mix all ingredients and cook until done.":
                     instructions = ing
                continue
                
            if len(ing) > 2:
                cleaned_ingredients.append(ing.title())

        if cleaned_ingredients:
            ingredients_list = cleaned_ingredients

        # Final Cleanup of instructions
        # Remove copyright notices (ML artifacts)
        instructions = self._remove_copyright_noise(instructions)
        instructions = self._remove_repetition(instructions)
        instructions = re.sub(r'\s+', ' ', instructions).strip()
        # Remove any leftover "TITLE |" garbage from instructions
        instructions = re.sub(r'TITLE\s*\|.*?;', '', instructions)


        
        return {
            'title': title,
            'ingredients': ingredients_list,
            'instructions': instructions
        }
    
    def _remove_repetition(self, text: str) -> str:
        """Remove excessive repetition from instructions"""
        sentences = text.split('.')
        seen = set()
        cleaned = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Normalize for comparison (lowercase, remove numbers/measurements)
            normalized = re.sub(r'\d+', '', sentence.lower())
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            
            # If we've seen this sentence (or very similar), skip it
            if normalized in seen:
                continue
            
            # Check for substring repetition (e.g., same phrase 3+ times)
            if len(normalized) > 20:
                # If a 10+ char phrase appears 3+ times, it's repetitive
                words = normalized.split()
                if len(words) > 3:
                    phrase = ' '.join(words[-4:])  # Last 4 words
                    if text.lower().count(phrase) >= 3:
                        continue
            
            seen.add(normalized)
            cleaned.append(sentence)
        
        return '. '.join(cleaned) + '.'
    

    def find_best_match(self, user_ingredients: str) -> dict:
        """Find the best matching recipe using SQLite FTS5 search"""
        if not self.db_conn:
            return None
        
        try:
            cursor = self.db_conn.cursor()
            
            # Clean and prepare search query
            ingredients_clean = user_ingredients.lower().strip()
            search_tokens = [t.strip() for t in ingredients_clean.split(',') if t.strip()]
            
            if not search_tokens:
                return None
            
            # Build FTS5 query (e.g., "chicken AND garlic")
            fts_query = ' AND '.join(search_tokens)
            
            # Search using FTS5 Full-Text Search (Ranked by relevance + ratings)
            cursor.execute("""
                SELECT 
                    r.id, r.title, r.ingredients, r.instructions, r.cuisine,
                    r.likes, r.dislikes, r.rating_score,
                    bm25(recipes_fts) as search_score,
                    (bm25(recipes_fts) * 0.7) + (r.rating_score * 0.3) as final_score
                FROM recipes r
                JOIN recipes_fts ON recipes_fts.rowid = r.id
                WHERE recipes_fts MATCH ?
                ORDER BY final_score
                LIMIT 1
            """, (fts_query,))
            
            row = cursor.fetchone()
            
            if row:
                print(f"🎯 Database Match Found! Recipe ID: {row['id']}, Final Score: {row['final_score']:.2f}")
                
                # Parse ingredients from database format
                ingredients_list = [i.strip() for i in row['ingredients'].split(';') if i.strip()]
                
                return {
                    'id': row['id'],
                    'title': row['title'],
                    'ingredients': ingredients_list,
                    'instructions': row['instructions'],
                    'cuisine': row['cuisine'] or 'Any',
                    'likes': row['likes'],
                    'dislikes': row['dislikes'],
                    'rating_score': row['rating_score']
                }
            
            # Fallback: Try OR search if AND was too strict
            fts_query_or = ' OR '.join(search_tokens)
            cursor.execute("""
                SELECT 
                    r.id, r.title, r.ingredients, r.instructions, r.cuisine,
                    r.likes, r.dislikes, r.rating_score,
                    bm25(recipes_fts) as search_score,
                    (bm25(recipes_fts) * 0.7) + (r.rating_score * 0.3) as final_score
                FROM recipes r
                JOIN recipes_fts ON recipes_fts.rowid = r.id
                WHERE recipes_fts MATCH ?
                ORDER BY final_score
                LIMIT 1
            """, (fts_query_or,))
            
            row = cursor.fetchone()
            
            if row:
                print(f"🎯 Partial Match Found (OR search): ID {row['id']}, Final Score: {row['final_score']:.2f}")
                ingredients_list = [i.strip() for i in row['ingredients'].split(';') if i.strip()]
                
                return {
                    'id': row['id'],
                    'title': row['title'],
                    'ingredients': ingredients_list,
                    'instructions': row['instructions'],
                    'cuisine': row['cuisine'] or 'Any',
                    'likes': row['likes'],
                    'dislikes': row['dislikes'],
                    'rating_score': row['rating_score']
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️ Database search failed: {e}")
            return None

    def rate_recipe(self, recipe_id: int, user_id: str, rating: int):
        """
        Rate a recipe (1 for like, -1 for dislike)
        Uses Wilson score for confident rating calculation
        """
        if not self.db_conn:
            raise Exception("Database not connected")
        
        if rating not in [1, -1]:
            raise ValueError("Rating must be 1 (like) or -1 (dislike)")
        
        cursor = self.db_conn.cursor()
        
        try:
            # Check if user already rated this recipe
            cursor.execute("""
                SELECT rating FROM user_ratings 
                WHERE user_id = ? AND recipe_id = ?
            """, (user_id, recipe_id))
            
            existing = cursor.fetchone()
            
            if existing:
                old_rating = existing['rating']
                
                # Update existing rating
                cursor.execute("""
                    UPDATE user_ratings 
                    SET rating = ?, created_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND recipe_id = ?
                """, (rating, user_id, recipe_id))
                
                # Adjust recipe stats
                if old_rating == 1 and rating == -1:
                    # Changed from like to dislike
                    cursor.execute("""
                        UPDATE recipes 
                        SET likes = likes - 1, dislikes = dislikes + 1
                        WHERE id = ?
                    """, (recipe_id,))
                elif old_rating == -1 and rating == 1:
                    # Changed from dislike to like
                    cursor.execute("""
                        UPDATE recipes 
                        SET likes = likes + 1, dislikes = dislikes - 1
                        WHERE id = ?
                    """, (recipe_id,))
            else:
                # Insert new rating
                cursor.execute("""
                    INSERT INTO user_ratings (user_id, recipe_id, rating)
                    VALUES (?, ?, ?)
                """, (user_id, recipe_id, rating))
                
                # Update recipe stats
                if rating == 1:
                    cursor.execute("""
                        UPDATE recipes SET likes = likes + 1 WHERE id = ?
                    """, (recipe_id,))
                else:
                    cursor.execute("""
                        UPDATE recipes SET dislikes = dislikes + 1 WHERE id = ?
                    """, (recipe_id,))
            
            # Calculate Wilson score for ranking
            # Formula: (positive + 1.9208) / (positive + negative + 3.8416)
            # This gives a conservative lower bound of the true rating
            cursor.execute("""
                UPDATE recipes
                SET rating_score = (likes + 1.9208) / (likes + dislikes + 3.8416),
                    rating_count = likes + dislikes
                WHERE id = ?
            """, (recipe_id,))
            
            self.db_conn.commit()
            
            # Return updated stats
            return self.get_recipe_rating(recipe_id)
            
        except sqlite3.Error as e:
            self.db_conn.rollback()
            raise Exception(f"Database error: {e}")
    
    def get_recipe_rating(self, recipe_id: int):
        """Get rating statistics for a recipe"""
        if not self.db_conn:
            raise Exception("Database not connected")
        
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT id, likes, dislikes, rating_score, rating_count
            FROM recipes
            WHERE id = ?
        """, (recipe_id,))
        
        row = cursor.fetchone()
        
        if not row:
            raise Exception(f"Recipe {recipe_id} not found")
        
        return {
            'recipe_id': row['id'],
            'likes': row['likes'],
            'dislikes': row['dislikes'],
            'rating_score': round(row['rating_score'], 3),
            'total_ratings': row['rating_count']
        }
    
    def search_recipes_by_name(self, query: str, limit: int = 10):
        """Search recipes by title using FTS5"""
        if not self.db_conn:
            raise Exception("Database not connected")
        
        cursor = self.db_conn.cursor()
        
        try:
            # Add wildcard for partial matching
            search_query = f"{query}*"
            
            # Search by title using FTS5
            cursor.execute("""
                SELECT 
                    r.id, r.title, r.cuisine, r.likes, r.dislikes, 
                    r.rating_score, r.rating_count,
                    bm25(recipes_fts) as relevance
                FROM recipes r
                JOIN recipes_fts ON recipes_fts.rowid = r.id
                WHERE recipes_fts.title MATCH ?
                ORDER BY rating_score DESC, relevance
                LIMIT ?
            """, (search_query, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'title': row['title'],
                    'cuisine': row['cuisine'] or 'Any',
                    'likes': row['likes'],
                    'dislikes': row['dislikes'],
                    'rating_score': round(row['rating_score'], 2),
                    'total_ratings': row['rating_count']
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Search failed: {e}")
    
    def get_recipe_by_id(self, recipe_id: int):
        """Get full recipe details by ID"""
        if not self.db_conn:
            raise Exception("Database not connected")
        
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT id, title, ingredients, instructions, cuisine,
                   likes, dislikes, rating_score, rating_count
            FROM recipes
            WHERE id = ?
        """, (recipe_id,))
        
        row = cursor.fetchone()
        
        if not row:
            raise Exception(f"Recipe {recipe_id} not found")
        
        # Parse ingredients
        ingredients_list = [i.strip() for i in row['ingredients'].split(';') if i.strip()]
        
        return {
            'id': row['id'],
            'title': row['title'],
            'ingredients': ingredients_list,
            'instructions': row['instructions'],
            'cuisine': row['cuisine'] or 'Any',
            'likes': row['likes'],
            'dislikes': row['dislikes'],
            'rating_score': round(row['rating_score'], 3),
            'total_ratings': row['rating_count']
        }
    
    def generate(self, request: RecipeRequest) -> RecipeResponse:
        print(f"DEBUG: Recipe Generation - Use ML? {self.use_ml}")
        
        # 1. Try Smart Retrieval (KNN) First
        try:
             retrieved_recipe = self.find_best_match(request.ingredients)
             if retrieved_recipe:
                 return RecipeResponse(
                    id=retrieved_recipe.get('id'),  # Include recipe ID for ratings
                    title=retrieved_recipe['title'] + " (Smart Match)",
                    ingredients=retrieved_recipe['ingredients'],
                    instructions=retrieved_recipe['instructions'],
                    cuisineType=request.cuisine,
                    calories=int(self.nutrition_service.estimate_calories(retrieved_recipe['ingredients'])['calories']),
                    imageUrl="https://via.placeholder.com/300?text=" + retrieved_recipe['title'].replace(" ", "+")
                )
        except Exception as e:
            print(f"⚠️ Retrieval failed: {e}")

        # 2. Fallback to ML
        if self.use_ml:
            try:
                ml_recipe = self._generate_with_ml(request.ingredients)
                
                user_ingredients = [i.strip() for i in request.ingredients.split(',')]
                nutrition = self.nutrition_service.estimate_calories(user_ingredients)
                ingredients_list = ml_recipe['ingredients'] if ml_recipe['ingredients'] else user_ingredients
                
                return RecipeResponse(
                    title=ml_recipe['title'] + " (ML Powered)",
                    ingredients=ingredients_list,
                    instructions=ml_recipe['instructions'] if ml_recipe['instructions'] else "Generated recipe instructions",
                    cuisineType=request.cuisine,
                    calories=int(nutrition['calories']), 
                    imageUrl="https://via.placeholder.com/300?text=" + ml_recipe['title'].replace(" ", "+")
                )
            except Exception as e:
                print(f"ML generation failed: {e}, falling back to templates")
        
        # 3. Fallback to Templates
        ings = [i.strip() for i in request.ingredients.split(",")]
        main_item = ings[0] if ings else "Dish"
        sides = ", ".join(ings[1:]) if len(ings) > 1 else "Spices"
        template_title = random.choice(RECIPE_TEMPLATES["Titles"])
        template_instr = random.choice(RECIPE_TEMPLATES["Instructions"])
        
        title = template_title.format(Cuisine=request.cuisine, Main=main_item, Sides=sides)
        instructions = template_instr.format(ingredients=request.ingredients, main_item=main_item)
        nutrition = self.nutrition_service.estimate_calories(ings)

        return RecipeResponse(
            title=title + " (Algorithmic AI)",
            ingredients=ings + ["Olive Oil", "Salt", "Special Herbs"],
            instructions=instructions,
            cuisineType=request.cuisine,
            calories=int(nutrition['calories']),
            imageUrl="https://via.placeholder.com/300?text=" + title.replace(" ", "+")
        )
