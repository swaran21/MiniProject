# Test Meal Plan API - Complete Flow (with full output)
import requests
import json

BASE_URL_PYTHON = "http://localhost:5000"
BASE_URL_JAVA = "http://localhost:8080"

print("=" * 70)
print("🧪 TESTING MEAL PLAN PERSISTENCE SYSTEM")
print("=" * 70)

# Test 1: Generate meal plan
print("\n1️⃣ Testing: Generate Meal Plan (Python)")
print("-" * 70)

meal_plan_request = {
    "conditions": ["diabetes_type2"],
    "user_id": 1,
    "duration_days": 3
}

try:
    response = requests.post(
        f"{BASE_URL_PYTHON}/health/generate-meal-plan",
        json=meal_plan_request,
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        meal_plan = response.json()
        plan_id = meal_plan.get("plan_id")
        print(f"✅ Meal plan generated successfully!")
        print(f"   Plan ID: {plan_id}")
        print(f"   Duration: {meal_plan.get('duration_days')} days")
        print(f"   Total days in plan: {len(meal_plan.get('daily_meals', []))}")
        
        # Show first day details
        if meal_plan.get('daily_meals'):
            day1 = meal_plan['daily_meals'][0]
            print(f"\n   Day 1 Preview:")
            print(f"   - Breakfast: {day1.get('breakfast', {}).get('title', 'N/A')}")
            print(f"   - Lunch: {day1.get('lunch', {}).get('title', 'N/A')}")
            print(f"   - Dinner: {day1.get('dinner', {}).get('title', 'N/A')}")
        
        # Test 2: Verify auto-save
        print("\n2️⃣ Testing: Verify Auto-Save to Database (Java)")
        print("-" * 70)
        
        import time
        time.sleep(1)  # Give Java a second to save
        
        java_response = requests.get(
            f"{BASE_URL_JAVA}/api/health/meal-plan/1/active",
            timeout=10
        )
        
        print(f"Status Code: {java_response.status_code}")
        
        if java_response.status_code == 200:
            saved_plan = java_response.json()
            print(f"✅ Plan retrieved from database!")
            print(f"   Saved Plan ID: {saved_plan.get('planId')}")
            print(f"   User ID: {saved_plan.get('userId')}")
            print(f"   Is Active: {saved_plan.get('isActive')}")
            print(f"   Daily Meals in DB: {len(saved_plan.get('dailyMeals', []))}")
            
            # Show DB data structure
            if saved_plan.get('dailyMeals'):
                db_day1 = saved_plan['dailyMeals'][0]
                print(f"\n   Day 1 from DB:")
                print(f"   - Day Number: {db_day1.get('day')}")
                print(f"   - Total Calories: {db_day1.get('totalCalories')}")
                print(f"   - Total Macros: {db_day1.get('totalMacros')}")
        else:
            print(f"❌ Plan not found in database")
            print(f"   Response: {java_response.text}")
            
        # Test 3: Get today's meals
        print("\n3️⃣ Testing: Get Today's Meals")
        print("-" * 70)
        
        today_response = requests.get(
            f"{BASE_URL_JAVA}/api/health/meal-plan/today/1",
            timeout=10
        )
        
        print(f"Status Code: {today_response.status_code}")
        
        if today_response.status_code == 200:
            today_meals = today_response.json()
            print(f"✅ Today's meals retrieved!")
            print(f"   Day: {today_meals.get('day')}")
            print(f"   Total Calories: {today_meals.get('totalCalories')}")
            
            breakfast = today_meals.get('breakfast', {})
            lunch = today_meals.get('lunch', {})
            dinner = today_meals.get('dinner', {})
            
            print(f"\n   🍳 Breakfast: {breakfast.get('title')}")
            print(f"      Calories: {breakfast.get('calories')}, Macros: {breakfast.get('macros')}")
            print(f"   🥗 Lunch: {lunch.get('title')}")
            print(f"      Calories: {lunch.get('calories')}, Macros: {lunch.get('macros')}")
            print(f"   🍽️  Dinner: {dinner.get('title')}")
            print(f"      Calories: {dinner.get('calories')}, Macros: {dinner.get('macros')}")
        else:
            print(f"⚠️  Today's meals not found")
            
    else:
        print(f"❌ Failed to generate meal plan")
        print(f"Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print(f"❌ Connection Error: Servers not running")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("🏁 TESTING COMPLETE")
print("=" * 70)
