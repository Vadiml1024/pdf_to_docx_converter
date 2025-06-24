#!/usr/bin/env python3
"""
Setup script for PDF to DOCX Converter
Handles installation and configuration of the project.
"""

import sys
import subprocess
import os
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    return True


def install_requirements():
    """Install Python dependencies from requirements.txt."""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install Python dependencies: {e}")
        return False


def check_tesseract():
    """Check if Tesseract OCR is installed."""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Tesseract OCR found: {result.stdout.splitlines()[0]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Tesseract OCR not found")
        return False


def install_tesseract():
    """Provide instructions for installing Tesseract OCR."""
    system = platform.system().lower()
    
    print("\nTesseract OCR Installation Instructions:")
    print("=" * 50)
    
    if system == "windows":
        print("Windows:")
        print("1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Run the installer")
        print("3. Add Tesseract to your PATH environment variable")
        print("   Default location: C:\\Program Files\\Tesseract-OCR")
    
    elif system == "darwin":  # macOS
        print("macOS:")
        print("1. Install Homebrew if not already installed:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        print("2. Install Tesseract:")
        print("   brew install tesseract")
        print("3. Install additional languages (optional):")
        print("   brew install tesseract-lang")
    
    elif system == "linux":
        print("Linux (Ubuntu/Debian):")
        print("1. Update package list:")
        print("   sudo apt update")
        print("2. Install Tesseract:")
        print("   sudo apt install tesseract-ocr")
        print("3. Install additional languages (optional):")
        print("   sudo apt install tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-spa")
        print("")
        print("Linux (CentOS/RHEL/Fedora):")
        print("1. Install Tesseract:")
        print("   sudo yum install tesseract  # CentOS/RHEL")
        print("   sudo dnf install tesseract  # Fedora")
    
    print("\nAfter installation, restart your terminal and run this setup script again.")


def create_output_directory():
    """Create default output directory."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Output directory created: {output_dir.absolute()}")


def test_installation():
    """Test the installation by importing key modules."""
    print("\nTesting installation...")
    
    try:
        import fitz
        print("✓ PyMuPDF (fitz) imported successfully")
    except ImportError:
        print("✗ PyMuPDF (fitz) import failed")
        return False
    
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✓ pytesseract and Tesseract connection successful")
    except ImportError:
        print("✗ pytesseract import failed")
        return False
    except Exception as e:
        print(f"✗ Tesseract connection failed: {e}")
        return False
    
    try:
        import docx
        print("✓ python-docx imported successfully")
    except ImportError:
        print("✗ python-docx import failed")
        return False
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError:
        print("✗ OpenCV import failed")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow imported successfully")
    except ImportError:
        print("✗ Pillow import failed")
        return False
    
    print("✓ All core dependencies are working")
    return True


def create_sample_script():
    """Create a sample usage script."""
    sample_script = '''#!/usr/bin/env python3
"""
Sample usage script for PDF to DOCX Converter
"""

import sys
from pathlib import Path

# Add the project directory to the path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from main import main

if __name__ == "__main__":
    # Example usage
    print("PDF to DOCX Converter - Sample Usage")
    print("=" * 40)
    print()
    print("Command line examples:")
    print("python main.py document.pdf")
    print("python main.py *.pdf -o output_folder")
    print("python main.py document.pdf --language fra --high-quality")
    print()
    print("For full help, run: python main.py --help")
'''
    
    script_path = Path("sample_usage.py")
    script_path.write_text(sample_script)
    print(f"✓ Sample usage script created: {script_path.absolute()}")


def main():
    """Main setup function."""
    print("PDF to DOCX Converter - Setup Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_requirements():
        print("Please fix the dependency installation issues and try again.")
        sys.exit(1)
    
    # Check Tesseract installation
    if not check_tesseract():
        install_tesseract()
        print("\nPlease install Tesseract OCR and run this setup script again.")
        sys.exit(1)
    
    # Create output directory
    create_output_directory()
    
    # Test installation
    if not test_installation():
        print("Installation test failed. Please check the error messages above.")
        sys.exit(1)
    
    # Create sample script
    create_sample_script()
    
    print("\n" + "=" * 50)
    print("✓ Setup completed successfully!")
    print("=" * 50)
    print("\nYou can now use the PDF to DOCX converter:")
    print("python main.py your_document.pdf")
    print("\nFor help and options:")
    print("python main.py --help")
    print("\nFor sample usage:")
    print("python sample_usage.py")


if __name__ == "__main__":
    main()
