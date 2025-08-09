import os
import sys

# 检查文件是否存在
def check_files():
    required_files = ["main.py", "requirements.txt", "app/database.py"]
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    if missing_files:
        print(f"Missing files: {missing_files}")
        sys.exit(1)
    print("All required files exist.")

if __name__ == "__main__":
    check_files()