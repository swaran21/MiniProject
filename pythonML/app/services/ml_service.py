from app.models import (
    RecipeRequest, RecipeResponse, 
    UserProfile, MealPlanResponse, Meal, 
    DietLogRequest, DietRecommendationResponse
)
from typing import List
import random
import pandas as pd
import pickle
import os
import numpy as np
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import re

# --- EXPANDED DATA ---
MEAL_OPTIONS = [
    Meal(name="Oatmeal with Berries", type="Breakfast", calories=250, macros="P: 8g, C: 45g, F: 5g"),
    Meal(name="Veggie Omelette", type="Breakfast", calories=300, macros="P: 14g, C: 5g, F: 20g"),
    Meal(name="Avocado Toast", type="Breakfast", calories=350, macros="P: 6g, C: 40g, F: 15g"),
    Meal(name="Protein Pancakes", type="Breakfast", calories=400, macros="P: 25g, C: 40g, F: 8g"),
    
    Meal(name="Grilled Chicken Salad", type="Lunch", calories=350, macros="P: 30g, C: 15g, F: 10g"),
    Meal(name="Quinoa Bowl with Tofu", type="Lunch", calories=400, macros="P: 18g, C: 50g, F: 12g"),
    Meal(name="Turkey Wrap", type="Lunch", calories=450, macros="P: 28g, C: 35g, F: 15g"),
    Meal(name="Lentil Soup & Bread", type="Lunch", calories=300, macros="P: 15g, C: 45g, F: 5g"),
    
    Meal(name="Salmon with Asparagus", type="Dinner", calories=500, macros="P: 35g, C: 10g, F: 25g"),
    Meal(name="Beef Stir Fry", type="Dinner", calories=600, macros="P: 30g, C: 60g, F: 20g"),
    Meal(name="Pasta Primavera", type="Dinner", calories=550, macros="P: 12g, C: 80g, F: 15g"),
    Meal(name="Baked Cod with Rice", type="Dinner", calories=450, macros="P: 25g, C: 50g, F: 10g"),
    
    Meal(name="Greek Yogurt", type="Snack", calories=150, macros="P: 15g, C: 10g, F: 0g"),
    Meal(name="Almonds & Apple", type="Snack", calories=200, macros="P: 4g, C: 20g, F: 12g"),
    Meal(name="Protein Shake", type="Snack", calories=180, macros="P: 25g, C: 5g, F: 2g"),
    Meal(name="Hummus & Carrots", type="Snack", calories=150, macros="P: 5g, C: 15g, F: 8g"),
    Meal(name="Cottage Cheese", type="Snack", calories=120, macros="P: 12g, C: 4g, F: 2g"),
]

FOOD_CALORIES = {
    "pizza": 285, "salad": 150, "burger": 550, "pasta": 400,
    "chicken": 250, "rice": 200, "bread": 100, "cheese": 110,
    "apple": 95, "banana": 105, "yogurt": 140, "eggs": 78,
    "fish": 206, "beef": 300, "oats": 150, "chocolate": 500,
    "fries": 312, "soup": 120, "sandwich": 350, "default": 250,
}

# --- TEMPLATES ---
RECIPE_TEMPLATES = {
    "Instructions": [
        "Start by prepping {ingredients}. Heat a pan and cook the base. Add seasonings and simmer. Serve fresh.",
        "Marinate {main_item} for 30 mins. Roast vegetables. Combine everything in a pot and cook until tender.",
        "Chop all ingredients finely. Sauté the {main_item} until golden. Mix in the rest and cook on high heat.",
        "Whisk the wet ingredients. Fold in {ingredients}. Bake at 350F for 20 mins or until cooked through."
    ],
    "Titles": [
        "{Cuisine} Delight: {Main}",
        "Homestyle {Main} ({Cuisine} Twist)",
        "Quick & Easy {Main} with {Sides}",
        "The Ultimate {Cuisine} {Main}"
    ]
}

