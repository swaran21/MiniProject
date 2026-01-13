"""
Medical Nutrition Rules Database
Evidence-based nutrition guidelines for common medical conditions
Sources: WHO, ADA, AHA, NIH medical guidelines
"""

MEDICAL_NUTRITION_RULES = {
    'diabetes_type2': {
        'display_name': 'Type 2 Diabetes',
        'type': 'chronic',
        'duration_days': 90,  # 3-month renewable plans
        
        'foods_to_avoid': [
            # Sugars (all types)
            'sugar', 'white sugar', 'brown sugar', 'cane sugar', 'table sugar',
            'honey', 'maple syrup', 'agave', 'corn syrup',
            
            # High-GI Grains & Starches
            'white rice', 'jasmine rice', 'sticky rice', 'instant rice',
            'rice noodles', 'rice vermicelli', 'rice paper',  # Added rice noodles!
            'white bread', 'refined flour', 'maida', 'all-purpose flour',
            'pasta', 'white pasta', 'noodles',
            'potatoes', 'mashed potatoes', 'french fries',
            
            # Processed/Packaged Foods
            'sweet beverages', 'soda', 'fruit juice', 'sports drinks',
            'candy', 'pastries', 'cakes', 'cookies', 'donuts',
            'sweetened yogurt', 'sweetened cereals', 'granola bars',
            'processed foods', 'fast food'
        ],
        
        'foods_to_eat': [
            # Low-GI Grains (SAFE alternatives to white rice!)
            'brown rice', 'wild rice', 'black rice', 'red rice',
            'whole grains', 'quinoa', 'oats', 'barley', 'buckwheat',
            
            # Vegetables (High Fiber)
            'vegetables', 'leafy greens', 'spinach', 'kale', 'broccoli',
            'cauliflower', 'brussels sprouts', 'bitter gourd', 'bok choy',
            
            # Lean Protein
            'lean protein', 'chicken breast', 'fish', 'salmon', 'tuna',
            'eggs', 'egg whites', 'tofu', 'tempeh',
            
            # Legumes (Low GI, High Protein)
            'legumes', 'lentils', 'chickpeas', 'beans', 'black beans',
            
            # Healthy Fats & Nuts
            'nuts', 'almonds', 'walnuts', 'chia seeds', 'flax seeds',
            
            # Low-GI Fruits
            'berries', 'strawberries', 'blueberries', 'raspberries',
            
            # Beneficial Spices
            'cinnamon', 'turmeric', 'fenugreek', 'ginger'
        ],
        
        'macro_targets': {
            'carbs_percent': 40,  # Low-carb approach
            'protein_percent': 30,
            'fat_percent': 30,
            'fiber_min_grams': 30
        },
        
        'meal_timing': 'Small frequent meals every 3-4 hours',
        'portion_control': 'Use plate method: 1/2 vegetables, 1/4 protein, 1/4 whole grains',
        
        'special_notes': [
            'Monitor blood sugar before and after meals',
            'Combine carbs with protein/fiber to slow absorption',
            'Choose low glycemic index (GI) foods',
            'Stay hydrated - drink 8-10 glasses of water',
            'Avoid skipping meals'
        ],
        
        'severity_adjustments': {
            'mild': 'Focus on weight loss and exercise',
            'moderate': 'Strict carb control, medication compliance',
            'severe': 'Very low carb, frequent monitoring, insulin timing'
        }
    },
    
    'hypertension': {
        'display_name': 'High Blood Pressure (Hypertension)',
        'type': 'chronic',
        'duration_days': 90,
        
        'foods_to_avoid': [
            'salt', 'sodium', 'table salt', 'salty snacks', 'chips',
            'processed meats', 'bacon', 'sausage', 'ham', 'salami',
            'canned foods', 'pickles', 'olives', 'soy sauce',
            'packaged soups', 'frozen meals', 'cheese', 'pizza',
            'fast food', 'restaurant food'
        ],
        
        'foods_to_eat': [
            'potassium-rich foods', 'bananas', 'oranges', 'spinach',
            'sweet potatoes', 'avocados', 'tomatoes', 'broccoli',
            'fatty fish', 'salmon', 'mackerel', 'tuna', 'omega-3',
            'oats', 'whole grains', 'berries', 'garlic', 'beets',
            'dark chocolate (85%+)', 'nuts', 'seeds', 'low-fat dairy',
            'beans', 'lentils', 'olive oil'
        ],
        
        'sodium_limit_mg': 1500,  # AHA recommendation
        'potassium_target_mg': 4700,
        
        'meal_approach': 'DASH Diet (Dietary Approaches to Stop Hypertension)',
        
        'special_notes': [
            'Read food labels carefully for hidden sodium',
            'Use herbs and spices instead of salt',
            'Avoid adding salt while cooking',
            'Limit alcohol to 1 drink per day (women) or 2 (men)',
            'Monitor blood pressure twice daily'
        ]
    },
    
    'high_cholesterol': {
        'display_name': 'High Cholesterol (Hypercholesterolemia)',
        'type': 'chronic',
        'duration_days': 90,
        
        'foods_to_avoid': [
            'trans fats', 'hydrogenated oils', 'margarine', 'fried foods',
            'red meat', 'beef', 'pork', 'lamb', 'processed meats',
            'full-fat dairy', 'butter', 'cream', 'cheese', 'ice cream',
            'egg yolks (limit)', 'fast food', 'baked goods', 'pastries',
            'coconut oil', 'palm oil'
        ],
        
        'foods_to_eat': [
            'oats', 'barley', 'whole grains', 'soluble fiber',
            'nuts', 'almonds', 'walnuts', 'pistachios',
            'fatty fish', 'salmon', 'mackerel', 'sardines',
            'olive oil', 'avocado', 'flaxseeds', 'chia seeds',
            'fruits', 'apples', 'grapes', 'strawberries', 'citrus',
            'vegetables', 'eggplant', 'okra', 'beans', 'lentils',
            'soy products', 'tofu', 'edamame', 'green tea'
        ],
        
        'macro_targets': {
            'saturated_fat_max_percent': 7,
            'trans_fat_max_grams': 0,
            'fiber_min_grams': 25,
            'omega3_target_mg': 1000
        },
        
        'special_notes': [
            'Choose lean cuts of poultry and fish',
            'Remove skin from chicken',
            'Use plant-based proteins',
            'Eat fatty fish 2-3 times per week',
            'Limit cholesterol intake to 200mg/day'
        ]
    },
    
    'kidney_disease': {
        'display_name': 'Chronic Kidney Disease (CKD)',
        'type': 'chronic',
        'duration_days': 90,
        
        'foods_to_avoid': [
            # High potassium
            'bananas', 'oranges', 'potatoes', 'tomatoes', 'spinach',
            'avocados', 'melons', 'dried fruits', 'coconut water',
            # High phosphorus
            'dairy products', 'milk', 'cheese', 'yogurt',
            'nuts', 'seeds', 'beans', 'lentils', 'whole grains',
            'dark sodas', 'processed meats',
            # High sodium
            'salt', 'canned foods', 'pickles', 'salty snacks'
        ],
        
        'foods_to_eat': [
            'low-protein options', 'white rice', 'pasta', 'bread',
            'cauliflower', 'cabbage', 'bell peppers', 'onions',
            'cucumber', 'green beans', 'zucchini',
            'apples', 'grapes', 'blueberries', 'strawberries',
            'cranberries', 'pineapple', 'watermelon (limited)',
            'egg whites', 'skinless chicken (limited)', 'fish (limited)'
        ],
        
        'restrictions': {
            'protein_max_grams': 60,  # Stage-dependent
            'potassium_max_mg': 2000,
            'phosphorus_max_mg': 1000,
            'sodium_max_mg': 2000,
            'fluid_max_liters': 1.5
        },
        
        'special_notes': [
            'Work closely with renal dietitian',
            'Restrictions vary by CKD stage (1-5)',
            'Monitor fluid intake carefully',
            'Avoid NSAIDs (ibuprofen, aspirin)',
            'Get regular kidney function tests'
        ]
    },
    
    'pcos': {
        'display_name': 'Polycystic Ovary Syndrome (PCOS)',
        'type': 'chronic',
        'duration_days': 90,
        
        'foods_to_avoid': [
            'refined carbs', 'white rice', 'white bread', 'pasta',
            'sugar', 'sweetened beverages', 'candy', 'pastries',
            'processed foods', 'fried foods', 'red meat',
            'dairy (for some)', 'inflammatory foods'
        ],
        
        'foods_to_eat': [
            'low GI foods', 'whole grains', 'oats', 'quinoa',
            'lean protein', 'chicken', 'fish', 'tofu', 'eggs',
            'anti-inflammatory foods', 'turmeric', 'ginger',
            'omega-3 fish', 'salmon', 'sardines',
            'leafy greens', 'berries', 'nuts', 'seeds',
            'cinnamon', 'spearmint tea', 'avocado'
        ],
        
        'macro_targets': {
            'carbs_percent': 35,  # Lower carb
            'protein_percent': 35,
            'fat_percent': 30
        },
        
        'special_notes': [
            'Focus on weight management',
            'Eat small frequent meals',
            'Combine carbs with protein/fat',
            'Consider inositol supplementation',
            'Regular exercise is crucial'
        ]
    },
    
    'thyroid_hypothyroid': {
        'display_name': 'Hypothyroidism (Underactive Thyroid)',
        'type': 'chronic',
        'duration_days': 90,
        
        'foods_to_avoid': [
            'raw cruciferous vegetables (in excess)', 'raw broccoli',
            'raw cauliflower', 'raw cabbage', 'raw kale',
            'soy products (large amounts)', 'highly processed foods',
            'sugary foods', 'refined grains'
        ],
        
        'foods_to_eat': [
            'iodine-rich foods', 'iodized salt', 'seaweed', 'fish',
            'selenium-rich foods', 'brazil nuts', 'tuna', 'eggs',
            'zinc-rich foods', 'shellfish', 'beef', 'chicken',
            'cooked vegetables', 'fruits', 'whole grains',
            'lean protein', 'gluten-free grains (if sensitive)'
        ],
        
        'special_notes': [
            'Take thyroid medication on empty stomach',
            'Wait 30-60 min before eating after medication',
            'Avoid calcium/iron supplements within 4 hours of medication',
            'Cook cruciferous vegetables before eating',
            'Get regular TSH blood tests'
        ]
    },
    
    'ibs': {
        'display_name': 'Irritable Bowel Syndrome (IBS)',
        'type': 'chronic',
        'duration_days': 90,
        
        'foods_to_avoid': [
            # High FODMAP foods
            'dairy', 'milk', 'ice cream', 'soft cheeses',
            'wheat', 'rye', 'onions', 'garlic',
            'apples', 'pears', 'watermelon', 'mangoes',
            'beans', 'lentils', 'chickpeas',
            'artificial sweeteners', 'sorbitol', 'xylitol',
            'fried foods', 'spicy foods', 'caffeine', 'alcohol'
        ],
        
        'foods_to_eat': [
            'low FODMAP foods', 'rice', 'quinoa', 'oats',
            'lactose-free dairy', 'hard cheeses', 'almond milk',
            'bananas', 'blueberries', 'strawberries', 'oranges',
            'carrots', 'cucumbers', 'potatoes', 'zucchini',
            'lean protein', 'chicken', 'fish', 'eggs', 'tofu',
            'ginger tea', 'peppermint tea', 'probiotics'
        ],
        
        'special_notes': [
            'Keep a food diary',
            'Follow low FODMAP diet (consult dietitian)',
            'Eat slowly and chew thoroughly',
            'Avoid large meals',
            'Manage stress levels',
            'Stay hydrated'
        ]
    },
    
    'anemia': {
        'display_name': 'Iron-Deficiency Anemia',
        'type': 'acute',  # Usually treatable within 3-6 months
        'duration_days': 90,
        
        'foods_to_avoid': [
            'tea and coffee with meals (block iron absorption)',
            'calcium-rich foods with iron-rich meals',
            'excess bran and whole grains with iron sources'
        ],
        
        'foods_to_eat': [
            'iron-rich foods', 'red meat', 'liver', 'chicken', 'fish',
            'spinach', 'kale', 'beans', 'lentils', 'tofu',
            'fortified cereals', 'pumpkin seeds', 'quinoa',
            'vitamin C foods', 'oranges', 'tomatoes', 'bell peppers',
            'strawberries', 'broccoli', 'brussels sprouts',
            'vitamin B12 foods', 'eggs', 'dairy', 'fortified foods',
            'folate foods', 'leafy greens', 'legumes', 'avocados'
        ],
        
        'special_notes': [
            'Combine iron-rich foods with vitamin C',
            'Avoid tea/coffee 1 hour before and after iron-rich meals',
            'Cook in cast iron cookware',
            'Take iron supplements if prescribed',
            'Get regular blood tests to monitor'
        ]
    },
    
    'gastritis': {
        'display_name': 'Gastritis / GERD (Acid Reflux)',
        'type': 'acute',
        'duration_days': 30,
        
        'foods_to_avoid': [
            'spicy foods', 'chili', 'black pepper', 'hot sauce',
            'acidic foods', 'citrus fruits', 'tomatoes', 'vinegar',
            'fried foods', 'fatty foods', 'chocolate',
            'coffee', 'alcohol', 'carbonated drinks',
            'mint', 'onions', 'garlic'
        ],
        
        'foods_to_eat': [
            'bland foods', 'oatmeal', 'rice', 'bananas',
            'lean protein', 'chicken', 'fish', 'tofu',
            'vegetables', 'carrots', 'green beans', 'peas',
            'whole grains', 'brown rice', 'whole wheat bread',
            'low-fat dairy', 'ginger', 'fennel', 'aloe vera juice'
        ],
        
        'meal_timing': 'Eat small meals every 3 hours',
        
        'special_notes': [
            'Don\'t lie down within 3 hours of eating',
            'Elevate head while sleeping',
            'Eat slowly and chew thoroughly',
            'Avoid eating late at night',
            'Stay upright after meals'
        ]
    },
    
    'post_surgery': {
        'display_name': 'Post-Surgical Recovery',
        'type': 'acute',
        'duration_days': 30,
        
        'foods_to_avoid': [
            'spicy foods', 'alcohol', 'caffeine',
            'hard-to-digest foods', 'raw vegetables',
            'fried foods', 'processed foods'
        ],
        
        'foods_to_eat': [
            'protein-rich foods', 'chicken', 'fish', 'eggs',
            'vitamin C foods', 'oranges', 'strawberries', 'broccoli',
            'zinc-rich foods', 'pumpkin seeds', 'chickpeas',
            'easy-to-digest foods', 'soups', 'broths', 'smoothies',
            'soft foods', 'mashed potatoes', 'yogurt', 'oatmeal'
        ],
        
        'progression': {
            'days_1_7': 'Clear liquids → Full liquids → Soft diet',
            'days_8_14': 'Soft foods → Semi-solid foods',
            'days_15_plus': 'Regular diet with restrictions'
        },
        
        'special_notes': [
            'Stay well hydrated',
            'Eat small frequent meals',
            'Focus on protein for healing',
            'Take prescribed supplements',
            'Follow surgeon\'s specific diet orders'
        ]
    },
    
    'celiac': {
        'display_name': 'Celiac Disease / Gluten Intolerance',
        'type': 'chronic',
        'duration_days': 365,  # Lifetime dietary change
        
        'foods_to_avoid': [
            # Gluten-containing grains (PRIMARY CONCERN!)
            'wheat', 'wheat flour', 'whole wheat', 'wheat bread',
            'white bread', 'whole wheat bread', 'sourdough bread',
            'barley', 'rye', 'malt', 'brewer\'s yeast',
            
            # Products made with gluten
            'pasta', 'noodles', 'couscous', 'bulgur',
            'bread', 'crackers', 'biscuits', 'cookies',
            'cakes', 'pastries', 'pie crust',
            'pizza', 'pizza dough',
            'cereal (most)', 'granola',
            
            # Hidden gluten sources
            'soy sauce', 'teriyaki sauce', 'some sauces',
            'beer', 'malt vinegar',
            'processed meats (check labels)'
        ],
        
        'foods_to_eat': [
            # Gluten-free grains (SAFE!)
            'rice', 'brown rice', 'white rice', 'wild rice',  # All rice is safe!
            'quinoa', 'buckwheat', 'millet', 'amaranth',
            'corn', 'cornmeal', 'polenta',
            'oats (certified gluten-free)',
            
            # Gluten-free products
            'gluten-free bread', 'gluten-free pasta',
            'rice noodles', 'rice cakes',
            
            # Naturally gluten-free
            'fruits', 'vegetables', 'potatoes',
            'lean protein', 'meat', 'poultry', 'fish', 'eggs',
            'beans', 'legumes', 'nuts', 'seeds',
            'dairy products (plain)', 'milk', 'cheese', 'yogurt'
        ],
        
        'special_notes': [
            'ZERO tolerance for gluten - even traces can cause damage',
            'Always read food labels carefully',
            'Avoid cross-contamination in kitchen',
            'Ask about ingredients when eating out',
            'Look for certified gluten-free labels',
            'Rice, quinoa, and potatoes are your staples'
        ]
    }
}

