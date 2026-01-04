from app.models import DietLogRequest, DietRecommendationResponse, RecipeRequest, RecommendedMeal
from app.services.recipe_service import RecipeService
from app.services.meal_service import MealPlanService
from app.services.nutrition_service import NutritionService
from app.utils.data_consts import FOOD_CALORIES
import pandas as pd
import pickle
import os
import random

class DietService:
    def __init__(self):
        self.model_path = "app/models/diet_model.pkl"
        self.data_path = "data/diet_recommendations/diet_recommendations_dataset.csv"
        self.model = None
        self.data = None
        self._load_model()
        self.recipe_service = RecipeService() # Reuse this instance
        self.mp_service = MealPlanService()
        self.nutrition_service = NutritionService()  # For real calorie calculations

    def _load_model(self):
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.data_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.data = pd.read_csv(self.data_path)
                print("ML Model Loaded (KNN).")
        except:
            pass 

    def recommend(self, request: DietLogRequest) -> DietRecommendationResponse:
        # 1. Analyze Context (Current Food) - Use real nutrition service
        item = request.foodItem.lower()
        est_cals = self.nutrition_service.estimate_meal_calories(item)
        
        # 2. Calculate Limits
        limit = self.mp_service._calculate_bmr(request.userProfile)
        rem = limit - est_cals
        
        # 3. ML Prediction (User Type / Strategy)
        diet_strategy = "Balanced" # Default
        
        if self.model:
            try:
                # Unpack Model
                clf = self.model['model'] if isinstance(self.model, dict) else self.model
                feats = self.model['features'] if isinstance(self.model, dict) else ['Age', 'Weight_kg', 'Height_cm', 'BMI']
                
                # Prepare Vector
                vals = {
                    'Age': request.userProfile.age,
                    'Weight_kg': request.userProfile.weightKg,
                    'Height_cm': request.userProfile.heightCm,
                    'BMI': request.userProfile.weightKg / ((request.userProfile.heightCm/100)**2)
                }
                
                if all(f in vals for f in feats):
                    vec = [vals[f] for f in feats]
                    input_df = pd.DataFrame([vec], columns=feats)
                    _, idxs = clf.kneighbors(input_df)
                    votes = self.data.iloc[idxs[0]]['Diet_Recommendation'].mode()
                    diet_strategy = votes[0] if not votes.empty else "Balanced"
                    print(f"DEBUG: User Profile -> Age: {request.userProfile.age}, W: {request.userProfile.weightKg}")
                    print(f"DEBUG: ML Predicted Strategy (KNN): {diet_strategy}")
            except Exception as e:
                print(f"ML Error: {e}")

        # 4. Determine Remaining Schedule
        current_meal_type = request.mealType.lower() if request.mealType else "lunch"
        schedule = []
        
        if "breakfast" in current_meal_type:
            schedule = [("Lunch", 0.45), ("Snack", 0.15), ("Dinner", 0.40)]
        elif "lunch" in current_meal_type:
            schedule = [("Snack", 0.20), ("Dinner", 0.80)]
        elif "dinner" in current_meal_type:
            schedule = [("Late Snack", 1.0)]
        else:
            # Fallback
            schedule = [("Next Meal", 1.0)]

        # 5. Generate Full Day Plan
        plan_text = []
        structured_plan = []
        
        plan_text.append(f"### 🥗 Day Plan (Strategy: {diet_strategy})")
        plan_text.append(f"**Goal**: {int(limit)} kcal | **Remaining**: {int(rem)} kcal")
        plan_text.append("---")
        
        diet_ingredients = {
            "Keto": ["Chicken", "Avocado", "Spinach", "Cheese", "Salmon", "Eggs"],
            "Vegan": ["Tofu", "Lentils", "Chickpeas", "Quinoa", "Kale"],
            "Low-Carb": ["Turkey", "Zucchini", "Broccoli", "Cauliflower"],
            "Paleo": ["Steak", "Carrots", "Asparagus", "Walnuts"],
            "Balanced": ["Rice", "Chicken", "Veggies", "Beans", "Yogurt"],
            "Mediterranean": ["Fish", "Olive Oil", "Tomatoes", "Feta"],
            "DASH": ["Oats", "Banana", "Almonds", "Milk"]
        }
        base_pool = diet_ingredients.get(diet_strategy, diet_ingredients["Balanced"])

        for meal_name, ratio in schedule:
            meal_cals = int(rem * ratio)
            if meal_cals < 200: meal_cals = 200 # Enforce minimum per meal to ensure generation
            
            # Select unique ingredients for this meal
            selected_ingredients = random.sample(base_pool, min(3, len(base_pool)))
            ingredients_str = ", ".join(selected_ingredients)
            
            # Generate Recipe
            gen_recipe = self.recipe_service.generate(RecipeRequest(
                ingredients=ingredients_str,
                cuisine=diet_strategy,
                dietaryRestrictions=diet_strategy
            ))
            
            # Update Recipe Calories to match allocation
            gen_recipe.calories = meal_cals
            
            # Add to Text Summary (Backward Compat)
            plan_text.append(f"**{meal_name}** (~{meal_cals} kcal)")
            plan_text.append(f"🍽️ **{gen_recipe.title}**")
            plan_text.append(f"_{', '.join(gen_recipe.ingredients[:5])}_")
            plan_text.append("") 
            
            # Add to Structured Plan
            structured_plan.append(RecommendedMeal(
                type=meal_name,
                recipe=gen_recipe,
                suggestionReason=f"Allocated {meal_cals} kcal for your {diet_strategy} plan."
            ))
            
        return DietRecommendationResponse(
            caloriesConsumedEstimate=est_cals,
            caloriesRemaining=int(rem),
            nutritionalAnalysis=f"Analyzed '{request.foodItem}'. Strategy: {diet_strategy}",
            nextMealSuggestion="\n".join(plan_text),
            dayPlan=structured_plan
        )
