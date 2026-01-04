"""Quick Meal Plan Test"""
from app.services.meal_service import MealPlanService
from app.models import UserProfile

profile = UserProfile(weightKg=70, heightCm=170, age=25, gender='M', activityLevel='Moderate', healthGoals='Balanced', dietaryRestrictions='None')
mp = MealPlanService()
result = mp.create_plan(profile)

print("Target:", result.totalDailyCalories, "kcal")
print("\nMeals:")
for m in result.meals:
    print(f"  {m.type}: {m.calories} kcal - {m.macros}")

total = sum(m.calories for m in result.meals)
print(f"\nTotal from meals: {total} kcal")
print(f"Using real nutrition: {'YES' if abs(total - result.totalDailyCalories) > 100 else 'MAYBE'}")
