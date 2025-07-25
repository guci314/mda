#!/usr/bin/env python3
"""
演示上下文压缩功能

这个演示展示了 Agent CLI v2 如何在处理大量文件时
自动压缩上下文以保持在 LLM 的上下文窗口限制内。
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_cli.core import LLMConfig
from agent_cli.core_v2_new import AgentCLI_V2


def create_demo_files(base_dir: str):
    """创建演示用的文件"""
    files = {
        "requirements.txt": """fastapi==0.100.0
uvicorn==0.23.0
pydantic==2.0.0
sqlalchemy==2.0.0
pytest==7.4.0
black==23.7.0
ruff==0.0.285
mypy==1.4.1
""",
        "config.yaml": """database:
  host: localhost
  port: 5432
  name: myapp
  user: admin
  
redis:
  host: localhost
  port: 6379
  
api:
  title: My API
  version: 1.0.0
  description: A sample API
  
features:
  authentication: true
  rate_limiting: true
  caching: true
  monitoring: true
""" * 50,  # 重复内容使文件更大
        
        "src/models.py": """from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    posts = relationship('Post', back_populates='author')
    
class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String(5000))
    author_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship('User', back_populates='posts')
""" * 30,  # 重复内容

        "src/api.py": """from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="My API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to My API"}
    
@app.get("/users")
def list_users(skip: int = 0, limit: int = 100):
    # Implementation here
    pass
    
@app.post("/users")
def create_user(user: UserCreate):
    # Implementation here
    pass
    
@app.get("/posts")
def list_posts(skip: int = 0, limit: int = 100):
    # Implementation here
    pass
""" * 25,

        "tests/test_models.py": """import pytest
from src.models import User, Post
from datetime import datetime

def test_user_creation():
    user = User(username="testuser", email="test@example.com")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    
def test_post_creation():
    post = Post(title="Test Post", content="Test content")
    assert post.title == "Test Post"
    assert post.content == "Test content"
""" * 20,

        "README.md": """# My Application

This is a demonstration application showing context compression.

## Features
- User management
- Post creation and management
- RESTful API
- Database integration

## Installation
1. Install dependencies: pip install -r requirements.txt
2. Run migrations: alembic upgrade head
3. Start server: uvicorn src.api:app --reload

## Usage
Visit http://localhost:8000/docs for API documentation.
""" * 10
    }
    
    # 创建文件
    for path, content in files.items():
        full_path = os.path.join(base_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
            
    return list(files.keys())


def run_compression_demo():
    """运行压缩演示"""
    print("=== Agent CLI v2 上下文压缩演示 ===\n")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        print("1. 创建演示项目文件...")
        files = create_demo_files(tmpdir)
        print(f"   ✓ 创建了 {len(files)} 个文件\n")
        
        # 配置 Agent CLI
        print("2. 初始化 Agent CLI v2...")
        llm_config = LLMConfig.from_env("deepseek")
        
        agent = AgentCLI_V2(
            llm_config=llm_config,
            enable_context_compression=True,
            context_size_limit=20 * 1024,  # 20KB 触发压缩
            recent_file_window=3,  # 保护最近3个文件
            max_actions_per_step=10
        )
        print("   ✓ 压缩功能已启用")
        print(f"   ✓ 上下文限制: 20 KB")
        print(f"   ✓ 保护最近: 3 个文件\n")
        
        # 定义任务
        task = f"""分析 {tmpdir} 目录下的项目结构，理解代码架构，
