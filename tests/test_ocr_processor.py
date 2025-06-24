"""
Tests for OCR processor module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import io
from PIL import Image
import numpy as np

from src.ocr_processor import OCRProcessor, OCRResult
from tests.conftest import TEST_IMAGE_DATA


class TestOCRProcessor:
    """Test cases for OCRProcessor class."""
    
    @patch('src.ocr_processor.pytesseract.get_tesseract_version')
    def test_init_success(self, mock_version):
        """Test OCRProcessor initialization."""
        mock_version.return_value = "5.0.0"
        processor = OCRProcessor()
        
        assert processor.language == 'eng'
        assert processor.confidence_threshold == 30.0
        assert processor.logger is not None
    
    @patch('src.ocr_processor.pytesseract.get_tesseract_version')
    def test_init_tesseract_error(self, mock_version):
        """Test OCRProcessor initialization with Tesseract error."""
        mock_version.side_effect = Exception("Tesseract not found")
        
        with pytest.raises(Exception):
            OCRProcessor()
    
    @patch('src.ocr_processor.pytesseract.image_to_data')
    def test_process_image_success(self, mock_ocr):
        """Test successful image processing."""
        processor = OCRProcessor()
        
        # Mock OCR data
        mock_ocr.return_value = {
            'text': ['', 'Sample', 'text', ''],
            'conf': ['-1', '85', '90', '-1']
        }
        
        # Create mock image block
        mock_image_block = Mock()
        mock_image_block.image_data = TEST_IMAGE_DATA
        mock_image_block.image_format = "png"
        mock_image_block.bbox = (100, 100, 200, 200)
        mock_image_block.page_num = 0
        
        with patch.object(processor, '_preprocess_image') as mock_preprocess:
            mock_preprocess.return_value = Image.new('RGB', (100, 100))
            result = processor.process_image(mock_image_block)
        
        assert isinstance(result, OCRResult)
        assert result.text == "Sample text"
        assert result.confidence == 87.5  # Average of 85 and 90
        assert result.page_num == 0
    
    @patch('src.ocr_processor.pytesseract.image_to_data')
    def test_process_image_low_confidence(self, mock_ocr):
        """Test image processing with low confidence results."""
        processor = OCRProcessor()
        
        # Mock OCR data with low confidence
        mock_ocr.return_value = {
            'text': ['low', 'confidence', 'text'],
            'conf': ['20', '25', '15']
        }
        
        mock_image_block = Mock()
        mock_image_block.image_data = TEST_IMAGE_DATA
        mock_image_block.image_format = "png"
        mock_image_block.bbox = (100, 100, 200, 200)
        mock_image_block.page_num = 0
        
        with patch.object(processor, '_preprocess_image') as mock_preprocess:
            mock_preprocess.return_value = Image.new('RGB', (100, 100))
            result = processor.process_image(mock_image_block)
        
        # Should return None due to low confidence
        assert result is None
    
    def test_preprocess_image(self):
        """Test image preprocessing pipeline."""
        processor = OCRProcessor()
        
        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='white')
        
        with patch.object(processor, '_enhance_contrast') as mock_contrast, \
             patch.object(processor, '_denoise_image') as mock_denoise, \
             patch.object(processor, '_deskew_image') as mock_deskew, \
             patch.object(processor, '_binarize_image') as mock_binarize:
            
            # Setup return values
            mock_contrast.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            mock_denoise.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            mock_deskew.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            mock_binarize.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            
            result = processor._preprocess_image(test_image)
            
            assert isinstance(result, Image.Image)
            mock_contrast.assert_called_once()
            mock_denoise.assert_called_once()
            mock_deskew.assert_called_once()
            mock_binarize.assert_called_once()
    
    def test_enhance_contrast(self):
        """Test contrast enhancement."""
        processor = OCRProcessor()
        
        # Create test image array
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        with patch('src.ocr_processor.cv2.createCLAHE') as mock_clahe:
            mock_clahe_obj = Mock()
            mock_clahe_obj.apply.return_value = np.ones((100, 100), dtype=np.uint8) * 150
            mock_clahe.return_value = mock_clahe_obj
            
            result = processor._enhance_contrast(test_image)
            
            assert result.shape == (100, 100, 3)
            mock_clahe.assert_called_once()
    
    def test_batch_process_images(self):
        """Test batch processing of multiple images."""
        processor = OCRProcessor()
        
        # Create mock image blocks
        mock_images = [Mock() for _ in range(3)]
        
        with patch.object(processor, 'process_image') as mock_process:
            mock_process.side_effect = [
                OCRResult("text1", 80, (0, 0, 100, 100), 0, (0, 0, 100, 100)),
                None,  # Failed processing
                OCRResult("text3", 90, (0, 0, 100, 100), 0, (0, 0, 100, 100))
            ]
            
            results = processor.batch_process_images(mock_images)
            
            assert len(results) == 2
            assert results[0].text == "text1"
            assert results[1].text == "text3"
    
    @patch('src.ocr_processor.pytesseract.image_to_data')
    def test_get_text_regions(self, mock_ocr):
        """Test text region detection."""
        processor = OCRProcessor()
        
        mock_ocr.return_value = {
            'left': [10, 20],
            'top': [10, 30],
            'width': [50, 60],
            'height': [20, 25],
            'conf': ['80', '85'],
            'text': ['word1', 'word2']
        }
        
        mock_image_block = Mock()
        mock_image_block.image_data = TEST_IMAGE_DATA
        mock_image_block.image_format = "png"
        
        regions = processor.get_text_regions(mock_image_block)
        
        assert len(regions) == 2
        assert regions[0]['bbox'] == (10, 10, 60, 30)
        assert regions[1]['bbox'] == (20, 30, 80, 55)
    
    def test_set_language(self):
        """Test language setting."""
        processor = OCRProcessor()
        
        processor.set_language('fra')
        assert processor.language == 'fra'
    
    def test_set_confidence_threshold(self):
        """Test confidence threshold setting."""
        processor = OCRProcessor()
        
        processor.set_confidence_threshold(50.0)
        assert processor.confidence_threshold == 50.0


class TestOCRResult:
    """Test OCRResult data class."""
    
    def test_ocr_result_creation(self):
        """Test OCRResult creation."""
        result = OCRResult(
            text="Sample text",
            confidence=85.5,
            bbox=(100, 100, 200, 200),
            page_num=0,
            original_image_bbox=(100, 100, 200, 200)
        )
        
        assert result.text == "Sample text"
        assert result.confidence == 85.5
        assert result.bbox == (100, 100, 200, 200)
        assert result.page_num == 0
        assert result.original_image_bbox == (100, 100, 200, 200)
