from app.models import UserProfile, MealPlanResponse, RecipeRequest, Meal
from app.services.recipe_service import RecipeService
import pandas as pd
import pickle
import os
import random

class MealPlanService:
    def __init__(self):
        self.recipe_service = RecipeService()
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
                print("✅ MealPlanService: ML Model Loaded.")
        except Exception as e:
            print(f"⚠️ MealPlanService ML Load Error: {e}")

    def _predict_strategy(self, profile: UserProfile) -> str:
        if not self.model: return "Balanced"
        
        try:
            # Unpack Model
            clf = self.model['model'] if isinstance(self.model, dict) else self.model
            feats = self.model['features'] if isinstance(self.model, dict) else ['Age', 'Weight_kg', 'Height_cm', 'BMI']
            
            # Prepare Vector
            vals = {
                'Age': profile.age,
                'Weight_kg': profile.weightKg,
                'Height_cm': profile.heightCm,
                'BMI': profile.weightKg / ((profile.heightCm/100)**2)
            }
            
            if all(f in vals for f in feats):
                vec = [vals[f] for f in feats]
                input_df = pd.DataFrame([vec], columns=feats)
                _, idxs = clf.kneighbors(input_df)
                votes = self.data.iloc[idxs[0]]['Diet_Recommendation'].mode()
                return votes[0] if not votes.empty else "Balanced"
        except Exception as e:
            print(f"Prediction Error: {e}")
        
        return "Balanced"

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
        target_calories = self._calculate_bmr(profile)
        strategy = self._predict_strategy(profile)
        
        print(f"DEBUG: Generating Plan for {profile.age}yo, Goal: {profile.healthGoals}")
        print(f"DEBUG: Predicted Strategy: {strategy}")
        
        meals = []
        current_cal = 0
        
        # Define ratios for meals
        structure = [
            ("Breakfast", 0.25, ["Oats", "Eggs", "Yogurt", "Berries"]),
            ("Lunch", 0.35, ["Chicken", "Rice", "Quinoa", "Salad"]),
            ("Snack", 0.10, ["Nuts", "Fruit", "Smoothie"]),
            ("Dinner", 0.30, ["Fish", "Steak", "Tofu", "Vegetables"])
        ]
        
        for m_type, ratio, base_ings in structure:
            meal_target = int(target_calories * ratio)
            
            # Generate a recipe using the ML strategy
            ings = ", ".join(random.sample(base_ings, 2))
            
            # Use RecipeService to generate content (uses GPT-2 if avail)
            recipe_req = RecipeRequest(
                ingredients=ings, 
                cuisine=strategy, 
                dietaryRestrictions=strategy
            )
            gen_recipe = self.recipe_service.generate(recipe_req)
            
            # Use the REAL calorie calculation from the generated recipe
            # (RecipeService now uses NutritionService for accurate calories)
            meals.append(Meal(
                name=gen_recipe.title,
                type=m_type,
                calories=gen_recipe.calories,  # ← Real calories from NutritionService!
                macros=f"{strategy} Optimized ({gen_recipe.calories} kcal)" 
            ))
            current_cal += gen_recipe.calories

        return MealPlanResponse(
            goal=profile.healthGoals,
            totalDailyCalories=int(target_calories),
            suggestion=f"AI Recommendation: {strategy} Diet. ({int(target_calories)} kcal)",
            meals=meals
        )
