"""
Command Line Interface Module
Handles command-line argument parsing and user interaction.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    
    parser = argparse.ArgumentParser(
        prog='pdf-to-docx',
        description='Convert PDF files to DOCX format with layout preservation and OCR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s document.pdf                    # Convert single PDF
  %(prog)s *.pdf                          # Convert all PDFs in directory
  %(prog)s file1.pdf file2.pdf -o output  # Convert multiple files to output directory
  %(prog)s document.pdf --no-ocr          # Convert without OCR processing
  %(prog)s document.pdf --language fra    # Use French OCR language
        '''
    )
    
    # Input files
    parser.add_argument(
        'pdf_files',
        nargs='+',
        metavar='FILE',
        help='PDF files to convert'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '-o', '--output',
        type=str,
        default='./output',
        metavar='DIR',
        help='Output directory for DOCX files (default: ./output)'
    )
    
    output_group.add_argument(
        '--suffix',
        type=str,
        default='',
        metavar='STR',
        help='Add suffix to output filenames'
    )
    
    # OCR options
    ocr_group = parser.add_argument_group('OCR Options')
    ocr_group.add_argument(
        '--no-ocr',
        action='store_true',
        help='Disable OCR processing of images'
    )
    
    ocr_group.add_argument(
        '--language',
        type=str,
        default='eng',
        metavar='LANG',
        help='OCR language code (default: eng). Common: eng, fra, deu, spa, rus'
    )
    
    ocr_group.add_argument(
        '--ocr-confidence',
        type=float,
        default=30.0,
        metavar='FLOAT',
        help='Minimum OCR confidence threshold (0-100, default: 30.0)'
    )
    
    # Processing options
    process_group = parser.add_argument_group('Processing Options')
    process_group.add_argument(
        '--dpi',
        type=int,
        default=300,
        metavar='INT',
        help='DPI for image processing (default: 300)'
    )
    
    process_group.add_argument(
        '--preserve-layout',
        action='store_true',
        help='Attempt to preserve exact layout positioning (experimental)'
    )
    
    process_group.add_argument(
        '--merge-columns',
        action='store_true',
        help='Merge multi-column layouts into single column'
    )
    
    # Logging and debugging
    debug_group = parser.add_argument_group('Logging Options')
    debug_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    debug_group.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with detailed logging'
    )
    
    debug_group.add_argument(
        '--log-file',
        type=str,
        metavar='FILE',
        help='Write logs to specified file'
    )
    
    # Performance options
    perf_group = parser.add_argument_group('Performance Options')
    perf_group.add_argument(
        '--threads',
        type=int,
        default=1,
        metavar='INT',
        help='Number of processing threads (default: 1)'
    )
    
    perf_group.add_argument(
        '--memory-limit',
        type=str,
        metavar='SIZE',
        help='Memory limit (e.g., 1GB, 512MB)'
    )
    
    # Quality options
    quality_group = parser.add_argument_group('Quality Options')
    quality_group.add_argument(
        '--high-quality',
        action='store_true',
        help='Use high-quality processing (slower but better results)'
    )
    
    quality_group.add_argument(
        '--fast',
        action='store_true',
        help='Use fast processing (faster but lower quality)'
    )
    
    # Version
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def validate_arguments(args) -> bool:
    """
    Validate command-line arguments.
    
    Args:
        args: Parsed arguments from argparse
        
    Returns:
        True if valid, False otherwise
    """
    errors = []
    
    # Validate PDF files
    valid_files = 0
    for file_path in args.pdf_files:
        path = Path(file_path)
        if not path.exists():
            errors.append(f"File not found: {file_path}")
        elif not path.is_file():
            errors.append(f"Not a file: {file_path}")
        elif path.suffix.lower() != '.pdf':
            errors.append(f"Not a PDF file: {file_path}")
        else:
            valid_files += 1
    
    if valid_files == 0:
        errors.append("No valid PDF files provided")
    
    # Validate output directory
    if args.output:
        output_path = Path(args.output)
        if output_path.exists() and not output_path.is_dir():
            errors.append(f"Output path exists but is not a directory: {args.output}")
    
    # Validate OCR confidence
    if not (0 <= args.ocr_confidence <= 100):
        errors.append("OCR confidence must be between 0 and 100")
    
    # Validate DPI
    if args.dpi < 72 or args.dpi > 600:
        errors.append("DPI must be between 72 and 600")
    
    # Validate threads
    if args.threads < 1 or args.threads > 16:
        errors.append("Number of threads must be between 1 and 16")
    
    # Check for conflicting options
    if args.fast and args.high_quality:
        errors.append("Cannot use both --fast and --high-quality options")
    
    # Print errors
    if errors:
        print("Error: Invalid arguments:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return False
    
    return True


def setup_logging_from_args(args) -> None:
    """Set up logging based on command-line arguments."""
    
    # Determine log level
    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler if specified
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True
    )
    
    # Suppress verbose logs from dependencies unless in debug mode
    if not args.debug:
        logging.getLogger('PIL').setLevel(logging.WARNING)
        logging.getLogger('matplotlib').setLevel(logging.WARNING)
        logging.getLogger('fitz').setLevel(logging.WARNING)


def print_summary(args, results: dict) -> None:
    """Print conversion summary."""
    
    total_files = len(args.pdf_files)
    successful = results.get('successful', 0)
    failed = results.get('failed', 0)
    
    print(f"\nConversion Summary:")
    print(f"  Total files: {total_files}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    
    if results.get('failed_files'):
        print(f"\nFailed files:")
        for file_path, error in results['failed_files']:
            print(f"  - {file_path}: {error}")
    
    if successful > 0:
        print(f"\nOutput directory: {args.output}")


def get_language_help() -> str:
    """Return help text for OCR language codes."""
    return """
Supported OCR language codes:
  eng - English
  fra - French  
  deu - German
  spa - Spanish
  rus - Russian
  ita - Italian
  por - Portuguese
  nld - Dutch
  pol - Polish
  jpn - Japanese
  chi_sim - Chinese Simplified
  chi_tra - Chinese Traditional
  kor - Korean
  ara - Arabic
  hin - Hindi
  
For multiple languages, use '+' separator: eng+fra
For complete list, run: tesseract --list-langs
"""


def check_dependencies() -> List[str]:
    """Check if required dependencies are available."""
    missing = []
    
    try:
        import fitz
    except ImportError:
        missing.append("PyMuPDF (install with: pip install PyMuPDF)")
    
    try:
        import pytesseract
        # Try to get version to check if Tesseract is installed
        pytesseract.get_tesseract_version()
    except ImportError:
        missing.append("pytesseract (install with: pip install pytesseract)")
    except Exception:
        missing.append("Tesseract OCR engine (install from: https://github.com/UB-Mannheim/tesseract/wiki)")
    
    try:
        import docx
    except ImportError:
        missing.append("python-docx (install with: pip install python-docx)")
    
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python (install with: pip install opencv-python)")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow (install with: pip install Pillow)")
    
    return missing
