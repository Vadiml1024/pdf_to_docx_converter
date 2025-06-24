#!/usr/bin/env python3
"""
Test runner script for PDF to DOCX Converter
Ensures proper Python path setup and runs pytest with correct configuration.
"""

import sys
import os
from pathlib import Path
import subprocess

def main():
    """Main test runner function."""
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Set PYTHONPATH environment variable
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if current_pythonpath:
        new_pythonpath = f"{project_root}:{current_pythonpath}"
    else:
        new_pythonpath = str(project_root)
    
    os.environ['PYTHONPATH'] = new_pythonpath
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Construct pytest command
    pytest_args = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--strict-markers'
    ]
    
    # Add any additional arguments passed to this script
    if len(sys.argv) > 1:
        pytest_args.extend(sys.argv[1:])
    
    print(f"Running tests from: {project_root}")
    print(f"PYTHONPATH: {new_pythonpath}")
    print(f"Command: {' '.join(pytest_args)}")
    print("=" * 60)
    
    # Run pytest
    try:
        result = subprocess.run(pytest_args, check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
