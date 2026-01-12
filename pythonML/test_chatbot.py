# Quick test of chatbot endpoint
import requests

# Test different queries
queries = [
    "hello",
    "find me chicken recipes",
    "can I replace eggs?",
    "how to cook rice?",
    "calories for weight loss"
]

print("Testing Chatbot Endpoint...\n")

for query in queries:
    try:
        r = requests.post('http://localhost:5000/chat', params={'message': query})
        response = r.json()
        print(f"Q: {query}")
        print(f"A: {response['reply'][:100]}...")
        print(f"Intent: {response.get('intent', 'N/A')}\n")
    except Exception as e:
        print(f"Error: {e}\n")
