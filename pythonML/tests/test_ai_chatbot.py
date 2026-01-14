"""
Test Script for AI Chatbot
Run this after getting your Gemini API key
"""

from app.services.ai_chatbot_service import create_ai_chatbot
import os

print("=" * 60)
print("🤖 AI CHATBOT TEST")
print("=" * 60)

# Check API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("\n❌ ERROR: GEMINI_API_KEY not found!")
    print("\n📝 SETUP INSTRUCTIONS:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Create API key")
    print("3. Create .env file with: GEMINI_API_KEY=your_key_here")
    print("\nOr set environment variable:")
    print("   Windows: set GEMINI_API_KEY=your_key")
    print("   Linux/Mac: export GEMINI_API_KEY=your_key")
    exit(1)

print(f"\n✅ API Key found: {api_key[:10]}...")

# Create chatbot
print("\n🔧 Initializing AI Chatbot...")
try:
    chatbot = create_ai_chatbot()
    print("✅ Chatbot initialized successfully!")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    exit(1)

# Test 1: General greeting
print("\n" + "=" * 60)
print("TEST 1: General Greeting")
print("=" * 60)

response1 = chatbot.chat("Hello!")
print(f"\n**User:** Hello!")
print(f"**Bot:** {response1['reply']}")
print(f"**Model:** {response1['model']}")

# Test 2: Diabetes - Safe substitution
print("\n" + "=" * 60)
print("TEST 2: Diabetes - Sugar Substitution (SAFE)")
print("=" * 60)

response2 = chatbot.chat(
    message="What can I use instead of sugar?",
    user_conditions=['diabetes_type2']
)
print(f"\n**User (Diabetes):** What can I use instead of sugar?")
print(f"**Bot:** {response2['reply']}")
print(f"**Medical Filtered:** {response2['medical_filtered']}")
print(f"**Validation Passed:** {response2.get('validation_passed', 'N/A')}")

# Test 3: Diabetes - Dangerous suggestion test
print("\n" + "=" * 60)
print("TEST 3: Diabetes - Testing Safety Validation")
print("=" * 60)

response3 = chatbot.chat(
    message="Can I eat honey?",
    user_conditions=['diabetes_type2']
)
print(f"\n**User (Diabetes):** Can I eat honey?")
print(f"**Bot:** {response3['reply']}")
if response3.get('validation_blocked'):
    print(f"**🛡️ SAFETY BLOCK:** {response3['blocked_reason']}")

# Test 4: Celiac - Recipe request
print("\n" + "=" * 60)
print("TEST 4: Celiac - Recipe Search")
print("=" * 60)

response4 = chatbot.chat(
    message="Find me a breakfast recipe",
    user_conditions=['celiac']
)
print(f"\n**User (Celiac):** Find me a breakfast recipe")
print(f"**Bot:** {response4['reply']}")

# Test 5: Multiple conditions
print("\n" + "=" * 60)
print("TEST 5: Multiple Conditions (Diabetes + Hypertension)")
print("=" * 60)

response5 = chatbot.chat(
    message="What should I eat for dinner?",
    user_conditions=['diabetes_type2', 'hypertension']
)
print(f"\n**User (Diabetes + HBP):** What should I eat for dinner?")
print(f"**Bot:** {response5['reply']}")

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED!")
print("=" * 60)
print("\n💡 TIP: Try asking your own questions:")
print("   from app.services.ai_chatbot_service import create_ai_chatbot")
print("   chatbot = create_ai_chatbot()")
print("   response = chatbot.chat('Your question', ['diabetes_type2'])")
print("   print(response['reply'])")
