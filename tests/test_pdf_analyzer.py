"""
Tests for PDF analyzer module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.pdf_analyzer import PDFAnalyzer, PDFDocument, TextBlock, ImageBlock


class TestPDFAnalyzer:
    """Test cases for PDFAnalyzer class."""
    
    def test_init(self):
        """Test PDFAnalyzer initialization."""
        analyzer = PDFAnalyzer()
        assert analyzer.logger is not None
    
    @patch('src.pdf_analyzer.fitz.open')
    def test_analyze_pdf_success(self, mock_fitz_open, temp_dir):
        """Test successful PDF analysis."""
        # Setup mocks
        mock_doc = Mock()
        mock_doc.metadata = {"Title": "Test Document"}
        mock_doc.__len__.return_value = 1
        
        mock_page = Mock()
        mock_page.rect.width = 612
        mock_page.rect.height = 792
        mock_doc.__getitem__.return_value = mock_page
        
        mock_fitz_open.return_value = mock_doc
        
        # Create analyzer and mock its methods
        analyzer = PDFAnalyzer()
        analyzer._extract_text_blocks = Mock(return_value=[])
        analyzer._extract_images = Mock(return_value=[])
        
        # Test
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_text("dummy")
        
        result = analyzer.analyze_pdf(pdf_path)
        
        # Assertions
        assert isinstance(result, PDFDocument)
        assert result.metadata == {"Title": "Test Document"}
        assert result.page_count == 1
        assert result.page_sizes == [(612, 792)]
        mock_doc.close.assert_called_once()
    
    def test_extract_text_blocks(self):
        """Test text block extraction from mock document."""
        analyzer = PDFAnalyzer()
        
        # Mock document with text blocks
        mock_doc = Mock()
        mock_page = Mock()
        
        # Mock text blocks structure
        mock_blocks = {
            "blocks": [
                {
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Sample text",
                                    "bbox": [100, 100, 200, 120],
                                    "font": "Arial",
                                    "size": 12,
                                    "flags": 0,
                                    "color": 0
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        mock_page.get_text.return_value = mock_blocks
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        
        result = analyzer._extract_text_blocks(mock_doc)
        
        assert len(result) == 1
        assert isinstance(result[0], TextBlock)
        assert result[0].text == "Sample text"
        assert result[0].font_name == "Arial"
        assert result[0].font_size == 12
    
    def test_extract_images(self):
        """Test image extraction from mock document."""
        analyzer = PDFAnalyzer()
        
        # Mock document with images
        mock_doc = Mock()
        mock_page = Mock()
        
        # Mock image data
        mock_page.get_images.return_value = [(1, 0, 0, 0, 0, 0, 0)]
        mock_page.get_image_rects.return_value = [(100, 100, 200, 200)]
        
        # Mock pixmap
        mock_pixmap = Mock()
        mock_pixmap.width = 100
        mock_pixmap.height = 100
        mock_pixmap.n = 4
        mock_pixmap.alpha = 0
        mock_pixmap.colorspace = None
        mock_pixmap.tobytes.return_value = b"image_data"
        
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        
        with patch('src.pdf_analyzer.fitz.Pixmap', return_value=mock_pixmap):
            result = analyzer._extract_images(mock_doc)
        
        assert len(result) == 1
        assert isinstance(result[0], ImageBlock)
        assert result[0].width == 100
        assert result[0].height == 100
    
    def test_detect_columns_single_column(self):
        """Test column detection with single column layout."""
        analyzer = PDFAnalyzer()
        
        text_blocks = [
            TextBlock("Text 1", (100, 100, 200, 120), "Arial", 12, 0, 0, 0),
            TextBlock("Text 2", (105, 130, 205, 150), "Arial", 12, 0, 0, 0),
            TextBlock("Text 3", (110, 160, 210, 180), "Arial", 12, 0, 0, 0),
        ]
        
        result = analyzer._detect_columns(text_blocks, 612)
        
        assert len(result) == 1
        assert result[0]["x_start"] == 100
        assert result[0]["x_end"] == 210
    
    def test_detect_headers_footers(self):
        """Test header and footer detection."""
        analyzer = PDFAnalyzer()
        
        text_blocks = [
            TextBlock("Header", (100, 50, 200, 70), "Arial", 12, 0, 0, 0),   # Header
            TextBlock("Body", (100, 400, 200, 420), "Arial", 12, 0, 0, 0),    # Body
            TextBlock("Footer", (100, 750, 200, 770), "Arial", 12, 0, 0, 0),  # Footer
        ]
        
        headers, footers = analyzer._detect_headers_footers(text_blocks, 792)
        
        assert len(headers) == 1
        assert headers[0].text == "Header"
        assert len(footers) == 1
        assert footers[0].text == "Footer"
    
    def test_get_page_layout(self, mock_pdf_document):
        """Test page layout analysis."""
        analyzer = PDFAnalyzer()
        
        layout = analyzer.get_page_layout(mock_pdf_document, 0)
        
        assert layout["page_num"] == 0
        assert layout["page_size"] == (612, 792)
        assert "columns" in layout
        assert "headers" in layout
        assert "footers" in layout
        assert "text_blocks" in layout
        assert "images" in layout


class TestDataClasses:
    """Test the data classes used by PDFAnalyzer."""
    
    def test_text_block_creation(self):
        """Test TextBlock creation."""
        block = TextBlock(
            text="Test text",
            bbox=(0, 0, 100, 20),
            font_name="Arial",
            font_size=12,
            font_flags=0,
            color=0,
            page_num=0
        )
        
        assert block.text == "Test text"
        assert block.bbox == (0, 0, 100, 20)
        assert block.font_name == "Arial"
        assert block.font_size == 12
        assert block.page_num == 0
    
    def test_image_block_creation(self):
        """Test ImageBlock creation."""
        block = ImageBlock(
            image_data=b"test_data",
            bbox=(0, 0, 100, 100),
            width=100,
            height=100,
            page_num=0,
            image_format="png"
        )
        
        assert block.image_data == b"test_data"
        assert block.bbox == (0, 0, 100, 100)
        assert block.width == 100
        assert block.height == 100
        assert block.page_num == 0
        assert block.image_format == "png"
    
    def test_pdf_document_creation(self):
        """Test PDFDocument creation."""
        doc = PDFDocument(
            metadata={"Title": "Test"},
            page_count=1,
            page_sizes=[(612, 792)],
            text_blocks=[],
            images=[]
        )
        
        assert doc.metadata == {"Title": "Test"}
        assert doc.page_count == 1
        assert doc.page_sizes == [(612, 792)]
        assert doc.text_blocks == []
        assert doc.images == []
