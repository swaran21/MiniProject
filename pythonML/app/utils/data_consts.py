from app.models import Meal

# --- Heuristic Data ---
RECIPE_TEMPLATES = {
    "Titles": [
        "{Cuisine} Style {Main}",
        "{Main} with {Sides}",
        "Easy {Cuisine} {Main}",
        "Homestyle {Main}"
    ],
    "Instructions": [
        "1. Prep {ingredients}\n2. Cook {main_item} until golden.\n3. Serve hot.",
        "1. Chop {ingredients}\n2. Sauté {main_item} with spices.\n3. Enjoy.",
    ]
}

# --- Mock Data for Validations ---
MEAL_OPTIONS = [
    Meal(name="Oatmeal & Berries", type="Breakfast", calories=350, macros="P:12 C:60 F:6"),
    Meal(name="Greek Yogurt Parfait", type="Breakfast", calories=300, macros="P:20 C:40 F:5"),
    Meal(name="Grilled Chicken Salad", type="Lunch", calories=450, macros="P:40 C:15 F:20"),
    Meal(name="Quinoa & Black Beans", type="Lunch", calories=500, macros="P:18 C:70 F:12"),
    Meal(name="Salmon & Asparagus", type="Dinner", calories=600, macros="P:35 C:10 F:30"),
    Meal(name="Stir Fry Tofu", type="Dinner", calories=400, macros="P:20 C:30 F:18"),
    Meal(name="Almonds (Handful)", type="Snack", calories=160, macros="P:6 C:6 F:14"),
    Meal(name="Apple & Peanut Butter", type="Snack", calories=250, macros="P:4 C:30 F:12")
]

FOOD_CALORIES = {
    "pizza": 285, "burger": 450, "salad": 150, "apple": 95, 
    "banana": 105, "chicken breast": 165, "rice": 206, 
    "pasta": 220, "chocolate": 500, "fries": 365,
    "coffee": 5, "coke": 140, "egg": 78, "pancake": 150
}
