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
        """Generate recipe using trained GPT-2 model"""
        # Format input for the model
        input_text = f"INPUT: {ingredients}\nOUTPUT:"
        
        # Tokenize (using cpu/gpu automatically handled by pytorch usually, but here default cpu is fine for inference)
        inputs = self.tokenizer(input_text, return_tensors='pt')
        
        # Generate
        outputs = self.model.generate(
            inputs['input_ids'],
            max_length=400,
            num_return_sequences=1,
            temperature=0.8,
            top_p=0.9,
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
        
        # Parse the generated recipe
        title = "AI Generated Recipe"
        ingredients_list = []
        instructions = ""
        
        # Extract title
        title_match = re.search(r'TITLE:\s*(.+?)(?:\||$)', recipe_text)
        if title_match:
            title = title_match.group(1).strip()
        
        # Extract ingredients
        ingredients_match = re.search(r'INGREDIENTS:\s*(.+?)(?:\|INSTRUCTIONS:|$)', recipe_text, re.DOTALL)
        if ingredients_match:
            ing_text = ingredients_match.group(1).strip()
            ingredients_list = [i.strip() for i in ing_text.split(';') if i.strip()]
        
        # Extract instructions
        instructions_match = re.search(r'INSTRUCTIONS:\s*(.+?)$', recipe_text, re.DOTALL)
        if instructions_match:
            instructions = instructions_match.group(1).strip()
        
        return {
            'title': title,
            'ingredients': ingredients_list,
            'instructions': instructions
        }
    
    def generate(self, request: RecipeRequest) -> RecipeResponse:
        print(f"DEBUG: Recipe Generation - Use ML? {self.use_ml}")
        if self.use_ml:
            # Use trained ML model
            try:
                ml_recipe = self._generate_with_ml(request.ingredients)
                
                # Calculate real calories and macros using NutritionService
                ingredients_list = ml_recipe['ingredients'] if ml_recipe['ingredients'] else request.ingredients.split(',')
                nutrition = self.nutrition_service.estimate_calories(ingredients_list)
                
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
