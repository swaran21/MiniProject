"""
Prescription Analyzer Service
Analyzes prescription text to extract medical conditions and medications
Uses keyword matching - no ML training needed
"""

from data.config.medical_nutrition_rules import (
    MEDICAL_NUTRITION_RULES,
    MEDICATION_INTERACTIONS,
    CONDITION_KEYWORDS
)
from typing import Dict, List
import re

class PrescriptionAnalyzer:
    """
    Analyzes prescription text to detect conditions and medications
    Rule-based approach using keyword matching
    """
    
    def __init__(self):
        self.condition_keywords = CONDITION_KEYWORDS
        self.medical_rules = MEDICAL_NUTRITION_RULES
        self.medication_db = MEDICATION_INTERACTIONS
    
    def analyze(self, prescription_text: str, user_id: int = None) -> Dict:
        """
        Main analysis method
        
        Args:
            prescription_text: OCR text from prescription
            user_id: Optional user ID for database storage
        
        Returns:
            dict with detected conditions, medications, restrictions, etc.
        """
        
        # Step 1: Detect conditions
        detected_conditions = self.detect_conditions(prescription_text)
        
        # Step 2: Extract medications
        medications = self.extract_medications(prescription_text)
        
        # Step 3: Classify as acute or chronic
        condition_types = self.classify_conditions(detected_conditions)
        
        # Step 4: Calculate plan duration
        duration = self.calculate_duration(detected_conditions, condition_types)
        
        # Step 5: Get nutrition restrictions
        restrictions = self.get_restrictions(detected_conditions)
        
        # Step 6: Get recommendations
        recommendations = self.get_recommendations(detected_conditions)
        
        return {
            'user_id': user_id,
            'detected_conditions': detected_conditions,
            'condition_details': [
                {
                    'name': cond,
                    'display_name': self.medical_rules[cond]['display_name'],
                    'type': self.medical_rules[cond]['type']
                }
                for cond in detected_conditions
            ],
            'medications': medications,
            'is_chronic': condition_types['is_chronic'],
            'plan_duration_days': duration,
            'foods_to_avoid': restrictions['avoid'],
            'foods_to_eat': restrictions['eat'],
            'special_notes': recommendations,
            'meal_timing': self.get_meal_timing(detected_conditions),
            'analysis_summary': self.generate_summary(detected_conditions, condition_types)
        }
    
    def detect_conditions(self, text: str) -> List[str]:
        """
        Detect medical conditions using keyword matching with word boundaries
        
        CRITICAL FIX: Uses regex \b to prevent false matches
        - 'age' won't match inside 'massage'
        - 'tea' won't match inside 'team'
        
        Also checks for negation ('no diabetes', 'not hypertensive')
        
        Args:
            text: Prescription text (from OCR or manual input)
        
        Returns:
            List of detected condition keys
        """
        detected = []
        text_lower = text.lower()
        
        for condition, keywords in self.condition_keywords.items():
            # Check if any keyword matches with word boundaries
            for keyword in keywords:
                # \b ensures we match whole words only
                # re.escape prevents special chars from breaking regex
                pattern = r'\b' + re.escape(keyword) + r'\b'
                
                match = re.search(pattern, text_lower)
                if match:
                    # Check for negation in preceding context
                    # IMPROVED: Increased window from 20 to 50 characters
                    # This catches longer negation phrases like:
                    # "Patient does not appear to have any symptoms of diabetes"
                    start_index = match.start()
                    preceding_text = text_lower[max(0, start_index - 50):start_index]
                    
                    # Skip if negated (e.g., "no diabetes", "not hypertensive")
                    negation_words = ['no ', 'not ', 'negative ', 'absent ', 'ruled out']
                    is_negated = any(neg in preceding_text for neg in negation_words)
                    
                    if not is_negated:
                        detected.append(condition)
                        break  # Found this condition, move to next
        
        return detected
    
    def extract_medications(self, text: str) -> List[Dict]:
        """
        Extract medications from prescription text using word boundaries
        
        CRITICAL FIX: Prevents partial matches
        - 'met' won't incorrectly match 'metformin'
        - 'lose' won't match 'losartan'
        
        Returns:
            List of detected medications with their interactions
        """
        medications = []
        text_lower = text.lower()
        
        for med_name, med_info in self.medication_db.items():
            # Use regex word boundary for exact matching
            pattern = r'\b' + re.escape(med_name) + r'\b'
            
            if re.search(pattern, text_lower):
                medications.append({
                    'name': med_name.title(),
                    'condition': med_info['condition'],
                    'avoid_with': med_info.get('avoid_with', []),
                    'take_with': med_info.get('take_with', ''),
                    'timing': med_info.get('timing', ''),
                    'alert': med_info.get('alert', ''),
                    'food_notes': med_info.get('food_notes', '')
                })
        
        return medications
    
    def classify_conditions(self, conditions: List[str]) -> Dict:
        """
        Classify if conditions are acute or chronic
        
        Returns:
            dict with classification info
        """
        has_chronic = False
        has_acute = False
        
        for condition in conditions:
            cond_type = self.medical_rules[condition]['type']
            if cond_type == 'chronic':
                has_chronic = True
            elif cond_type == 'acute':
                has_acute = True
        
        return {
            'is_chronic': has_chronic,
            'is_acute': has_acute,
            'primary_type': 'chronic' if has_chronic else 'acute'
        }
    
    def calculate_duration(self, conditions: List[str], condition_types: Dict) -> int:
        """
        Calculate meal plan duration in days
        
        Chronic conditions: 90 days (3 months)
        Acute conditions: 30 days (1 month)
        Mixed: 90 days
        """
        if condition_types['is_chronic']:
            return 90
        else:
            # For acute conditions, use the max duration
            max_duration = 30
            for condition in conditions:
                cond_duration = self.medical_rules[condition].get('duration_days', 30)
                max_duration = max(max_duration, cond_duration)
            return max_duration
    
    def get_restrictions(self, conditions: List[str]) -> Dict:
        """
        Aggregate foods to eat and avoid across all conditions
        """
        avoid_set = set()
        eat_set = set()
        
        for condition in conditions:
            rules = self.medical_rules[condition]
            avoid_set.update(rules['foods_to_avoid'])
            eat_set.update(rules['foods_to_eat'])
        
        return {
            'avoid': sorted(list(avoid_set)),
            'eat': sorted(list(eat_set))
        }
    
    def get_recommendations(self, conditions: List[str]) -> List[str]:
        """
        Get special notes and recommendations
        """
        notes = []
        
        for condition in conditions:
            rules = self.medical_rules[condition]
            if 'special_notes' in rules:
                notes.extend(rules['special_notes'])
        
        return notes
    
    def get_meal_timing(self, conditions: List[str]) -> str:
        """
        Get meal timing recommendations
        """
        for condition in conditions:
            rules = self.medical_rules[condition]
            if 'meal_timing' in rules:
                return rules['meal_timing']
        
        return 'Regular meal timing - 3 meals per day with healthy snacks'
    
    def generate_summary(self, conditions: List[str], condition_types: Dict) -> str:
        """
        Generate a human-readable summary
        """
        if not conditions:
            return "No medical conditions detected in the prescription."
        
        condition_names = [
            self.medical_rules[c]['display_name'] 
            for c in conditions
        ]
        
        summary = f"Detected {len(conditions)} condition(s): {', '.join(condition_names)}. "
        
        if condition_types['is_chronic']:
            summary += "These are chronic conditions requiring ongoing dietary management. "
            summary += "A 90-day meal plan will be generated with recipes tailored to your health needs."
        else:
            summary += "These are acute/temporary conditions. "
            summary += "A 30-day recovery meal plan will be generated."
        
        return summary
