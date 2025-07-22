#!/usr/bin/env python
"""Setup script for PIM Engine"""

from setuptools import setup, find_packages

setup(
    name="pim-engine",
    version="0.1.0",
    description="Platform Independent Model Execution Engine",
    author="PIM Engine Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        # Add your dependencies here
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "mypy",
            "black",
            "flake8",
        ]
    }
)