"""Merge CulinaryDB and new recipe datasets"""
import os

files = [
    ('data/recipe_training.txt', 'Original'),
    ('data/recipe_training_large.txt', 'New')
]

all_content = []
for filepath, name in files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            all_content.append(content)
            print(f"Loaded {name}: {content.count('<END>')} recipes")

with open('data/recipe_training_combined.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_content))

print(f"\nCreated combined file with {sum(c.count('<END>') for c in all_content)} recipes")
