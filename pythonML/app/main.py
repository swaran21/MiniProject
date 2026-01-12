from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
    RecipeRequest, RecipeResponse, 
    UserProfile, MealPlanResponse, 
    DietLogRequest, DietRecommendationResponse
)
from app.services.recipe_service import RecipeService
from app.services.meal_service import MealPlanService
from app.services.diet_service import DietService

app = FastAPI(title="NutriChef AI - Machine Learning Microservice")

# Configure CORS to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "NutriChef AI Microservice is Running!", "docs": "/docs"}

# Service Instances
recipe_service = RecipeService()
meal_service = MealPlanService()
diet_service = DietService()

@app.post("/predict/recipe")
async def predict_recipe(request: RecipeRequest):
    return recipe_service.generate(request)

@app.post("/predict/recipe/rate")
async def rate_recipe(
    recipe_id: int,
    user_id: str,
    rating: int  # 1 for like, -1 for dislike
):
    """Rate a recipe to improve search quality"""
    try:
        result = recipe_service.rate_recipe(recipe_id, user_id, rating)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/predict/recipe/{recipe_id}/rating")
async def get_recipe_rating(recipe_id: int):
    """Get rating statistics for a recipe"""
    try:
        stats = recipe_service.get_recipe_rating(recipe_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/predict/recipes/search")
async def search_recipes(query: str, limit: int = 10):
    """Search recipes by name/title"""
    try:
        results = recipe_service.search_recipes_by_name(query, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/predict/recipes/{recipe_id}")
async def get_recipe_by_id(recipe_id: int):
    """Get full recipe details by ID"""
    try:
        recipe = recipe_service.get_recipe_by_id(recipe_id)
        return recipe
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/predict/meal-plan", response_model=MealPlanResponse)
def generate_meal_plan(profile: UserProfile):
    return meal_service.create_plan(profile)

@app.post("/predict/adaptive-diet", response_model=DietRecommendationResponse)
def adaptive_diet(request: DietLogRequest):
    return diet_service.recommend(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
