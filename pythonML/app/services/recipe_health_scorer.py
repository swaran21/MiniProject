"""
Recipe Health Scorer
Scores recipes 0-100 based on medical conditions
Pure rule-based approach - no ML needed
"""

from data.config.medical_nutrition_rules import MEDICAL_NUTRITION_RULES
from typing import Dict, List
import re

class RecipeHealthScorer:
    """
    Scores recipes based on medical conditions
    Higher score = safer for the user's conditions
    """
    
    def __init__(self):
        self.medical_rules = MEDICAL_NUTRITION_RULES
    
    def _normalize_ingredient(self, ingredient: str) -> List[str]:
        """
        Normalize ingredient to base forms for better matching
        
        Examples:
            'Basmati Rice' -> ['basmati', 'rice']
            'Brown Sugar' -> ['brown', 'sugar']
            'Long-grain White Rice' -> ['long', 'grain', 'white', 'rice']
        
        Returns:
            List of normalized tokens
        """
        # Remove common measurements and quantities
        ignore_words = {'cup', 'cups', 'tablespoon', 'tablespoons', 'teaspoon', 'teaspoons',
                       'tsp', 'tbsp', 'oz', 'ounce', 'ounces', 'pound', 'pounds', 'lb', 'lbs',
                       'gram', 'grams', 'g', 'kg', 'ml', 'liter', 'liters', 'of', 'chopped',
                       'diced', 'sliced', 'minced', 'fresh', 'dried', 'frozen', 'canned'}
        
        # Tokenize and filter
        tokens = re.split(r'[\s,\-()]+', ingredient.lower())
        normalized = [t for t in tokens if t and t not in ignore_words and len(t) > 1]
        return normalized
    
    def _matches_food_item(self, ingredient: str, food_item: str) -> bool:
        """
        Check if ingredient contains the food item using smart matching
        
        CRITICAL FIX: Handles variations!
        - 'white rice' matches: 'Basmati Rice', 'Long-grain Rice', 'White Rice'
        - 'sugar' matches: 'Brown Sugar', 'Cane Sugar', 'Sugar'
        - BUT 'rice' won't match 'price' (word boundaries)
        
        Returns:
            True if ingredient contains the food item
        """
        ingredient_tokens = self._normalize_ingredient(ingredient)
        food_tokens = self._normalize_ingredient(food_item)
        
        # Check each food token with word boundaries
        for food_token in food_tokens:
            # Use word boundary to avoid partial matches
            pattern = r'\b' + re.escape(food_token) + r'\b'
            
            # Check if this token appears in the original ingredient
            if re.search(pattern, ingredient.lower()):
                return True
        
        return False
    
    def calculate_health_score(self, recipe: Dict, conditions: List[str]) -> int:
        """
        Calculate health score 0-100 for a recipe
        
        IMPROVED: Now catches ingredient variations!
        - 'white rice' restriction catches 'Basmati Rice', 'Jasmine Rice', etc.
        - Word boundaries prevent false positives
        
        Args:
            recipe: Recipe dict with ingredients, title, instructions
            conditions: List of user's medical conditions
        
        Returns:
            int score (0-100)
        """
        
        if not conditions:
            return 100  # No restrictions
        
        score = 100  # Start perfect
        
        # Get recipe ingredients as lowercase list
        ingredients = recipe.get('ingredients', [])
        if isinstance(ingredients, str):
            ingredients = [ing.strip() for ing in ingredients.split(';')]
        
        # Check against each condition
        for condition in conditions:
            if condition not in self.medical_rules:
                continue
                
            rules = self.medical_rules[condition]
            
            # Check for restricted foods with improved matching
            for bad_food in rules['foods_to_avoid']:
                # Use smart matching to catch variations
                for ingredient in ingredients:
                    if self._matches_food_item(ingredient, bad_food):
                        score -= 40  # Heavy penalty for restricted foods
                        break  # Count each bad food only once per ingredient
            
            # Bonus for recommended foods
            for good_food in rules['foods_to_eat']:
                for ingredient in ingredients:
                    if self._matches_food_item(ingredient, good_food):
                        score += 5  # Small bonus
                        break  # Count once
        
        # Clamp score to 0-100
        return max(0, min(100, score))
    
    def get_warnings(self, recipe: Dict, conditions: List[str]) -> List[Dict]:
        """
        Get specific warnings about restricted ingredients
        
        Returns:
            List of warnings with severity levels
        """
        warnings = []
        
        ingredients = recipe.get('ingredients', [])
        if isinstance(ingredients, str):
            ingredients = [ing.strip() for ing in ingredients.split(';')]
        
        ingredients_lower = [ing.lower() for ing in ingredients]
        
        for condition in conditions:
            if condition not in self.medical_rules:
                continue
            
            rules = self.medical_rules[condition]
            condition_name = rules['display_name']
            
            # Check each ingredient against restrictions with smart matching
            for ingredient in ingredients:
                for bad_food in rules['foods_to_avoid']:
                    # Use improved matching to catch variations
                    if self._matches_food_item(ingredient, bad_food):
                        warnings.append({
                            'ingredient': ingredient,
                            'condition': condition_name,
                            'reason': f'Restricted for {condition_name}',
                            'severity': 'high',
                            'message': f'⚠️ Contains {bad_food} - avoid for {condition_name}'
                        })
        
        return warnings
    
    def filter_safe_recipes(self, recipes: List[Dict], conditions: List[str], 
                           min_score: int = 70) -> List[Dict]:
        """
        Filter recipes to only include safe ones
        
        Args:
            recipes: List of all recipes
            conditions: User's medical conditions
            min_score: Minimum health score to include (default 70)
        
        Returns:
            List of safe recipes with health scores
        """
        safe_recipes = []
        
        for recipe in recipes:
            health_score = self.calculate_health_score(recipe, conditions)
            
            if health_score >= min_score:
                recipe_copy = recipe.copy()
                recipe_copy['health_score'] = health_score
                recipe_copy['warnings'] = self.get_warnings(recipe, conditions)
                recipe_copy['is_safe'] = health_score >= 80
                safe_recipes.append(recipe_copy)
        
        # Sort by health score (highest first)
        safe_recipes.sort(key=lambda r: r['health_score'], reverse=True)
        
        return safe_recipes
    
    def categorize_recipe(self, recipe: Dict, conditions: List[str]) -> str:
        """
        Categorize recipe as safe, moderate, or avoid
        
        Returns:
            'safe', 'moderate', or 'avoid'
        """
        score = self.calculate_health_score(recipe, conditions)
        
        if score >= 80:
            return 'safe'
        elif score >= 60:
            return 'moderate'
        else:
            return 'avoid'
    
    def get_recipe_recommendations(self, recipe: Dict, conditions: List[str]) -> str:
        """
        Get personalized recommendations for the recipe
        """
        score = self.calculate_health_score(recipe, conditions)
        category = self.categorize_recipe(recipe, conditions)
        
        if category == 'safe':
            return f"✅ This recipe is safe for your conditions (Score: {score}/100)"
        elif category == 'moderate':
            return f"⚠️ This recipe is acceptable but use caution (Score: {score}/100)"
        else:
            return f"❌ Not recommended for your conditions (Score: {score}/100)"
