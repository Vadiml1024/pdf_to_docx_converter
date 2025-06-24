# PDF to DOCX Converter

A powerful Python tool that converts PDF files to Microsoft Word DOCX format while preserving layout, styling, and performing OCR on embedded images.

## Features

- **Layout Preservation**: Maintains original document structure, fonts, and formatting
- **OCR Integration**: Extracts text from images using Tesseract OCR with preprocessing
- **Multi-language Support**: Supports 15+ languages for OCR processing
- **Batch Processing**: Convert multiple PDF files simultaneously
- **Flexible Output**: Customizable output directory and file naming
- **Quality Control**: Configurable confidence thresholds and quality settings
- **Command-line Interface**: Easy-to-use CLI with comprehensive options

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR Engine**
   - Windows: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Ubuntu/Debian: `sudo apt install tesseract-ocr`

### Install Dependencies

```bash
# Clone or download the project
cd pdf_to_docx_converter

# Install Python dependencies
pip install -r requirements.txt
```

### Additional OCR Languages (Optional)

```bash
# Install additional Tesseract language packs
# Ubuntu/Debian example:
sudo apt install tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-spa

# macOS example:
brew install tesseract-lang
```

## Quick Start

### Basic Usage

```bash
# Convert a single PDF
python main.py document.pdf

# Convert multiple PDFs
python main.py file1.pdf file2.pdf file3.pdf

# Specify output directory
python main.py document.pdf -o /path/to/output
```

### Advanced Usage

```bash
# Convert with French OCR
python main.py document.pdf --language fra

# High quality conversion (slower but better)
python main.py document.pdf --high-quality

# Fast conversion (faster but lower quality)
python main.py document.pdf --fast

# Disable OCR completely
python main.py document.pdf --no-ocr

# Verbose output with custom confidence threshold
python main.py document.pdf -v --ocr-confidence 40
```

## Command Line Options

### Input/Output
- `pdf_files`: PDF files to convert (required)
- `-o, --output DIR`: Output directory (default: ./output)
- `--suffix STR`: Add suffix to output filenames

### OCR Options
- `--no-ocr`: Disable OCR processing
- `--language LANG`: OCR language code (default: eng)
- `--ocr-confidence FLOAT`: Minimum confidence threshold (0-100)

### Quality Options
- `--high-quality`: Use high-quality processing
- `--fast`: Use fast processing
- `--dpi INT`: DPI for image processing (default: 300)

### Layout Options
- `--preserve-layout`: Attempt exact layout preservation
- `--merge-columns`: Merge multi-column layouts

### Logging
- `-v, --verbose`: Enable verbose logging
- `--debug`: Enable debug mode
- `--log-file FILE`: Write logs to file

## Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| eng | English | fra | French |
| deu | German | spa | Spanish |
| ita | Italian | por | Portuguese |
| rus | Russian | nld | Dutch |
| pol | Polish | jpn | Japanese |
| chi_sim | Chinese (Simplified) | chi_tra | Chinese (Traditional) |
| kor | Korean | ara | Arabic |
| heb | Hebrew | hin | Hindi |

For multiple languages: `--language eng+fra`

## Project Structure

```
pdf_to_docx_converter/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── PROGRESS.md            # Development progress
├── src/                   # Source code
│   ├── pdf_analyzer.py    # PDF parsing and analysis
│   ├── ocr_processor.py   # OCR processing
│   ├── layout_engine.py   # Layout reconstruction
│   ├── docx_builder.py    # DOCX document creation
│   └── cli.py             # Command-line interface
├── config/                # Configuration files
│   ├── font_mappings.json # Font mapping rules
│   └── ocr_languages.json # OCR language settings
└── tests/                 # Test files
```

## How It Works

1. **PDF Analysis**: Extracts text blocks, images, and layout information
2. **OCR Processing**: Processes images with text using Tesseract OCR
3. **Layout Reconstruction**: Combines text and OCR results while preserving structure
4. **DOCX Generation**: Creates Word document with original formatting

## Configuration

### Font Mapping
Edit `config/font_mappings.json` to customize PDF-to-Word font mappings.

### OCR Settings
Modify `config/ocr_languages.json` to adjust OCR parameters and language settings.

## Performance Tips

- Use `--fast` for quick conversions of simple documents
- Use `--high-quality` for complex layouts or poor quality scans
- Adjust `--ocr-confidence` based on image quality (lower for poor scans)
- Use `--no-ocr` if PDFs contain no images with text

## Troubleshooting

### Common Issues

1. **"Tesseract not found"**
   - Ensure Tesseract is installed and in PATH
   - On Windows, add Tesseract installation directory to PATH

2. **Poor OCR results**
   - Try `--high-quality` option
   - Lower `--ocr-confidence` threshold
   - Check if correct language is specified

3. **Layout issues**
   - Use `--preserve-layout` for complex documents
   - Try `--merge-columns` for multi-column layouts

4. **Memory issues with large files**
   - Process files individually
   - Use `--fast` option
   - Ensure sufficient available memory

### Debug Mode

Enable detailed logging to troubleshoot issues:

```bash
python main.py document.pdf --debug --log-file debug.log
```

## Development

### Requirements for Development
- Python 3.8+
- All dependencies from requirements.txt
- pytest for testing

### Running Tests
```bash
pytest tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. See individual library licenses for dependencies.

## Dependencies

- **PyMuPDF**: PDF processing and analysis
- **pytesseract**: OCR text extraction
- **python-docx**: Word document generation
- **OpenCV**: Image preprocessing
- **Pillow**: Image manipulation

## Limitations

- Complex table structures may not convert perfectly
- Handwritten text OCR accuracy varies
- Some advanced PDF features (forms, annotations) are not preserved
- Font availability may affect output appearance

## Support

For issues and questions:
1. Check this README and troubleshooting section
2. Review the debug logs
3. Check if all dependencies are properly installed
4. Verify Tesseract is correctly configured

## Version History

- **v1.0.0**: Initial release with core functionality
  - PDF parsing and text extraction
  - OCR processing with Tesseract
  - Layout reconstruction
  - DOCX generation with formatting preservation
