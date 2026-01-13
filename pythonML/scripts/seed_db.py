#!/usr/bin/env python3
"""
Database Seeder: Converts recipe_training_improved.txt → SQLite
Run this ONCE to build the recipes.db file.
"""

import sqlite3
import os
import re

def create_database(db_path='data/recipes.db'):
    """Create SQLite database with FTS5 search index"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Main table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            cuisine TEXT,
            input_raw TEXT
        )
    ''')
    
    # Full-Text Search index (The Magic Sauce)
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS recipes_fts USING fts5(
            title, 
            ingredients, 
            instructions,
            content='recipes',
            content_rowid='id'
        )
    ''')
    
    # Triggers to keep FTS in sync
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS recipes_ai AFTER INSERT ON recipes BEGIN
            INSERT INTO recipes_fts(rowid, title, ingredients, instructions)
            VALUES (new.id, new.title, new.ingredients, new.instructions);
        END
    ''')
    
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS recipes_ad AFTER DELETE ON recipes BEGIN
            DELETE FROM recipes_fts WHERE rowid = old.id;
        END
    ''')
    
    conn.commit()
    return conn

def parse_recipe_text(text):
    """Parse a single OUTPUT block into structured data"""
    title = "Untitled Recipe"
    ingredients = []
    instructions = ""
    cuisine = ""
    
    # Extract Title
    title_match = re.search(r'TITLE:\s*([^\|]+)', text, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
    
    # Extract Cuisine
    cuisine_match = re.search(r'CUISINE[*]?:\s*([^;]+)', text, re.IGNORECASE)
    if cuisine_match:
        cuisine = cuisine_match.group(1).strip()
    
    # Extract Ingredients
    ing_match = re.search(r'INGREDIENTS?:?\s*(.+?)(?:\s*\|\s*INSTRUCTIONS?:|$)', text, re.DOTALL | re.IGNORECASE)
    if ing_match:
        raw_ings = ing_match.group(1)
        ingredients = [i.strip() for i in raw_ings.split(';') if i.strip()]
    
    # Extract Instructions
    inst_match = re.search(r'INSTRUCTIONS?:\s*(.+?)(?:<END>|$)', text, re.DOTALL | re.IGNORECASE)
    if inst_match:
        instructions = inst_match.group(1).strip()
    
    return {
        'title': title,
        'ingredients': '; '.join(ingredients),
        'instructions': instructions,
        'cuisine': cuisine
    }

def seed_from_text_file(conn, text_file='data/training/recipe_training_improved.txt'):
    """Read text file and populate database"""
    if not os.path.exists(text_file):
        print(f"❌ Error: {text_file} not found!")
        return 0
    
    cursor = conn.cursor()
    
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by INPUT blocks
    blocks = content.split('INPUT:')
    recipes_added = 0
    
    for block in blocks:
        if not block.strip():
            continue
        
        try:
            parts = block.split('OUTPUT:', 1)
            if len(parts) < 2:
                continue
            
            input_raw = parts[0].strip()
            output_text = parts[1].strip()
            
            # Parse the OUTPUT section
            recipe_data = parse_recipe_text(output_text)
            recipe_data['input_raw'] = input_raw
            
            # Insert into database
            cursor.execute('''
                INSERT INTO recipes (title, ingredients, instructions, cuisine, input_raw)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                recipe_data['title'],
                recipe_data['ingredients'],
                recipe_data['instructions'],
                recipe_data['cuisine'],
                recipe_data['input_raw']
            ))
            
            recipes_added += 1
            
            if recipes_added % 1000 == 0:
                print(f"📦 Processed {recipes_added} recipes...")
                
        except Exception as e:
            print(f"⚠️ Skipped invalid recipe: {e}")
            continue
    
    conn.commit()
    return recipes_added

def main():
    """Main seeding process"""
    print("🌱 Starting Database Seeding...")
    print("=" * 50)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Create database
    db_path = 'data/recipes.db'
    if os.path.exists(db_path):
        print(f"⚠️  Database already exists at {db_path}")
        response = input("Delete and recreate? (y/N): ")
        if response.lower() != 'y':
            print("❌ Aborted.")
            return
        os.remove(db_path)
    
    conn = create_database(db_path)
    print(f"✅ Created database: {db_path}")
    
    # Seed data
    count = seed_from_text_file(conn)
    print(f"✅ Successfully imported {count} recipes!")
    
    # Verify
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM recipes")
    total = cursor.fetchone()[0]
    print(f"📊 Total recipes in database: {total}")
    
    # Test FTS
    cursor.execute("SELECT COUNT(*) FROM recipes_fts")
    fts_count = cursor.fetchone()[0]
    print(f"🔍 FTS index contains: {fts_count} recipes")
    
    conn.close()
    print("=" * 50)
    print("🎉 Seeding Complete!")
    print(f"\n💡 Database ready at: {os.path.abspath(db_path)}")

if __name__ == "__main__":
    main()
