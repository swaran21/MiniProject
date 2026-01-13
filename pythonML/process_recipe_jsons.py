"""
Process Recipe JSON files into GPT-2 training format
Combines FoodNetwork, Epicurious, and AllRecipes data
"""
import json
import os

print("="*60)
print("PROCESSING RECIPE JSON FILES")
print("="*60)

json_files = [
    ('data/raw/recipes_raw/recipes_raw_nosource_fn.json', 'FoodNetwork'),
    ('data/raw/recipes_raw/recipes_raw_nosource_epi.json', 'Epicurious'),
    ('data/raw/recipes_raw/recipes_raw_nosource_ar.json', 'AllRecipes')
]

all_formatted = []
total_loaded = 0

for filepath, source_name in json_files:
    print(f"\nProcessing {source_name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"  Loaded {len(data)} recipes")
    total_loaded += len(data)
    
    processed = 0
    skipped = 0
    
    for recipe_id, recipe in data.items():
        try:
            title = recipe.get('title', 'Unknown')
            ingredients = recipe.get('ingredients', [])
            instructions = recipe.get('instructions', '')
            
            # Validation
            if not title or not ingredients or not instructions:
                skipped += 1
                continue
            if len(ingredients) < 3:
                skipped += 1
                continue
            if len(instructions) < 30:
                skipped += 1
                continue
            
            # Extract simple ingredient names
            simple_ings = []
            for ing in ingredients[:10]:
                # Take last word or 2 words as ingredient name
                words = str(ing).split()
                if len(words) > 1:
                    simple_ings.append(' '.join(words[-2:]))
                else:
                    simple_ings.append(words[0])
            
            # Format instructions (clean up)
            if isinstance(instructions, list):
                clean_instructions = ' '.join([f"{i+1}. {s}" for i, s in enumerate(instructions[:10])])
            else:
                clean_instructions = str(instructions)[:800]
            
            # Format ingredients
            ing_list = [str(ing) for ing in ingredients[:15]]
            
            # Create training format
            input_text = f"INPUT: {', '.join(simple_ings)}"
            output_text = f"OUTPUT: TITLE: {title[:100]} | INGREDIENTS: {' ; '.join(ing_list)} | INSTRUCTIONS: {clean_instructions}"
            
            all_formatted.append(f"{input_text}\\n{output_text}\\n<END>\\n")
            processed += 1
            
        except Exception as e:
            skipped += 1
            continue
    
    print(f"  ✅ Processed: {processed}")
    print(f"  ⚠️  Skipped: {skipped}")

print(f"\n{'='*60}")
print("SUMMARY")
print("="*60)
print(f"Total loaded: {total_loaded}")
print(f"Total formatted: {len(all_formatted)}")
print(f"Success rate: {len(all_formatted)/total_loaded*100:.1f}%")

# Save
output_file = 'data/json_recipes_formatted.txt'
os.makedirs('data', exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(all_formatted)

print(f"\n✅ Saved to {output_file}")
print(f"   Size: {os.path.getsize(output_file)/1024/1024:.1f} MB")
print(f"   Recipes: {len(all_formatted)}")
