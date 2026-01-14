"""
Meal Plan Service - ML-Powered Diet Strategy Prediction

Architecture:
- KNN-based diet strategy prediction (collaborative filtering)
- BMR calculation with activity level adjustment
- Single-day meal plan generation
- Singleton pattern for ML model caching
"""

import logging
import pandas as pd
import pickle
import os
import random
from typing import Optional
from app.models import UserProfile, MealPlanResponse, RecipeRequest, Meal
from app.services.recipe_service import RecipeService

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GLOBAL MODEL CACHE (Singleton Pattern)
# Ensures we load the ML model ONCE per application, not per request
_MEAL_MODEL_CACHE: Optional[object] = None
_MEAL_DATA_CACHE: Optional[pd.DataFrame] = None
_MEAL_CACHE_LOADED = False


class MealPlanService:
    """
    General-purpose meal planning service
    
    Features:
    1. KNN-based diet strategy prediction
    2. BMR calculation (Mifflin-St Jeor equation)
    3. Activity level adjustment
    4. Single-day meal generation (4 meals)
    
    Note: For medical condition-aware planning, use MedicalMealPlanner instead
    """
    
    def __init__(self):
        self.model_path = "app/models/diet_model.pkl"
        self.data_path = "data/training/diet_recommendations/diet_recommendations_dataset.csv"
        
        # Ensure model loaded into global cache (singleton)
        self._ensure_model_loaded()
        
        # Initialize recipe service
        self.recipe_service = RecipeService()
    
    def _ensure_model_loaded(self):
        """
        Loads ML model into global memory (singleton pattern)
        
        Performance: Called only ONCE per application lifecycle
        Error Handling: Logs failures instead of silent pass
        """
        global _MEAL_MODEL_CACHE, _MEAL_DATA_CACHE, _MEAL_CACHE_LOADED
        
        if _MEAL_CACHE_LOADED:
            return  # Already loaded
        
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.data_path):
                # Load KNN model
                with open(self.model_path, 'rb') as f:
                    _MEAL_MODEL_CACHE = pickle.load(f)
                
                # Load training dataset
                _MEAL_DATA_CACHE = pd.read_csv(self.data_path)
                
                _MEAL_CACHE_LOADED = True
                logger.info("✅ MealPlanService: ML Model & Data Loaded")
                logger.info(f"   Model: {self.model_path}")
                logger.info(f"   Data: {_MEAL_DATA_CACHE.shape[0]} samples")
            else:
                logger.warning(f"⚠️ MealPlanService: Model files not found")
                logger.warning(f"   Model: {self.model_path} (exists: {os.path.exists(self.model_path)})")
                logger.warning(f"   Data: {self.data_path} (exists: {os.path.exists(self.data_path)})")
                logger.warning("   Falling back to 'Balanced' diet for all users")
                
        except Exception as e:
            logger.error(f"❌ MealPlanService: Failed to load ML model: {str(e)}", exc_info=True)
            logger.error("   System will use fallback 'Balanced' diet strategy")
    
    def _predict_strategy(self, profile: UserProfile) -> str:
        """
        Uses KNN to predict optimal diet strategy
        
        Algorithm:
        1. Calculate user's BMI
        2. Find K=5 nearest neighbors (similar Age/Weight/Height/BMI)
        3. Vote: "What diet worked for them?"
        4. Return majority diet strategy
        
        Args:
            profile: User's physical profile
        
        Returns:
            Diet strategy name (e.g., 'Keto', 'Balanced')
        """
        if _MEAL_MODEL_CACHE is None or _MEAL_DATA_CACHE is None:
            logger.warning("ML model not available, using Balanced diet")
            return "Balanced"
        
        try:
            # Extract KNN model
            clf = _MEAL_MODEL_CACHE['model'] if isinstance(_MEAL_MODEL_CACHE, dict) else _MEAL_MODEL_CACHE
            features = _MEAL_MODEL_CACHE['features'] if isinstance(_MEAL_MODEL_CACHE, dict) else ['Age', 'Weight_kg', 'Height_cm', 'BMI']
            
            # Calculate BMI
            height_m = profile.heightCm / 100.0
            bmi = profile.weightKg / (height_m ** 2)
            
            # Create feature vector
            vals = {
                'Age': profile.age,
                'Weight_kg': profile.weightKg,
                'Height_cm': profile.heightCm,
                'BMI': bmi
            }
            
            # Ensure all features exist
            if all(f in vals for f in features):
                vec = [vals[f] for f in features]
                input_df = pd.DataFrame([vec], columns=features)
                
                # Find K-Nearest Neighbors
                _, neighbor_indices = clf.kneighbors(input_df)
                
                # Vote: What diet worked for similar users?
                similar_users = _MEAL_DATA_CACHE.iloc[neighbor_indices[0]]
                diet_votes = similar_users['Diet_Recommendation'].mode()
                
                predicted_strategy = diet_votes[0] if not diet_votes.empty else "Balanced"
                
                logger.info(f"🧠 ML Prediction for User (BMI: {bmi:.1f}): {predicted_strategy}")
                
                return predicted_strategy
            
        except Exception as e:
            logger.error(f"❌ Prediction Error: {str(e)}", exc_info=True)
        
        return "Balanced"
    
    def _calculate_bmr(self, profile: UserProfile) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor equation
        
        Formula:
        - Men: BMR = (10 × weight) + (6.25 × height) - (5 × age) + 5
        - Women: BMR = (10 × weight) + (6.25 × height) - (5 × age) - 161
        
        Then adjusted for:
        - Activity level (sedentary=1.2x, moderate=1.55x, active=1.7x)
        - Health goals (lose weight=-500, gain weight=+500)
        
        Args:
            profile: User's physical profile and goals
        
        Returns:
            Daily calorie target
        """
        # Mifflin-St Jeor equation
        gender_factor = 5 if profile.gender.lower() == "male" else -161
        bmr = (10 * profile.weightKg) + (6.25 * profile.heightCm) - (5 * profile.age) + gender_factor
        
        # Activity level multiplier
        activity_multipliers = {
            "sedentary": 1.2,
            "moderate": 1.55,
            "active": 1.7,
            "very active": 1.9
        }
        activity_factor = activity_multipliers.get(profile.activityLevel.lower(), 1.2)
        
        # Goal adjustment
        goals = profile.healthGoals.lower()
        goal_adjustment = 500 if "gain" in goals else -500 if "lose" in goals else 0
        
        total_calories = (bmr * activity_factor) + goal_adjustment
        
        logger.info(f"📊 BMR Calculation: {bmr:.0f} × {activity_factor} + {goal_adjustment} = {total_calories:.0f} kcal")
        
        return total_calories
    
    def create_plan(self, profile: UserProfile) -> MealPlanResponse:
        """
        Generate single-day meal plan with 4 meals
        
        Process:
        1. Calculate daily calorie target (BMR)
        2. Predict diet strategy (KNN ML)
        3. Generate 4 meals (Breakfast, Lunch, Snack, Dinner)
        4. Distribute calories: 25% / 35% / 10% / 30%
        
        Args:
            profile: User's profile (age, weight, activity, goals)
        
        Returns:
            Single day meal plan with 4 meals
        """
        # Step 1: Calculate calorie budget
        target_calories = self._calculate_bmr(profile)
        
        # Step 2: Predict diet strategy using ML
        strategy = self._predict_strategy(profile)
        
        logger.info(f"🍽️ Generating Plan for {profile.age}yo, Goal: {profile.healthGoals}")
        logger.info(f"   Strategy: {strategy}, Target: {int(target_calories)} kcal")
        
        meals = []
        
        # Step 3: Define meal structure (type, calorie ratio, base ingredients)
        meal_structure = [
            ("Breakfast", 0.25, ["Oats", "Eggs", "Yogurt", "Berries", "Avocado"]),
            ("Lunch", 0.35, ["Chicken", "Rice", "Quinoa", "Salad", "Turkey"]),
            ("Snack", 0.10, ["Nuts", "Fruit", "Smoothie", "Protein Bar"]),
            ("Dinner", 0.30, ["Fish", "Steak", "Tofu", "Vegetables", "Salmon"])
        ]
        
        # Step 4: Generate each meal
        for meal_type, calorie_ratio, base_ingredients in meal_structure:
            meal_target = int(target_calories * calorie_ratio)
            
            # Select random ingredients for variety
            selected_ingredients = ", ".join(random.sample(base_ingredients, min(2, len(base_ingredients))))
            
            # Generate recipe using ML strategy
            recipe_request = RecipeRequest(
                ingredients=selected_ingredients,
                cuisine=strategy,
                dietaryRestrictions=strategy
            )
            generated_recipe = self.recipe_service.generate(recipe_request)
            
            # Use real calorie calculation from RecipeService
            # (RecipeService uses NutritionService for accuracy)
            meals.append(Meal(
                name=generated_recipe.title,
                type=meal_type,
                calories=generated_recipe.calories,  # Real calories!
                macros=f"{strategy} Optimized ({generated_recipe.calories} kcal)",
                ingredients=generated_recipe.ingredients,
                instructions=generated_recipe.instructions
            ))
        
        return MealPlanResponse(
            goal=profile.healthGoals,
            totalDailyCalories=int(target_calories),
            suggestion=f"AI Recommendation: {strategy} Diet. ({int(target_calories)} kcal)",
            meals=meals
        )
