"""
Database Migration: Add Health-Based Meal Planning Tables
Run this script to add health tracking tables to your SQLite database
"""

import sqlite3
from datetime import datetime

def migrate_health_tables():
    """Add health-related tables to recipes database"""
    
    conn = sqlite3.connect('app/data/recipes.db')
    cursor = conn.cursor()
    
    print("Starting health tables migration...")
    
    # 1. Health Reports Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_type TEXT DEFAULT 'manual_input',
            file_path TEXT,
            ocr_text TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    """)
    print("✅ Created health_reports table")
    
    # 2. User Conditions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_conditions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            condition_name TEXT NOT NULL,
            severity TEXT DEFAULT 'moderate',
            diagnosed_date DATE,
            notes TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created user_conditions table")
    
    # 3. User Medications Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            medication_name TEXT NOT NULL,
            dosage TEXT,
            frequency TEXT,
            food_interactions TEXT,
            start_date DATE,
            end_date DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created user_medications table")
    
    # 4. Medical Meal Plans Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_meal_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_name TEXT,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            conditions TEXT,
            duration_days INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created medical_meal_plans table")
    
    # 5. Daily Meals Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            meal_date DATE NOT NULL,
            meal_type TEXT,
            recipe_id INTEGER,
            is_completed BOOLEAN DEFAULT 0,
            user_rating INTEGER,
            FOREIGN KEY (plan_id) REFERENCES medical_meal_plans(id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(id)
        )
    """)
    print("✅ Created daily_meals table")
    
    # Create indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_conditions_user ON user_conditions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_medications_user ON user_medications(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meal_plans_user ON medical_meal_plans(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_meals_plan ON daily_meals(plan_id)")
    print("✅ Created indexes")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Migration complete! Health tables are ready.")
    print("\nCreated tables:")
    print("  - health_reports")
    print("  - user_conditions")
    print("  - user_medications")
    print("  - medical_meal_plans")
    print("  - daily_meals")

if __name__ == "__main__":
    migrate_health_tables()
