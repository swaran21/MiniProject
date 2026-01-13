#!/usr/bin/env python3
"""
Database Migration: Add Recipe Rating System
Run this ONCE to add rating columns to existing database
"""

import sqlite3
import os

def migrate_database(db_path='data/recipes.db'):
    """Add rating columns and user_ratings table"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("💡 Run 'python seed_db.py' first")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Starting database migration...")
    print("=" * 50)
    
    try:
        # Check if migration already ran
        cursor.execute("PRAGMA table_info(recipes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'likes' in columns:
            print("⚠️  Migration already applied!")
            response = input("Re-run migration? This will reset ratings (y/N): ")
            if response.lower() != 'y':
                print("❌ Aborted")
                return False
        
        # Add rating columns to recipes table
        print("📊 Adding rating columns to recipes table...")
        
        cursor.execute("""
            ALTER TABLE recipes ADD COLUMN likes INTEGER DEFAULT 0
        """)
        
        cursor.execute("""
            ALTER TABLE recipes ADD COLUMN dislikes INTEGER DEFAULT 0
        """)
        
        cursor.execute("""
            ALTER TABLE recipes ADD COLUMN rating_score REAL DEFAULT 0.5
        """)
        
        cursor.execute("""
            ALTER TABLE recipes ADD COLUMN rating_count INTEGER DEFAULT 0
        """)
        
        print("✅ Rating columns added")
        
        # Create user_ratings table
        print("📋 Creating user_ratings table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                recipe_id INTEGER NOT NULL,
                rating INTEGER CHECK(rating IN (-1, 1)) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id),
                UNIQUE(user_id, recipe_id)
            )
        """)
        
        print("✅ user_ratings table created")
        
        # Create indexes for performance
        print("🔍 Creating indexes...")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_ratings_user 
            ON user_ratings(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_ratings_recipe 
            ON user_ratings(recipe_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipes_rating_score 
            ON recipes(rating_score)
        """)
        
        print("✅ Indexes created")
        
        conn.commit()
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM recipes")
        recipe_count = cursor.fetchone()[0]
        
        print("=" * 50)
        print("🎉 Migration Complete!")
        print(f"📊 {recipe_count} recipes now support ratings")
        print(f"💡 Ratings will improve search quality over time")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_database()
    exit(0 if success else 1)
