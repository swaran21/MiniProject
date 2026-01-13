# Database Setup Instructions

## 🚀 Quick Start

### First Time Setup
Run this command ONCE to create the recipe database:

```bash
cd pythonML
python seed_db.py
```

**Expected Output:**
```
🌱 Starting Database Seeding...
==================================================
✅ Created database: data/recipes.db
📦 Processed 1000 recipes...
📦 Processed 2000 recipes...
...
✅ Successfully imported 15000+ recipes!
📊 Total recipes in database: 15247
🔍 FTS index contains: 15247 recipes
==================================================
🎉 Seeding Complete!
```

### Starting the Server
```bash
uvicorn app.main:app --reload --port 5000
```

You should see:
```
✅ Connected to recipe database (15247 recipes loaded)
```

## 🔍 How It Works

1. **Database File**: `data/recipes.db` (SQLite, ~30MB)
2. **Search Engine**: FTS5 (Full-Text Search with BM25 ranking)
3. **Source Data**: `data/recipe_training_improved.txt` (kept locally, not pushed to Git)

## 🎯 Search Examples

The new system understands:
- ✅ "chicken, garlic" → Finds recipes with BOTH
- ✅ "chicken OR beef" → Finds recipes with EITHER
- ✅ "spicy chicken" → Smart matching (understands "hot sauce chicken")

## 🛠️ Troubleshooting

**Problem**: `⚠️ Database not found`
**Solution**: Run `python seed_db.py`

**Problem**: Import errors
**Solution**: The database uses standard Python `sqlite3` (built-in, no installation needed)

## 📦 Git Strategy

**What's Pushed:**
- ✅ Code (`seed_db.py`, `recipe_service.py`)
- ✅ Instructions (this file)

**What's Ignored:**
- ❌ `data/recipes.db` (build locally)
- ❌ `data/*.txt` (source file, too large)

**Result**: Your Git repo stays small (<5MB instead of 20MB+)
