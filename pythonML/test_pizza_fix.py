"""
Quick test to verify pizza now has correct calories
"""
import requests
import json

print("Testing Pizza Calories in Live System")
print("="*50)

payload = {
    'foodItem': 'pizza',
    'mealType': 'Lunch',
    'userProfile': {
        'weightKg': 70,
        'heightCm': 170,
        'age': 25,
        'gender': 'M',
        'activityLevel': 'Moderate',
        'healthGoals': 'Balanced',
        'dietaryRestrictions': 'None'
    }
}

try:
    r = requests.post('http://localhost:5000/api/diet', json=payload, timeout=5)
    result = r.json()
    
    print(f"\n✓ Food Item: {payload['foodItem']}")
    print(f"✓ Calories Consumed: {result['caloriesConsumedEstimate']} kcal")
    print(f"✓ Remaining: {result['caloriesRemaining']} kcal")
    
    if result['caloriesConsumedEstimate'] > 400:
        print("\n✅ SUCCESS - Pizza calories are now realistic!")
        print(f"   (266 kcal/100g × 200g serving = ~532 kcal)")
    else:
        print(f"\n⚠️  Still low: {result['caloriesConsumedEstimate']} kcal")
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*50)
