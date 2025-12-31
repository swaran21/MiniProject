import requests
import json

# URL of your local API
url = "http://localhost:5000/predict/recipe"

# Sample Data matching 'RecipeRequest'
payload = {
    "ingredients": "Chicken, Tomato, Basil",
    "cuisine": "Italian",
    "dietaryRestrictions": "None"
}

print("--- Testing NutriChef AI RECIPE Endpoint ---")
print(f"Target: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Response from Server:")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        # Check title
        print(f"\nGenerated Title: {data.get('title')}")
    else:
        print(f"\n❌ FAILED. Status Code: {response.status_code}")
        print("Error Details:", response.text)
        
except requests.exceptions.ConnectionError:
    print("\n❌ FAILED: Could not connect to server.")
    print("Make sure the server is running!")
