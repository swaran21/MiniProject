"""
Test Medical Meal Planner
"""

from app.services.prescription_analyzer import PrescriptionAnalyzer
from app.services.medical_meal_planner import MedicalMealPlanner
import sqlite3

# Connect to database  
# Use the same database the recipe service uses
from app.services.recipe_service import RecipeService
recipe_svc = RecipeService()
conn = recipe_svc.db_conn

# Sample prescription
diabetes_prescription = """
Patient: Test User
Diagnosis: Type 2 Diabetes Mellitus
HbA1c: 8.5%
Medications: Metformin 500mg BD
"""

print("=" * 70)
print("MEDICAL MEAL PLANNER TEST")
print("=" * 70)

# Step 1: Analyze prescription
print("\n📄 Step 1: Analyzing Prescription...")
analyzer = PrescriptionAnalyzer()
analysis = analyzer.analyze(diabetes_prescription, user_id=1)

print(f"✅ Detected: {analysis['detected_conditions']}")
print(f"✅ Duration: {analysis['plan_duration_days']} days")
print(f"✅ Foods to avoid: {len(analysis['foods_to_avoid'])} items")

# Step 2: Generate meal plan
print("\n🍽️  Step 2: Generating Meal Plan...")
planner = MedicalMealPlanner(conn)

try:
    meal_plan = planner.create_plan(analysis, duration_days=7)  # 7-day test
    
    print(f"\n✅ Meal Plan Generated!")
    print(f"   Plan ID: {meal_plan['plan_id']}")
    print(f"   Duration: {meal_plan['duration_days']} days")
    print(f"   Conditions: {', '.join(meal_plan['conditions'])}")
    print(f"   Start Date: {meal_plan['start_date']}")
    
    # Show sample days
    print(f"\n📅 Sample Daily Meals:")
    for day in meal_plan['daily_meals'][:3]:  # Show first 3 days
        print(f"\n   Day {day['day']} ({day['date']}):")
        print(f"      Breakfast: {day['breakfast']['title']} ({day['breakfast']['health_score']}/100)")
        print(f"      Lunch: {day['lunch']['title']} ({day['lunch']['health_score']}/100)")
        print(f"      Dinner: {day['dinner']['title']} ({day['dinner']['health_score']}/100)")
        print(f"      Snacks: {len(day['snacks'])} items")
        print(f"      Total Calories: {day['total_calories']}")
    
    print(f"\n📋 Summary:")
    print(meal_plan['summary'])
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE - Meal Planner Working!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

conn.close()
