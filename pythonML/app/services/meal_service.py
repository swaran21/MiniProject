from app.models import UserProfile, MealPlanResponse
from app.utils.data_consts import MEAL_OPTIONS
import random

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
