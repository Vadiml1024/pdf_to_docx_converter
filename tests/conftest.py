"""
Test configuration and utilities for PDF to DOCX converter.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import tempfile
from unittest.mock import Mock, patch


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_path:
        yield Path(temp_path)


@pytest.fixture
def sample_pdf_path():
    """Path to a sample PDF file for testing."""
    # This would be a real PDF file in a real test environment
    return Path("tests/sample_files/sample.pdf")


@pytest.fixture
def mock_pdf_document():
    """Mock PDF document for testing."""
    from src.pdf_analyzer import PDFDocument, TextBlock, ImageBlock
    
    text_blocks = [
        TextBlock(
            text="Sample text content",
            bbox=(100, 100, 200, 120),
            font_name="Arial",
            font_size=12,
            font_flags=0,
            color=0,
            page_num=0
        )
    ]
    
    images = [
        ImageBlock(
            image_data=b"fake_image_data",
            bbox=(100, 200, 300, 400),
            width=200,
            height=200,
            page_num=0,
            image_format="png"
        )
    ]
    
    return PDFDocument(
        metadata={"Title": "Test Document"},
        page_count=1,
        page_sizes=[(612, 792)],  # Standard letter size
        text_blocks=text_blocks,
        images=images
    )


@pytest.fixture
def mock_ocr_result():
    """Mock OCR result for testing."""
    from src.ocr_processor import OCRResult
    
    return OCRResult(
        text="OCR extracted text",
        confidence=85.5,
        bbox=(100, 200, 300, 400),
        page_num=0,
        original_image_bbox=(100, 200, 300, 400)
    )


# Test constants - Create a valid minimal PNG image
TEST_PDF_CONTENT = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"

# Create a valid 1x1 pixel PNG image
TEST_IMAGE_DATA = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00'
    b'\x00\x04\x00\x01\xddV\xe7\xb8\x00\x00\x00\x00IEND\xaeB`\x82'
)


def create_test_pdf(path: Path) -> None:
    """Create a minimal test PDF file."""
    path.write_bytes(TEST_PDF_CONTENT)


def create_test_image(path: Path) -> None:
    """Create a minimal test image file."""
    path.write_bytes(TEST_IMAGE_DATA)
