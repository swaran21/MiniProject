# Detailed Test with JSON Results
import requests
import json
import time
from datetime import datetime

BASE_URL_PYTHON = "http://localhost:5000"
BASE_URL_JAVA = "http://localhost:8080"

test_results = {
    "timestamp": datetime.now().isoformat(),
    "tests": []
}

def log_test(name, status, details):
    test_results["tests"].append({
        "name": name,
        "status": status,
        "details": details
    })
    print(f"[{status}] {name}")
    if details.get("error"):
        print(f"      Error: {details['error']}")

print("=" * 70)
print("MEAL PLAN INTEGRATION TEST - Detailed Results")
print("=" * 70)

try:
    # Test 1: Generate meal plan from Python
    print("\n[TEST 1] Generate Meal Plan via Python Backend")
    print("-" * 70)
    
    meal_plan_request = {
        "conditions": ["diabetes_type2"],
        "user_id": 1,
        "duration_days": 3
    }
    
    response = requests.post(
        f"{BASE_URL_PYTHON}/health/generate-meal-plan",
        json=meal_plan_request,
        timeout=60
    )
    
    if response.status_code == 200:
        meal_plan = response.json()
        log_test("Generate Meal Plan", "PASS", {
            "status_code": response.status_code,
            "plan_id": meal_plan.get("plan_id"),
            "duration_days": meal_plan.get("duration_days"),
            "num_days": len(meal_plan.get("daily_meals", []))
        })
        print(f"      Plan ID: {meal_plan.get('plan_id')}")
        print(f"      Days: {len(meal_plan.get('daily_meals', []))}")
    else:
        log_test("Generate Meal Plan", "FAIL", {
            "status_code": response.status_code,
            "error": response.text
        })
    
    # Test 2: Wait and verify auto-save
    print("\n[TEST 2] Verify Auto-Save to Java Backend")
    print("-" * 70)
    time.sleep(2)
    
    java_response = requests.get(
        f"{BASE_URL_JAVA}/api/health/meal-plan/1/active",
        timeout=10
    )
    
    if java_response.status_code == 200:
        saved_plan = java_response.json()
        log_test("Auto-Save Verification", "PASS", {
            "status_code": java_response.status_code,
            "plan_id": saved_plan.get("planId"),
            "user_id": saved_plan.get("userId"),
            "is_active": saved_plan.get("isActive"),
            "num_days_saved": len(saved_plan.get("dailyMeals", []))
        })
        print(f"      Plan ID in DB: {saved_plan.get('planId')}")
        print(f"      Active: {saved_plan.get('isActive')}")
        print(f"      Days saved: {len(saved_plan.get('dailyMeals', []))}")
        
        # Check day 1 data
        if saved_plan.get("dailyMeals"):
            day1 = saved_plan["dailyMeals"][0]
            print(f"      Day 1 Total Calories: {day1.get('totalCalories')}")
            print(f"      Day 1 Macros: {day1.get('totalMacros')}")
            
    else:
        log_test("Auto-Save Verification", "FAIL", {
            "status_code": java_response.status_code,
            "error": java_response.text
        })
    
    # Test 3: Get today's meals
    print("\n[TEST 3] Retrieve Today's Meals")
    print("-" * 70)
    
    today_response = requests.get(
        f"{BASE_URL_JAVA}/api/health/meal-plan/today/1",
        timeout=10
    )
    
    if today_response.status_code == 200:
        today_meals = today_response.json()
        log_test("Get Today's Meals", "PASS", {
            "status_code": today_response.status_code,
            "day": today_meals.get("day"),
            "total_calories": today_meals.get("totalCalories"),
            "has_breakfast": today_meals.get("breakfast") is not None,
            "has_lunch": today_meals.get("lunch") is not None,
            "has_dinner": today_meals.get("dinner") is not None
        })
        print(f"      Day Number: {today_meals.get('day')}")
        print(f"      Total Calories: {today_meals.get('totalCalories')}")
        print(f"      Meals present: B={bool(today_meals.get('breakfast'))}, "
              f"L={bool(today_meals.get('lunch'))}, D={bool(today_meals.get('dinner'))}")
    else:
        log_test("Get Today's Meals", "FAIL", {
            "status_code": today_response.status_code,
            "error": today_response.text
        })
    
    # Calculate pass rate
    passed = sum(1 for t in test_results["tests"] if t["status"] == "PASS")
    total = len(test_results["tests"])
    test_results["summary"] = {
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": f"{(passed/total*100):.1f}%"
    }
    
except Exception as e:
    log_test("Unexpected Error", "FAIL", {
        "error": str(e),
        "type": type(e).__name__
    })

# Save results to JSON
with open("test_results.json", "w") as f:
    json.dump(test_results, f, indent=2)

print("\n" + "=" * 70)
print(f"TESTING COMPLETE - {test_results.get('summary', {}).get('pass_rate', 'N/A')} Pass Rate")
print(f"Results saved to: test_results.json")
print("=" * 70)
