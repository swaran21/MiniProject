"""
IMPROVED Recipe Extraction with COMPREHENSIVE Noun Validation
& DATA QUALITY FIXES (Fractions, Accents, Artifacts)
& CUISINE ATTRIBUTE (Heuristic Detection)
& PEARL POLISH (Adverbs, Connectors, Title Leakage)

1. Extracts ALL nouns from title for consistency checks
2. Preserves fractions like 1/2 (doesn't strip to /2)
3. Preserves accents (jalapeño, soufflé)
4. Removes data artifacts
5. Improved INPUT phrasing + CUISINE TAGS + AGGRESSIVE NOISE FILTERING
"""

import json
import re
import random
from pathlib import Path

# Configuration
TARGET_RECIPES = 15000
MIN_INGREDIENTS = 3
MIN_INSTRUCTIONS_LENGTH = 50
OUTPUT_FILE = "data/recipe_training_improved.txt"

def clean_text(text):
    """Clean text by removing special characters and normalizing whitespace"""
    if not text:
        return ""
    text = str(text)
    
    # FIX: Remove source tags or weird db artifacts (Angle brackets AND Square brackets)
    text = re.sub(r'<[^>]+>', '', text)  # Remove <source>
    text = re.sub(r'\[source:[^\]]+\]', '', text) # Remove [source:123]
    text = re.sub(r'\[[^\]]*\]', '', text) # Remove ANY [content] (often artifacts)
    
    text = text.replace('``', '"').replace("''", '"')
    
    # Normalize whitespace
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\r', '', text)
    text = re.sub(r'\t', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # FIX: Preserving Accents (Removed ascii encoding line)
    
    text = text.strip()
    return text

def extract_nouns_from_title(title):
    """
    Extract meaningful nouns from title by removing common words.
    """
    # Common stop words to ignore
    stop_words = {
        'a', 'an', 'the', 'with', 'and', 'or', 'for', 'to', 'in', 'on', 'of',
        'at', 'by', 'from', 'about', 'as', 'into', 'like', 'through', 'over',
        'before', 'after', 'above', 'below', 'between', 'under', 'during', 'without',
        'your', 'my', 'our', 'his', 'her', 'its', 'their',
        'this', 'that', 'these', 'those',
        'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
        'will', 'would', 'could', 'should', 'may', 'might', 'must',
        'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'plus', 'approx', 'approximately', 'near',
        'can', 'cans', 'jar', 'jars',
        # Pearl Polish (Title Leakage):
        'vampire', 'love', 'polka', 'fired', 'dream', 'lighter', 'slushie', 
        'best', 'easy', 'quick', 'simple', 'perfect', 'ultimate'
    }
    
    # Also ignore cooking method words (these are processes, not ingredients)
    cooking_methods = {
        'baked', 'baking', 'grilled', 'grilling', 'fried', 'frying', 'roasted', 'roasting',
        'sauteed', 'sauteing', 'braised', 'braising', 'seared', 'searing',
        'poached', 'poaching', 'steamed', 'steaming', 'boiled', 'boiling',
        'broiled', 'broiling', 'marinated', 'marinating', 'glazed', 'glazing',
        'stuffed', 'stuffing', 'breaded', 'breading', 'smoked', 'smoking',
        'pickled', 'pickling', 'candied', 'caramelized', 'toasted'
    }
    
    # Descriptive words that aren't ingredients
    descriptors = {
        'easy', 'quick', 'simple', 'best', 'perfect', 'classic', 'traditional',
        'homemade', 'fresh', 'healthy', 'light', 'crispy', 'creamy', 'spicy',
        'sweet', 'savory', 'tangy', 'rich', 'delicious', 'tasty', 'favorite',
        'ultimate', 'authentic', 'original', 'special', 'famous', 'secret',
        'mom', 'grandma', 'old', 'new', 'modern', 'style'
    }
    
    # Clean and tokenize title
    title_lower = title.lower()
    # Remove possessives
    title_lower = re.sub(r"'s\b", '', title_lower)
    # Split into words, remove punctuation
    words = re.findall(r'\b[a-z]+\b', title_lower)
    
    # Extract meaningful nouns (content words)
    nouns = []
    for word in words:
        if word in stop_words or word in cooking_methods or word in descriptors:
            continue
        if len(word) < 3:
            continue
        nouns.append(word)
    
    return nouns

def validate_comprehensive_consistency(recipe):
    """
    IMPROVED: Extract ALL nouns from title and verify they appear in 
    ingredients AND instructions.
    """
    title = recipe.get('title', '')
    ingredients = recipe.get('ingredients', [])
    instructions = recipe.get('instructions', '')
    
    if not title or not ingredients or not instructions:
        return False, "Missing required fields"
    
    # Extract ALL nouns from the title
    title_nouns = extract_nouns_from_title(title)
    
    if not title_nouns:
        return True, "OK - no specific nouns to validate"
    
    # Prepare text for checking
    ingredients_text = ' '.join([str(ing).lower() for ing in ingredients])
    instructions_lower = instructions.lower()
    
    # Check each noun from the title
    missing_from_ingredients = []
    missing_from_instructions = []
    
    for noun in title_nouns:
        # Check if noun appears in ingredients
        if noun not in ingredients_text:
            missing_from_ingredients.append(noun)
        
        # Check if noun appears in instructions
        if noun not in instructions_lower:
            missing_from_instructions.append(noun)
    
    # If significant nouns are missing, reject
    if len(missing_from_ingredients) > len(title_nouns) * 0.5:
        return False, f"Title nouns missing from ingredients: {', '.join(missing_from_ingredients[:3])}"
    
    if len(missing_from_instructions) > len(title_nouns) * 0.5:
        return False, f"Title nouns missing from instructions: {', '.join(missing_from_instructions[:3])}"
    
    # Special check for protein conflicts
    proteins = ['chicken', 'turkey', 'beef', 'pork', 'lamb', 'duck', 'salmon', 'shrimp', 'fish']
    title_proteins = [p for p in proteins if p in title.lower()]
    
    if title_proteins:
        main_protein = title_proteins[0]
        other_proteins = [p for p in proteins if p != main_protein and p in instructions_lower]
        if other_proteins and main_protein not in instructions_lower:
            return False, f"Title has '{main_protein}' but instructions primarily use '{other_proteins[0]}'"
    
    return True, "OK"

def is_valid_recipe(recipe):
    """Check if recipe meets quality standards AND comprehensive consistency"""
    if not recipe.get('title') or len(recipe['title'].strip()) < 5:
        return False, "Invalid title"
    
    ingredients = recipe.get('ingredients', [])
    if not ingredients or len(ingredients) < MIN_INGREDIENTS:
        return False, "Too few ingredients"
    
    valid_ingredients = [ing for ing in ingredients if ing and len(str(ing).strip()) > 2]
    if len(valid_ingredients) < MIN_INGREDIENTS:
        return False, "Too few valid ingredients"
    
    instructions = recipe.get('instructions', '')
    if not instructions or len(str(instructions).strip()) < MIN_INSTRUCTIONS_LENGTH:
        return False, "Instructions too short"
    
    # COMPREHENSIVE CONSISTENCY VALIDATION
    is_consistent, reason = validate_comprehensive_consistency(recipe)
    if not is_consistent:
        return False, f"Consistency: {reason}"
    
    return True, "Valid"

def format_ingredient(ingredient):
    """Format a single ingredient cleanly"""
    ingredient = clean_text(ingredient)
    if not ingredient:
        return ""
    
    # Remove bullets (•, *, -)
    ingredient = re.sub(r'^\s*[\•\*\-]+\s+', '', ingredient)
    
    # Remove numbered identifiers
    ingredient = re.sub(r'^\s*\d+[\.\)]\s+', '', ingredient)
    
    ingredient = ingredient.rstrip('.,;')
    return ingredient.strip()

def format_recipe_for_training(recipe):
    """Format a recipe into training format (WITH CUISINE ATTRIBUTE)"""
    title = clean_text(recipe['title'])
    title = title[:100]
    
    ingredients = recipe.get('ingredients', [])
    cleaned_ingredients = []
    
    for ing in ingredients:
        cleaned = format_ingredient(ing)
        if cleaned and len(cleaned) > 2:
            cleaned = cleaned[:150]
            cleaned_ingredients.append(cleaned)
    
    cleaned_ingredients = cleaned_ingredients[:15]
    
    if len(cleaned_ingredients) < MIN_INGREDIENTS:
        return None
    
    instructions = clean_text(recipe.get('instructions', ''))
    if instructions.lower().startswith(title.lower()):
        instructions = instructions[len(title):].strip()
    instructions = instructions[:600]
    
    # === NEW FEATURE: Heuristic Cuisine Detection ===
    def detect_cuisine(title_words, ingredients_text):
        cuisine_map = {
            'italian': ['pasta', 'spaghetti', 'risotto', 'lasagna', 'tiramisu', 'pesto', 'parmesan', 'mozzarella', 'basil', 'marinara', 'oregano', 'ricotta', 'provolone', 'gnocchi', 'ravioli', 'fettuccine', 'linguine', 'penne'],
            'mexican': ['taco', 'burrito', 'enchilada', 'quesadilla', 'fajita', 'salsa', 'guacamole', 'tortilla', 'jalapeño', 'chipotle', 'cilantro', 'lime', 'cumin', 'chili powder', 'chorizo', 'tequila', 'tomatillo'],
            'asian': ['soy sauce', 'ginger', 'sesame', 'tofu', 'teriyaki', 'miso', 'bok choy', 'sushi', 'stir-fry', 'dumpling', 'spring roll', 'wonton', 'ramen', 'udon', 'curry paste', 'coconut milk', 'fish sauce', 'lemongrass', 'wasabi'],
            'indian': ['curry', 'masala', 'naan', 'tikka', 'tandoori', 'dal', 'paneer', 'chutney', 'turmeric', 'cardamom', 'cumin', 'coriander', 'garam masala', 'lentil', 'samosa', 'biryani'],
            'american': ['burger', 'sandwich', 'bbq', 'barbecue', 'casserole', 'meatloaf', 'macaroni', 'cheese', 'ranch', 'buffalo', 'thanksgiving', 'pie', 'cobbler', 'brownie', 'cookie', 'hot dog', 'steak'],
            'mediterranean': ['hummus', 'feta', 'olive', 'tahini', 'falafel', 'couscous', 'phyllo', 'gyro', 'kabob', 'tzatziki', 'halloumi'],
            'french': ['baguette', 'croissant', 'quiche', 'souffle', 'crepe', 'dijon', 'provence', 'tarragon', 'brie', 'camembert'],
        }
        
        for cuisine, keywords in cuisine_map.items():
            for kw in keywords:
                if kw in title_words: return cuisine
                
        text = ingredients_text.lower()
        scores = {}
        for cuisine, keywords in cuisine_map.items():
            count = 0
            for kw in keywords:
                if kw in text: count += 1
            if count > 0: scores[cuisine] = count
                
        if scores:
            best_match = max(scores, key=scores.get)
            if scores[best_match] >= 2: return best_match
        return ""

    title_nouns = extract_nouns_from_title(recipe['title'])
    ing_text_blob = ' '.join(cleaned_ingredients).lower()
    
    detected_cuisine = detect_cuisine(title_nouns, ing_text_blob)
    cuisine_output = detected_cuisine.capitalize() if detected_cuisine else ""
    
    simplified_input = []
    
    # Add Cuisine to INPUT
    if detected_cuisine:
         simplified_input.append(detected_cuisine.capitalize())
    
    # Add other Title Keywords
    unique_title_keywords = []
    for word in title_nouns:
        if word != detected_cuisine and word not in ing_text_blob and len(word) > 3:
             unique_title_keywords.append(word)
             
    if unique_title_keywords:
        simplified_input.extend(unique_title_keywords[:2]) 

    # === Ingredient Extraction with AGGRESSIVE FILTERING ===
    skip_words = {'cup', 'cups', 'tablespoon', 'tablespoons', 'teaspoon', 'teaspoons',
                 'tbsp', 'tsp', 'pound', 'pounds', 'lb', 'lbs', 'ounce', 'ounces', 
                 'oz','gram', 'grams', 'kg', 'ml', 'liter', 'pinch', 'dash', 'stick', 'sticks',
                 'large', 'small', 'medium', 'fresh', 'dried', 'chopped', 'diced',
                 'minced', 'sliced', 'whole', 'halved', 'quartered', 'crushed', 'grated',
                 'peeled', 'seeded', 'beaten', 'melted', 'room', 'temperature', 'warm', 'cold',
                 'package', 'can', 'box', 'bag', 'bottle',
                 'finely', 'heaping', 'recipe', 'to', 'or', 'chilled', 'club', 'plus', 
                 'about', 'usually', 'approximately', 'roughly', 'nearly', 'almost', 'melted', 
                 'frozen', 'thawed', 'raw', 'cooked', 'baked', 'prepared', 'dry', 'instant',
                 'and', 'of', 'sheets', 'slices', 'strips', 'pieces', 'thin', 'thick', 'lean', 'extra',
                 # Punch List Additions (Containers & Units):
                 'cans', 'jar', 'jars', 'pint', 'pints', 'quart', 'quarts', 'gallon', 'gallons',
                 'inch', 'inches', 'clove', 'cloves', 'head', 'heads', 'stalk', 'stalks', 
                 'rib', 'ribs', 'ear', 'ears', 'bunch', 'bunches', 'sprig', 'sprigs', 'one',
                 # Punch List Additions (Adjectives & Descriptors):
                 'drained', 'canned', 'boneless', 'skinless', 'deveined', 'ground', 'cracked',
                 'softened', 'packed', 'pitted', 'shaved', 'crusted', 'ripe', 'freshly',
                 'squeezed', 'sweetened', 'toasted', 'rubbed', 'tasty', 'eating', 'bone', 'in', 'washed',
                 'cut', 'shredded', 'beaten',
                 # Punch List Additions (Non-Ingredient/Glitches):
                 'store', 'bought', 'brand', 'nonstick', 'spray', 'cooking', 'disposable', 'thermometer',
                 'percent', 'such', 'white', 'red', 'green', 'yellow', 'blue', 'black', 'brown',
                 # Pearl Polish (Adverbs, Connectors, Cut-offs):
                 'thickly', 'thinly', 'coarsely', 'generous', 'firm', 'splash', 'but',
                 'on', 'the', 'for', 'as', 'with', 'part', 'parts'} 
    
    for ing in cleaned_ingredients[:5]: # Take first 5 ingredients
        base_ing = ing.split(',')[0].split(';')[0].strip()
        base_ing = base_ing.split('(')[0].strip()
        base_ing = base_ing.replace('-', ' ')
        
        # FIX: Handle slashes and asterisks
        base_ing = base_ing.replace('/', ' ').replace('*', '')
        
        parts = base_ing.split()
        ingredient_keywords = []
        
        for part in parts:
            if re.match(r'^[\d\/\-\.]+$', part):
                continue
            
            # Skip digits (glitch protection)
            if re.search(r'\d', part):
                continue
            
            if part.endswith(':'):
                continue
                
            clean_part = part.lower().strip('.,*')
            
            if clean_part in skip_words:
                continue
            
            if '_' in part or len(part) < 2:
                continue
            
            if clean_part in {'to', 'plus', 'in', 'of', 'and'}:
                 continue
                 
            ingredient_keywords.append(part.rstrip(','))
        
        if ingredient_keywords:
            simplified_input.append(' '.join(ingredient_keywords[:3]))
    
    seen = set()
    final_input = []
    for item in simplified_input:
        if item not in seen:
            final_input.append(item)
            seen.add(item)
            
    input_text = ', '.join(final_input)
    ingredients_text = '; '.join(cleaned_ingredients)
    
    training_line = f"INPUT: {input_text}\nOUTPUT: TITLE: {title} | CUISINE: {cuisine_output} | INGREDIENTS: {ingredients_text} | INSTRUCTIONS: {instructions} <END>"
    
    return training_line

def load_recipes(file_path):
    """Load recipes from JSON file"""
    print(f"Loading recipes from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        recipes = list(data.values())
    else:
        recipes = data
    print(f"  Found {len(recipes)} total recipes")
    return recipes

def main():
    """Main extraction with COMPREHENSIVE validation & QUALITY FIXES"""
    print("="*80)
    print("IMPROVED EXTRACTION: A+ DIAMOND GRADE")
    print("="*80)
    
    sources = [
        ('data/raw/recipes_raw/recipes_raw_nosource_fn.json', 'Food Network'),
        ('data/raw/recipes_raw/recipes_raw_nosource_epi.json', 'Epicurious')
    ]
    
    all_valid_recipes = []
    
    for file_path, source_name in sources:
        if not Path(file_path).exists():
            print(f"⚠️  {file_path} not found, skipping...")
            continue
        
        recipes = load_recipes(file_path)
        for recipe in recipes:
            is_valid, reason = is_valid_recipe(recipe)
            if is_valid:
                recipe['_source'] = source_name
                all_valid_recipes.append(recipe)
        
        print(f"  ✅ {source_name}: Validated")
    
    if len(all_valid_recipes) > TARGET_RECIPES:
        sampled = random.sample(all_valid_recipes, TARGET_RECIPES)
    else:
        sampled = all_valid_recipes
    
    random.shuffle(sampled)
    
    print(f"\n📝 Writing to {OUTPUT_FILE}...")
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for recipe in sampled:
            training_line = format_recipe_for_training(recipe)
            if training_line:
                f.write(training_line + '\n')
    
    print(f"\n✅ SUCCESS! File: {output_path.absolute()}")
    print("✅ COMPREHENSIVE extraction complete with PEARL POLISH!")

if __name__ == "__main__":
    random.seed(42)
    main()