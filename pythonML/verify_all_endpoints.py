import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_recipe():
    print("\n--- Testing Recipe Generation ---")
    try:
        resp = requests.post(f"{BASE_URL}/predict/recipe", json={"ingredients": "Chicken, Garlic", "cuisine": "Italian", "dietaryRestrictions": ""})
        if resp.status_code == 200:
            data = resp.json()
            print("STATUS: SUCCESS")
            print(f"Title: {data.get('title')}")
            print(f"Calories: {data.get('calories')}")
        else:
            print(f"STATUS: FAILED ({resp.status_code})")
            print(resp.text)
    except Exception as e:
        print(f"STATUS: ERROR ({e})")

def test_meal_plan():
    print("\n--- Testing Meal Plan ---")
    payload = {
        "weightKg": 70, "heightCm": 175, "age": 25, "gender": "Male",
        "activityLevel": "Active", "healthGoals": "Lose Weight", "dietaryRestrictions": "None"
    }
    try:
        resp = requests.post(f"{BASE_URL}/predict/meal-plan", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            print("STATUS: SUCCESS")
            print(f"Target Calories: {data.get('totalDailyCalories')}")
            print(f"Meals: {len(data.get('meals', []))}")
        else:
            print(f"STATUS: FAILED ({resp.status_code})")
            print(resp.text)
    except Exception as e:
        print(f"STATUS: ERROR ({e})")

def test_diet():
    print("\n--- Testing Diet Recommendation (ML) ---")
    payload = {
        "foodItem": "Pizza",
        "mealType": "Lunch",
        "userProfile": {
            "weightKg": 70, "heightCm": 175, "age": 25, "gender": "Male",
            "activityLevel": "Sedentary", "healthGoals": "Lose Weight", "dietaryRestrictions": "None"
        }
    }
    try:
        resp = requests.post(f"{BASE_URL}/predict/adaptive-diet", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            print("STATUS: SUCCESS")
            print(f"Note: {data.get('nutritionalAnalysis')}")
            print(f"Suggestion: {data.get('nextMealSuggestion')}")
        else:
            print(f"STATUS: FAILED ({resp.status_code})")
            print(resp.text)
    except Exception as e:
        print(f"STATUS: ERROR ({e})")

if __name__ == "__main__":
    test_recipe()
    test_meal_plan()
    test_diet()
