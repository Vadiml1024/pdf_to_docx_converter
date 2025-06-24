# Makefile for PDF to DOCX Converter

.PHONY: help install test test-basic test-all clean lint format setup dev-install

# Default target
help:
	@echo "PDF to DOCX Converter - Development Commands"
	@echo "============================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install       Install dependencies"
	@echo "  dev-install   Install in development mode with dev dependencies"
	@echo "  setup         Run full setup (dependencies + Tesseract check)"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test          Run all tests with proper Python path"
	@echo "  test-basic    Run basic setup tests only"
	@echo "  test-all      Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          Run code linting (flake8)"
	@echo "  format        Format code with black"
	@echo "  type-check    Run type checking with mypy"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean         Clean up build artifacts"
	@echo "  run           Run the converter (requires arguments)"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

dev-install:
	pip install -e .[dev]

setup:
	python setup.py

# Testing
test:
	python run_tests.py

test-basic:
	python run_tests.py tests/test_basic_setup.py

test-all:
	python run_tests.py --cov=src --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src tests main.py

format:
	black src tests main.py setup.py run_tests.py

type-check:
	mypy src

# Utility
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

run:
	@if [ -z "$(ARGS)" ]; then \
		echo "Usage: make run ARGS='document.pdf'"; \
		echo "Example: make run ARGS='document.pdf --language fra --high-quality'"; \
	else \
		python main.py $(ARGS); \
	fi

# Git helpers
git-status:
	git status

git-add-all:
	git add .

git-commit:
	@if [ -z "$(MSG)" ]; then \
		echo "Usage: make git-commit MSG='your commit message'"; \
	else \
		git commit -m "$(MSG)"; \
	fi

# Development workflow
dev-check: lint type-check test
	@echo "All development checks passed!"

# Quick test runner without coverage
quick-test:
	PYTHONPATH=. python -m pytest tests/ -v

# Install and test everything
full-setup: install setup test
	@echo "Full setup completed successfully!"
