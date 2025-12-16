import requests
import json

# URL of your local API
url = "http://localhost:5000/predict/adaptive-diet"

# Sample Data matching 'DietLogRequest'
payload = {
    "foodItem": "Cheese Pizza",
    "mealType": "Lunch",
    "userProfile": {
        "weightKg": 80,
        "heightCm": 175,
        "age": 30,
        "gender": "Male",
        "activityLevel": "Moderate",
        "healthGoals": "Lose Weight",
        "dietaryRestrictions": "None"
    }
}

print("--- Testing NutriChef AI ML Endpoint ---")
print(f"Target: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        # Check if we got a real suggestion
        print(f"Suggestion: {data.get('nextMealSuggestion')}")
    else:
        print(f"\n❌ FAILED. Status Code: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n❌ FAILED: Could not connect to server.")
    print("Make sure the server is running! (Run 'run_server.bat')")
