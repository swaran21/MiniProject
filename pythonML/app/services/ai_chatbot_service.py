"""
AI-Powered Medical Chatbot using Google Gemini + RAG
SAFETY: Grounded in medical_nutrition_rules.py with custom domain layer
"""

from google import genai
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from data.config.medical_nutrition_rules import MEDICAL_NUTRITION_RULES
import re

# Load environment variables
load_dotenv()

class AIChatbotService:
    """
    Generative AI chatbot with medical safety through RAG + Custom Domain Layer
    
    Architecture:
    1. RAG: Inject medical rules into context
    2. Gemini API: Generate natural language responses
    3. Custom Domain Layer: Safety validation + domain models
    """
    
    def __init__(self, recipe_service=None):
        self.recipe_service = recipe_service
        self.medical_rules = MEDICAL_NUTRITION_RULES
        
        # Configure Gemini API (new library)
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found! "
                "Get it from: https://makersuite.google.com/app/apikey"
            )
        
        # Create client with new API
        os.environ['GEMINI_API_KEY'] = api_key  # Set for client auto-detection
        self.client = genai.Client(api_key=api_key)
        
        # Model configuration
        self.model_name = 'gemini-3-flash-preview'  # Latest model
        self.generation_config = {
            'temperature': 0.7,  # Balance creativity and accuracy
            'top_p': 0.9,
            'top_k': 40,
            'max_output_tokens': 1024,
        }
        
        # System prompt template
        self.system_prompt_template = """You are **NutriChef AI**, a medical nutrition assistant specialized in personalized meal planning.

**Your Role:**
- Provide evidence-based nutrition advice
- Suggest safe ingredient substitutions based on medical conditions
- Recommend recipes from the database
- Answer cooking and nutrition questions with empathy

**CRITICAL SAFETY RULES:**
1. ⚠️ NEVER suggest foods that are restricted for the user's medical conditions
2. ✅ ALWAYS check the medical rules provided in context before answering
3. 🏥 If medical question is complex, recommend consulting a doctor/dietitian
4. 📚 Cite the medical rules when giving condition-specific advice
5. ❤️ Be empathetic, supportive, and encouraging

**Response Guidelines:**
- Be conversational and friendly (not robotic)
- Use 1-2 emojis per response (not excessive)
- Include actionable tips and specific recommendations
- Format with markdown (bold, lists, etc.)
- Keep responses concise (3-5 short paragraphs max)

**User's Medical Context:**
{conditions_context}

**Relevant Medical Rules:**
{rules_context}

**Available Recipes Context:**
{recipes_context}
"""
    
    def chat(self, message: str, user_conditions: List[str] = None) -> Dict:
        """
        Main chat handler with AI generation + domain validation
        
        Args:
            message: User's message
            user_conditions: List of medical conditions (e.g., ['diabetes_type2'])
        
        Returns:
            dict with AI-generated response and metadata
        """
        # Step 1: Build medical context (RAG)
        context = self._build_medical_context(user_conditions)
        
        # Step 2: Check if recipe search is needed
        if self._is_recipe_query(message) and self.recipe_service:
            context['recipes_context'] = self._get_recipe_context(message)
        else:
            context['recipes_context'] = "No specific recipes searched."
        
        # Step 3: Build full prompt with context
        full_prompt = self._build_prompt(message, context)
        
        # Step 4: Generate AI response
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=self.generation_config
            )
            ai_response = response.text
            
            # Step 5: Domain Layer Validation
            validation = self._validate_response(ai_response, user_conditions or [])
            
            if not validation['is_safe']:
                # CRITICAL: AI suggested dangerous food!
                return {
                    'reply': self._get_safe_fallback_response(message, user_conditions),
                    'medical_filtered': True,
                    'conditions': user_conditions or [],
                    'model': self.model_name,
                    'validation_blocked': True,
                    'blocked_reason': validation['reason']
                }
            
            # Safe response
            return {
                'reply': ai_response,
                'medical_filtered': user_conditions is not None,
                'conditions': user_conditions or [],
                'model': self.model_name,
                'validation_passed': True
            }
        
        except Exception as e:
            # Fallback to safe error message
            # Print error for debugging
            print(f"\n⚠️ API Error: {str(e)}")
            
            return {
                'reply': (
                    "I apologize, but I'm having trouble processing your request right now. "
                    "For medical advice, please consult your healthcare provider.\n\n"
                    "**I can still help with:**\n"
                    "• Recipe searches\n"
                    "• Ingredient substitutions\n"
                    "• General cooking tips"
                ),
                'error': str(e),
                'medical_filtered': False,
                'model': 'fallback'
            }
    
    def _build_medical_context(self, user_conditions: List[str]) -> Dict:
        """
        RAG: Retrieve relevant medical rules for context injection
        """
        if not user_conditions:
            return {
                'conditions_context': 'No specific medical conditions provided. General healthy eating advice applies.',
                'rules_context': 'Focus on balanced nutrition, whole foods, and portion control.'
            }
        
        # Build condition context
        condition_names = []
        rules_text = ""
        
        for condition in user_conditions:
            if condition in self.medical_rules:
                rules = self.medical_rules[condition]
                condition_names.append(rules['display_name'])
                
                # Format rules for AI context
                rules_text += f"\n### {rules['display_name']}\n\n"
                
                # Foods to avoid (critical for safety!)
                avoid_foods = rules['foods_to_avoid'][:15]  # Top 15 restrictions
                rules_text += f"**🚫 Foods to AVOID:** {', '.join(avoid_foods)}\n\n"
                
                # Foods to eat
                eat_foods = rules['foods_to_eat'][:15]
                rules_text += f"**✅ Foods to EAT:** {', '.join(eat_foods)}\n\n"
                
                # Special notes
                if 'special_notes' in rules:
                    rules_text += f"**📋 Important Notes:**\n"
                    for note in rules['special_notes'][:4]:
                        rules_text += f"- {note}\n"
                    rules_text += "\n"
        
        return {
            'conditions_context': f"User has: **{', '.join(condition_names)}**",
            'rules_context': rules_text
        }
    
    def _build_prompt(self, user_message: str, context: Dict) -> str:
        """
        Build complete prompt with system instructions + context + user message
        """
        # Inject context into system prompt
        system_with_context = self.system_prompt_template.format(**context)
        
        # Combine system + user message
        full_prompt = f"{system_with_context}\n\n**User Question:**\n{user_message}\n\n**Your Response:**"
        
        return full_prompt
    
    def _is_recipe_query(self, message: str) -> bool:
        """Check if user is asking for recipes"""
        recipe_keywords = ['recipe', 'find', 'search', 'suggest', 'show me', 'recommend']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in recipe_keywords)
    
    def _get_recipe_context(self, message: str) -> str:
        """Get relevant recipes from database"""
        try:
            results = self.recipe_service.search_recipes_by_name(message, limit=5)
            
            if results:
                recipe_text = "\n**Available Recipes from Database:**\n\n"
                for i, recipe in enumerate(results[:5], 1):
                    rating_pct = round((recipe['likes'] / max(recipe['total_ratings'], 1)) * 100)
                    recipe_text += f"{i}. **{recipe['title']}** ({recipe['cuisine']}) - 👍 {recipe['likes']} likes ({rating_pct}%)\n"
                return recipe_text
            else:
                return "No matching recipes found in database."
        
        except:
            return "Recipe search unavailable."
    
    def _validate_response(self, response: str, user_conditions: List[str]) -> Dict:
        """
        CUSTOM DOMAIN LAYER: Validate AI response for medical safety
        
        Checks if AI response RECOMMENDS restricted foods (not just mentions them)
        """
        if not user_conditions:
            return {'is_safe': True, 'reason': None}
        
        response_lower = response.lower()
        
        # Check each condition's restricted foods
        for condition in user_conditions:
            if condition in self.medical_rules:
                avoid_foods = self.medical_rules[condition]['foods_to_avoid']
                
                for food in avoid_foods[:20]:  # Check top 20 restrictions
                    # Use word boundaries to avoid false positives
                    pattern = r'\b' + re.escape(food.lower()) + r'\b'
                    
                    # Check if AI mentions this food
                    if re.search(pattern, response_lower):
                        # Get surrounding context (more context = better detection)
                        match = re.search(pattern, response_lower)
                        if match:
                            start = max(0, match.start() - 100)
                            end = min(len(response_lower), match.end() + 100)
                            context = response_lower[start:end]
                            
                            # Positive words (recommending the food)
                            positive_keywords = [
                                'try', 'use it', 'eat it', 'have it', 'good choice',
                                'recommend', 'great option', 'perfect', 'excellent',
                                'can have', 'is fine', 'is okay', 'go ahead'
                            ]
                            
                            # Negative words (warning against the food)
                            negative_keywords = [
                                'avoid', 'don\'t', 'do not', 'not', 'shouldn\'t',
                                'should not', 'restrict', 'stay away', 'skip',
                                'eliminate', 'remove', 'cut out', 'dangerous',
                                'harmful', 'risky', 'problematic', 'bad', 'unsafe',
                                'instead of'  # KEY: "instead of X" means X is bad!
                            ]
                            
                            # More sophisticated check
                            has_positive = any(kw in context for kw in positive_keywords)
                            has_negative = any(kw in context for kw in negative_keywords)
                            
                            # Special case: Check for "instead of [restricted food]" pattern
                            # This is ALWAYS a warning, never a recommendation
                            if f'instead of {food.lower()}' in response_lower:
                                # This is safe - AI is recommending alternatives
                                continue
                            
                            # BLOCK only if recommending WITHOUT warning
                            if has_positive and not has_negative:
                                print(f"\n🛡️ VALIDATION BLOCKED: '{food}' for {self.medical_rules[condition]['display_name']}")
                                print(f"   Context: ...{context}...")
                                print(f"   Positive keywords found: {has_positive}")
                                print(f"   Negative keywords found: {has_negative}")
                                
                                return {
                                    'is_safe': False,
                                    'reason': f"AI recommended restricted food '{food}' for {self.medical_rules[condition]['display_name']}"
                                }
                            
                            # If just mentioning or warning, that's OK
        
        return {'is_safe': True, 'reason': None}
    
    def _get_safe_fallback_response(self, message: str, user_conditions: List[str]) -> str:
        """
        Fallback response when AI validation fails
        """
        condition_names = [
            self.medical_rules[c]['display_name'] 
            for c in (user_conditions or []) 
            if c in self.medical_rules
        ]
        
        return (
            f"⚠️ **Safety Check Triggered**\n\n"
            f"I detected a potential safety issue in my response for your conditions "
            f"({', '.join(condition_names)}).\n\n"
            f"**For your safety, I recommend:**\n"
            f"1. Consulting your healthcare provider or dietitian\n"
            f"2. Checking our medical nutrition rules for specific guidance\n"
            f"3. Asking me a more specific question about safe alternatives\n\n"
            f"What specific aspect would you like help with?"
        )


# Convenience function for simple usage
def create_ai_chatbot(recipe_service=None):
    """Factory function to create AI chatbot instance"""
    return AIChatbotService(recipe_service)
