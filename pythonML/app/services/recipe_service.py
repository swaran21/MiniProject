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
        
        model_path = "app/models/recipe_gpt2"
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
    
    def _generate_with_ml(self, ingredients: str) -> dict:
        """Generate recipe using trained GPT-2 model with improved output quality"""
        # Format input for the model
        input_text = f"INPUT: {ingredients}\nOUTPUT:"
        
        # Tokenize
        inputs = self.tokenizer(input_text, return_tensors='pt')
        
        # IMPROVED GENERATION PARAMETERS (Session 2)
        outputs = self.model.generate(
            inputs['input_ids'],
            max_length=400,
            num_return_sequences=1,
            temperature=0.7,           # Lower = more conservative (was 0.8)
            top_p=0.85,                # Lower = less wild (was 0.9)
            repetition_penalty=1.3,    # NEW: Prevent repetition
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.encode('<END>')[0] if '<END>' in self.tokenizer.get_vocab() else self.tokenizer.eos_token_id
        )
        
        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract OUTPUT section
        if 'OUTPUT:' in generated_text:
            recipe_text = generated_text.split('OUTPUT:')[1].strip()
            if '<END>' in recipe_text:
                recipe_text = recipe_text.split('<END>')[0].strip()
        else:
            recipe_text = generated_text
        
        # Parse with IMPROVED VALIDATION
        title = "AI Generated Recipe"
        ingredients_list = []
        instructions = ""
        
        # Extract title (with cleanup)
        title_match = re.search(r'TITLE:\s*(.+?)(?:\||INGREDIENTS:|$)', recipe_text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up title
            title = re.sub(r'\s+', ' ', title)  # Remove extra whitespace
            title = title[:100]  # Limit length
        
        # Extract ingredients (FIXED: Better parsing to avoid instructions bleeding in)
        ingredients_match = re.search(r'INGREDIENTS?:\s*(.+?)(?:INSTRUCTIONS?:|$)', recipe_text, re.DOTALL | re.IGNORECASE)
        if ingredients_match:
            ing_text = ingredients_match.group(1).strip()
            
            # VALIDATION: Remove anything that looks like instructions
            ing_lines = ing_text.split('\n')
            for line in ing_lines:
                line = line.strip()
                # Skip if it looks like instructions (contains action verbs)
                if any(word in line.lower() for word in ['cook', 'heat', 'add the', 'boil', 'fry', 'bake', 'mix', 'combine', 'stir']):
                    continue
                # Skip if it has pipe character or "INSTRUCTIONS" text
                if '|' in line or 'INSTRUCTION' in line.upper():
                    continue
                # Split by semicolon or newline
                if ';' in line:
                    ingredients_list.extend([i.strip() for i in line.split(';') if i.strip()])
                elif line:
                    ingredients_list.append(line)
            
            # Clean up ingredients
            ingredients_list = [i for i in ingredients_list if i and len(i) > 2 and len(i) < 100]
        
        # Extract instructions (with repetition detection)
        instructions_match = re.search(r'INSTRUCTIONS?:\s*(.+?)$', recipe_text, re.DOTALL | re.IGNORECASE)
        if instructions_match:
            instructions = instructions_match.group(1).strip()
            
            # VALIDATION: Remove excessive repetition
            instructions = self._remove_repetition(instructions)
            
            # Clean up formatting
            instructions = re.sub(r'\n\s*\n', '\n', instructions)  # Remove blank lines
            instructions = re.sub(r'\s+', ' ', instructions)  # Normalize whitespace
            instructions = instructions[:800]  # Limit length
        
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
    
    def generate(self, request: RecipeRequest) -> RecipeResponse:
        print(f"DEBUG: Recipe Generation - Use ML? {self.use_ml}")
        if self.use_ml:
            # Use trained ML model
            try:
                ml_recipe = self._generate_with_ml(request.ingredients)
                
                # QUICK FIX: Calculate calories from USER'S original ingredients ONLY
                # (GPT-2 adds extra ingredients which inflates the calorie count)
                user_ingredients = [i.strip() for i in request.ingredients.split(',')]
                nutrition = self.nutrition_service.estimate_calories(user_ingredients)
                
                # But show GPT-2's full ingredient list in the recipe
                ingredients_list = ml_recipe['ingredients'] if ml_recipe['ingredients'] else user_ingredients
                
                return RecipeResponse(
                    title=ml_recipe['title'] + " (ML Powered)",
                    ingredients=ingredients_list,
                    instructions=ml_recipe['instructions'] if ml_recipe['instructions'] else "Generated recipe instructions",
                    cuisineType=request.cuisine,
                    calories=nutrition['calories'],  # ← Based on USER input, not GPT-2 extras
                    imageUrl="https://via.placeholder.com/300?text=" + ml_recipe['title'].replace(" ", "+")
                )
            except Exception as e:
                print(f"ML generation failed: {e}, falling back to templates")
                # Fall through to template generation
        
        # Template-based fallback
        ings = [i.strip() for i in request.ingredients.split(",")]
        main_item = ings[0] if ings else "Dish"
        sides = ", ".join(ings[1:]) if len(ings) > 1 else "Spices"
        
        template_title = random.choice(RECIPE_TEMPLATES["Titles"])
        template_instr = random.choice(RECIPE_TEMPLATES["Instructions"])
        
        title = template_title.format(Cuisine=request.cuisine, Main=main_item, Sides=sides)
        instructions = template_instr.format(ingredients=request.ingredients, main_item=main_item)
        
        # Calculate real calories for template recipes
        nutrition = self.nutrition_service.estimate_calories(ings)

        return RecipeResponse(
            title=title + " (Algorithmic AI)",
            ingredients=ings + ["Olive Oil", "Salt", "Special Herbs"],
            instructions=instructions,
            cuisineType=request.cuisine,
            calories=nutrition['calories'],
            imageUrl="https://via.placeholder.com/300?text=" + title.replace(" ", "+")
        )
