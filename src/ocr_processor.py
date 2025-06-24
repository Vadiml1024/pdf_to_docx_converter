"""
OCR Processor Module
Handles image preprocessing and text extraction from images using OCR.
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import io


@dataclass
class OCRResult:
    """Represents OCR extraction result with confidence and positioning."""
    text: str
    confidence: float
    bbox: Tuple[float, float, float, float]
    page_num: int
    original_image_bbox: Tuple[float, float, float, float]


class OCRProcessor:
    """Processes images for OCR text extraction with preprocessing."""
    
    def __init__(self, language: str = 'eng', confidence_threshold: float = 30.0):
        self.language = language
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        
        # Try to get Tesseract version to verify installation
        try:
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"Tesseract version: {version}")
        except Exception as e:
            self.logger.error(f"Tesseract not properly installed: {e}")
            raise
    
    def process_image(self, image_block) -> Optional[OCRResult]:
        """
        Process an image block and extract text using OCR.
        
        Args:
            image_block: ImageBlock object containing image data and metadata
            
        Returns:
            OCRResult object if text found, None otherwise
        """
        try:
            # Convert image data to PIL Image
            if image_block.image_format == "png":
                image = Image.open(io.BytesIO(image_block.image_data))
            else:
                # Handle raw image data
                image_array = np.frombuffer(image_block.image_data, dtype=np.uint8)
                image_array = image_array.reshape((image_block.height, image_block.width, -1))
                image = Image.fromarray(image_array)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Extract text with confidence scores
            ocr_data = pytesseract.image_to_data(
                processed_image,
                lang=self.language,
                output_type=pytesseract.Output.DICT,
                config='--psm 6'  # Uniform block of text
            )
            
            # Filter and combine text with confidence above threshold
            text_parts = []
            confidences = []
            
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                conf = float(ocr_data['conf'][i])
                
                if text and conf > self.confidence_threshold:
                    text_parts.append(text)
                    confidences.append(conf)
            
            if not text_parts:
                return None
            
            # Combine text and calculate average confidence
            extracted_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences)
            
            self.logger.debug(f"OCR extracted: '{extracted_text[:50]}...' (confidence: {avg_confidence:.1f})")
            
            return OCRResult(
                text=extracted_text,
                confidence=avg_confidence,
                bbox=image_block.bbox,
                page_num=image_block.page_num,
                original_image_bbox=image_block.bbox
            )
            
        except Exception as e:
            self.logger.error(f"Error processing image with OCR: {str(e)}")
            return None
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert PIL to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Apply preprocessing steps
        cv_image = self._enhance_contrast(cv_image)
        cv_image = self._denoise_image(cv_image)
        cv_image = self._deskew_image(cv_image)
        cv_image = self._binarize_image(cv_image)
        
        # Convert back to PIL
        processed_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
        
        return processed_image
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    
    def _denoise_image(self, image: np.ndarray) -> np.ndarray:
        """Remove noise from the image."""
        return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Correct skew in the image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Find all white pixels
        coords = np.column_stack(np.where(gray > 0))
        
        # Find minimum area rectangle
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            
            # Correct the angle
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # Only apply rotation if angle is significant
            if abs(angle) > 0.5:
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        return image
    
    def _binarize_image(self, image: np.ndarray) -> np.ndarray:
        """Convert image to binary (black and white) for better OCR."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive threshold
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    
    def batch_process_images(self, image_blocks: List) -> List[OCRResult]:
        """
        Process multiple images in batch.
        
        Args:
            image_blocks: List of ImageBlock objects
            
        Returns:
            List of OCRResult objects
        """
        results = []
        
        for i, image_block in enumerate(image_blocks):
            self.logger.info(f"Processing image {i+1}/{len(image_blocks)}")
            ocr_result = self.process_image(image_block)
            if ocr_result:
                results.append(ocr_result)
        
        self.logger.info(f"OCR completed: {len(results)}/{len(image_blocks)} images processed successfully")
        return results
    
    def get_text_regions(self, image_block) -> List[Dict]:
        """
        Detect text regions in an image without extracting text.
        
        Args:
            image_block: ImageBlock object
            
        Returns:
            List of dictionaries containing text region information
        """
        try:
            # Convert image data to PIL Image
            if image_block.image_format == "png":
                image = Image.open(io.BytesIO(image_block.image_data))
            else:
                image_array = np.frombuffer(image_block.image_data, dtype=np.uint8)
                image_array = image_array.reshape((image_block.height, image_block.width, -1))
                image = Image.fromarray(image_array)
            
            # Use Tesseract to detect text regions
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                output_type=pytesseract.Output.DICT
            )
            
            regions = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > self.confidence_threshold:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    regions.append({
                        'bbox': (x, y, x + w, y + h),
                        'confidence': float(data['conf'][i]),
                        'text_length': len(data['text'][i].strip())
                    })
            
            return regions
            
        except Exception as e:
            self.logger.error(f"Error detecting text regions: {str(e)}")
            return []
    
    def set_language(self, language: str) -> None:
        """Set OCR language."""
        self.language = language
        self.logger.info(f"OCR language set to: {language}")
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """Set confidence threshold for text extraction."""
        self.confidence_threshold = threshold
        self.logger.info(f"OCR confidence threshold set to: {threshold}")