# Medication-Food Interactions
MEDICATION_INTERACTIONS = {
    'metformin': {
        'condition': 'diabetes',
        'avoid_with': ['alcohol'],
        'take_with': 'meals',
        'timing': 'Twice daily with breakfast and dinner',
        'food_notes': 'May cause vitamin B12 deficiency - eat B12-rich foods',
        'alert': 'Take with food to reduce stomach upset'
    },
    
    'insulin': {
        'condition': 'diabetes',
        'timing': 'Before meals (varies by type)',
        'food_notes': 'Eat within 15-30 minutes of injection',
        'alert': 'Always carry fast-acting carbs for hypoglycemia'
    },
    
    'amlodipine': {
        'condition': 'hypertension',
        'avoid_with': ['grapefruit', 'grapefruit juice'],
        'timing': 'Once daily, same time each day',
        'alert': 'Grapefruit can increase drug levels dangerously'
    },
    
    'losartan': {
        'condition': 'hypertension',
        'avoid_with': ['potassium supplements', 'salt substitutes'],
        'alert': 'Can increase potassium levels'
    },
    
    'atorvastatin': {
        'condition': 'high_cholesterol',
        'avoid_with': ['grapefruit', 'alcohol'],
        'timing': 'Evening (cholesterol is produced at night)',
        'alert': 'Grapefruit inhibits metabolism, increasing side effects'
    },
    
    'levothyroxine': {
        'condition': 'thyroid',
        'take_with': 'Empty stomach, 30-60 min before breakfast',
        'avoid_with': ['calcium', 'iron', 'soy', 'coffee (within 1 hour)'],
        'timing': 'Same time every day (preferably morning)',
        'alert': 'Many foods and supplements interfere with absorption'
    },
    
    'warfarin': {
        'condition': 'blood_clots',
        'avoid_with': ['vitamin K-rich foods (in varying amounts)', 'alcohol', 'cranberry juice'],
        'alert': 'Maintain consistent vitamin K intake - don\'t suddenly increase leafy greens',
        'food_notes': 'Major changes in diet affect blood thinning'
    },
    
    'pantoprazole': {
        'condition': 'gastritis',
        'take_with': 'Empty stomach, 30 minutes before first meal',
        'timing': 'Morning, before breakfast',
        'alert': 'May reduce absorption of vitamin B12, calcium, magnesium over time'
    }
}

