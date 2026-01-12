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
from app.services.chatbot_service import ChatbotService

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

# Initialize chatbot service
chatbot_service = ChatbotService(recipe_service)

# Initialize health services
from app.services.prescription_analyzer import PrescriptionAnalyzer
from app.services.recipe_health_scorer import RecipeHealthScorer
from app.services.medical_meal_planner import MedicalMealPlanner

prescription_analyzer = PrescriptionAnalyzer()
health_scorer = RecipeHealthScorer()
medical_meal_planner = MedicalMealPlanner(recipe_service.db_conn)

@app.post("/chat")
async def chat(message: str):
    """AI Chatbot endpoint - Retrieval + Templates"""
    try:
        response = chatbot_service.chat(message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

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

# ===== HEALTH-BASED MEAL PLANNING ENDPOINTS =====

@app.post("/health/analyze-prescription")
async def analyze_prescription(prescription_text: str, user_id: int = None):
    """Analyze prescription text to extract conditions and generate recommendations"""
    try:
        analysis = prescription_analyzer.analyze(prescription_text, user_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/health/filter-recipes")
async def filter_recipes_by_health(conditions: list, min_score: int = 70, limit: int = 50):
    """
    Filter recipes based on health conditions
    conditions: list of condition keys (e.g., ['diabetes_type2', 'hypertension'])
    min_score: minimum health score (0-100)
    """
    try:
        # Get all recipes from database
        conn = recipe_service.db_conn
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, ingredients, instructions, cuisine, calories,
                   likes, dislikes, rating_score
            FROM recipes
            LIMIT 1000
        """)
        
        recipes = []
        for row in cursor.fetchall():
            recipes.append({
                'id': row['id'],
                'title': row['title'],
                'ingredients': row['ingredients'],
                'instructions': row['instructions'],
                'cuisine': row['cuisine'] or 'Any',
                'calories': row['calories'],
                'likes': row['likes'],
                'dislikes': row['dislikes'],
                'rating_score': row['rating_score']
            })
        
        # Filter by health score
        safe_recipes = health_scorer.filter_safe_recipes(recipes, conditions, min_score)
       
        return {
            'total_checked': len(recipes),
            'safe_recipes_count': len(safe_recipes),
            'recipes': safe_recipes[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filtering error: {str(e)}")

@app.get("/health/recipe-score/{recipe_id}")
async def get_recipe_health_score(recipe_id: int, conditions: str):
    """
    Get health score for a specific recipe
    conditions: comma-separated condition keys
    """
    try:
        condition_list = [c.strip() for c in conditions.split(',')]
        
        # Get recipe from database
        conn = recipe_service.db_conn
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        recipe = {
            'id': row['id'],
            'title': row['title'],
            'ingredients': row['ingredients']
        }
        
        score = health_scorer.calculate_health_score(recipe, condition_list)
        category = health_scorer.categorize_recipe(recipe, condition_list)
        warnings = health_scorer.get_warnings(recipe, condition_list)
        recommendation = health_scorer.get_recipe_recommendations(recipe, condition_list)
        
        return {
            'recipe_id': recipe_id,
            'health_score': score,
            'category': category,
            'warnings': warnings,
            'recommendation': recommendation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/health/generate-meal-plan")
async def generate_medical_meal_plan(
    prescription_text: str = None,
    conditions: list = None,
    user_id: int = None,
    duration_days: int = None
):
    """
    Generate complete medical meal plan
    Either provide prescription_text OR conditions list
    """
    try:
        # Analyze prescription if provided
        if prescription_text:
            analysis = prescription_analyzer.analyze(prescription_text, user_id)
        elif conditions:
            # Create minimal analysis from condition list
            analysis = {
                'user_id': user_id,
                'detected_conditions': conditions,
                'plan_duration_days': duration_days or 90,
                'medications': [],
                'special_notes': []
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail="Provide either prescription_text or conditions list"
            )
        
        # Generate meal plan
        meal_plan = medical_meal_planner.create_plan(analysis, duration_days)
        
        return meal_plan
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meal plan error: {str(e)}")

# ===== END HEALTH ENDPOINTS =====

@app.post("/predict/adaptive-diet", response_model=DietRecommendationResponse)
def adaptive_diet(request: DietLogRequest):
    return diet_service.recommend(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
