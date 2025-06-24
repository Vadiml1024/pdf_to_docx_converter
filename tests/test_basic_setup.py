"""
Simple test to verify test setup is working.
"""

import sys
import os
from pathlib import Path
import pytest

def test_python_path_setup():
    """Test that Python path is set up correctly."""
    project_root = Path(__file__).parent.parent
    assert str(project_root) in sys.path or str(project_root) in os.environ.get('PYTHONPATH', '')

def test_src_module_import():
    """Test that we can import from src module."""
    try:
        import src
        assert src is not None
    except ImportError as e:
        pytest.fail(f"Cannot import src module: {e}")

def test_main_modules_import():
    """Test that main modules can be imported."""
    try:
        from src import pdf_analyzer, ocr_processor, layout_engine, docx_builder
        assert pdf_analyzer is not None
        assert ocr_processor is not None
        assert layout_engine is not None
        assert docx_builder is not None
    except ImportError as e:
        pytest.fail(f"Cannot import main modules: {e}")

def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    # Simple test that doesn't require external libraries
    assert 1 + 1 == 2
    assert "pdf" in "pdf-to-docx-converter"
    
def test_project_structure():
    """Test that project structure is correct."""
    project_root = Path(__file__).parent.parent
    
    # Check that main files exist
    assert (project_root / "main.py").exists()
    assert (project_root / "requirements.txt").exists()
    assert (project_root / "README.md").exists()
    assert (project_root / "src").is_dir()
    assert (project_root / "tests").is_dir()
    
    # Check that src modules exist
    src_dir = project_root / "src"
    assert (src_dir / "__init__.py").exists()
    assert (src_dir / "pdf_analyzer.py").exists()
    assert (src_dir / "ocr_processor.py").exists()
    assert (src_dir / "layout_engine.py").exists()
    assert (src_dir / "docx_builder.py").exists()
    assert (src_dir / "cli.py").exists()

if __name__ == "__main__":
    # Run tests directly if executed as script
    import pytest
    pytest.main([__file__, "-v"])
