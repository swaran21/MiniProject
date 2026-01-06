"""
Merge ALL recipe sources into comprehensive training file
Combines CulinaryDB + JSON recipes, deduplicates, and shuffles
"""
import os
import random

print("="*60)
print("MERGING ALL RECIPE SOURCES")
print("="*60)

sources = [
    ('data/culinary_formatted.txt', 'CulinaryDB'),
    ('data/json_recipes_formatted.txt', 'Recipe JSONs')
]

all_recipes = []
source_stats = {}

for filepath, source_name in sources:
    if os.path.exists(filepath):
        print(f"\nLoading {source_name}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            recipes = content.split('<END>\\n')
            recipes = [r.strip() + '\\n<END>\\n' for r in recipes if r.strip()]
            all_recipes.extend(recipes)
            source_stats[source_name] = len(recipes)
            print(f"  Added {len(recipes)} recipes")
    else:
        print(f"\n⚠️  {source_name} not found: {filepath}")
        print(f"   Run the preprocessing script first!")

print(f"\n{'='*60}")
print("DEDUPLICATION")
print("="*60)
print(f"Before: {len(all_recipes)} recipes")

# Deduplicate based on content
unique_recipes = list(set(all_recipes))
duplicates_removed = len(all_recipes) - len(unique_recipes)

print(f"After: {len(unique_recipes)} recipes")
print(f"Removed: {duplicates_removed} duplicates")

# Shuffle for better training
print("\nShuffling...")
random.shuffle(unique_recipes)

# Save
output_file = 'data/recipe_training_COMPREHENSIVE.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(unique_recipes)

print(f"\n{'='*60}")
print("FINAL COMPREHENSIVE DATASET")
print("="*60)
print(f"File: {output_file}")
print(f"Size: {os.path.getsize(output_file)/1024/1024:.1f} MB")
print(f"Total recipes: {len(unique_recipes):,}")
print(f"\nSource breakdown:")
for source, count in source_stats.items():
    print(f"  {source}: {count:,} recipes")

# Show sample
print(f"\n{'='*60}")
print("SAMPLE RECIPE")
print("="*60)
print(unique_recipes[0][:400] + "...")

print(f"\n✅ Ready for training!")
print(f"\nNext: Upload to Google Colab or run train_recipe_model_cpu.py")
