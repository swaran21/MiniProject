"""
Recipe Data Preparation Script
Prepares 83K recipes for GPT-2 training by formatting them as INPUT/OUTPUT pairs
Optimized for 16GB RAM system
"""

import json
import random
from pathlib import Path

def load_recipes():
    """Load all recipes from the 3 JSON files"""
    recipe_files = [
        'recipes_raw/recipes_raw_nosource_ar.json',
        'recipes_raw/recipes_raw_nosource_epi.json',
        'recipes_raw/recipes_raw_nosource_fn.json'
    ]
    
    all_recipes = []
    
    for file_path in recipe_files:
        print(f"Loading {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_recipes.extend([
                {
                    'title': recipe_data.get('title', ''),
                    'ingredients': recipe_data.get('ingredients', []),
                    'instructions': recipe_data.get('instructions', '')
                }
                for recipe_data in data.values()
            ])
    
    print(f"Total recipes loaded: {len(all_recipes)}")
    return all_recipes

def extract_simple_ingredients(ingredient_list):
    """
    Extract simple ingredient names from detailed ingredient strings
    Example: "2 cups all-purpose flour" -> "flour"
    """
    simple_ingredients = []
    
    for ingredient in ingredient_list:
        # Remove common measurement words and numbers
        ingredient = ingredient.lower()
        # Split and take meaningful words
        words = ingredient.split()
        # Filter out measurements, numbers, and common words
        filtered = [w for w in words if not any(c.isdigit() for c in w) 
                   and w not in ['cup', 'cups', 'tablespoon', 'tablespoons', 'tbsp', 
                                'teaspoon', 'teaspoons', 'tsp', 'ounce', 'ounces', 
                                'oz', 'pound', 'pounds', 'lb', 'lbs', 'advertisement',
                                'gram', 'grams', 'g', 'kg', 'kilogram', 'ml', 'liter']]
        
        if filtered:
            # Take the last 1-2 words as the ingredient name
            simple_ingredients.append(' '.join(filtered[-2:] if len(filtered) > 1 else filtered))
    
    return list(set(simple_ingredients))  # Remove duplicates

def format_recipe_for_training(recipe):
    """
    Format recipe as INPUT/OUTPUT pair for GPT-2 training
    INPUT: simple ingredient names
    OUTPUT: full recipe with quantities
    """
    # Get simple ingredient names
    simple_ingredients = extract_simple_ingredients(recipe['ingredients'])
    
    # Clean ingredients list (remove ADVERTISEMENT tags)
    clean_ingredients = [ing for ing in recipe['ingredients'] 
                        if 'ADVERTISEMENT' not in ing.upper() and ing.strip()]
    
    # Clean instructions
    clean_instructions = recipe['instructions'].replace('\\n', ' ').strip()
    
    # Format as training text
    input_text = f"INPUT: {', '.join(simple_ingredients[:10])}"  # Limit to 10 ingredients
    output_text = (
        f"OUTPUT: TITLE: {recipe['title']} | "
        f"INGREDIENTS: {' ; '.join(clean_ingredients[:15])} | "
        f"INSTRUCTIONS: {clean_instructions[:500]}"  # Limit instruction length
    )
    
    return f"{input_text}\n{output_text}\n<END>\n"

def main():
    print("="*60)
    print("Recipe Data Preparation for ML Training")
    print("="*60)
    
    # Create data directory if it doesn't exist
    Path('data').mkdir(exist_ok=True)
    
    # Load all recipes
    all_recipes = load_recipes()
    
    # Sample 20,000 recipes (optimized for 16GB RAM)
    sample_size = min(20000, len(all_recipes))
    print(f"\nSampling {sample_size} recipes for training...")
    sampled_recipes = random.sample(all_recipes, sample_size)
    
    # Format recipes for training
    print("Formatting recipes...")
    formatted_texts = []
    
    for i, recipe in enumerate(sampled_recipes):
        try:
            if recipe['title'] and recipe['ingredients'] and recipe['instructions']:
                formatted_text = format_recipe_for_training(recipe)
                formatted_texts.append(formatted_text)
                
                if (i + 1) % 1000 == 0:
                    print(f"  Processed {i + 1}/{sample_size} recipes...")
        except Exception as e:
            print(f"  Skipping recipe due to error: {e}")
            continue
    
    # Save to file
    output_file = 'data/recipe_training.txt'
    print(f"\nSaving {len(formatted_texts)} formatted recipes to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(formatted_texts)
    
    # Print sample
    print("\n" + "="*60)
    print("Sample formatted recipe:")
    print("="*60)
    print(formatted_texts[0])
    
    print("="*60)
    print(f"✅ Data preparation complete!")
    print(f"   Total recipes formatted: {len(formatted_texts)}")
    print(f"   Output file: {output_file}")
    print(f"   File size: {Path(output_file).stat().st_size / (1024*1024):.2f} MB")
    print("="*60)

if __name__ == "__main__":
    main()
