#!/usr/bin/env python3
"""
PDF to DOCX Converter
Main entry point for the PDF-to-DOCX conversion tool.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

from src.pdf_analyzer import PDFAnalyzer
from src.ocr_processor import OCRProcessor
from src.layout_engine import LayoutEngine
from src.docx_builder import DocxBuilder
from src.cli import create_parser, validate_arguments, setup_logging_from_args, print_summary, check_dependencies


def convert_pdf_to_docx(pdf_path: Path, output_dir: Path, args) -> bool:
    """
    Convert a single PDF file to DOCX format.
    
    Args:
        pdf_path: Path to the input PDF file
        output_dir: Directory for output DOCX file
        args: Command line arguments
    
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        logging.info(f"Starting conversion of {pdf_path}")
        
        # Initialize components
        analyzer = PDFAnalyzer()
        
        ocr_processor = None
        if not args.no_ocr:
            ocr_processor = OCRProcessor(
                language=args.language,
                confidence_threshold=args.ocr_confidence
            )
        
        layout_engine = LayoutEngine()
        docx_builder = DocxBuilder()
        
        # Step 1: Analyze PDF structure
        logging.info("Analyzing PDF structure...")
        pdf_data = analyzer.analyze_pdf(pdf_path)
        
        # Step 2: Extract text and images
        logging.info("Extracting content...")
        text_blocks = analyzer.extract_text_blocks(pdf_data)
        images = analyzer.extract_images(pdf_data)
        
        # Step 3: Process images with OCR if enabled
        ocr_results = []
        if not args.no_ocr and images and ocr_processor:
            logging.info(f"Processing {len(images)} images with OCR...")
            ocr_results = ocr_processor.batch_process_images(images)
        
        # Step 4: Reconstruct layout
        logging.info("Reconstructing layout...")
        layout_data = layout_engine.reconstruct_layout(
            text_blocks, images, ocr_results, pdf_data
        )
        
        # Step 5: Build DOCX document
        logging.info("Building DOCX document...")
        suffix = args.suffix if hasattr(args, 'suffix') and args.suffix else ""
        output_filename = f"{pdf_path.stem}{suffix}.docx"
        output_path = output_dir / output_filename
        docx_builder.create_document(layout_data, output_path)
        
        logging.info(f"Conversion completed: {output_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error converting {pdf_path}: {str(e)}")
        return False


def main():
    """Main application entry point."""
    # Check dependencies first
    missing_deps = check_dependencies()
    if missing_deps:
        print("Error: Missing required dependencies:", file=sys.stderr)
        for dep in missing_deps:
            print(f"  - {dep}", file=sys.stderr)
        sys.exit(1)
    
    # Parse command-line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate arguments
    if not validate_arguments(args):
        sys.exit(1)
    
    # Setup logging
    setup_logging_from_args(args)
    
    # Validate input files
    valid_files = []
    for file_path in args.pdf_files:
        path = Path(file_path)
        if path.exists() and path.suffix.lower() == '.pdf':
            valid_files.append(path)
    
    if not valid_files:
        logging.error("No valid PDF files provided")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each file
    results = {
        'successful': 0,
        'failed': 0,
        'failed_files': []
    }
    
    for pdf_file in valid_files:
        try:
            if convert_pdf_to_docx(pdf_file, output_dir, args):
                results['successful'] += 1
                logging.info(f"Successfully converted: {pdf_file}")
            else:
                results['failed'] += 1
                results['failed_files'].append((str(pdf_file), "Conversion failed"))
        except Exception as e:
            results['failed'] += 1
            results['failed_files'].append((str(pdf_file), str(e)))
            logging.error(f"Error converting {pdf_file}: {str(e)}")
    
    # Print summary
    print_summary(args, results)
    
    if results['successful'] == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
