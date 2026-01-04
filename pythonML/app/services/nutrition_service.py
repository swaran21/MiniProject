"""
NutritionService - Real calorie and macro calculations from FoodData Central
"""
import json
import os
from typing import List, Dict, Optional
import re

class NutritionService:
    def __init__(self):
        """Initialize nutrition database from FoodData Central"""
        self.nutrition_db = {}
        self._load_fooddata()
    
    def _load_fooddata(self):
        """Load and parse FoodData Central JSON"""
        json_path = "FoodData_Central_foundation_food_json_2025-04-24/FoodData_Central_foundation_food_json_2025-04-24.json"
        
        if not os.path.exists(json_path):
            print(f"⚠️  FoodData Central not found at {json_path}, using defaults")
            self._load_defaults()
            return
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            foods = data.get('FoundationFoods', [])
            print(f"Loading nutrition data from {len(foods)} foundation foods...")
            
            for food in foods:
                description = food.get('description', '').lower()
                nutrients = self._extract_nutrients(food.get('foodNutrients', []))
                
                if nutrients:
                    self.nutrition_db[description] = nutrients
            
            print(f"✅ Loaded {len(self.nutrition_db)} foods into nutrition database")
        
        except Exception as e:
            print(f"⚠️  Error loading FoodData Central: {e}")
            self._load_defaults()
    
    def _extract_nutrients(self, food_nutrients: List[Dict]) -> Dict[str, float]:
        """Extract calories, protein, fat, carbs from nutrient array"""
        nutrients = {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0
        }
        
        for nutrient in food_nutrients:
            nutrient_info = nutrient.get('nutrient', {})
            nutrient_id = nutrient_info.get('id')
            amount = nutrient.get('amount', 0)
            
            # Map nutrient IDs to our keys
            if nutrient_id == 1008:  # Energy (kcal)
                nutrients['calories'] = amount
            elif nutrient_id == 1003:  # Protein
                nutrients['protein'] = amount
            elif nutrient_id == 1004:  # Total lipid (fat)
                nutrients['fat'] = amount
            elif nutrient_id == 1005:  # Carbohydrate
                nutrients['carbs'] = amount
        
        return nutrients
    
    def _load_defaults(self):
        """Load common ingredient defaults if FoodData Central is unavailable"""
        self.nutrition_db = {
            'chicken breast': {'calories': 165, 'protein': 31, 'fat': 3.6, 'carbs': 0},
            'chicken': {'calories': 165, 'protein': 31, 'fat': 3.6, 'carbs': 0},
            'beef': {'calories': 250, 'protein': 26, 'fat': 15, 'carbs': 0},
            'rice': {'calories': 130, 'protein': 2.7, 'fat': 0.3, 'carbs': 28},
            'pasta': {'calories': 131, 'protein': 5, 'fat': 1.1, 'carbs': 25},
            'egg': {'calories': 155, 'protein': 13, 'fat': 11, 'carbs': 1.1},
            'cheese': {'calories': 402, 'protein': 25, 'fat': 33, 'carbs': 1.3},
            'tomato': {'calories': 18, 'protein': 0.9, 'fat': 0.2, 'carbs': 3.9},
            'broccoli': {'calories': 34, 'protein': 2.8, 'fat': 0.4, 'carbs': 7},
            'potato': {'calories': 77, 'protein': 2, 'fat': 0.1, 'carbs': 17},
            'bread': {'calories': 265, 'protein': 9, 'fat': 3.2, 'carbs': 49},
            'milk': {'calories': 42, 'protein': 3.4, 'fat': 1, 'carbs': 5},
            'salmon': {'calories': 208, 'protein': 20, 'fat': 13, 'carbs': 0},
            'apple': {'calories': 52, 'protein': 0.3, 'fat': 0.2, 'carbs': 14},
        }
        print(f"✅ Loaded {len(self.nutrition_db)} default ingredients")
    
    def _fuzzy_match_ingredient(self, ingredient: str) -> Optional[Dict[str, float]]:
        """Find best match for ingredient in database using fuzzy matching"""
        ingredient_clean = ingredient.lower().strip()
        
        # Remove common words and measurements
        ingredient_clean = re.sub(r'\b(chopped|diced|sliced|fresh|raw|cooked|boiled|grilled|fried|cup|cups|tablespoon|teaspoon|grams?|g|kg|oz|pound|lb)\b', '', ingredient_clean)
        ingredient_clean = ingredient_clean.strip()
        
        # Direct match
        if ingredient_clean in self.nutrition_db:
            return self.nutrition_db[ingredient_clean]
        
        # Partial match (find if any db key contains the ingredient or vice versa)
        for db_food, nutrients in self.nutrition_db.items():
            if ingredient_clean in db_food or db_food in ingredient_clean:
                return nutrients
        
        # No match found
        return None
    
    def estimate_calories(self, ingredients: List[str], serving_size_g: int = 200) -> Dict[str, float]:
        """
        Estimate total nutrition for a list of ingredients
        
        Args:
            ingredients: List of ingredient names
            serving_size_g: Assumed serving size in grams (default 200g per ingredient)
        
        Returns:
            Dictionary with total calories, protein, fat, carbs
        """
        total = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
        matched_count = 0
        
        for ingredient in ingredients:
            nutrients = self._fuzzy_match_ingredient(ingredient)
            
            if nutrients:
                # FoodData Central values are per 100g, scale to serving size
                scaling_factor = serving_size_g / 100.0
                
                total['calories'] += nutrients['calories'] * scaling_factor
                total['protein'] += nutrients['protein'] * scaling_factor
                total['fat'] += nutrients['fat'] * scaling_factor
                total['carbs'] += nutrients['carbs'] * scaling_factor
                matched_count += 1
            else:
                # Use average fallback for unmatched ingredients
                total['calories'] += 150  # Average calories per 200g serving
                total['protein'] += 5
                total['fat'] += 3
                total['carbs'] += 20
        
        # Round to integers
        return {
            'calories': int(total['calories']),
            'protein': round(total['protein'], 1),
            'fat': round(total['fat'], 1),
            'carbs': round(total['carbs'], 1),
            'matched_ingredients': matched_count,
            'total_ingredients': len(ingredients)
        }
    
    def estimate_meal_calories(self, ingredients_str: str) -> int:
        """
        Simple wrapper to get just calorie estimate from comma-separated ingredient string
        
        Args:
            ingredients_str: Comma-separated ingredient string
        
        Returns:
            Estimated calories as integer
        """
        ingredients = [i.strip() for i in ingredients_str.split(',') if i.strip()]
        nutrition = self.estimate_calories(ingredients)
        return nutrition['calories']
