from fastapi import FastAPI
from app.models import (
    RecipeRequest, RecipeResponse, 
    UserProfile, MealPlanResponse, 
    DietLogRequest, DietRecommendationResponse
)
from app.services.ml_service import RecipeService, MealPlanService, DietService

app = FastAPI(title="NutriChef AI - Machine Learning Microservice")

@app.get("/")
def read_root():
    return {"message": "NutriChef AI Microservice is Running!", "docs": "/docs"}

# Service Instances
recipe_service = RecipeService()
meal_service = MealPlanService()
diet_service = DietService()

@app.post("/predict/recipe", response_model=RecipeResponse)
def generate_recipe(request: RecipeRequest):
    return recipe_service.generate(request)

@app.post("/predict/meal-plan", response_model=MealPlanResponse)
def generate_meal_plan(profile: UserProfile):
    return meal_service.create_plan(profile)

@app.post("/predict/adaptive-diet", response_model=DietRecommendationResponse)
def adaptive_diet(request: DietLogRequest):
    return diet_service.recommend(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
