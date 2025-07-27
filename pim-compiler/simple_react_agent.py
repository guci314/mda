#!/usr/bin/env python3
"""使用DeepSeek API模拟React Agent行为"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 全局输出目录
output_dir = Path("output/react_agent_enhanced_v2")

def call_deepseek(prompt: str, system_prompt: str = None) -> str:
    """调用DeepSeek API"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7
    }
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=180
    )
    
    if response.status_code != 200:
        raise Exception(f"API call failed: {response.text}")
    
    return response.json()["choices"][0]["message"]["content"]

def generate_psm(pim_content: str) -> str:
    """生成PSM"""
    prompt = f"""你是一个专业的软件架构师，负责生成 PSM（Platform Specific Model）。

目标平台: FastAPI

请根据以下PIM生成详细的PSM文档：

{pim_content}

要求：
1. 包含详细的数据模型定义（字段类型、约束等）
2. API端点设计（RESTful）  
3. 服务层方法定义
4. 认证和权限控制
5. 数据库设计

请使用Markdown格式输出。"""

    return call_deepseek(prompt)

def simulate_react_agent(psm_content: str):
    """模拟React Agent生成代码"""
    
    # 系统提示词
    system_prompt = """你是一个专业的 FastAPI 开发专家。

你的任务是根据 PSM（Platform Specific Model）生成完整的 FastAPI 应用代码。

你可以使用以下工具：
- write_file(file_path, content): 写入文件
- create_directory(directory_path): 创建目录
- list_directory(directory_path): 列出目录内容

请按照以下格式输出你的操作：
ACTION: tool_name
ARGS: {
  "arg1": "value1",
  "arg2": "value2"
}

每次只能执行一个操作。"""

    # 第一步：让Agent规划项目结构
    plan_prompt = f"""请根据以下PSM规划FastAPI项目的目录结构和文件列表：

{psm_content}

请列出需要创建的所有目录和文件。"""

    print("\n🤖 ReactAgent: Planning project structure...")
    plan = call_deepseek(plan_prompt, system_prompt)
    print(plan[:500] + "..." if len(plan) > 500 else plan)
    
    # 创建基本项目结构
    print("\n🤖 ReactAgent: Creating project structure...")
    
    # 创建目录
    directories = [
        "app",
        "app/api",
        "app/api/endpoints",
        "app/core",
        "app/db",
        "app/models",
        "app/schemas",
        "app/services",
        "app/crud",
        "tests"
    ]
    
    for dir_path in directories:
        (output_dir / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created directory: {dir_path}")
    
    # 生成文件内容
    files_to_generate = [
        ("requirements.txt", "生成requirements.txt，包含FastAPI及所有必要的依赖"),
        ("README.md", "生成项目README文档"),
        ("main.py", "生成主应用入口文件"),
        ("app/__init__.py", "创建空的__init__.py"),
        ("app/core/__init__.py", "创建空的__init__.py"),
        ("app/core/config.py", "生成配置文件"),
        ("app/core/security.py", "生成安全相关功能"),
        ("app/db/__init__.py", "创建空的__init__.py"),
        ("app/db/base.py", "生成数据库基础配置"),
        ("app/db/session.py", "生成数据库会话管理"),
        ("app/models/__init__.py", "创建空的__init__.py"),
        ("app/models/user.py", "根据PSM生成用户模型"),
        ("app/schemas/__init__.py", "创建空的__init__.py"),
        ("app/schemas/user.py", "根据PSM生成用户Schema"),
        ("app/api/__init__.py", "创建空的__init__.py"),
        ("app/api/api.py", "生成API路由配置"),
        ("app/api/endpoints/__init__.py", "创建空的__init__.py"),
        ("app/api/endpoints/users.py", "根据PSM生成用户API端点"),
        ("app/api/endpoints/auth.py", "根据PSM生成认证API端点"),
        ("app/services/__init__.py", "创建空的__init__.py"),
        ("app/services/user_service.py", "根据PSM生成用户服务"),
        ("app/services/auth_service.py", "根据PSM生成认证服务"),
        (".env.example", "生成环境变量示例文件")
    ]
    
    print("\n🤖 ReactAgent: Generating files...")
    
    for file_path, description in files_to_generate:
        print(f"\n  Generating: {file_path}")
        
        if file_path.endswith("__init__.py"):
            content = ""
        else:
            # 生成文件内容
            file_prompt = f"""基于以下PSM，{description}：

{psm_content}

请直接输出文件内容，不要包含任何额外的说明。"""
            
            content = call_deepseek(file_prompt)
        
        # 写入文件
        file_full_path = output_dir / file_path
        file_full_path.parent.mkdir(parents=True, exist_ok=True)
        file_full_path.write_text(content, encoding='utf-8')
        print(f"  ✓ Created: {file_path}")
    
    print("\n✅ All files generated successfully!")

def main():
    """主函数"""
    print("=== Simulated ReactAgent Compilation ===")
    
    # 检查API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not set")
        return
    
    # 读取PIM
    pim_file = Path("../models/domain/用户管理_pim.md")
    if not pim_file.exists():
        print(f"❌ PIM file not found: {pim_file}")
        return
    
    pim_content = pim_file.read_text(encoding='utf-8')
    print(f"✅ Loaded PIM: {pim_file}")
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # 创建日志文件
    log_file = output_dir / "compile_output.log"
    log_content = []
    
    def log(message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        log_line = f"{timestamp} - ReactAgent - INFO - {message}"
        print(message)
        log_content.append(log_line)
    
    try:
        # 生成PSM
        log("Starting compilation of ../models/domain/用户管理_pim.md")
        log("Using generator: react-agent")
        log("Target platform: fastapi")
        log(f"Output directory: {output_dir}")
        
        log("\nStep 1: Generating PSM...")
        start_time = time.time()
        psm_content = generate_psm(pim_content)
        psm_time = time.time() - start_time
        
        # 保存PSM
        psm_file = output_dir / "user_management_psm.md"
        psm_file.write_text(psm_content, encoding='utf-8')
        log(f"PSM generated in {psm_time:.2f} seconds")
        
        # 生成代码
        log("\nStep 2: Generating code...")
        log("\n[1m> Entering new AgentExecutor chain...[0m")
        
        start_time = time.time()
        simulate_react_agent(psm_content)
        code_time = time.time() - start_time
        
        log(f"\n[1m> Finished chain.[0m")
        log(f"Code generated in {code_time:.2f} seconds")
        
        # 统计文件
        python_files = list(output_dir.rglob("*.py"))
        total_files = list(output_dir.rglob("*.*"))
        
        log(f"\n✅ Compilation Successful!")
        log(f"Total time: {psm_time + code_time:.2f} seconds")
        log(f"Files generated: {len(total_files)}")
        log(f"Python files: {len(python_files)}")
        
        # 保存日志
        log_file.write_text("\n".join(log_content), encoding='utf-8')
        
        print(f"\n✅ Compilation complete!")
        print(f"Output directory: {output_dir}")
        print(f"Log file: {log_file}")
        
    except Exception as e:
        log(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        log_file.write_text("\n".join(log_content), encoding='utf-8')

if __name__ == "__main__":
    main()