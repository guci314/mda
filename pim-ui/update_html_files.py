#!/usr/bin/env python3
"""Update HTML files to use dynamic API configuration"""

import os
import re

def update_html_file(filepath):
    """Update HTML file to use dynamic API configuration"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add config.js script if not present
    if 'config.js' not in content:
        # Find </head> tag and insert script before it
        content = content.replace(
            '</head>',
            '    <script src="/js/config.js"></script>\n</head>'
        )
    
    # Replace hardcoded API URLs with API_BASE_URL variable
    # Pattern 1: fetch('http://localhost:8000/...')
    content = re.sub(
        r"fetch\(['\"]http://localhost:8000(/[^'\"]*)['\"]",
        r"fetch(API_BASE_URL + '\1'",
        content
    )
    
    # Pattern 2: const API_URL = 'http://localhost:8000'
    content = re.sub(
        r"const\s+API_URL\s*=\s*['\"]http://localhost:8000['\"]",
        "// API_URL is now defined in config.js as API_BASE_URL",
        content
    )
    
    # Pattern 3: Direct usage of API_URL
    content = re.sub(
        r"\$\{API_URL\}",
        "${API_BASE_URL}",
        content
    )
    content = re.sub(
        r"API_URL\s*\+",
        "API_BASE_URL +",
        content
    )
    
    # Write updated content back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated: {filepath}")

def main():
    public_dir = os.path.join(os.path.dirname(__file__), 'public')
    
    # Update all HTML files
    for filename in os.listdir(public_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(public_dir, filename)
            update_html_file(filepath)

if __name__ == "__main__":
    main()