# PDF to DOCX Converter - Quick Start Guide

## 🚀 Quick Installation & Usage

### Step 1: Install Dependencies
```bash
# Run the setup script
python setup.py
```

### Step 2: Basic Usage
```bash
# Convert a single PDF
python main.py document.pdf

# Convert multiple PDFs
python main.py file1.pdf file2.pdf file3.pdf

# Convert with custom output directory
python main.py document.pdf -o /path/to/output
```

### Step 3: Advanced Usage
```bash
# High quality conversion with French OCR
python main.py document.pdf --language fra --high-quality

# Fast conversion without OCR
python main.py document.pdf --fast --no-ocr

# Batch conversion with verbose output
python main.py *.pdf -v --ocr-confidence 40
```

## 📋 Prerequisites
- Python 3.8+
- Tesseract OCR engine

## 🔧 Installation Steps

### 1. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # For additional languages
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-fra tesseract-ocr-deu  # Additional languages
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Test Installation
```bash
python setup.py
```

## 📖 Common Use Cases

### Convert Academic Papers
```bash
python main.py research_paper.pdf --high-quality --language eng
```

### Convert Foreign Language Documents
```bash
python main.py document_francais.pdf --language fra
python main.py documento_espanol.pdf --language spa
python main.py dokument_deutsch.pdf --language deu
```

### Batch Convert Scanned Documents
```bash
python main.py scanned_*.pdf --high-quality --ocr-confidence 25 -v
```

### Quick Convert Without OCR
```bash
python main.py text_only.pdf --no-ocr --fast
```

## 🎯 Quality Settings

- `--fast`: Quick conversion, lower quality
- `--high-quality`: Best results, slower processing
- `--ocr-confidence 30`: Adjust OCR sensitivity (0-100)

## 🌍 Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| eng | English | fra | French |
| deu | German | spa | Spanish |
| ita | Italian | por | Portuguese |
| rus | Russian | jpn | Japanese |
| chi_sim | Chinese (Simplified) | ara | Arabic |

## ❓ Troubleshooting

**"Tesseract not found"**
- Ensure Tesseract is installed and in PATH
- Restart terminal after installation

**Poor OCR results**
- Use `--high-quality` option
- Lower `--ocr-confidence` threshold
- Verify correct language setting

**Memory issues**
- Process files individually
- Use `--fast` option

## 📞 Getting Help
```bash
python main.py --help  # Full option list
python setup.py        # Check installation
```

## 🎉 You're Ready!
Start converting your PDF files to editable Word documents while preserving their original layout and formatting!
