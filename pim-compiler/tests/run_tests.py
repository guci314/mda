#!/usr/bin/env python
"""Test runner for PSM generator tests"""

import sys
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Now run the tests
if __name__ == "__main__":
    import pytest
    
    # Run pytest on the test file
    exit_code = pytest.main([
        str(Path(__file__).parent / "test_psm_generator.py"),
        "-v",
        "--tb=short"
    ])
    
    sys.exit(exit_code)