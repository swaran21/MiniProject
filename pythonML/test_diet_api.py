import requests
import json

url = "http://localhost:5000/predict/adaptive-diet"
payload = {
    "foodItem": "Cheese Pizza",
    "mealType": "Lunch",
    "userProfile": {
        "weightKg": 75,
        "heightCm": 175,
        "age": 25,
        "gender": "Male",
        "activityLevel": "Moderate",
        "healthGoals": "Balanced"
    }
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        if "dayPlan" in data and len(data["dayPlan"]) > 0:
            print("\n✅ dayPlan is present and populated!")
        else:
            print("\n❌ dayPlan is missing or empty!")
    else:
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
