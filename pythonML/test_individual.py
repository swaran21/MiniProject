"""Test each feature individually"""
import requests
import json

print("Test 1: Recipe Generator")
print("-"*40)
try:
    r = requests.post('http://localhost:5000/api/recipe', 
                     json={'ingredients': 'chicken, rice', 'cuisine': 'Asian', 'dietaryRestrictions': 'None'}, 
                     timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"Recipe: {result.get('title', 'NO TITLE')}")
        print(f"Calories: {result.get('calories', 'NO CALORIES')}")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Exception: {e}")

print("\nTest 2: Meal Planner")  
print("-"*40)
try:
    r = requests.post('http://localhost:5000/api/meal-plan',
                     json={'weightKg': 70, 'heightCm': 170, 'age': 25, 'gender': 'M', 
                          'activityLevel': 'Moderate', 'healthGoals': 'Balanced', 'dietaryRestrictions': 'None'},
                     timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"Daily calories: {result.get('totalDailyCalories', 'NONE')}")
        print(f"Meals count: {len(result.get('meals', []))}")
        if result.get('meals'):
            print(f"First meal: {result['meals'][0].get('name', 'NO NAME')} - {result['meals'][0].get('calories', 'NO CALS')} kcal")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Exception: {e}")

print("\nTest 3: Diet Tracker")
print("-"*40)
try:
    r = requests.post('http://localhost:5000/api/diet',
                     json={'foodItem': 'pizza', 'mealType': 'Lunch',
                          'userProfile': {'weightKg': 70, 'heightCm': 170, 'age': 25, 'gender': 'M',
                                        'activityLevel': 'Moderate', 'healthGoals': 'Balanced', 'dietaryRestrictions': 'None'}},
                     timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"Consumed: {result.get('caloriesConsumedEstimate', 'NONE')} kcal")
        print(f"Remaining: {result.get('caloriesRemaining', 'NONE')} kcal")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Exception: {e}")
