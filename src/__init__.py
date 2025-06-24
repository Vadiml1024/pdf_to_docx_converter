"""
PDF to DOCX Converter Package
A tool for converting PDF files to DOCX format with layout preservation and OCR.
"""

__version__ = "1.0.0"
__author__ = "PDF to DOCX Converter Team"
__description__ = "Convert PDF files to DOCX format with layout preservation and OCR"

from .pdf_analyzer import PDFAnalyzer, PDFDocument, TextBlock, ImageBlock
from .ocr_processor import OCRProcessor, OCRResult
from .layout_engine import LayoutEngine, DocumentLayout, PageLayout, LayoutElement
from .docx_builder import DocxBuilder

__all__ = [
    'PDFAnalyzer', 'PDFDocument', 'TextBlock', 'ImageBlock',
    'OCRProcessor', 'OCRResult', 
    'LayoutEngine', 'DocumentLayout', 'PageLayout', 'LayoutElement',
    'DocxBuilder'
]
