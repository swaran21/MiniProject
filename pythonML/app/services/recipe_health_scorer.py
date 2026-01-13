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
    
    def calculate_health_score(self, recipe: Dict, conditions: List[str]) -> int:
        """
        Calculate health score 0-100 for a recipe
        
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
        
        ingredients_lower = [ing.lower() for ing in ingredients]
        ingredients_text = ' '.join(ingredients_lower)
        
        # Check against each condition
        for condition in conditions:
            if condition not in self.medical_rules:
                continue
                
            rules = self.medical_rules[condition]
            
            # Check for restricted foods
            for bad_food in rules['foods_to_avoid']:
                bad_food_lower = bad_food.lower()
                
                # Check if bad food appears in any ingredient
                if any(bad_food_lower in ing for ing in ingredients_lower):
                    score -= 40  # Heavy penalty for restricted foods
                    break  # Count each bad food only once
            
            # Bonus for recommended foods
            for good_food in rules['foods_to_eat']:
                good_food_lower = good_food.lower()
                
                if any(good_food_lower in ing for ing in ingredients_lower):
                    score += 5  # Small bonus
        
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
            
            # Check each ingredient against restrictions
            for ingredient in ingredients_lower:
                for bad_food in rules['foods_to_avoid']:
                    if bad_food.lower() in ingredient:
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
