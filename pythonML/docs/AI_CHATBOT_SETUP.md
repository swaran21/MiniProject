# AI Chatbot Setup Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Get API Key

1. Go to: **https://makersuite.google.com/app/apikey**
2. Sign in with Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)

### Step 2: Configure Environment

Create `.env` file in `pythonML/` directory:

```bash
GEMINI_API_KEY=AIza...your_actual_key_here
```

### Step 3: Install Dependencies

```bash
pip install google-generativeai python-dotenv
```

### Step 4: Test It!

```bash
python test_ai_chatbot.py
```

---

## 📖 Usage Examples

### Basic Chat

```python
from app.services.ai_chatbot_service import create_ai_chatbot

chatbot = create_ai_chatbot()
response = chatbot.chat("Hello!")
print(response['reply'])
```

### Medical-Aware Chat

```python
# User with diabetes
response = chatbot.chat(
    message="What can I substitute for sugar?",
    user_conditions=['diabetes_type2']
)
print(response['reply'])
# Output: Suggests stevia, erythritol (NOT honey/maple syrup!)
```

### With Recipe Search

```python
from app.services.recipe_service import RecipeService

recipe_service = RecipeService(db_conn)
chatbot = create_ai_chatbot(recipe_service)

response = chatbot.chat(
    message="Find me a diabetes-friendly breakfast",
    user_conditions=['diabetes_type2']
)
# Chatbot will search database and suggest safe recipes!
```

---

## 🛡️ Safety Features

The chatbot has **3 layers of safety**:

1. **RAG:** Injects medical rules into context
2. **Domain Validation:** Checks responses for restricted foods
3. **Fallback:** Safe responses if validation fails

**Example:**

User (Diabetes): "Can I have honey?"

```
✅ If AI says "NO, use stevia instead" → Response passes validation
❌ If AI says "YES, honey is fine" → BLOCKED by validation layer!
```

---

## 🎯 Response Format

```python
{
    'reply': 'AI generated response text...',
    'medical_filtered': True,  # If conditions were provided
    'conditions': ['diabetes_type2'],
    'model': 'gemini-pro',
    'validation_passed': True,  # Safety check result
    # If validation failed:
    'validation_blocked': True,
    'blocked_reason': 'AI suggested honey for diabetes'
}
```

---

## 💰 Cost & Limits

**Gemini Free Tier:**
- 60 requests/minute
- 1,500 requests/day
- **FREE** ✅

**Your usage:** ~750 requests/day → **Well within limits!**

---

## 🔧 Troubleshooting

### "API Key not found"
→ Create `.env` file with `GEMINI_API_KEY=your_key`

### "Quota exceeded"
→ Wait 1 minute (60 req/min limit) or upgrade to paid tier

### "Model not responding"
→ Check internet connection, API might be down

---

## 📊 Architecture

```
User Question
     ↓
[1. RAG: Retrieve Medical Rules for context]
     ↓
[2. Gemini API: Generate natural language response]
     ↓
[3. Domain Validation: Check for dangerous suggestions]
     ↓
     ├─ SAFE → Return AI response
     └─ UNSAFE → Return fallback safe response
```

---

Ready to use! 🎉
