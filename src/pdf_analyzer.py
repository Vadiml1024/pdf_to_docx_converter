"""
PDF Analyzer Module
Handles PDF parsing, structure analysis, and content extraction.
"""

import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import json


@dataclass
class TextBlock:
    """Represents a text block with positioning and formatting."""
    text: str
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    font_name: str
    font_size: float
    font_flags: int
    color: int
    page_num: int


@dataclass
class ImageBlock:
    """Represents an image with positioning information."""
    image_data: bytes
    bbox: Tuple[float, float, float, float]
    width: int
    height: int
    page_num: int
    image_format: str


@dataclass
class PDFDocument:
    """Represents the complete PDF document structure."""
    metadata: Dict[str, Any]
    page_count: int
    page_sizes: List[Tuple[float, float]]
    text_blocks: List[TextBlock]
    images: List[ImageBlock]


class PDFAnalyzer:
    """Analyzes PDF documents and extracts content with layout information."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_pdf(self, pdf_path: Path) -> PDFDocument:
        """
        Analyze a PDF file and extract its structure and content.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            PDFDocument object containing all extracted information
        """
        try:
            doc = fitz.open(str(pdf_path))
            
            # Extract metadata
            metadata = doc.metadata
            page_count = len(doc)
            
            # Get page sizes
            page_sizes = []
            for page_num in range(page_count):
                page = doc[page_num]
                page_sizes.append((page.rect.width, page.rect.height))
            
            # Extract text blocks and images
            text_blocks = self._extract_text_blocks(doc)
            images = self._extract_images(doc)
            
            doc.close()
            
            pdf_document = PDFDocument(
                metadata=metadata,
                page_count=page_count,
                page_sizes=page_sizes,
                text_blocks=text_blocks,
                images=images
            )
            
            self.logger.info(f"Analyzed PDF: {page_count} pages, {len(text_blocks)} text blocks, {len(images)} images")
            return pdf_document
            
        except Exception as e:
            self.logger.error(f"Error analyzing PDF {pdf_path}: {str(e)}")
            raise
    
    def _extract_text_blocks(self, doc: fitz.Document) -> List[TextBlock]:
        """Extract text blocks with formatting and positioning information."""
        text_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get text blocks with detailed information
            blocks = page.get_text("dict")
            
            for block in blocks["blocks"]:
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                text_block = TextBlock(
                                    text=text,
                                    bbox=tuple(span["bbox"]),
                                    font_name=span["font"],
                                    font_size=span["size"],
                                    font_flags=span["flags"],
                                    color=span["color"],
                                    page_num=page_num
                                )
                                text_blocks.append(text_block)
        
        self.logger.debug(f"Extracted {len(text_blocks)} text blocks")
        return text_blocks
    
    def _extract_images(self, doc: fitz.Document) -> List[ImageBlock]:
        """Extract images with positioning information."""
        images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    # Skip if image is too small or in CMYK color space
                    if pix.width < 10 or pix.height < 10:
                        pix = None
                        continue
                    
                    if pix.colorspace and pix.colorspace.name == "DeviceCMYK":
                        # Convert CMYK to RGB
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    
                    # Get image positioning
                    img_rects = page.get_image_rects(xref)
                    bbox = img_rects[0] if img_rects else (0, 0, pix.width, pix.height)
                    
                    # Extract image data
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        image_data = pix.tobytes("png")
                        image_format = "png"
                    else:
                        image_data = pix.tobytes()
                        image_format = "raw"
                    
                    image_block = ImageBlock(
                        image_data=image_data,
                        bbox=bbox,
                        width=pix.width,
                        height=pix.height,
                        page_num=page_num,
                        image_format=image_format
                    )
                    images.append(image_block)
                    
                    pix = None  # Free memory
                    
                except Exception as e:
                    self.logger.warning(f"Error extracting image {img_index} from page {page_num}: {str(e)}")
                    continue
        
        self.logger.debug(f"Extracted {len(images)} images")
        return images
    
    def extract_text_blocks(self, pdf_document: PDFDocument) -> List[TextBlock]:
        """Return text blocks from the analyzed PDF document."""
        return pdf_document.text_blocks
    
    def extract_images(self, pdf_document: PDFDocument) -> List[ImageBlock]:
        """Return images from the analyzed PDF document."""
        return pdf_document.images
    
    def get_page_layout(self, pdf_document: PDFDocument, page_num: int) -> Dict[str, Any]:
        """
        Analyze the layout of a specific page.
        
        Args:
            pdf_document: The analyzed PDF document
            page_num: Page number to analyze
            
        Returns:
            Dictionary containing layout information
        """
        page_text_blocks = [tb for tb in pdf_document.text_blocks if tb.page_num == page_num]
        page_images = [img for img in pdf_document.images if img.page_num == page_num]
        
        page_width, page_height = pdf_document.page_sizes[page_num]
        
        # Detect columns by analyzing text block positions
        columns = self._detect_columns(page_text_blocks, page_width)
        
        # Detect headers and footers
        headers, footers = self._detect_headers_footers(page_text_blocks, page_height)
        
        layout = {
            "page_num": page_num,
            "page_size": (page_width, page_height),
            "columns": columns,
            "headers": headers,
            "footers": footers,
            "text_blocks": page_text_blocks,
            "images": page_images
        }
        
        return layout
    
    def _detect_columns(self, text_blocks: List[TextBlock], page_width: float) -> List[Dict[str, float]]:
        """Detect column layout from text block positions."""
        if not text_blocks:
            return [{"x_start": 0, "x_end": page_width}]
        
        # Group text blocks by approximate x-position
        x_positions = [tb.bbox[0] for tb in text_blocks]
        x_positions.sort()
        
        # Simple column detection - look for gaps in x-positions
        columns = []
        current_col_start = 0
        
        # For now, assume single column (can be enhanced)
        columns.append({
            "x_start": min(x_positions) if x_positions else 0,
            "x_end": max([tb.bbox[2] for tb in text_blocks]) if text_blocks else page_width
        })
        
        return columns
    
    def _detect_headers_footers(self, text_blocks: List[TextBlock], page_height: float) -> Tuple[List[TextBlock], List[TextBlock]]:
        """Detect headers and footers based on position."""
        header_threshold = page_height * 0.1  # Top 10%
        footer_threshold = page_height * 0.9  # Bottom 10%
        
        headers = [tb for tb in text_blocks if tb.bbox[1] < header_threshold]
        footers = [tb for tb in text_blocks if tb.bbox[3] > footer_threshold]
        
        return headers, footers
