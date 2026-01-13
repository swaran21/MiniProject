"""
Test script for Prescription Analyzer and Recipe Health Scorer
"""

from app.services.prescription_analyzer import PrescriptionAnalyzer
from app.services.recipe_health_scorer import RecipeHealthScorer

# Sample prescription texts
diabetes_prescription = """
Patient Name: Test User
Date: 2024-01-10

Diagnosis: Type 2 Diabetes Mellitus
HbA1c: 8.2%

Medications:
- Metformin 500mg - 1 tablet twice daily with meals
- Monitor blood glucose regularly

Dietary advice: Low carbohydrate diet recommended
"""

hypertension_prescription = """
Patient: John Doe
BP: 160/95 mmHg

Diagnosis: Hypertension (High Blood Pressure)

Rx:
- Amlodipine 5mg OD
- Losartan 50mg OD
- Low sodium diet
- Regular exercise
"""

# Sample recipes
sample_recipes = [
    {
        'id': 1,
        'title': 'Grilled Chicken Salad',
        'ingredients': 'chicken breast; lettuce; tomatoes; olive oil; lemon juice'
    },
    {
        'id': 2,
        'title': 'Sweet Rice Pudding',
        'ingredients': 'white rice; sugar; milk; cardamom; raisins'
    },
    {
        'id': 3,
        'title': 'Brown Rice Buddha Bowl',
        'ingredients': 'brown rice; chickpeas; spinach; avocado; quinoa'
    }
]

print("=" * 60)
print("PRESCRIPTION ANALYZER TEST")
print("=" * 60)

analyzer = PrescriptionAnalyzer()

# Test 1: Diabetes prescription
print("\n📄 Test 1: Analyzing Diabetes Prescription")
print("-" * 60)
result1 = analyzer.analyze(diabetes_prescription)
print(f"Detected Conditions: {result1['detected_conditions']}")
print(f"Is Chronic: {result1['is_chronic']}")
print(f"Plan Duration: {result1['plan_duration_days']} days")
print(f"Medications: {[m['name'] for m in result1['medications']]}")
print(f"Summary: {result1['analysis_summary']}")
print(f"\n Foods to AVOID ({len(result1['foods_to_avoid'])}): {result1['foods_to_avoid'][:5]}...")
print(f"Foods to EAT ({len(result1['foods_to_eat'])}): {result1['foods_to_eat'][:5]}...")

# Test 2: Hypertension prescription
print("\n\n📄 Test 2: Analyzing Hypertension Prescription")
print("-" * 60)
result2 = analyzer.analyze(hypertension_prescription)
print(f"Detected Conditions: {result2['detected_conditions']}")
print(f"Is Chronic: {result2['is_chronic']}")
print(f"Medications: {[m['name'] for m in result2['medications']]}")
print(f"Summary: {result2['analysis_summary']}")

print("\n\n" + "=" * 60)
print("RECIPE HEALTH SCORER TEST")
print("=" * 60)

scorer = RecipeHealthScorer()

# Test with diabetes condition
print("\n🍽️  Testing Recipes for Diabetes Patient")
print("-" * 60)

for recipe in sample_recipes:
    score = scorer.calculate_health_score(recipe, ['diabetes_type2'])
    category = scorer.categorize_recipe(recipe, ['diabetes_type2'])
    warnings = scorer.get_warnings(recipe, ['diabetes_type2'])
    
    print(f"\n{recipe['title']}")
    print(f"  Score: {score}/100")
    print(f"  Category: {category.upper()}")
    print(f"  Recommendation: {scorer.get_recipe_recommendations(recipe, ['diabetes_type2'])}")
    if warnings:
        print(f"  Warnings: {len(warnings)} issue(s)")
        for w in warnings:
            print(f"    - {w['message']}")

# Test filtering
print("\n\n🔍 Filtering Safe Recipes for Diabetes")
print("-" * 60)
safe_recipes = scorer.filter_safe_recipes(sample_recipes, ['diabetes_type2'], min_score=70)
print(f"Found {len(safe_recipes)} safe recipe(s) out of {len(sample_recipes)}")
for r in safe_recipes:
    print(f"  ✅ {r['title']} - Score: {r['health_score']}/100")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE!")
print("=" * 60)
