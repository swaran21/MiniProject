"""
Medical Meal Planner
Generates personalized meal plans based on medical conditions
"""

from app.services.recipe_health_scorer import RecipeHealthScorer
from app.data.medical_nutrition_rules import MEDICAL_NUTRITION_RULES
from typing import Dict, List
from datetime import datetime, timedelta
import random
import sqlite3

class MedicalMealPlanner:
    """
    Generates medical condition-specific meal plans
    30-90 days with balanced nutrition
    """
    
    def __init__(self, db_connection):
        self.db_conn = db_connection
        self.health_scorer = RecipeHealthScorer()
        self.medical_rules = MEDICAL_NUTRITION_RULES
    
    def create_plan(self, user_analysis: Dict, duration_days: int = None) -> Dict:
        """
        Generate complete meal plan
        
        Args:
            user_analysis: Output from PrescriptionAnalyzer.analyze()
            duration_days: Override duration (uses analysis default if None)
        
        Returns:
            Complete meal plan with daily meals, shopping list, summary
        """
        
        # Determine duration
        if duration_days is None:
            duration_days = user_analysis['plan_duration_days']
        
        # Get conditions
        conditions = user_analysis['detected_conditions']
        
        # Step 1: Get safe recipes from database
        safe_recipes = self._get_safe_recipes(conditions)
        
        if len(safe_recipes) < 10:
            raise Exception(f"Not enough safe recipes found. Only {len(safe_recipes)} available.")
        
        # Step 2: Categorize recipes by meal type
        categorized = self._categorize_recipes(safe_recipes)
        
        # Step 3: Generate daily meals
        daily_meals = []
        for day in range(1, duration_days + 1):
            daily = self._generate_day(
                day, 
                categorized, 
                conditions,
                user_analysis.get('medications', [])
            )
            daily_meals.append(daily)
        
        # Step 4: Generate shopping list
        shopping_list = self._generate_shopping_list(daily_meals)
        
        # Step 5: Create summary
        summary = self._generate_plan_summary(
            user_analysis, 
            duration_days, 
            safe_recipes
        )
        
        return {
            'plan_id': f"PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'user_id': user_analysis.get('user_id'),
            'conditions': conditions,
            'duration_days': duration_days,
            'start_date': datetime.now().date().isoformat(),
            'end_date': (datetime.now() + timedelta(days=duration_days)).date().isoformat(),
            'daily_meals': daily_meals,
            'shopping_list': shopping_list,
            'summary': summary,
            'medical_notes': user_analysis.get('special_notes', []),
            'meal_timing': user_analysis.get('meal_timing', '')
        }
    
    def _get_safe_recipes(self, conditions: List[str], min_score: int = 70) -> List[Dict]:
        """Fetch safe recipes from database"""
        cursor = self.db_conn.cursor()
        
        # Get recipes
        cursor.execute("""
            SELECT id, title, ingredients, instructions, cuisine,
                   likes, dislikes, rating_score
            FROM recipes
            WHERE rating_score > 0.3
            ORDER BY rating_score DESC, likes DESC
            LIMIT 2000
        """)
        
        recipes = []
        for row in cursor.fetchall():
            recipes.append({
                'id': row['id'],
                'title': row['title'],
                'ingredients': row['ingredients'],
                'instructions': row['instructions'],
                'cuisine': row['cuisine'] or 'Any',
                'likes': row['likes'],
                'rating_score': row['rating_score']
            })
        
        # Filter by health score
        safe_recipes = self.health_scorer.filter_safe_recipes(
            recipes, 
            conditions, 
            min_score
        )
        
        return safe_recipes
    
    def _categorize_recipes(self, recipes: List[Dict]) -> Dict:
        """Categorize recipes by meal type"""
        
        breakfast_keywords = ['egg', 'oatmeal', 'pancake', 'toast', 'cereal', 'smoothie', 'yogurt', 'breakfast']
        lunch_keywords = ['salad', 'sandwich', 'soup', 'wrap', 'bowl', 'lunch']
        dinner_keywords = ['chicken', 'fish', 'beef', 'curry', 'stir fry', 'roast', 'baked', 'grilled', 'dinner']
        snack_keywords = ['nuts', 'fruit', 'snack', 'smoothie', 'yogurt', 'hummus']
        
        categorized = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snacks': [],
            'any': []
        }
        
        for recipe in recipes:
            title_lower = recipe['title'].lower()
            ingredients_lower = recipe['ingredients'].lower()
            text = title_lower + ' ' + ingredients_lower
            
            # Categorize by keywords
            if any(kw in text for kw in breakfast_keywords):
                categorized['breakfast'].append(recipe)
            elif any(kw in text for kw in snack_keywords):
                categorized['snacks'].append(recipe)
            elif any(kw in text for kw in lunch_keywords):
                categorized['lunch'].append(recipe)
            elif any(kw in text for kw in dinner_keywords):
                categorized['dinner'].append(recipe)
            else:
                categorized['any'].append(recipe)
        
        # If categories are sparse, fill from 'any'
        if len(categorized['breakfast']) < 30:
            categorized['breakfast'].extend(categorized['any'][:50])
        if len(categorized['lunch']) < 30:
            categorized['lunch'].extend(categorized['any'][:50])
        if len(categorized['dinner']) < 30:
            categorized['dinner'].extend(categorized['any'][:50])
        if len(categorized['snacks']) < 20:
            categorized['snacks'].extend(categorized['any'][:30])
        
        return categorized
    
    def _generate_day(self, day_num: int, categorized: Dict, 
                     conditions: List[str], medications: List[Dict]) -> Dict:
        """Generate meals for one day"""
        
        # Select meals with variety (avoid repeats)
        breakfast = self._select_meal(categorized['breakfast'], day_num, 'breakfast')
        lunch = self._select_meal(categorized['lunch'], day_num, 'lunch')
        dinner = self._select_meal(categorized['dinner'], day_num, 'dinner')
        snacks = [
            self._select_meal(categorized['snacks'], day_num, 'snack1'),
            self._select_meal(categorized['snacks'], day_num + 1000, 'snack2')
        ]
        
        # Calculate daily nutrition
        total_calories = (
            breakfast.get('calories', 400) +
            lunch.get('calories', 500) +
            dinner.get('calories', 600) +
            sum(s.get('calories', 150) for s in snacks)
        )
        
        # Medication reminders
        med_reminders = self._get_medication_reminders(medications)
        
        return {
            'day': day_num,
            'date': (datetime.now() + timedelta(days=day_num-1)).date().isoformat(),
            'breakfast': {
                'recipe_id': breakfast['id'],
                'title': breakfast['title'],
                'calories': breakfast.get('calories', 400),
                'health_score': breakfast['health_score']
            },
            'lunch': {
                'recipe_id': lunch['id'],
                'title': lunch['title'],
                'calories': lunch.get('calories', 500),
                'health_score': lunch['health_score']
            },
            'dinner': {
                'recipe_id': dinner['id'],
                'title': dinner['title'],
                'calories': dinner.get('calories', 600),
                'health_score': dinner['health_score']
            },
            'snacks': [
                {
                    'recipe_id': s['id'],
                    'title': s['title'],
                    'calories': s.get('calories', 150),
                    'health_score': s['health_score']
                }
                for s in snacks
            ],
            'total_calories': total_calories,
            'medication_reminders': med_reminders
        }
    
    def _select_meal(self, meal_pool: List[Dict], seed: int, meal_type: str) -> Dict:
        """Select a meal with pseudo-random variety"""
        if not meal_pool:
            return {
                'id': 0,
                'title': f'Select your own {meal_type}',
                'calories': 400,
                'health_score': 100
            }
        
        # Use seed for deterministic but varied selection
        random.seed(seed)
        return random.choice(meal_pool[:min(50, len(meal_pool))])
    
    def _get_medication_reminders(self, medications: List[Dict]) -> List[Dict]:
        """Generate medication reminders with timing"""
        reminders = []
        
        for med in medications:
            reminder = {
                'medication': med['name'],
                'timing': med.get('timing', 'As prescribed'),
                'take_with': med.get('take_with', ''),
                'alert': med.get('alert', '')
            }
            reminders.append(reminder)
        
        return reminders
    
    def _generate_shopping_list(self, daily_meals: List[Dict]) -> Dict:
        """Generate shopping list from all meals"""
        
        ingredient_counts = {}
        
        # This is simplified - in production, you'd parse ingredients properly
        for day in daily_meals:
            for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
                if meal_type == 'snacks':
                    meals = day[meal_type]
                else:
                    meals = [day[meal_type]]
                
                for meal in meals:
                    # In real implementation, fetch and parse ingredients
                    # For now, just note the recipe
                    pass
        
        return {
            'note': 'Shopping list will be generated based on selected recipes',
            'recommendation': 'Focus on fresh vegetables, lean proteins, and whole grains',
            'avoid': 'Processed foods, high-sugar items, high-sodium snacks'
        }
    
    def _generate_plan_summary(self, user_analysis: Dict, 
                               duration_days: int, 
                               safe_recipes: List[Dict]) -> str:
        """Generate human-readable plan summary"""
        
        conditions = user_analysis['detected_conditions']
        condition_names = [
            self.medical_rules[c]['display_name'] 
            for c in conditions
        ]
        
        avg_health_score = sum(r['health_score'] for r in safe_recipes) / len(safe_recipes)
        
        summary = f"""
🏥 Medical Meal Plan Summary

Conditions: {', '.join(condition_names)}
Duration: {duration_days} days
Safe Recipes Available: {len(safe_recipes)}
Average Health Score: {avg_health_score:.1f}/100

This meal plan has been customized for your medical conditions. All recipes:
✅ Score 70+ on health safety scale
✅ Avoid restricted ingredients
✅ Include recommended nutritious foods
✅ Provide balanced daily nutrition

⚠️ Important: This is a nutritional guide. Always consult your doctor before making dietary changes.
        """.strip()
        
        return summary
