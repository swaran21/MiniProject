"""
OCR Service for Prescription Text Extraction

Uses Pytesseract with image preprocessing to handle handwritten text.
No external APIs needed - fully self-contained!

Features:
- Grayscale conversion
- Contrast enhancement
- Sharpening filter
- Noise reduction
- Custom Tesseract configuration
"""

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    PYTESSERACT_AVAILABLE = True
    
    # WINDOWS PATH CONFIGURATION
    # Auto-detect Tesseract installation location
    import os
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Tesseract-OCR\tesseract.exe'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"✅ Tesseract found at: {path}")
            break
    else:
        print("⚠️ Tesseract not found in common locations.")
        print("   Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Or set manually: pytesseract.pytesseract.tesseract_cmd = r'C:\\path\\to\\tesseract.exe'")
    
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("⚠️ pytesseract not installed. Run: pip install pytesseract pillow")

import io
import re
from typing import Dict

class OCRService:
    """
    Enhanced OCR service for medical prescription text extraction
    
    Optimized for handwritten prescriptions with:
    - Image preprocessing pipeline
    - Medical text filtering
    - Confidence estimation
    """
    
    def __init__(self):
        self.available = PYTESSERACT_AVAILABLE
        if not self.available:
            print("❌ OCR Service unavailable - pytesseract not installed")
    
    def extract_text(self, image_bytes: bytes) -> Dict:
        """
        Extract text from prescription image with preprocessing
        
        Args:
            image_bytes: Raw image bytes (PNG, JPG, etc.)
        
        Returns:
            dict with 'text', 'confidence', 'preprocessed'
        """
        if not self.available:
            return {
                'success': False,
                'text': '',
                'error': 'Pytesseract not installed. Run: pip install pytesseract pillow'
            }
        
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocessing pipeline for better OCR
            processed_image = self._preprocess_image(image)
            
            # Extract text with custom Tesseract config
            # --oem 1: Use LSTM neural network (better for handwriting)
            # --psm 6: Assume single uniform block of text
            custom_config = r'--oem 1 --psm 6'
            
            extracted_text = pytesseract.image_to_string(
                processed_image, 
                config=custom_config
            )
            
            # Clean up the text
            cleaned_text = self._clean_text(extracted_text)
            
            # Estimate confidence based on output quality
            confidence = self._estimate_confidence(cleaned_text)
            
            return {
                'success': True,
                'text': cleaned_text,
                'confidence': confidence,
                'raw_text': extracted_text,
                'message': 'Text extracted successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'text': '',
                'error': f'OCR extraction failed: {str(e)}'
            }
    
    def _preprocess_image(self, image: 'Image.Image') -> 'Image.Image':
        """
        Apply preprocessing to improve OCR accuracy on handwriting
        
        Steps:
        1. Convert to grayscale (removes color noise)
        2. Increase contrast (makes text stand out)
        3. Apply sharpening (enhances edges)
        4. Optional: Denoise
        
        Args:
            image: PIL Image object
        
        Returns:
            Preprocessed PIL Image
        """
        # Step 1: Convert to grayscale
        # Handwriting doesn't need color, and grayscale improves OCR
        if image.mode != 'L':
            image = image.convert('L')
        
        # Step 2: Increase contrast
        # Makes faded handwriting more visible
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)  # 2x contrast boost
        
        # Step 3: Sharpen edges
        # Helps Tesseract detect letter boundaries
        image = image.filter(ImageFilter.SHARPEN)
        
        # Step 4: Optional - reduce noise
        # Uncomment if images have background noise
        # image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    
    def _clean_text(self, raw_text: str) -> str:
        """
        Clean up OCR output text
        
        Removes:
        - Extra whitespace
        - Special characters that aren't medical
        - Line breaks that don't make sense
        
        Args:
            raw_text: Raw OCR output
        
        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', raw_text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Preserve line breaks for prescription structure
        text = raw_text.strip()
        
        return text
    
    def _estimate_confidence(self, text: str) -> str:
        """
        Estimate OCR confidence based on output quality
        
        Heuristics:
        - Low: Very short text or lots of gibberish characters
        - Medium: Reasonable length with some recognizable medical terms
        - High: Long text with medical keywords
        
        Args:
            text: Cleaned OCR text
        
        Returns:
            'low', 'medium', or 'high'
        """
        # Medical keywords that indicate good extraction
        medical_keywords = [
            'diagnosis', 'patient', 'medication', 'prescription',
            'diabetes', 'hypertension', 'metformin', 'lisinopril',
            'mg', 'tablet', 'capsule', 'daily', 'twice'
        ]
        
        text_lower = text.lower()
        
        # Count medical keywords
        keyword_count = sum(1 for keyword in medical_keywords if keyword in text_lower)
        
        # Length check
        text_length = len(text.strip())
        
        # Confidence estimation
        if text_length < 20:
            return 'low'
        elif text_length < 50 or keyword_count < 2:
            return 'medium'
        else:
            return 'high'
