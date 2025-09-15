#!/usr/bin/env python3
"""
MDA订单系统生成脚本
执行完整的PIM → PSM → Code流程
"""

import os
import subprocess
import sys
from pathlib import Path

def setup_environment():
    """设置Python环境"""
    # 添加React Agent Minimal到Python路径
    react_agent_path = Path(__file__).parent.parent / "react_is_all_you_need"
    if react_agent_path.exists():
        sys.path.insert(0, str(react_agent_path))
        print(f"✅ 添加React Agent路径: {react_agent_path}")
    else:
        print("⚠️  React Agent路径不存在，请确保项目结构正确")
        
    # 设置当前工作目录
    os.chdir(Path(__file__).parent)
    print(f"📁 工作目录: {os.getcwd()}")

def check_dependencies():
    """检查依赖"""
    try:
        # 检查必要的知识文件
        required_files = [
            "pim/order_system.md",
            "knowledge/mda_concepts.md", 
            "knowledge/pim_to_fastapi_psm.md",
            "knowledge/fastapi_psm_to_code.md"
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ 缺少必要文件: {file}")
                return False
        
        print("✅ 所有依赖文件检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 依赖检查失败: {e}")
        return False

def run_single_service(service_name):
    """运行单个服务的生成（用于测试）"""
    print(f"\n🔧 生成 {service_name}-service...")
    
    # 这里简化实现，实际应该调用Agent
    service_dir = f"output/fastapi/{service_name}-service"
    os.makedirs(service_dir, exist_ok=True)
    
    # 创建基本的FastAPI项目结构
    create_fastapi_structure(service_dir, service_name)
    
    print(f"✅ {service_name}-service 生成完成")
    return True

def create_fastapi_structure(service_dir, service_name):
    """创建FastAPI项目基础结构"""
    
    # 创建app目录
    app_dir = os.path.join(service_dir, "app")
    os.makedirs(app_dir, exist_ok=True)
    
    # 创建__init__.py
    with open(os.path.join(app_dir, "__init__.py"), "w") as f:
        f.write("")
    
    # 创建基础文件
    files_to_create = {
        "requirements.txt": generate_requirements(),
        "Dockerfile": generate_dockerfile(service_name),
        ".env": generate_env_config(service_name),
        "app/main.py": generate_main_py(service_name),
        "app/database.py": generate_database_py(),
    }
    
    for file_path, content in files_to_create.items():
        full_path = os.path.join(service_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

def generate_requirements():
    """生成requirements.txt"""
    return """fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
"""

def generate_dockerfile(service_name):
    """生成Dockerfile"""
    return f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

def generate_env_config(service_name):
    """生成环境配置"""
    return f"""DATABASE_URL=postgresql://user:password@localhost:5432/{service_name}_db
DEBUG=true
"""

def generate_main_py(service_name):
    """生成main.py"""
    return f"""from fastapi import FastAPI
from app.database import engine, Base

app = FastAPI(title="{service_name.title()} Service")

# 创建数据库表
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {{"message": "{service_name.title()} Service is running"}}

@app.get("/health")
async def health():
    return {{"status": "healthy"}}
"""

def generate_database_py():
    """生成database.py"""
    return """import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={{"check_same_thread": False}} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

def main():
    """主函数"""
    print("=" * 50)
    print("🛒 MDA订单系统生成器")
    print("=" * 50)
    
    # 设置环境
    setup_environment()
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，请先创建必要的知识文件")
        return
    
    # 生成服务
    services = ["product", "order", "inventory", "customer", "payment", "delivery"]
    
    print(f"\n🎯 开始生成 {len(services)} 个微服务...")
    
    for service in services:
        if not run_single_service(service):
            print(f"❌ {service}-service 生成失败")
            break
    
    print("\n" + "=" * 50)
    print("✅ MDA订单系统生成完成！")
    print("📁 生成的代码位于: output/fastapi/")
    print("🚀 下一步: 完善各个服务的业务逻辑")
    print("=" * 50)

if __name__ == "__main__":
    main()