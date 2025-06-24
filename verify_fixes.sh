#!/bin/bash
# Quick test script to verify fixes
echo "🧪 Running quick tests to verify fixes..."
echo "========================================"

cd /Users/vadim/work/pdf_to_docx_converter

echo "1. Testing basic setup..."
python run_tests.py tests/test_basic_setup.py -v

echo ""
echo "2. Testing specific previously failing tests..."
python run_tests.py tests/test_pdf_analyzer.py::TestPDFAnalyzer::test_analyze_pdf_success -v
python run_tests.py tests/test_pdf_analyzer.py::TestPDFAnalyzer::test_extract_text_blocks -v
python run_tests.py tests/test_pdf_analyzer.py::TestPDFAnalyzer::test_extract_images -v
python run_tests.py tests/test_ocr_processor.py::TestOCRProcessor::test_process_image_success -v

echo ""
echo "3. Running all tests..."
python run_tests.py

echo ""
echo "✅ Test verification complete!"
