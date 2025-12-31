import requests
import json
import time

URL = "http://localhost:5000"

def test_recipe():
    print("\n--- 1. Testing Dynamic Recipes (Same Input, Different Output) ---")
    payload = {"ingredients": "Chicken, Lemon", "cuisine": "Mediterranean"}
    
    for i in range(2):
        res = requests.post(f"{URL}/predict/recipe", json=payload).json()
        print(f"Attempt {i+1}:")
        print(f"  Title: {res['title']}")
        print(f"  Cal: {res['calories']}")
        print(f"  Instr: {res['instructions'][:50]}...")

def test_meal():
    print("\n--- 2. Testing Dynamic Meal Plan (Goal: Gain vs Lose) ---")
    
    # User 1: Gain Muscle (High Calorie)
    p1 = {"weightKg": 80, "heightCm": 180, "age": 25, "gender": "Male", "activityLevel": "Active", "healthGoals": "Gain Muscle", "dietaryRestrictions": "None"}
    res1 = requests.post(f"{URL}/predict/meal-plan", json=p1).json()
    print(f"Gain Muscle Target: {res1['totalDailyCalories']}")
    print(f"  Meals: {[m['name'] for m in res1['meals']]}")
    
    # User 2: Lose Weight (Low Calorie)
    p2 = {**p1, "healthGoals": "Lose Weight", "activityLevel": "Sedentary"}
    res2 = requests.post(f"{URL}/predict/meal-plan", json=p2).json()
    print(f"Lose Weight Target: {res2['totalDailyCalories']}")
    print(f"  Meals: {[m['name'] for m in res2['meals']]}")

def test_diet():
    print("\n--- 3. Testing Context-Aware Diet (Burger vs Salad) ---")
    base_profile = {"weightKg": 85, "heightCm": 175, "age": 30, "gender": "Male", "activityLevel": "Sedentary", "healthGoals": "Lose Weight", "dietaryRestrictions": "None"}
    
    # Scenario A: Ate Pizza (High Carb)
    req1 = {"foodItem": "Cheese Pizza", "mealType": "Lunch", "userProfile": base_profile}
    res1 = requests.post(f"{URL}/predict/adaptive-diet", json=req1).json()
    print(f"Context: Ate Pizza")
    print(f"  Analysis: {res1['nutritionalAnalysis']}")
    print(f"  Suggestion: {res1['nextMealSuggestion']}")
    
    # Scenario B: Ate Salad (Light)
    req2 = {"foodItem": "Green Salad", "mealType": "Lunch", "userProfile": base_profile}
    res2 = requests.post(f"{URL}/predict/adaptive-diet", json=req2).json()
    print(f"Context: Ate Salad")
    print(f"  Analysis: {res2['nutritionalAnalysis']}")
    print(f"  Suggestion: {res2['nextMealSuggestion']}")

try:
    test_recipe()
    test_meal()
    test_diet()
except Exception as e:
    print(f"Test Failed: {e}")
