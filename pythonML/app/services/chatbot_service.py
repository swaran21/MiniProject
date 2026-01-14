"""
Medical-Aware Chatbot Service
CRITICAL UPDATE: Now respects user medical conditions
Prevents dangerous suggestions (e.g., honey for diabetics)
"""

from typing import Dict, List
import re
from data.config.medical_nutrition_rules import MEDICAL_NUTRITION_RULES

class ChatbotService:
    """
    Medical-Aware Rule-Based Chatbot
    
    SAFETY: Filters all suggestions through medical_nutrition_rules
    to prevent dangerous recommendations
    """
    
    def __init__(self, recipe_service):
        self.recipe_service = recipe_service
        self.medical_rules = MEDICAL_NUTRITION_RULES
        
        # Intent patterns (regex for flexibility)
        self.intent_patterns = {
            'greeting': r'\b(hi|hello|hey|greetings)\b',
            'substitute': r'\b(substitute|replace|swap|instead of|alternative)\b',
            'cooking_tips': r'\b(how to cook|cooking tip|how do i|preparation)\b',
            'ingredient_info': r'\b(what is|tell me about|info about|nutritional)\b',
            'recipe_search': r'\b(recipe|find|search|show me|suggest)\b'
        }
        
        # Medical-aware substitutions
        self.substitutions = {
            'sugar': {
                'generic': ['honey', 'maple syrup', 'agave nectar', 'stevia', 'monk fruit sweetener'],
                'diabetes_safe': ['stevia', 'erythritol', 'monk fruit sweetener', 'allulose'],
                'avoid_diabetes': ['honey', 'maple syrup', 'agave nectar', 'brown sugar', 'coconut sugar']
            },
            'white rice': {
                'generic': ['brown rice', 'quinoa', 'cauliflower rice', 'barley'],
                'diabetes_safe': ['brown rice', 'quinoa', 'barley', 'bulgur', 'cauliflower rice'],
                'avoid_diabetes': []
            },
            'butter': {
                'generic': ['olive oil', 'coconut oil', 'avocado oil', 'ghee'],
                'cholesterol_safe': ['olive oil', 'avocado oil', 'vegetable oil spray'],
                'avoid_cholesterol': ['ghee', 'coconut oil']
            },
            'salt': {
                'generic': ['herbs', 'spices', 'lemon juice', 'garlic', 'onion powder'],
                'hypertension_safe': ['herbs', 'spices', 'lemon juice', 'garlic', 'vinegar'],
                'avoid_hypertension': []
            },
            'wheat flour': {
                'generic': ['all-purpose flour', 'almond flour', 'coconut flour', 'rice flour'],
                'celiac_safe': ['rice flour', 'almond flour', 'coconut flour', 'oat flour (certified GF)'],
                'avoid_celiac': ['all-purpose flour', 'whole wheat flour', 'barley flour']
            },
            'milk': {
                'generic': ['almond milk', 'soy milk', 'oat milk', 'coconut milk'],
                'lactose_free': ['almond milk', 'soy milk', 'oat milk', 'coconut milk', 'lactose-free milk'],
                'avoid_dairy': []
            }
        }
    
    def chat(self, message: str, user_conditions: List[str] = None) -> Dict:
        """
        Main chat handler with medical awareness
        
        Args:
            message: User's message
            user_conditions: List of user's medical conditions (e.g., ['diabetes_type2'])
        
        Returns:
            dict with response and metadata
        """
        # Classify intent
        intent = self._classify_intent(message)
        
        # Route to appropriate handler
        if intent == 'greeting':
            response = self._handle_greeting()
        elif intent == 'substitute':
            response = self._handle_substitution(message, user_conditions)
        elif intent == 'cooking_tips':
            response = self._handle_cooking_tips(message)
        elif intent == 'ingredient_info':
            response = self._handle_ingredient_info(message)
        elif intent == 'recipe_search':
            response = self._handle_recipe_search(message)
        else:
            response = self._handle_fallback()
        
        return {
            'reply': response,
            'intent': intent,
            'medical_filtered': user_conditions is not None
        }
    
    def _classify_intent(self, message: str) -> str:
        """Classify user intent using regex patterns"""
        message_lower = message.lower()
        
        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, message_lower):
                return intent
        
        return 'unknown'
    
    def _handle_greeting(self) -> str:
        """Handle greeting"""
        return ("👋 Hello! I'm your Medical Nutrition Assistant.\n\n"
                "I can help you with:\n"
                "• **Ingredient substitutions** (medical-safe!)\n"
                "• **Cooking tips** for healthier meals\n"
                "• **Recipe suggestions** for your diet\n"
                "• **Nutritional information**\n\n"
                "💡 Tip: Tell me about your medical conditions for personalized advice!")
    
    def _handle_substitution(self, query: str, user_conditions: List[str] = None) -> str:
        """
        MEDICAL-AWARE Substitution Logic
        
        CRITICAL: Filters suggestions based on user's medical conditions
        Prevents dangerous recommendations (e.g., honey for diabetics)
        """
        query_lower = query.lower()
        
        # Find which ingredient they're asking about
        for ingredient, subs_data in self.substitutions.items():
            if ingredient in query_lower:
                # Extract safe substitutions based on conditions
                safe_subs = []
                warnings = []
                condition_names = []
                
                if user_conditions:
                    # Get condition-specific safe options
                    for condition in user_conditions:
                        if condition in self.medical_rules:
                            condition_names.append(self.medical_rules[condition]['display_name'])
                        
                        # Check for condition-specific safe list
                        safe_key = f'{condition}_safe'
                        avoid_key = f'avoid_{condition}'
                        
                        # Start with generic options
                        if not safe_subs:
                            safe_subs = subs_data.get('generic', []).copy()
                        
                        # Filter using condition-specific avoid list
                        if avoid_key in subs_data:
                            avoid_list = subs_data[avoid_key]
                            for avoid_item in avoid_list:
                                if avoid_item in safe_subs:
                                    safe_subs.remove(avoid_item)
                                    warnings.append(f"⚠️ Removed **{avoid_item}** (unsafe for {self.medical_rules[condition]['display_name']})")
                        
                        # Use condition-specific safe list if available
                        if safe_key in subs_data:
                            condition_safe = subs_data[safe_key]
                            # Only keep items that are in the safe list
                            safe_subs = [item for item in safe_subs if item in condition_safe or item not in subs_data.get(avoid_key, [])]
                            # Add condition-specific items
                            for safe_item in condition_safe:
                                if safe_item not in safe_subs:
                                    safe_subs.append(safe_item)
                    
                    # Additional filtering through medical rules
                    safe_subs = self._filter_by_medical_rules(safe_subs, user_conditions)
                    
                else:
                    # No conditions specified - use generic
                    safe_subs = subs_data.get('generic', [])
                
                # Generate response
                if not safe_subs:
                    return (f"⚠️ **MEDICAL ALERT**\n\n"
                            f"For **{ingredient}**, standard substitutes are not safe for your conditions "
                            f"({', '.join(condition_names)}).\n\n"
                            f"**Recommendation:** Please consult your dietitian for safe alternatives specific to your case.")
                
                # Build response
                condition_note = f" (safe for {', '.join(condition_names)})" if condition_names else ""
                response = f"✅ For **{ingredient}**{condition_note}:\n\n"
                
                for i, sub in enumerate(safe_subs, 1):
                    response += f"{i}. **{sub}**\n"
                
                if warnings:
                    response += "\n**Safety Notes:**\n" + "\n".join(warnings)
                
                if user_conditions:
                    response += f"\n\n💡 *Filtered for your medical safety*"
                
                return response
        
        # No matching ingredient found
        return ("I couldn't find substitution suggestions for that ingredient.\n\n"
                "Try: 'substitute for sugar', 'replace butter', or 'alternative to white rice'")
    
    def _filter_by_medical_rules(self, substitutions: List[str], conditions: List[str]) -> List[str]:
        """
        Additional safety filter using medical_nutrition_rules
        
        Double-checks that suggested substitutions don't contain restricted foods
        """
        safe_items = []
        
        for sub in substitutions:
            is_safe = True
            sub_lower = sub.lower()
            
            # Check against each condition's restricted foods
            for condition in conditions:
                if condition in self.medical_rules:
                    avoid_foods = self.medical_rules[condition].get('foods_to_avoid', [])
                    
                    # Simple substring check (you could use your Scorer logic here for better accuracy)
                    for bad_food in avoid_foods:
                        if bad_food.lower() in sub_lower:
                            is_safe = False
                            break
                
                if not is_safe:
                    break
            
            if is_safe:
                safe_items.append(sub)
        
        return safe_items
    
    def _handle_cooking_tips(self, query: str) -> str:
        """Handle cooking tips request"""
        return ("🍳 **General Healthy Cooking Tips:**\n\n"
                "• Use **low-sodium** seasonings like herbs and spices\n"
                "• **Grill, bake, or steam** instead of frying\n"
                "• Add **vegetables** to every meal (aim for half your plate)\n"
                "• Use **whole grains** instead of refined grains\n"
                "• Measure **portions** to control calorie intake\n\n"
                "💡 *Ask about specific ingredients for personalized medical-safe tips!*")
    
    def _handle_ingredient_info(self, query: str) -> str:
        """Handle ingredient information request"""
        return ("📖 **Ingredient Information:**\n\n"
                "I can provide nutritional info! Try asking:\n"
                "• 'Tell me about quinoa'\n"
                "• 'What is the glycemic index of brown rice?'\n"
                "• 'Nutritional value of spinach'\n\n"
                "💡 *Share your medical conditions for personalized insights!*")
    
    def _handle_recipe_search(self, query: str) -> str:
        """Handle recipe search request"""
        return ("🔍 **Recipe Search:**\n\n"
                "I'll help you find safe recipes! Try:\n"
                "• 'Find diabetes-friendly breakfast recipes'\n"
                "• 'Low-sodium dinner ideas'\n"
                "• 'Gluten-free desserts'\n\n"
                "💡 *Tell me your dietary needs for better suggestions!*")
    
    def _handle_fallback(self) -> str:
        """Handle unknown intents"""
        return ("🤔 I'm not sure I understood that.\n\n"
                "I can help with:\n"
                "• **Substitutions** - 'substitute for sugar'\n"
                "• **Cooking tips** - 'how to cook quinoa'\n"
                "• **Recipes** - 'find heart-healthy recipes'\n"
                "• **Nutrition info** - 'nutritional value of spinach'\n\n"
                "What would you like to know?")
