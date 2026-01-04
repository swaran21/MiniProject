"""Test Meal Plan Service Integration with Nutrition"""
from app.services.meal_service import MealPlanService
from app.models import UserProfile
import json

print("="*60)
print("TESTING MEAL PLAN SERVICE - NUTRITION INTEGRATION")
print("="*60)

# Create a test profile
profile = UserProfile(
    weightKg=70,
    heightCm=170,
    age=25,
    gender='M',
    activityLevel='Moderate',
    healthGoals='Balanced',
    dietaryRestrictions='None'
)

# Generate meal plan
mp_service = MealPlanService()
result = mp_service.create_plan(profile)

print(f"\n📊 RESULTS:")
print(f"  Target Daily Calories: {result.totalDailyCalories} kcal")
print(f"  Number of Meals: {len(result.meals)}")
print(f"\n🍽️ INDIVIDUAL MEALS:")

total_from_meals = 0
for i, meal in enumerate(result.meals, 1):
    print(f"\n  {i}. {meal.type}: {meal.name}")
    print(f"     Calories: {meal.calories} kcal")
    print(f"     Macros: {meal.macros}")
    total_from_meals += meal.calories

print(f"\n📈 ANALYSIS:")
print(f"  Sum of all meals: {total_from_meals} kcal")
print(f"  Target was: {result.totalDailyCalories} kcal")
print(f"  Difference: {abs(total_from_meals - result.totalDailyCalories)} kcal")

# Check if calories are realistic
realistic = all(200 < m.calories < 1000 for m in result.meals)
print(f"\n✅ All meals have realistic calories (200-1000 kcal): {'YES' if realistic else 'NO'}")

# Check if using real nutrition (not just allocated targets)
# Real nutrition should vary, not be exact percentages
breakfast_cal = result.meals[0].calories if len(result.meals) > 0 else 0
expected_25_percent = result.totalDailyCalories * 0.25

variance = abs(breakfast_cal - expected_25_percent)
using_real_nutrition = variance > 50  # If more than 50 cal difference, it's using real data

print(f"\n✅ Using real nutrition (not just allocated %): {'YES' if using_real_nutrition else 'NO'}")
print(f"   Breakfast: {breakfast_cal} kcal")
print(f"   Expected 25% allocation: {expected_25_percent} kcal")
print(f"   Variance: {variance} kcal {'(REAL DATA!)' if variance > 50 else '(Still using allocation?)'}")

print("\n" + "="*60)
print("VERDICT:")
if realistic and using_real_nutrition:
    print("✅ MEAL PLAN SERVICE IS PROPERLY INTEGRATED!")
    print("   • Uses real nutrition calculations")
    print("   • All meal calories are realistic")
else:
    print("⚠️  NEEDS ATTENTION:")
    if not realistic:
        print("   • Some meals have unrealistic calories")
    if not using_real_nutrition:
        print("   • Still using allocated percentages, not real nutrition")
print("="*60)
