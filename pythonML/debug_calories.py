"""Debug why Rice + Egg = 4108 calories"""
from app.services.recipe_service import RecipeService
from app.services.nutrition_service import NutritionService
from app.models import RecipeRequest

# Test nutrition service directly
ns = NutritionService()
print("="*50)
print("DEBUGGING CALORIE CALCULATION")
print("="*50)

# Test 1: Individual ingredients
print("\n1. Individual Ingredients (200g each):")
for ing in ['rice', 'egg']:
    result = ns.estimate_calories([ing], serving_size_g=200)
    print(f"   {ing}: {result['calories']} kcal")

# Test 2: Combined
print("\n2. Combined (Rice + Egg):")
result = ns.estimate_calories(['rice', 'egg'], serving_size_g=200)
print(f"   Total: {result['calories']} kcal")
print(f"   Matched: {result['matched_ingredients']}/{result['total_ingredients']}")

# Test 3: What RecipeService generates
print("\n3. RecipeService (Full Pipeline):")
rs = RecipeService()
req = RecipeRequest(ingredients='Rice, Egg', cuisine='any', dietaryRestrictions='None')
recipe = rs.generate(req)
print(f"   Recipe: {recipe.title}")
print(f"   Calories: {recipe.calories} kcal")
print(f"   Ingredients: {recipe.ingredients}")

print("\n" + "="*50)
print(f"ISSUE: {recipe.calories} kcal is {'CORRECT' if 400 < recipe.calories < 700 else 'WRONG'}")
print("="*50)
