"""
Layout Engine Module
Reconstructs document layout by combining text blocks, images, and OCR results.
"""

import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import numpy as np
from collections import defaultdict


@dataclass
class LayoutElement:
    """Represents a layout element (text, image, or OCR text)."""
    element_type: str  # 'text', 'image', 'ocr_text'
    content: Any
    bbox: Tuple[float, float, float, float]
    page_num: int
    z_order: int = 0  # For layering elements


@dataclass
class PageLayout:
    """Represents the layout of a single page."""
    page_num: int
    page_size: Tuple[float, float]
    elements: List[LayoutElement]
    columns: List[Dict[str, float]]
    margins: Dict[str, float]
    headers: List[LayoutElement]
    footers: List[LayoutElement]


@dataclass
class DocumentLayout:
    """Represents the complete document layout."""
    pages: List[PageLayout]
    global_styles: Dict[str, Any]
    font_mapping: Dict[str, str]


class LayoutEngine:
    """Reconstructs document layout from extracted content."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.font_mapping = self._create_font_mapping()
    
    def reconstruct_layout(
        self,
        text_blocks: List,
        images: List,
        ocr_results: List,
        pdf_document
    ) -> DocumentLayout:
        """
        Reconstruct the complete document layout.
        
        Args:
            text_blocks: List of TextBlock objects
            images: List of ImageBlock objects
            ocr_results: List of OCRResult objects
            pdf_document: PDFDocument object
            
        Returns:
            DocumentLayout object
        """
        self.logger.info("Starting layout reconstruction...")
        
        pages = []
        
        for page_num in range(pdf_document.page_count):
            page_layout = self._reconstruct_page_layout(
                page_num, text_blocks, images, ocr_results, pdf_document
            )
            pages.append(page_layout)
        
        # Extract global styles
        global_styles = self._extract_global_styles(text_blocks)
        
        document_layout = DocumentLayout(
            pages=pages,
            global_styles=global_styles,
            font_mapping=self.font_mapping
        )
        
        self.logger.info(f"Layout reconstruction completed for {len(pages)} pages")
        return document_layout
    
    def _reconstruct_page_layout(
        self,
        page_num: int,
        text_blocks: List,
        images: List,
        ocr_results: List,
        pdf_document
    ) -> PageLayout:
        """Reconstruct layout for a single page."""
        
        # Filter content for this page
        page_text_blocks = [tb for tb in text_blocks if tb.page_num == page_num]
        page_images = [img for img in images if img.page_num == page_num]
        page_ocr = [ocr for ocr in ocr_results if ocr.page_num == page_num]
        
        page_width, page_height = pdf_document.page_sizes[page_num]
        
        # Create layout elements
        elements = []
        
        # Add text elements
        for text_block in page_text_blocks:
            element = LayoutElement(
                element_type='text',
                content=text_block,
                bbox=text_block.bbox,
                page_num=page_num,
                z_order=1
            )
            elements.append(element)
        
        # Add image elements
        for image_block in page_images:
            element = LayoutElement(
                element_type='image',
                content=image_block,
                bbox=image_block.bbox,
                page_num=page_num,
                z_order=0  # Images behind text
            )
            elements.append(element)
        
        # Add OCR text elements
        for ocr_result in page_ocr:
            element = LayoutElement(
                element_type='ocr_text',
                content=ocr_result,
                bbox=ocr_result.bbox,
                page_num=page_num,
                z_order=2  # OCR text on top
            )
            elements.append(element)
        
        # Sort elements by reading order (top to bottom, left to right)
        elements.sort(key=lambda e: (e.bbox[1], e.bbox[0]))
        
        # Detect layout structure
        columns = self._detect_columns(page_text_blocks, page_width)
        margins = self._calculate_margins(elements, page_width, page_height)
        headers, footers = self._separate_headers_footers(elements, page_height)
        
        page_layout = PageLayout(
            page_num=page_num,
            page_size=(page_width, page_height),
            elements=elements,
            columns=columns,
            margins=margins,
            headers=headers,
            footers=footers
        )
        
        return page_layout
    
    def _detect_columns(self, text_blocks: List, page_width: float) -> List[Dict[str, float]]:
        """Detect column layout from text positioning."""
        if not text_blocks:
            return [{"x_start": 0, "x_end": page_width, "width": page_width}]
        
        # Get all text block x-coordinates
        left_coords = [tb.bbox[0] for tb in text_blocks]
        right_coords = [tb.bbox[2] for tb in text_blocks]
        
        # Cluster similar x-coordinates to find column boundaries
        left_clusters = self._cluster_coordinates(left_coords, tolerance=10)
        right_clusters = self._cluster_coordinates(right_coords, tolerance=10)
        
        # Simple column detection - assume single column for now
        # This can be enhanced with more sophisticated clustering
        min_x = min(left_coords) if left_coords else 0
        max_x = max(right_coords) if right_coords else page_width
        
        columns = [{
            "x_start": min_x,
            "x_end": max_x,
            "width": max_x - min_x
        }]
        
        return columns
    
    def _cluster_coordinates(self, coordinates: List[float], tolerance: float = 5.0) -> List[float]:
        """Cluster similar coordinates together."""
        if not coordinates:
            return []
        
        sorted_coords = sorted(set(coordinates))
        clusters = []
        current_cluster = [sorted_coords[0]]
        
        for coord in sorted_coords[1:]:
            if coord - current_cluster[-1] <= tolerance:
                current_cluster.append(coord)
            else:
                clusters.append(sum(current_cluster) / len(current_cluster))
                current_cluster = [coord]
        
        clusters.append(sum(current_cluster) / len(current_cluster))
        return clusters
    
    def _calculate_margins(
        self,
        elements: List[LayoutElement],
        page_width: float,
        page_height: float
    ) -> Dict[str, float]:
        """Calculate page margins based on content positioning."""
        if not elements:
            return {"top": 72, "bottom": 72, "left": 72, "right": 72}  # Default 1 inch
        
        # Find content boundaries
        min_x = min(elem.bbox[0] for elem in elements)
        max_x = max(elem.bbox[2] for elem in elements)
        min_y = min(elem.bbox[1] for elem in elements)
        max_y = max(elem.bbox[3] for elem in elements)
        
        margins = {
            "top": max(0, min_y),
            "bottom": max(0, page_height - max_y),
            "left": max(0, min_x),
            "right": max(0, page_width - max_x)
        }
        
        return margins
    
    def _separate_headers_footers(
        self,
        elements: List[LayoutElement],
        page_height: float
    ) -> Tuple[List[LayoutElement], List[LayoutElement]]:
        """Separate header and footer elements from main content."""
        header_threshold = page_height * 0.15  # Top 15%
        footer_threshold = page_height * 0.85  # Bottom 15%
        
        headers = []
        footers = []
        main_elements = []
        
        for element in elements:
            y_center = (element.bbox[1] + element.bbox[3]) / 2
            
            if y_center < header_threshold:
                headers.append(element)
            elif y_center > footer_threshold:
                footers.append(element)
            else:
                main_elements.append(element)
        
        # Update main elements list (removing headers/footers)
        elements[:] = main_elements
        
        return headers, footers
    
    def _extract_global_styles(self, text_blocks: List) -> Dict[str, Any]:
        """Extract global document styles."""
        if not text_blocks:
            return {}
        
        # Analyze font usage
        font_usage = defaultdict(int)
        font_sizes = defaultdict(int)
        
        for tb in text_blocks:
            font_usage[tb.font_name] += len(tb.text)
            font_sizes[tb.font_size] += len(tb.text)
        
        # Find most common font and size
        default_font = max(font_usage.items(), key=lambda x: x[1])[0] if font_usage else "Arial"
        default_size = max(font_sizes.items(), key=lambda x: x[1])[0] if font_sizes else 12
        
        global_styles = {
            "default_font": default_font,
            "default_font_size": default_size,
            "font_usage": dict(font_usage),
            "size_usage": dict(font_sizes)
        }
        
        return global_styles
    
    def _create_font_mapping(self) -> Dict[str, str]:
        """Create mapping from PDF fonts to Word-compatible fonts."""
        return {
            # Common PDF fonts to Word fonts
            "Arial": "Arial",
            "ArialMT": "Arial",
            "Arial-Bold": "Arial",
            "Arial-Italic": "Arial",
            "Arial-BoldItalic": "Arial",
            "Helvetica": "Arial",
            "Helvetica-Bold": "Arial",
            "Times-Roman": "Times New Roman",
            "Times-Bold": "Times New Roman",
            "Times-Italic": "Times New Roman",
            "Times-BoldItalic": "Times New Roman",
            "TimesNewRomanPSMT": "Times New Roman",
            "Courier": "Courier New",
            "Courier-Bold": "Courier New",
            "Courier-Oblique": "Courier New",
            "Symbol": "Symbol",
            "ZapfDingbats": "Wingdings"
        }
    
    def get_reading_order(self, page_layout: PageLayout) -> List[LayoutElement]:
        """
        Determine the reading order of elements on a page.
        
        Args:
            page_layout: PageLayout object
            
        Returns:
            List of LayoutElement objects in reading order
        """
        elements = page_layout.elements.copy()
        
        # Sort by reading order (top to bottom, left to right)
        # Use center points for more accurate ordering
        elements.sort(key=lambda e: (
            (e.bbox[1] + e.bbox[3]) / 2,  # y-center
            (e.bbox[0] + e.bbox[2]) / 2   # x-center
        ))
        
        return elements
    
    def merge_overlapping_elements(self, elements: List[LayoutElement]) -> List[LayoutElement]:
        """Merge elements that overlap significantly."""
        if len(elements) <= 1:
            return elements
        
        merged = []
        skip_indices = set()
        
        for i, elem1 in enumerate(elements):
            if i in skip_indices:
                continue
            
            merged_elem = elem1
            
            for j, elem2 in enumerate(elements[i+1:], i+1):
                if j in skip_indices:
                    continue
                
                # Check if elements overlap significantly
                if self._elements_overlap(elem1, elem2, threshold=0.7):
                    # Merge elements (prefer text over images)
                    if elem1.element_type == 'text' or elem2.element_type == 'image':
                        merged_elem = elem1
                    else:
                        merged_elem = elem2
                    skip_indices.add(j)
            
            merged.append(merged_elem)
        
        return merged
    
    def _elements_overlap(self, elem1: LayoutElement, elem2: LayoutElement, threshold: float = 0.5) -> bool:
        """Check if two elements overlap significantly."""
        box1 = elem1.bbox
        box2 = elem2.bbox
        
        # Calculate intersection
        x_overlap = max(0, min(box1[2], box2[2]) - max(box1[0], box2[0]))
        y_overlap = max(0, min(box1[3], box2[3]) - max(box1[1], box2[1]))
        
        if x_overlap == 0 or y_overlap == 0:
            return False
        
        intersection_area = x_overlap * y_overlap
        
        # Calculate areas
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        # Calculate overlap ratio
        overlap_ratio = intersection_area / min(area1, area2)
        
        return overlap_ratio > threshold