# Condition Detection Keywords
CONDITION_KEYWORDS = {
    'diabetes_type2': [
        'diabetes', 'diabetic', 'type 2 dm', 't2dm', 'type ii diabetes',
        'high blood sugar', 'hyperglycemia', 'hba1c', 'glycated hemoglobin',
        'metformin', 'insulin', 'glucometer', 'blood glucose',
        'fasting sugar', 'pp sugar', 'post prandial'
    ],
    
    'hypertension': [
        'hypertension', 'high bp', 'high blood pressure', 'hbp', 'bp',
        'amlodipine', 'losartan', 'telmisartan', 'enalapril', 'ramipril',
        'bp >140', 'bp>140', 'systolic', 'diastolic'
    ],
    
    'high_cholesterol': [
        'high cholesterol', 'hypercholesterolemia', 'ldl', 'hdl',
        'triglycerides', 'lipid profile', 'dyslipidemia',
        'statin', 'atorvastatin', 'rosuvastatin', 'simvastatin',
        'cholesterol >200', 'elevated cholesterol'
    ],
    
    'kidney_disease': [
        'kidney disease', 'renal', 'ckd', 'chronic kidney disease',
        'creatinine', 'elevated creatinine', 'gfr', 'renal failure',
        'nephropathy', 'dialysis', 'proteinuria'
    ],
    
    'pcos': [
        'pcos', 'polycystic ovary', 'polycystic ovarian syndrome',
        'pcod', 'irregular periods', 'ovarian cysts', 'hyperandrogenism'
    ],
    
    'thyroid_hypothyroid': [
        'hypothyroid', 'underactive thyroid', 'low thyroid',
        'hypothyroidism', 'tsh high', 'elevated tsh',
        'levothyroxine', 'thyroxine', 'thyronorm', 'eltroxin'
    ],
    
    'ibs': [
        'ibs', 'irritable bowel syndrome', 'irritable bowel',
        'functional bowel disorder', 'spastic colon'
    ],
    
    'anemia': [
        'anemia', 'anaemia', 'iron deficiency', 'low hemoglobin',
        'low hb', 'hb <12', 'hemoglobin', 'iron deficient',
        'ferritin low', 'iron supplements'
    ],
    
    'gastritis': [
        'gastritis', 'acidity', 'gerd', 'acid reflux',
        'heartburn', 'peptic ulcer', 'stomach ulcer',
        'omeprazole', 'pantoprazole', 'esomeprazole', 'h. pylori'
    ],
    
    'post_surgery': [
        'post operative', 'post-operative', 'post surgery',
        'post-surgery', 'surgical recovery', 'operation',
        'wound healing', 'after surgery'
    ],
    
    'celiac': [
        'celiac', 'celiac disease', 'coeliac', 'coeliac disease',
        'gluten intolerance', 'gluten sensitivity', 'gluten allergy',
        'wheat allergy', 'gluten-free diet', 'avoid gluten',
        'gluten enteropathy', 'dermatitis herpetiformis'
    ]
}
