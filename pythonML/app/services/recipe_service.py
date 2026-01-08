from app.models import RecipeRequest, RecipeResponse
from app.utils.data_consts import RECIPE_TEMPLATES
from app.services.nutrition_service import NutritionService
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os
import random
import re

class RecipeService:
    def __init__(self):
        """Initialize and load the trained GPT-2 recipe model"""
        # Initialize nutrition service for real calorie calculations
        self.nutrition_service = NutritionService()
        
        model_path = "app/models/recipe_gpt2_improved"
        if os.path.exists(model_path):
            try:
                print(f"Loading trained recipe model from {model_path}...")
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
            
        # Initialize Dataset for Retrieval (Hybrid RAG)
        self.load_dataset_for_retrieval()
    
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
        print(f"DEBUG RAW MODEL OUTPUT: {generated_text}") # Debugging line
        
        # Extract OUTPUT section
        if 'OUTPUT:' in generated_text:
            recipe_text = generated_text.split('OUTPUT:')[1].strip()
            if '<END>' in recipe_text:
                recipe_text = recipe_text.split('<END>')[0].strip()
        else:
            recipe_text = generated_text
        
        # Use centralized parser
        return self._parse_recipe_text(recipe_text)

    def _parse_recipe_text(self, recipe_text: str) -> dict:
        """Robustly parse raw recipe text into structured data"""
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
    
    
    def load_dataset_for_retrieval(self):
        """Load the training dataset into memory for KNN/Search retrieval"""
        self.dataset_recipes = []
        data_path = "data/recipe_training_improved.txt"
        
        if not os.path.exists(data_path):
            print(f"⚠️ Dataset not found at {data_path}, skipping retrieval mode.")
            return

        print("📚 Loading dataset for Smart Retrieval...")
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Split by recipe blocks
            blocks = content.split('INPUT:')
            for block in blocks:
                if not block.strip(): continue
                
                try:
                    parts = block.split('OUTPUT:')
                    if len(parts) < 2: continue
                    
                    input_Ings = parts[0].strip().lower()
                    output_Text = parts[1].strip()
                    
                    # Store for search
                    self.dataset_recipes.append({
                        'input_tokens': set([t.strip() for t in input_Ings.split(',') if t.strip()]),
                        'full_text': output_Text,
                        'original_input': input_Ings
                    })
                except:
                    continue
            print(f"✅ Loaded {len(self.dataset_recipes)} recipes for smart retrieval.")
        except Exception as e:
            print(f"⚠️ Failed to load dataset: {e}")

    def find_best_match(self, user_ingredients: str) -> dict:
        """Find the best matching recipe from the dataset"""
        if not hasattr(self, 'dataset_recipes') or not self.dataset_recipes:
             return None
             
        user_tokens = set([t.strip() for t in user_ingredients.lower().split(',') if t.strip()])
        if not user_tokens: return None
        
        best_recipe = None
        best_score = 0
        
        for recipe in self.dataset_recipes:
            # Score methods
            recipe_tokens = recipe['input_tokens']
            
            # Intersection count
            intersection = len(user_tokens.intersection(recipe_tokens))
            
            if intersection > best_score:
                best_score = intersection
                best_recipe = recipe
        
        # Strictness: Must match at least 50% of user inputs?
        if best_recipe and best_score > 0:
             match_pct = best_score / len(user_tokens)
             # If user provides 2 ingredients, at least 1 must match.
             if match_pct >= 0.5:
                 print(f"🎯 Exact Match Found! Score: {best_score}/{len(user_tokens)}")
                 # Parse the stored text
                 return self._parse_recipe_text(best_recipe['full_text'].replace('<END>', '').strip())
        
        return None

    def generate(self, request: RecipeRequest) -> RecipeResponse:
        print(f"DEBUG: Recipe Generation - Use ML? {self.use_ml}")
        
        # 1. Try Smart Retrieval (KNN) First
        try:
             retrieved_recipe = self.find_best_match(request.ingredients)
             if retrieved_recipe:
                 return RecipeResponse(
                    title=retrieved_recipe['title'] + " (Smart Match)",
                    ingredients=retrieved_recipe['ingredients'],
                    instructions=retrieved_recipe['instructions'],
                    cuisineType=request.cuisine,
                    calories=self.nutrition_service.estimate_calories(retrieved_recipe['ingredients'])['calories'],
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
                    calories=nutrition['calories'], 
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
            calories=nutrition['calories'],
            imageUrl="https://via.placeholder.com/300?text=" + title.replace(" ", "+")
        )
