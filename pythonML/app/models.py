from pydantic import BaseModel
from typing import List, Optional

# --- Input Models ---

class RecipeRequest(BaseModel):
    ingredients: str
    cuisine: str = "Any"
    dietaryRestrictions: str = ""

class UserProfile(BaseModel):
    weightKg: float
    heightCm: float
    age: int
    gender: str
    activityLevel: str
    healthGoals: str  # e.g., "Lose Weight", "Gain Muscle"
    dietaryRestrictions: str = "None"

class DietLogRequest(BaseModel):
    foodItem: str       # e.g., "Cheese Pizza"
    mealType: str       # e.g., "Lunch"
    userProfile: UserProfile

# --- Output Models ---

class RecipeResponse(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    cuisineType: str
    calories: int
    imageUrl: str  # Placeholder URL is fine for now

class Meal(BaseModel):
    name: str
    type: str       # Breakfast, Lunch, Dinner, Snack
    calories: int
    macros: str     # e.g., "P: 20g, C: 40g, F: 10g"

class MealPlanResponse(BaseModel):
    goal: str
    totalDailyCalories: int
    suggestion: str
    meals: List[Meal]

class RecommendedMeal(BaseModel):
    type: str # Breakfast, Lunch, Dinner, Snack
    recipe: RecipeResponse
    suggestionReason: str

class DietRecommendationResponse(BaseModel):
    caloriesConsumedEstimate: int
    caloriesRemaining: int
    nutritionalAnalysis: str
    nextMealSuggestion: str
    dayPlan: List[RecommendedMeal] = []