找出所有的模型定义和API端点，并生成一个项目分析报告。"""
        
        print("3. 执行任务...")
        print(f"   任务: {task}\n")
        
        # 手动模拟文件读取来展示压缩过程
        print("4. 模拟读取项目文件...\n")
        
        from agent_cli.core_v2_new import Action
        
        for i, file_path in enumerate(files):
            full_path = os.path.join(tmpdir, file_path)
            
            # 读取文件内容
            with open(full_path, "r") as f:
                content = f.read()
            
            # 创建动作
            action = Action(
                tool_name="read_file",
                description=f"读取 {file_path}",
                params={"path": full_path},
                result=content,
                success=True
            )
            
            # 更新上下文
            print(f"   [{i+1}/{len(files)}] 读取 {file_path}")
            agent._update_context_from_action(action)
            
            # 显示上下文大小
            size = agent.get_context_size()
            print(f"        上下文大小: {size:,} bytes ({size/1024:.1f} KB)")
            
            # 检查是否需要压缩
            if agent.context_compressor and agent.context_compressor.should_compress(agent.context):
                print(f"        ⚠️  上下文超过限制！")
                print(f"        正在压缩...")
                
                # 创建模拟的步骤计划
                from agent_cli.core_v2_new import Step, StepStatus
                steps = [
                    Step(
                        name="分析项目结构",
                        description="读取并分析所有项目文件",
                        expected_output="项目结构和组件列表",
                        status=StepStatus.IN_PROGRESS
                    )
                ]
                
                # 执行压缩
                original_size = size
                agent.context = agent.context_compressor.compress_with_attention(
                    agent.context,
                    task=task,
                    step_plan=steps,
                    current_step=steps[0],
                    current_action=f"读取 {file_path}"
                )
                
                new_size = agent.get_context_size()
                compression_ratio = (1 - new_size/original_size) * 100
                
                print(f"        ✓ 压缩完成!")
                print(f"        压缩前: {original_size:,} bytes")
                print(f"        压缩后: {new_size:,} bytes")
                print(f"        节省: {compression_ratio:.1f}%")
                
                # 显示哪些文件被保护
                if "file_contents" in agent.context:
                    protected_files = sorted(
                        agent.context["file_contents"].items(),
                        key=lambda x: x[1].get("timestamp", 0),
                        reverse=True
                    )[:agent.recent_file_window]
                    
                    print(f"        受保护的最近文件:")
                    for path, _ in protected_files:
                        print(f"          - {os.path.basename(path)}")
                
                print()
            
            # 添加小延迟使演示更清晰
            time.sleep(0.5)
        
        print("\n5. 生成分析报告...")
        
        # 显示最终统计
        print("\n6. 最终统计:")
        print(f"   - 读取文件数: {len(files)}")
        print(f"   - 最终上下文大小: {agent.get_context_size():,} bytes")
        
        stats = agent.get_compression_stats()
        if stats:
            print(f"   - 压缩节省空间: {stats['space_saved_percentage']:.1f}%")
        
        if "file_contents" in agent.context:
            print(f"   - 保留的文件数: {len(agent.context['file_contents'])}")
        
        print("\n✅ 演示完成!")
        print("\n关键要点:")
        print("1. Agent CLI v2 自动管理上下文大小")
        print("2. 超过限制时使用 LLM 智能压缩")
        print("3. 最近访问的文件受到保护")
        print("4. 压缩考虑任务目标和执行计划")
        print("5. 确保后续步骤所需信息不丢失")


def show_compression_benefits():
    """展示压缩的好处"""
    print("\n\n=== 上下文压缩的好处 ===\n")
    
    benefits = [
        ("更大的工作集", "可以处理更多文件而不超过 LLM 限制"),
        ("智能保留", "根据任务需求保留关键信息"),
        ("性能优化", "减少 token 使用，降低 API 成本"),
        ("连续性保证", "压缩后任务仍能正常执行"),
        ("自动化管理", "无需手动清理上下文")
    ]
    
    for title, desc in benefits:
        print(f"✓ {title}")
        print(f"  {desc}\n")


if __name__ == "__main__":
    try:
        # 运行演示
        run_compression_demo()
        show_compression_benefits()
        
    except KeyboardInterrupt:
        print("\n\n演示被中断")
    except Exception as e:
        print(f"\n\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()