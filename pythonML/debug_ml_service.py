from app.services.ml_service import DietService
from app.models import DietLogRequest, UserProfile
import traceback

print("START_DEBUG")
try:
    s = DietService()
    if s.model is None: print("MODEL_IS_NONE"); exit()
    
    # Manually trigger the logic block
    if isinstance(s.model, dict):
        print("MODEL_IS_DICT")
        clf = s.model['model']
        feats = s.model['features']
        print(f"FEATURES: {feats}")
    else:
        print("MODEL_IS_RAW")
        
    p = UserProfile(weightKg=80, heightCm=175, age=30, gender="Male", activityLevel="Moderate", healthGoals="L", dietaryRestrictions="N")
    req = DietLogRequest(foodItem="Pizza", mealType="L", userProfile=p)
    
    res = s.recommend(req)
    print(f"RESULT: {res.nextMealSuggestion}")

except Exception:
    traceback.print_exc()
print("END_DEBUG")
