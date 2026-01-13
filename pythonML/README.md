# NutriChef AI - Medical Nutrition Assistant

AI-powered nutrition management system with prescription-based meal planning.

##  Project Structure

\\\
pythonML/
 app/                    # Main application code
    models/            # ML models
    services/          # Business logic services
    utils/             # Helper utilities
    main.py           # FastAPI application entry point

 data/                   # Data storage
    config/            # Configuration files
    database/          # SQLite databases
    training/          # Training datasets
    raw/               # Raw source data

 tests/                  # Test suite
    test_chatbot.py
    test_health_system.py
    test_meal_planner.py

 scripts/                # Utility scripts
    seed_db.py         # Database seeding
    migrate_ratings.py # Database migrations

 docs/                   # Documentation
    DATABASE_SETUP.md

 requirements.txt        # Production dependencies
 requirements_training.txt  # Training dependencies
 pytest.ini             # Test configuration
\\\

##  Quick Start

### 1. Install Dependencies
\\\ash
pip install -r requirements.txt
\\\

### 2. Setup Database
\\\ash
python scripts/seed_db.py
python scripts/migrate_ratings.py
\\\

### 3. Run Backend
\\\ash
uvicorn app.main:app --reload --port 5000
\\\

### 4. Run Tests
\\\ash
pytest tests/
\\\

##  Documentation

- [Database Setup](docs/DATABASE_SETUP.md)

##  Testing

Run all tests:
\\\ash
pytest tests/ -v
\\\

Run specific test:
\\\ash
pytest tests/test_chatbot.py
\\\

##  Database Management

### Seed Database
\\\ash
python scripts/seed_db.py
\\\

### Run Migrations
\\\ash
python scripts/migrate_ratings.py
\\\
