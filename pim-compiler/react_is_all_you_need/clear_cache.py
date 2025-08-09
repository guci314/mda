#!/usr/bin/env python3
"""Clear or manage LangChain cache"""

import os
import sys
import shutil
from pathlib import Path

def main():
    cache_file = Path(__file__).parent / ".langchain.db"
    
    if not cache_file.exists():
        print("Cache file not found.")
        return
    
    # Get file size
    size_mb = cache_file.stat().st_size / (1024 * 1024)
    print(f"Current cache size: {size_mb:.2f} MB")
    
    # Ask for confirmation
    response = input("\nDo you want to clear the cache? (y/n): ")
    
    if response.lower() == 'y':
        # Backup old cache
        backup_path = cache_file.with_suffix('.db.bak')
        if backup_path.exists():
            backup_path.unlink()
        shutil.move(str(cache_file), str(backup_path))
        print(f"Old cache backed up to: {backup_path}")
        print("Cache cleared successfully!")
        print("\nNote: The cache will be recreated on next run.")
    else:
        print("Cache not cleared.")
        
        # Suggest optimization
        if size_mb > 100:
            print("\nTip: Your cache is quite large. Consider:")
            print("1. Clearing it periodically with this script")
            print("2. Disabling cache: export DISABLE_LANGCHAIN_CACHE=true")
            print("3. Using a different cache backend (e.g., Redis)")

if __name__ == "__main__":
    main()