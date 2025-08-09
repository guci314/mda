import os
import subprocess

# 验证项目结构
def verify_structure():
    required_dirs = ["app", "app/models", "app/repositories", "app/services", "app/routers"]
    missing_dirs = []
    for dir in required_dirs:
        if not os.path.exists(dir):
            missing_dirs.append(dir)
    if missing_dirs:
        print(f"Missing directories: {missing_dirs}")
        return False
    print("Project structure is valid.")
    return True

# 验证依赖安装
def verify_dependencies():
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install dependencies.")
        return False

# 验证应用启动
def verify_startup():
    try:
        subprocess.check_call(["uvicorn", "main:app", "--reload", "--port", "8001"])
        print("Application started successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Failed to start application.")
        return False

if __name__ == "__main__":
    if verify_structure() and verify_dependencies() and verify_startup():
        print("Project verification passed.")
    else:
        print("Project verification failed.")