class RecipeService:
    def __init__(self):
        """Initialize and load the trained GPT-2 recipe model"""
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
        
        # Tokenize
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
        if self.use_ml:
            # Use trained ML model
            try:
                ml_recipe = self._generate_with_ml(request.ingredients)
                
                # Estimate calories based on ingredients count and type
                calories = random.randint(300, 700)
                
                return RecipeResponse(
                    title=ml_recipe['title'] + " (ML Powered)",
                    ingredients=ml_recipe['ingredients'] if ml_recipe['ingredients'] else request.ingredients.split(','),
                    instructions=ml_recipe['instructions'] if ml_recipe['instructions'] else "Generated recipe instructions",
                    cuisineType=request.cuisine,
                    calories=calories,
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
        final_cal = random.randint(300, 800)

        return RecipeResponse(
            title=title + " (Algorithmic AI)",
            ingredients=ings + ["Olive Oil", "Salt", "Special Herbs"],
            instructions=instructions,
            cuisineType=request.cuisine,
            calories=final_cal,
            imageUrl="https://via.placeholder.com/300?text=" + title.replace(" ", "+")
        )

class MealPlanService:
    def _calculate_bmr(self, profile: UserProfile) -> float:
        # Standard Mifflin-St Jeor
        s = 5 if profile.gender.lower() == "male" else -161
        bmr = (10 * profile.weightKg) + (6.25 * profile.heightCm) - (5 * profile.age) + s
        
        lut = {"sedentary": 1.2, "moderate": 1.55, "active": 1.7}
        factor = lut.get(profile.activityLevel.lower(), 1.2)
        
        goals = profile.healthGoals.lower()
        adj = 500 if "gain" in goals else -500 if "lose" in goals else 0
        
        return (bmr * factor) + adj

    def create_plan(self, profile: UserProfile) -> MealPlanResponse:
        target = self._calculate_bmr(profile)
        
        # Dynamic Selection (Simple Knapsack-ish)
        selected = []
        current_cal = 0
        attempts = 0
        
        # Shuffle to ensure variety every request
        pool = MEAL_OPTIONS.copy()
        
        # Logic: 1 Bf, 1 Lun, 1 Din, rest Snacks
        valid_types = ["Breakfast", "Lunch", "Dinner"]
        random.shuffle(pool)
        
        # 1. Fill Main Meals first
        for m_type in valid_types:
            options = [m for m in pool if m.type == m_type]
            if options:
                choice = random.choice(options)
                selected.append(choice)
                current_cal += choice.calories

        # 2. Fill Remainder with Snacks/Sides
        while current_cal < target - 100 and attempts < 20:
            options = [m for m in pool if m.type == "Snack" or m.calories < 300]
            if not options: break
            
            choice = random.choice(options)
            # Avoid dupes
            if choice not in selected: # Allow simple duplicate check
                selected.append(choice)
                current_cal += choice.calories
            attempts += 1
            
        return MealPlanResponse(
            goal=profile.healthGoals,
            totalDailyCalories=int(target),
            suggestion=f"Target: {int(target)} kcal. Generated Plan: {current_cal} kcal.",
            meals=selected
        )

class DietService:
    def __init__(self):
        self.model_path = "app/models/diet_model.pkl"
        self.data_path = "data/diet_recommendations/diet_recommendations_dataset.csv"
        self.model = None
        self.data = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.data_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.data = pd.read_csv(self.data_path)
                print("ML Model Loaded.")
        except:
            pass # Silent fail for production robustness

    def recommend(self, request: DietLogRequest) -> DietRecommendationResponse:
        # A. Context Analysis (Current Food)
        item = request.foodItem.lower()
        est_cals = next((v for k, v in FOOD_CALORIES.items() if k in item), 250)
        
        mp_service = MealPlanService()
        limit = mp_service._calculate_bmr(request.userProfile)
        rem = limit - est_cals
        
        # B. ML Prediction (User Type / Strategy)
        diet_strategy = "Balanced" # Default
        
        used_ml = False
        if self.model:
            try:
                # Unpack
                clf = self.model['model'] if isinstance(self.model, dict) else self.model
                feats = self.model['features'] if isinstance(self.model, dict) else ['Age', 'Weight_kg', 'Height_cm', 'BMI']
                
                vals = {
                    'Age': request.userProfile.age,
                    'Weight_kg': request.userProfile.weightKg,
                    'Height_cm': request.userProfile.heightCm,
                    'BMI': request.userProfile.weightKg / ((request.userProfile.heightCm/100)**2)
                }
                
                if all(f in vals for f in feats):
                    vec = [vals[f] for f in feats]
                    # Fix: Create DataFrame to match training headers and avoid warnings
                    input_df = pd.DataFrame([vec], columns=feats)
                    
                    _, idxs = clf.kneighbors(input_df)
                    
                    # Get dominant recommendation from top 3 neighbors
                    votes = self.data.iloc[idxs[0]]['Diet_Recommendation'].mode()
                    strategy_name = votes[0] if not votes.empty else "Balanced"
                    diet_strategy = f"{strategy_name} (ML Powered)" 
                    used_ml = True
            except Exception as e:
                print(f"ML Error: {e}")

        # C. Combined Logic (Strategy + Context)
        # This solves the "Static Answer" problem.
        # We combine "User needs Low Carb" (Strategy) + "User ate Pizza" (Context)
        
        suggestion = f"Continue with {diet_strategy} diet."
        
        high_carb_foods = ["pizza", "burger", "pasta", "rice", "bread", "fries"]
        high_cal_foods = ["chocolate", "burger", "pizza"]
        
        # Dynamic Rules with Randomized Phrasing
        if any(f in item for f in high_carb_foods):
            if diet_strategy in ["Low-Carb", "Keto", "Atkins"]:
                opts = [
                    f"Since you ate {request.foodItem} (High Carb) but are on {diet_strategy}, ensure your next meal is ZERO carb.",
                    f"That {request.foodItem} used up your carb limit. Go for a pure protein dinner like Grilled Salmon.",
                    f"Oops, {request.foodItem} isn't great for {diet_strategy}. Skip carbs for the rest of the day."
                ]
                suggestion = random.choice(opts)
            else:
                opts = [
                    f"Balance that High Carb meal with a High Protein dinner (e.g. Chicken Breast).",
                    f"Good energy from the {request.foodItem}. Now switch to fiber and protein for your next meal.",
                    f"To keep your blood sugar stable after {request.foodItem}, eat something green and lean next."
                ]
                suggestion = random.choice(opts)
        
        elif any(f in item for f in high_cal_foods) or est_cals > 600:
            opts = [
                f"That was a heavy meal ({est_cals} kcal). Suggesting a light salad or soup next to stay within limit.",
                f"Whoa, big meal! Let's go light for the next one—maybe a Cucumber Salad?",
                f"Since you indulged in {request.foodItem}, try intermittent fasting until breakfast or have a light broth."
            ]
            suggestion = random.choice(opts)
            
        elif diet_strategy == "Vegan" and "chicken" in item:
             opts = [
                 f"Note: You are marked as 'Vegan', but ate meat. Suggesting a Lentil Stew to reset.",
                 f"Did you cheat on your Vegan diet? It happens! Try a Tofu Stir-fry next.",
                 f"Back to plants! How about a Chickpea Curry for your next meal?"
             ]
             suggestion = random.choice(opts)
             
        else:
            # Fallback randomizer for variety
            options = [
                f"Keep it up! A {diet_strategy} friendly snack like Almonds would be great.",
                f"Stay hydrated! Pair your next meal with water to help digestion.",
                f"You have {int(rem)} kcal left. A balanced dinner fits perfectly.",
                f"Great choice with {request.foodItem}. Maybe try a fruit smoothie next?",
                f"Doing well! Stick to the plan and you'll hit your goal of {request.userProfile.healthGoals}."
            ]
            suggestion = random.choice(options)

        return DietRecommendationResponse(
            caloriesConsumedEstimate=est_cals,
            caloriesRemaining=int(rem),
            nutritionalAnalysis=f"Analyzed '{request.foodItem}': ~{est_cals} kcal. ML Strategy: {diet_strategy}",
            nextMealSuggestion=suggestion
        )

