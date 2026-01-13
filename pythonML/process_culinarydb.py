"""
Process CulinaryDB CSV files into GPT-2 training format
Reads structured CSV data and converts to INPUT/OUTPUT format
"""
import pandas as pd
import os

print("="*60)
print("PROCESSING CULINARYDB CSV")
print("="*60)

# Load recipe details
print("\nLoading Recipe_Details.csv...")
recipes = pd.read_csv('data/raw/CulinaryDB/01_Recipe_Details.csv')
print(f"Loaded {len(recipes)} recipes")

# Load ingredients
print("Loading Ingredients.csv...")
ingredients = pd.read_csv('data/raw/CulinaryDB/02_Ingredients.csv')

# Load recipe-ingredient relationships
print("Loading Recipe-Ingredients relationships...")
recipe_ing = pd.read_csv('data/raw/CulinaryDB/04_Recipe-Ingredients_Aliases.csv')

print("\nProcessing and formatting...")
formatted_recipes = []
errors = 0

for idx, recipe in recipes.iterrows():
    try:
        recipe_id = recipe['Recipe ID']
        title = recipe.get('Title', 'Untitled')
        cuisine = recipe.get('Cuisine', 'Unknown')
        
        # Get ingredients for this recipe
        recipe_ingredients = recipe_ing[recipe_ing['Recipe ID'] == recipe_id]
        if len(recipe_ingredients) == 0:
            continue
            
        # Get ingredient names  
        ingredient_ids = recipe_ingredients['Aliased Ingredient ID'].unique().tolist()
        ing_data = ingredients[ingredients['Aliased Ingredient ID'].isin(ingredient_ids)]
        ing_names = ing_data['Aliased Ingredient Name'].tolist()
        
        if len(ing_names) < 3:  # Need at least 3 ingredients
            continue
        
        # Simple ingredient names for INPUT
        simple_ings = []
        for ing in ing_names[:10]:
            words = str(ing).split()
            if len(words) > 1:
                simple_ings.append(words[-1])
            else:
                simple_ings.append(ing)
        
        # Create detailed ingredient list with quantities
        detailed_ings = []
        for _, ing_row in recipe_ingredients.head(15).iterrows():
            ing_id = ing_row['Aliased Ingredient ID']
            ing_name = ingredients[ingredients['Aliased Ingredient ID'] == ing_id]['Aliased Ingredient Name'].values
            if len(ing_name) > 0:
                detailed_ings.append(str(ing_name[0]))
        
        # Generate instructions based on cuisine
        instructions = f"Prepare this {cuisine} dish by combining the ingredients and cooking according to traditional {cuisine} methods."
        
        # Format for training
        input_text = f"INPUT: {', '.join(simple_ings)}"
        output_text = f"OUTPUT: TITLE: {title} | INGREDIENTS: {' ; '.join(detailed_ings)} | INSTRUCTIONS: {instructions}"
        
        formatted_recipes.append(f"{input_text}\\n{output_text}\\n<END>\\n")
        
        if (len(formatted_recipes)) % 1000 == 0:
            print(f"  Processed {len(formatted_recipes)} recipes...")
            
    except Exception as e:
        errors += 1
        continue

print(f"\n✅ Processed {len(formatted_recipes)} recipes")
print(f"⚠️  Errors: {errors}")

# Save
output_file = 'data/culinary_formatted.txt'
os.makedirs('data', exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(formatted_recipes)

print(f"\n✅ Saved to {output_file}")
print(f"   Size: {os.path.getsize(output_file)/1024/1024:.1f} MB")
print(f"   Recipes: {len(formatted_recipes)}")
