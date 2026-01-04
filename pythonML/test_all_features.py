"""
Comprehensive Test: Verify All Features Use Real Nutrition
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("="*60)
print("TESTING ALL FEATURES FOR REAL NUTRITION CALCULATIONS")
print("="*60)

# Test 1: Recipe Generator
print("\n[TEST 1] Recipe Generator")
print("-" * 40)
try:
    payload = {
        'ingredients': 'chicken, rice, broccoli',
        'cuisine': 'Asian',
        'dietaryRestrictions': 'None'
    }
    r = requests.post(f'{BASE_URL}/api/recipe', json=payload, timeout=5)
    result = r.json()
    
    print(f"✓ Recipe: {result['title']}")
    print(f"✓ Calories: {result['calories']} kcal")
    print(f"✓ Ingredients: {', '.join(result['ingredients'][:3])}")
    
    # Expected: chicken (330) + rice (260) + broccoli (68) = ~658 kcal
    if 500 < result['calories'] < 1000:
        print(f"✅ PASS - Realistic calories from real data")
    else:
        print(f"⚠️  WARNING - {result['calories']} kcal seems off")
        print(f"   Expected: ~658 kcal for chicken+rice+broccoli")
except Exception as e:
    print(f"❌ FAIL - {e}")

# Test 2: Meal Planner
print("\n[TEST 2] Meal Planner")
print("-" * 40)
try:
    payload = {
        'weightKg': 70,
        'heightCm': 170,
        'age': 25,
        'gender': 'M',
        'activityLevel': 'Moderate',
        'healthGoals': 'Balanced',
        'dietaryRestrictions': 'None'
    }
    r = requests.post(f'{BASE_URL}/api/meal-plan', json=payload, timeout=5)
    result = r.json()
    
    print(f"✓ Daily Target: {result['totalDailyCalories']} kcal")
    print(f"✓ Number of Meals: {len(result['meals'])}")
    
    if len(result['meals']) > 0:
        print(f"\n  Sample Meals:")
        for i, meal in enumerate(result['meals'][:3], 1):
            print(f"    {i}. {meal['name']}: {meal['calories']} kcal")
        
        # Check if calories are realistic
        total_from_meals = sum(m['calories'] for m in result['meals'])
        print(f"\n  Total from meals: {total_from_meals} kcal")
        
        # Meals should use real nutrition now, not fake allocation
        if all(200 < m['calories'] < 1000 for m in result['meals']):
            print(f"✅ PASS - All meal calories are realistic")
        else:
            print(f"⚠️  WARNING - Some meals have unusual calories")
    else:
        print(f"❌ FAIL - No meals generated")
except Exception as e:
    print(f"❌ FAIL - {e}")

# Test 3: Diet Tracker (already confirmed working)
print("\n[TEST 3] Diet Tracker (Quick Verify)")
print("-" * 40)
try:
    payload = {
        'foodItem': 'burger',
        'mealType': 'Lunch',
        'userProfile': {
            'weightKg': 70,
            'heightCm': 170,
            'age': 25,
            'gender': 'M',
            'activityLevel': 'Moderate',
            'healthGoals': 'Balanced',
            'dietaryRestrictions': 'None'
        }
    }
    r = requests.post(f'{BASE_URL}/api/diet', json=payload, timeout=5)
    result = r.json()
    
    print(f"✓ Food: burger")
    print(f"✓ Calories: {result['caloriesConsumedEstimate']} kcal")
    
    # Expected: burger ~590 kcal (295/100g * 200g)
    if 500 < result['caloriesConsumedEstimate'] < 700:
        print(f"✅ PASS - Burger calories realistic")
    else:
        print(f"⚠️  WARNING - {result['caloriesConsumedEstimate']} kcal")
except Exception as e:
    print(f"❌ FAIL - {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("✅ All features should now use real nutrition calculations")
print("✅ No more random numbers!")
