import re
from typing import Dict, List, Tuple

class ChatbotService:
    """
    Retrieval + Template-based chatbot for cooking/nutrition assistance
    """
    
    def __init__(self, recipe_service):
        self.recipe_service = recipe_service
        
        # Intent patterns - made more flexible
        self.intents = {
            'recipe_search': [
                r'(?:find|search|show|get|suggest|recommend|looking for|need|want).*?(?:recipe|dish|meal)',
                r'(?:how to|want to)\s+(?:make|cook|prepare)',
                r'recipe\s+(?:for|with)',
                r'(?:any|some)\s+recipe',
                r'chicken|beef|pork|fish|pasta|rice|curry|soup'  # Common food keywords
            ],
            'ingredient_substitute': [
                r'(?:replace|substitute|swap|instead of|alternative)',
                r'can i use\s+\w+\s+instead',
                r'what can i use instead',
                r'don\'t have|no\s+\w+|out of'
            ],
            'nutrition': [
                r'(?:calorie|protein|fat|carb|nutrition|healthy|diet)',
                r'how many calories',
                r'is this (?:good|bad) for',
                r'(?:lose|gain) weight'
            ],
            'cooking_tips': [
                r'how (?:to|do i|should i)',
                r'what (?:temperature|time)',
                r'(?:tip|advice|best way)',
                r'should i cook'
            ],
            'greeting': [
                r'^(?:hi|hello|hey|greetings)',
                r'good (?:morning|afternoon|evening)'
            ]
        }
        
        # Common substitutions database
        self.substitutions = {
            'egg': ['1/4 cup applesauce', '1 tbsp flaxseed + 3 tbsp water', '3 tbsp aquafaba', '1/4 cup mashed banana'],
            'butter': ['coconut oil', 'olive oil', 'applesauce (for baking)', 'margarine'],
            'milk': ['almond milk', 'soy milk', 'oat milk', 'coconut milk'],
            'flour': ['almond flour', 'coconut flour', 'oat flour', 'rice flour'],
            'sugar': ['honey', 'maple syrup', 'agave nectar', 'stevia', 'monk fruit sweetener'],
            'cream': ['coconut cream', 'cashew cream', 'greek yogurt'],
            'cheese': ['nutritional yeast', 'cashew cheese', 'vegan cheese'],
            'soy sauce': ['tamari', 'coconut aminos', 'worcestershire sauce']
        }
        
        # Cooking tips database
        self.cooking_tips = {
            'chicken': 'Cook chicken to internal temperature of 165°F (75°C). Let rest 5 minutes before slicing.',
            'steak': 'For medium-rare, cook to 130-135°F (54-57°C). Let rest 5-10 minutes.',
            'pasta': 'Use 4-6 quarts water per pound of pasta. Add salt after water boils. Cook al dente.',
            'rice': 'Use 2:1 water to rice ratio. Bring to boil, then simmer covered for 18-20 minutes.',
            'vegetables': 'Don\'t overcrowd the pan when sautéing. High heat for crispy exterior.',
            'baking': 'Always preheat oven. Room temperature ingredients mix better.',
            'garlic': 'Add garlic towards end of cooking to prevent burning and bitter taste.',
            'onion': 'Caramelize onions slowly over medium-low heat for 30-40 minutes.'
        }
    
    def classify_intent(self, query: str) -> str:
        """Classify user intent using keyword matching"""
        query_lower = query.lower().strip()
        
        for intent, patterns in self.intents.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        return 'general'
    
    def extract_entities(self, query: str) -> Dict[str, any]:
        """Extract ingredients, cuisines, and dietary restrictions"""
        query_lower = query.lower()
        
        entities = {
            'ingredients': [],
            'cuisine': None,
            'dietary': []
        }
        
        # Common ingredients to look for
        common_ingredients = ['chicken', 'beef', 'pork', 'fish', 'rice', 'pasta', 
                            'tomato', 'potato', 'garlic', 'onion', 'cheese', 'egg',
                            'vegetables', 'tofu', 'beans', 'lentils']
        
        for ingredient in common_ingredients:
            if ingredient in query_lower:
                entities['ingredients'].append(ingredient)
        
        # Cuisines
        cuisines = ['italian', 'mexican', 'indian', 'chinese', 'japanese', 'thai',
                   'greek', 'french', 'american', 'mediterranean']
        
        for cuisine in cuisines:
            if cuisine in query_lower:
                entities['cuisine'] = cuisine.capitalize()
        
        # Dietary restrictions
        dietary_keywords = {
            'vegetarian': ['vegetarian', 'veggie', 'no meat'],
            'vegan': ['vegan', 'plant-based'],
            'gluten-free': ['gluten-free', 'no gluten'],
            'low-carb': ['low-carb', 'keto', 'ketogenic'],
            'healthy': ['healthy', 'nutritious', 'diet']
        }
        
        for restriction, keywords in dietary_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    entities['dietary'].append(restriction)
                    break
        
        return entities
    
    def handle_recipe_search(self, query: str, entities: Dict) -> str:
        """Handle recipe search queries"""
        ingredients = ', '.join(entities['ingredients']) if entities['ingredients'] else query
        
        try:
            # Search database
            results = self.recipe_service.search_recipes_by_name(ingredients, limit=5)
            
            if results:
                response = f"I found {len(results)} recipe"
                response += "s" if len(results) > 1 else ""
                response += f" for you! Here are the top ones:\n\n"
                
                for i, recipe in enumerate(results[:3], 1):
                    rating_pct = round((recipe['likes'] / max(recipe['total_ratings'], 1)) * 100)
                    response += f"{i}. **{recipe['title']}** ({recipe['cuisine']})\n"
                    response += f"   👍 {recipe['likes']} likes • {rating_pct}% positive\n"
                
                return response
            else:
                return f"I couldn't find recipes for '{ingredients}'. Try searching for common ingredients like 'chicken', 'pasta', or 'curry'."
        
        except Exception as e:
            return "Sorry, I had trouble searching recipes. Please try again!"
    
    def handle_substitution(self, query: str) -> str:
        """Handle ingredient substitution queries"""
        query_lower = query.lower()
        
        for ingredient, subs in self.substitutions.items():
            if ingredient in query_lower:
                response = f"Great question! You can substitute **{ingredient}** with:\n\n"
                for i, sub in enumerate(subs, 1):
                    response += f"{i}. {sub}\n"
                response += f"\nChoose based on your dietary needs and what you have available!"
                return response
        
        return "I'd love to help with substitutions! Try asking about eggs, butter, milk, flour, sugar, cream, cheese, or soy sauce."
    
    def handle_nutrition(self, query: str) -> str:
        """Handle nutrition-related queries"""
        query_lower = query.lower()
        
        tips = {
            'lose weight': 'For weight loss:\n• Focus on whole foods\n• Eat more vegetables and lean proteins\n• Control portion sizes\n• Stay hydrated\n• Choose recipes with 300-500 calories per serving',
            'gain muscle': 'For muscle gain:\n• Eat 1.6-2.2g protein per kg body weight\n• Choose recipes with chicken, fish, eggs, legumes\n• Don\'t skip carbs - they fuel workouts\n• Eat within 2 hours after exercise',
            'healthy': 'For general health:\n• Eat a variety of colorful vegetables\n• Choose whole grains over refined\n• Include healthy fats (nuts, avocado, olive oil)\n• Limit processed foods and added sugars',
            'protein': 'Good protein sources:\n• Chicken breast (31g per 100g)\n• Fish (20-25g per 100g)\n• Eggs (6g per egg)\n• Greek yogurt (10g per 100g)\n• Lentils (9g per 100g cooked)',
            'calories': 'Calorie guidelines:\n• Moderately active women: 2000 cal/day\n• Moderately active men: 2500 cal/day\n• Adjust based on your goals and activity level'
        }
        
        for keyword, tip in tips.items():
            if keyword in query_lower:
                return tip
        
        return "I can help with nutrition! Ask about weight loss, muscle gain, protein sources, or general healthy eating."
    
    def handle_cooking_tips(self, query: str) -> str:
        """Handle cooking tips queries"""
        query_lower = query.lower()
        
        for food, tip in self.cooking_tips.items():
            if food in query_lower:
                return f"**Tip for {food.title()}:**\n{tip}"
        
        # General cooking tips
        if 'temperature' in query_lower:
            return "Always preheat your oven! Bake at 350°F (175°C) is standard. Roast vegetables at 400-425°F (200-220°C) for crispy edges."
        elif 'time' in query_lower:
            return "Cooking times vary, but here are basics:\n• Chicken breast: 20-25 min at 375°F\n• Vegetables: 15-20 min at 400°F\n• Rice: 18-20 min simmering\n• Pasta: 8-12 min boiling"
        
        return "I can help with cooking tips! Ask about specific ingredients like chicken, pasta, rice, vegetables, or general techniques."
    
    def handle_greeting(self) -> str:
        """Handle greetings"""
        return "👋 Hello! I'm your NutriChef AI assistant. I can help you with:\n\n• 🔍 Finding recipes\n• 🔄 Ingredient substitutions\n• 📊 Nutrition advice\n• 👨‍🍳 Cooking tips\n\nWhat would you like to know?"
    
    def chat(self, message: str) -> Dict[str, str]:
        """Main chat interface"""
        if not message or not message.strip():
            return {'reply': "Please ask me something! I'm here to help with recipes, cooking, and nutrition."}
        
        # Classify intent
        intent = self.classify_intent(message)
        
        # Extract entities
        entities = self.extract_entities(message)
        
        # Generate response based on intent
        if intent == 'greeting':
            reply = self.handle_greeting()
        elif intent == 'recipe_search':
            reply = self.handle_recipe_search(message, entities)
        elif intent == 'ingredient_substitute':
            reply = self.handle_substitution(message)
        elif intent == 'nutrition':
            reply = self.handle_nutrition(message)
        elif intent == 'cooking_tips':
            reply = self.handle_cooking_tips(message)
        else:
            reply = "I can help you with:\n• Finding recipes\n• Ingredient substitutions\n• Nutrition questions\n• Cooking tips\n\nWhat would you like to know?"
        
        return {
            'reply': reply,
            'intent': intent,
            'entities': entities
        }
