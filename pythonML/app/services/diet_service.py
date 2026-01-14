"""
Diet Service - ML-Powered Dietary Recommendation Engine

Architecture:
- Hybrid Approach: Rule-Based Calculations + ML-Based Preferences
- KNN Collaborative Filtering: "Users like you succeeded with X diet"
- Singleton Pattern: Model loaded ONCE per application lifecycle
"""

import logging
import pickle
import pandas as pd
import os
import random
from typing import Optional
from app.services.recipe_service import RecipeService
from app.services.meal_service import MealPlanService
from app.services.nutrition_service import NutritionService
from app.models import DietLogRequest, DietRecommendationResponse, RecipeRequest, RecommendedMeal

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GLOBAL MODEL CACHE (Singleton Pattern)
# Ensures we load the ML model ONCE per application, not per request
# This prevents loading the 15MB model hundreds of times per second
_ML_MODEL_CACHE: Optional[object] = None
_ML_DATA_CACHE: Optional[pd.DataFrame] = None
_CACHE_LOADED = False


class DietService:
    """
    ML-Powered Diet Recommendation Service
    
    Key Features:
    1. KNN-based diet strategy prediction (collaborative filtering)
    2. BMR-based calorie budget calculation
    3. Real-time nutrition analysis
    4. Dynamic meal schedule generation
    """
    
    def __init__(self):
        self.model_path = "app/models/diet_model.pkl"
        self.data_path = "data/training/diet_recommendations/diet_recommendations_dataset.csv"
        
        # Load model into global cache (singleton pattern)
        self._ensure_model_loaded()
        
        # Initialize services
        self.recipe_service = RecipeService()
        self.mp_service = MealPlanService()
        self.nutrition_service = NutritionService()
        
        # Expanded ingredient database (strategy-specific)
        self.diet_ingredients = {
            'Keto': [
                'chicken breast', 'salmon', 'avocado', 'spinach', 'broccoli',
                'eggs', 'cheese', 'bacon', 'cauliflower', 'zucchini',
                'olive oil', 'butter', 'almonds', 'macadamia nuts', 'beef'
            ],
            'Low-Carb': [
                'lean protein', 'fish', 'tofu', 'vegetables', 'leafy greens',
                'bell peppers', 'mushrooms', 'asparagus', 'green beans', 'turkey'
            ],
            'High-Protein': [
                'chicken', 'turkey', 'fish', 'eggs', 'greek yogurt',
                'cottage cheese', 'lentils', 'chickpeas', 'quinoa', 'tempeh'
            ],
            'Vegan': [
                'tofu', 'tempeh', 'chickpeas', 'lentils', 'quinoa',
                'black beans', 'spinach', 'kale', 'nutritional yeast', 'tahini'
            ],
            'Mediterranean': [
                'olive oil', 'fish', 'tomatoes', 'cucumbers', 'olives',
                'feta cheese', 'whole grains', 'legumes', 'fresh herbs', 'hummus'
            ],
            'Balanced': [
                'whole grains', 'lean protein', 'vegetables', 'fruits', 'healthy fats',
                'brown rice', 'chicken', 'salmon', 'sweet potato', 'mixed greens'
            ]
        }
    
    def _ensure_model_loaded(self):
        """
        Loads ML model into global memory (singleton pattern)
        
        Performance: Called only ONCE per application lifecycle
        Error Handling: Logs failures instead of silent pass
        """
        global _ML_MODEL_CACHE, _ML_DATA_CACHE, _CACHE_LOADED
        
        if _CACHE_LOADED:
            return  # Already loaded
        
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.data_path):
                # Load KNN model
                with open(self.model_path, 'rb') as f:
                    _ML_MODEL_CACHE = pickle.load(f)
                
                # Load training dataset
                _ML_DATA_CACHE = pd.read_csv(self.data_path)
                
                _CACHE_LOADED = True
                logger.info(f"✅ ML Model & Data Loaded Successfully")
                logger.info(f"   Model: {self.model_path}")
                logger.info(f"   Data: {_ML_DATA_CACHE.shape[0]} samples")
            else:
                logger.warning(f"⚠️ Model files not found:")
                logger.warning(f"   Model: {self.model_path} (exists: {os.path.exists(self.model_path)})")
                logger.warning(f"   Data: {self.data_path} (exists: {os.path.exists(self.data_path)})")
                logger.warning("   Falling back to 'Balanced' diet for all users")
                
        except Exception as e:
            logger.error(f"❌ Failed to load ML model: {str(e)}", exc_info=True)
            logger.error("   System will use fallback 'Balanced' diet strategy")
    
    def get_predicted_strategy(self, user_profile) -> str:
        """
        Uses KNN to predict optimal diet strategy based on similar users
        
        Algorithm:
        1. Calculate user's BMI
        2. Find K=5 nearest neighbors (users with similar Age, Weight, Height, BMI)
        3. Vote: "What diet worked for them?"
        4. Return majority diet strategy
        
        Args:
            user_profile: User's physical profile
        
        Returns:
            Diet strategy name (e.g., 'Keto', 'Low-Carb', 'Balanced')
        """
        # Fallback if model not loaded
        if _ML_MODEL_CACHE is None or _ML_DATA_CACHE is None:
            logger.warning("ML model not available, using Balanced diet")
            return "Balanced"
        
        try:
            # Extract KNN model
            clf = _ML_MODEL_CACHE['model'] if isinstance(_ML_MODEL_CACHE, dict) else _ML_MODEL_CACHE
            
            # Feature engineering
            features = ['Age', 'Weight_kg', 'Height_cm', 'BMI']
            
            # Calculate BMI
            height_m = user_profile.heightCm / 100.0
            bmi = user_profile.weightKg / (height_m ** 2)
            
            # Create feature vector
            user_vector = [[
                user_profile.age,
                user_profile.weightKg,
                user_profile.heightCm,
                bmi
            ]]
            input_df = pd.DataFrame(user_vector, columns=features)
            
            # Find K-Nearest Neighbors (K=5)
            # Question: "Who are the 5 users most physically similar to me?"
            distances, neighbor_indices = clf.kneighbors(input_df)
            
            # Collaborative Filtering Vote
            # Question: "What diet strategy worked for them?"
            similar_users = _ML_DATA_CACHE.iloc[neighbor_indices[0]]
            diet_votes = similar_users['Diet_Recommendation'].mode()
            
            # Get majority vote
            predicted_strategy = diet_votes[0] if not diet_votes.empty else "Balanced"
            
            logger.info(f"🧠 ML Prediction for User (BMI: {bmi:.1f}): {predicted_strategy}")
            logger.info(f"   Similar users' diets: {similar_users['Diet_Recommendation'].value_counts().to_dict()}")
            
            return predicted_strategy
        
        except Exception as e:
            logger.error(f"❌ ML Prediction Error: {str(e)}", exc_info=True)
            return "Balanced"
    
    def recommend(self, request: DietLogRequest) -> DietRecommendationResponse:
        """
        Main recommendation engine - combines ML prediction with nutritional science
        
        Flow:
        1. Analyze current meal calories (NutritionService)
        2. Calculate remaining calorie budget (MealPlanService - BMR)
        3. Predict optimal diet strategy (KNN ML Model)
        4. Generate remaining meals that fit strategy + budget
        
        Args:
            request: User's diet log (what they ate + profile)
        
        Returns:
            Personalized meal plan for rest of day
        """
        # Step 1: Real-time Nutrition Analysis
        food_item = request.foodItem.lower()
        estimated_calories = self.nutrition_service.estimate_meal_calories(food_item)
        
        # Step 2: Calculate Metabolic Budget (BMR-based)
        bmr_daily_limit = self.mp_service._calculate_bmr(request.userProfile)
        calories_remaining = bmr_daily_limit - estimated_calories
        
        # Step 3: Get AI Strategy Prediction
        diet_strategy = self.get_predicted_strategy(request.userProfile)
        
        # Step 4: Determine Remaining Meal Schedule
        current_meal_type = request.mealType.lower() if request.mealType else "lunch"
        remaining_schedule = self._get_remaining_schedule(current_meal_type)
        
        # Step 5: Generate Personalized Meal Plan
        structured_plan = []
        plan_summary = [
            f"### 🥗 Personalized Plan ({diet_strategy})",
            f"**Remaining Budget**: {int(calories_remaining)} kcal"
        ]
        
        for meal_name, calorie_ratio in remaining_schedule:
            # Calculate target calories for this meal
            target_calories = max(200, int(calories_remaining * calorie_ratio))
            
            # Get strategy-specific ingredients
            base_ingredients = self._get_base_ingredients(diet_strategy)
            
            # Generate recipe that matches strategy AND calorie target
            recipe_request = RecipeRequest(
                ingredients=base_ingredients,
                cuisine=diet_strategy,  # Hint for recipe style
                dietaryRestrictions=diet_strategy
            )
            
            generated_recipe = self.recipe_service.generate(recipe_request)
            
            # Add to structured plan
            structured_plan.append(RecommendedMeal(
                type=meal_name,
                recipe=generated_recipe,
                suggestionReason=f"Matches your {diet_strategy} profile ({target_calories} kcal target)"
            ))
            
            plan_summary.append(
                f"- **{meal_name}**: {generated_recipe.title} "
                f"({generated_recipe.calories} kcal)"
            )
        
        return DietRecommendationResponse(
            caloriesConsumedEstimate=estimated_calories,
            caloriesRemaining=int(calories_remaining),
            nutritionalAnalysis=f"Logged: {food_item} (~{estimated_calories} kcal)",
            nextMealSuggestion="\n".join(plan_summary),
            dayPlan=structured_plan
        )
    
    def _get_remaining_schedule(self, current_meal: str):
        """
        Returns dynamic meal schedule based on time of day
        
        Returns:
            List of (MealName, CalorieRatio) tuples
            
        Example:
            If current_meal = "breakfast" → [("Lunch", 0.50), ("Dinner", 0.50)]
            If current_meal = "lunch" → [("Snack", 0.20), ("Dinner", 0.80)]
        """
        schedule_map = {
            'breakfast': [("Lunch", 0.40), ("Snack", 0.10), ("Dinner", 0.50)],
            'lunch': [("Snack", 0.20), ("Dinner", 0.80)],
            'dinner': [("Late Snack", 1.0)],
            'snack': [("Next Meal", 1.0)]
        }
        
        # Find matching schedule
        for key, schedule in schedule_map.items():
            if key in current_meal:
                return schedule
        
        # Default fallback
        return [("Next Meal", 1.0)]
    
    def _get_base_ingredients(self, strategy: str) -> str:
        """
        Returns strategy-specific ingredients to inspire recipe generation
        
        Args:
            strategy: Diet strategy name (e.g., 'Keto', 'Vegan')
        
        Returns:
            Comma-separated ingredient string
        """
        if strategy in self.diet_ingredients:
            # Return 3-5 random ingredients from the strategy
            ingredients = random.sample(
                self.diet_ingredients[strategy],
                k=min(5, len(self.diet_ingredients[strategy]))
            )
            return ", ".join(ingredients)
        
        # Fallback to balanced
        return "whole grains, lean protein, vegetables"
