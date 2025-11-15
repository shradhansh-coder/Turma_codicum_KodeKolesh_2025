"""OCR module for extracting text from images"""

import os
from typing import Dict, Any

# Try to import OCR dependencies - graceful fallback if not available
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except (ImportError, ValueError):
    # ValueError catches numpy compatibility issues
    pass


class OCRProcessor:
    """Process images and extract text using OCR"""
    
    SUPPORTED_FORMATS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff'}
    
    def __init__(self):
        self.available = TESSERACT_AVAILABLE
        if TESSERACT_AVAILABLE:
            # Try to configure Tesseract path for Windows
            try:
                pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            except:
                pass  # Use system PATH if not found
    
    def is_available(self) -> bool:
        """Check if OCR is available"""
        return self.available
    
    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text, confidence, and metadata
        """
        if not self.available:
            return {
                'success': False,
                'error': 'Tesseract OCR not installed. Install with: pip install pytesseract pillow',
                'text': '',
                'confidence': 0
            }
        
        try:
            # Open and process image
            image = Image.open(image_path)
            
            # Get image metadata
            image_info = {
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'mode': image.mode
            }
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image)
            
            # Get detailed data (includes confidence scores)
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            average_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Get OCR statistics
            text_length = len(text)
            word_count = len(text.split())
            
            return {
                'success': True,
                'text': text.strip(),
                'confidence': round(average_confidence, 2),
                'word_count': word_count,
                'character_count': text_length,
                'image_info': image_info,
                'language': 'eng'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0
            }
    
    def extract_text_with_preprocessing(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text with image preprocessing for better accuracy
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not self.available:
            return self.extract_text(image_path)
        
        try:
            from PIL import ImageEnhance, ImageFilter
            
            # Open image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Preprocessing steps
            # 1. Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # 2. Enhance brightness
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
            
            # 3. Apply sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # 4. Apply slight blur to reduce noise
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Extract text
            text = pytesseract.image_to_string(image)
            
            # Get confidence
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            average_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'success': True,
                'text': text.strip(),
                'confidence': round(average_confidence, 2),
                'word_count': len(text.split()),
                'character_count': len(text),
                'preprocessed': True
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0
            }
    
    def batch_extract(self, image_paths: list) -> Dict[str, Any]:
        """
        Extract text from multiple images
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            Dictionary with results for each image
        """
        results = {
            'total_images': len(image_paths),
            'successful': 0,
            'failed': 0,
            'documents': [],
            'combined_text': ''
        }
        
        all_text = []
        
        for image_path in image_paths:
            result = self.extract_text(image_path)
            
            if result['success']:
                results['successful'] += 1
                all_text.append(result['text'])
            else:
                results['failed'] += 1
            
            results['documents'].append({
                'path': image_path,
                'success': result['success'],
                'text': result.get('text', ''),
                'confidence': result.get('confidence', 0)
            })
        
        results['combined_text'] = '\n\n'.join(all_text)
        results['total_words'] = len(results['combined_text'].split())
        
        return results
