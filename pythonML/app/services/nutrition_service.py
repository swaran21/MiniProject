"""
Nutrition Service - USDA FoodData Central Integration

Medical-Grade Nutrition Calculator:
- Uses official USDA FoodData Central database
- Intelligent portion size estimation (category-based heuristics)
- Singleton pattern for performance
- Optimized fuzzy matching
"""

import json
import os
import logging
from typing import Dict, List, Optional
from difflib import get_close_matches

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GLOBAL USDA DATABASE CACHE (Singleton Pattern)
# Load the massive USDA JSON only ONCE per application
_USDA_DATABASE_CACHE: Optional[Dict] = None
_USDA_CACHE_LOADED = False


class NutritionService:
    """
    Medical-Grade Nutrition Calculator using USDA FoodData Central
    
    Features:
    1. Intelligent portion size estimation (no more "200g olive oil"!)
    2. Category-based heuristics for realistic serving sizes
    3. Singleton pattern for database loading (performance)
    4. Optimized fuzzy matching
    """
    
    def __init__(self):
        # Ensure USDA database loaded into global cache
        self._ensure_usda_loaded()
        
        # Category-based default weights (grams)
        # Solves the "200g olive oil" problem!
        self.default_weights = {
            # Fats & Oils (tablespoon portions)
            'oil': 14,          # 1 tbsp olive/canola oil
            'butter': 14,       # 1 tbsp butter
            'ghee': 14,         # 1 tbsp ghee
            'margarine': 14,    # 1 tbsp
            
            # Condiments & Seasonings (teaspoon/small portions)
            'salt': 5,          # 1 tsp
            'pepper': 2,        # 1/2 tsp
            'spice': 2,         # 1/2 tsp spices
            'sauce': 30,        # 2 tbsp
            'ketchup': 17,      # 1 tbsp
            'mayonnaise': 15,   # 1 tbsp
            'mustard': 15,      # 1 tbsp
            
            # Sweeteners
            'sugar': 12,        # 1 tbsp
            'honey': 21,        # 1 tbsp
            'syrup': 20,        # 1 tbsp
            
            # Dairy
            'cheese': 28,       # 1 oz (1 slice)
            'milk': 240,        # 1 cup
            'yogurt': 170,      # 6 oz container
            'cream': 30,        # 2 tbsp
            
            # Proteins (typical serving)
            'meat': 113,        # 4 oz (deck of cards)
            'chicken': 113,     # 4 oz
            'beef': 113,        # 4 oz
            'fish': 113,        # 4 oz
            'pork': 113,        # 4 oz
            'tofu': 100,        # 3.5 oz
            'egg': 50,          # 1 large egg
            
            # Nuts & Seeds (handful)
            'nut': 28,          # 1 oz (small handful)
            'almond': 28,
            'walnut': 28,
            'seed': 14,         # 1/2 oz
            
            # Grains (cooked portion)
            'rice': 150,        # 3/4 cup cooked
            'pasta': 140,       # 1 cup cooked
            'bread': 30,        # 1 slice
            'oat': 40,          # 1/2 cup dry
            'quinoa': 150,      # 3/4 cup cooked
            
            # Vegetables (typical serving)
            'vegetable': 100,   # 1 cup raw / 1/2 cup cooked
            'potato': 150,      # 1 medium
            'tomato': 123,      # 1 medium
            'onion': 110,       # 1 medium
            'carrot': 61,       # 1 medium
            
            # Fruits
            'fruit': 100,       # 1 medium fruit
            'apple': 182,       # 1 medium
            'banana': 118,      # 1 medium
            'berry': 150,       # 1 cup
            
            # Default fallback
            'default': 100      # Conservative 100g (safer than 200g)
        }
        
        # Fallback nutrition for common items (if USDA lookup fails)
        self._load_fallback_defaults()
    
    def _ensure_usda_loaded(self):
        """
        Load USDA FoodData Central database into global memory (singleton)
        
        Performance: Loaded ONCE per application startup
        Size: ~30MB JSON file with 5000+ food items
        """
        global _USDA_DATABASE_CACHE, _USDA_CACHE_LOADED
        
        if _USDA_CACHE_LOADED:
            return  # Already loaded
        
        try:
            # Path to USDA data (update to match your actual path)
            usda_path = "data/raw/FoodData_Central_foundation_food_json_2024-10-31/food.json"
            
            if os.path.exists(usda_path):
                logger.info(f"📊 Loading USDA FoodData Central database...")
                
                with open(usda_path, 'r', encoding='utf-8') as f:
                    usda_data = json.load(f)
                
                # Convert to dictionary for faster lookups
                # Key: lowercase food name, Value: nutrients per 100g
                _USDA_DATABASE_CACHE = {}
                
                for food in usda_data.get('FoundationFoods', []):
                    food_name = food.get('description', '').lower()
                    
                    # Extract nutrients per 100g
                    nutrients = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
                    
                    for nutrient in food.get('foodNutrients', []):
                        nutrient_name = nutrient.get('nutrient', {}).get('name', '').lower()
                        amount = nutrient.get('amount', 0)
                        
                        if 'energy' in nutrient_name:
                            nutrients['calories'] = amount
                        elif 'protein' in nutrient_name:
                            nutrients['protein'] = amount
                        elif 'total lipid' in nutrient_name or 'fat' in nutrient_name:
                            nutrients['fat'] = amount
                        elif 'carbohydrate' in nutrient_name:
                            nutrients['carbs'] = amount
                    
                    _USDA_DATABASE_CACHE[food_name] = nutrients
                
                _USDA_CACHE_LOADED = True
                logger.info(f"✅ USDA Database Loaded: {len(_USDA_DATABASE_CACHE)} food items")
                
            else:
                logger.warning(f"⚠️ USDA database not found at: {usda_path}")
                logger.warning("   Using fallback nutrition estimates")
                _USDA_DATABASE_CACHE = {}
                _USDA_CACHE_LOADED = True
                
        except Exception as e:
            logger.error(f"❌ Failed to load USDA database: {str(e)}", exc_info=True)
            logger.error("   System will use fallback nutrition estimates")
            _USDA_DATABASE_CACHE = {}
            _USDA_CACHE_LOADED = True
    
    def _load_fallback_defaults(self):
        """Fallback nutrition data if USDA lookup fails (per 100g)"""
        self.fallback_nutrition = {
            'chicken': {'calories': 165, 'protein': 31, 'fat': 3.6, 'carbs': 0},
            'rice': {'calories': 130, 'protein': 2.7, 'fat': 0.3, 'carbs': 28},
            'oil': {'calories': 884, 'protein': 0, 'fat': 100, 'carbs': 0},
            'egg': {'calories': 155, 'protein': 13, 'fat': 11, 'carbs': 1.1},
            'bread': {'calories': 265, 'protein': 9, 'fat': 3.2, 'carbs': 49},
            'milk': {'calories': 42, 'protein': 3.4, 'fat': 1, 'carbs': 5},
            'apple': {'calories': 52, 'protein': 0.3, 'fat': 0.2, 'carbs': 14},
            'potato': {'calories': 77, 'protein': 2, 'fat': 0.1, 'carbs': 17},
            'default': {'calories': 150, 'protein': 5, 'fat': 5, 'carbs': 20}
        }
    
    def _get_heuristic_weight(self, ingredient_name: str) -> int:
        """
        Estimate realistic portion size based on ingredient category
        
        This solves the "200g olive oil" problem!
        
        Args:
            ingredient_name: Raw ingredient string (e.g., "olive oil", "salt")
        
        Returns:
            Estimated weight in grams based on typical usage
        """
        name = ingredient_name.lower()
        
        # Fats & Oils (small portions)
        if any(keyword in name for keyword in ['oil', 'olive', 'canola', 'vegetable oil']):
            return self.default_weights['oil']
        if any(keyword in name for keyword in ['butter', 'ghee', 'margarine']):
            return self.default_weights['butter']
        
        # Seasonings (very small portions)
        if any(keyword in name for keyword in ['salt', 'pepper', 'cinnamon', 'paprika', 'cumin', 'turmeric', 'garlic powder']):
            return self.default_weights['spice']
        
        # Sweeteners
        if any(keyword in name for keyword in ['sugar', 'honey', 'syrup', 'maple']):
            return self.default_weights.get('sugar', 12)
        
        # Proteins
        if any(keyword in name for keyword in ['chicken', 'beef', 'fish', 'pork', 'steak', 'salmon', 'turkey']):
            return self.default_weights['meat']
        if 'egg' in name:
            return self.default_weights['egg']
        if 'tofu' in name:
            return self.default_weights['tofu']
        
        # Grains
        if any(keyword in name for keyword in ['rice', 'pasta', 'quinoa', 'couscous', 'noodle']):
            return self.default_weights['rice']
        if any(keyword in name for keyword in ['bread', 'toast', 'roll', 'bun']):
            return self.default_weights['bread']
        
        # Dairy
        if any(keyword in name for keyword in ['cheese', 'cheddar', 'mozzarella']):
            return self.default_weights['cheese']
        if 'milk' in name or 'yogurt' in name:
            return self.default_weights.get(name.split()[0], 170)
        
        # Nuts
        if any(keyword in name for keyword in ['nut', 'almond', 'walnut', 'cashew', 'pecan']):
            return self.default_weights['nut']
        
        # Vegetables (larger portions)
        if any(keyword in name for keyword in ['vegetable', 'broccoli', 'spinach', 'kale', 'lettuce', 'carrot', 'tomato']):
            return self.default_weights['vegetable']
        
        # Default conservative estimate
        return self.default_weights['default']
    
    def _fuzzy_match_ingredient(self, ingredient: str) -> Optional[Dict]:
        """
        Find matching food in USDA database using fuzzy matching
        
        Optimization: Uses get_close_matches for faster substring matching
        
        Args:
            ingredient: Ingredient name to search
        
        Returns:
            Nutrients dict if found, None otherwise
        """
        if not _USDA_DATABASE_CACHE:
            return None
        
        ingredient_clean = ingredient.lower().strip()
        
        # Direct match (fastest)
        if ingredient_clean in _USDA_DATABASE_CACHE:
            return _USDA_DATABASE_CACHE[ingredient_clean]
        
        # Fuzzy match (optimized with difflib)
        matches = get_close_matches(ingredient_clean, _USDA_DATABASE_CACHE.keys(), n=1, cutoff=0.6)
        
        if matches:
            logger.info(f"🔍 Fuzzy matched '{ingredient}' → '{matches[0]}'")
            return _USDA_DATABASE_CACHE[matches[0]]
        
        return None
    
    def estimate_calories(self, ingredients: List[str]) -> Dict[str, float]:
        """
        Calculate total nutrition for a list of ingredients
        
        Uses intelligent portion sizing and USDA data
        
        Args:
            ingredients: List of ingredient strings
        
        Returns:
            Dict with total calories, protein, fat, carbs
        """
        total = {'calories': 0.0, 'protein': 0.0, 'fat': 0.0, 'carbs': 0.0}
        
        for ingredient in ingredients:
            # Get nutrients from USDA database
            nutrients = self._fuzzy_match_ingredient(ingredient)
            
            if not nutrients:
                # Fallback to hardcoded estimates
                for key, fallback_nutrients in self.fallback_nutrition.items():
                    if key in ingredient.lower():
                        nutrients = fallback_nutrients
                        break
                
                if not nutrients:
                    nutrients = self.fallback_nutrition['default']
            
            # INTELLIGENT WEIGHT ESTIMATION (fixes the "200g oil" problem!)
            estimated_weight_g = self._get_heuristic_weight(ingredient)
            
            # Scale nutrients from 100g to estimated weight
            scaling_factor = estimated_weight_g / 100.0
            
            logger.info(f"📊 {ingredient}: {estimated_weight_g}g → {nutrients['calories'] * scaling_factor:.0f} kcal")
            
            # Add to totals
            total['calories'] += nutrients['calories'] * scaling_factor
            total['protein'] += nutrients['protein'] * scaling_factor
            total['fat'] += nutrients['fat'] * scaling_factor
            total['carbs'] += nutrients['carbs'] * scaling_factor
        
        return total
    
    def estimate_meal_calories(self, meal_description: str) -> int:
        """
        Estimate calories from a meal description (simple string)
        
        Args:
            meal_description: E.g., "chicken with rice and vegetables"
        
        Returns:
            Estimated total calories
        """
        # Simple word-based extraction
        words = meal_description.lower().split()
        
        # Try to identify food items
        ingredients = []
        for word in words:
            if len(word) > 3 and word not in ['with', 'and', 'the', 'some']:
                ingredients.append(word)
        
        if not ingredients:
            # Fallback: average meal
            logger.warning(f"Could not parse meal: {meal_description}, using average")
            return 500
        
        nutrition = self.estimate_calories(ingredients)
        return int(nutrition['calories'])
