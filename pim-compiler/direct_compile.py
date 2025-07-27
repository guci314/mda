#!/usr/bin/env python3
"""直接使用DeepSeek API编译，不依赖LangChain"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def call_deepseek(prompt: str) -> str:
    """调用DeepSeek API"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
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

def compile_user_management():
    """编译用户管理PIM"""
    print("=== Direct Compilation with DeepSeek API ===")
    print(f"Working directory: {os.getcwd()}")
    
    # 读取PIM
    pim_file = Path("examples/user_management.md")
    if not pim_file.exists():
        print(f"❌ PIM file not found: {pim_file}")
        return
    
    pim_content = pim_file.read_text(encoding='utf-8')
    print(f"✅ Loaded PIM: {pim_file}")
    
    # 设置输出目录
    output_dir = Path("output/direct_compile")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n1. Generating PSM...")
    
    # 生成PSM
    psm_prompt = f"""你是一个专业的软件架构师，负责生成 PSM（Platform Specific Model）。

目标平台: FastAPI
技术栈:
- 框架: FastAPI
- ORM: SQLAlchemy
- 验证库: Pydantic

请根据以下PIM生成详细的PSM文档：

{pim_content}

要求：
1. 包含详细的数据模型定义（字段类型、约束等）
2. API端点设计（RESTful）
3. 服务层方法定义
4. 配置说明

请使用Markdown格式输出。"""
    
    start_time = time.time()
    try:
        psm_content = call_deepseek(psm_prompt)
        psm_time = time.time() - start_time
        
        # 保存PSM
        psm_file = output_dir / "user_management_psm.md"
        psm_file.write_text(psm_content, encoding='utf-8')
        print(f"✅ PSM generated in {psm_time:.2f}s")
        
    except Exception as e:
        print(f"❌ PSM generation failed: {e}")
        return
    
    print("\n2. Generating code structure...")
    
    # 生成代码结构
    code_prompt = f"""你是一个专业的FastAPI开发者。请根据以下PSM生成完整的FastAPI应用代码结构。

{psm_content}

请按照以下格式生成代码文件列表（使用JSON格式，确保正确转义）：
{{
  "files": [
    {{
      "path": "main.py",
      "content": "文件内容"
    }}
  ]
}}

注意：
1. 所有的换行符使用\\n
2. 所有的引号使用\\\"转义
3. 避免在字符串中使用三引号
4. 每个文件的content必须是单行字符串

要求：
1. 包含完整的项目结构
2. 每个Python包都需要__init__.py
3. 包含requirements.txt
4. 包含README.md
5. 使用FastAPI、SQLAlchemy、Pydantic

重要：确保输出的是合法的JSON格式，不要包含任何额外的说明文字。"""
    
    start_time = time.time()
    try:
        code_response = call_deepseek(code_prompt)
        code_time = time.time() - start_time
        
        # 解析JSON响应
        # 提取JSON部分（处理可能的markdown代码块）
        if "```json" in code_response:
            json_start = code_response.find("```json") + 7
            json_end = code_response.find("```", json_start)
            json_str = code_response[json_start:json_end].strip()
        elif "```" in code_response:
            json_start = code_response.find("```") + 3
            json_end = code_response.find("```", json_start)
            json_str = code_response[json_start:json_end].strip()
        else:
            json_str = code_response.strip()
        
        # 清理JSON字符串
        # 移除开头和结尾的额外文字
        if json_str.startswith("{"):
            end_idx = json_str.rfind("}")
            if end_idx != -1:
                json_str = json_str[:end_idx + 1]
        
        # 解析JSON
        code_data = json.loads(json_str)
        
        # 生成文件
        generated_dir = output_dir / "generated"
        generated_dir.mkdir(exist_ok=True)
        
        file_count = 0
        for file_info in code_data.get("files", []):
            file_path = generated_dir / file_info["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_info["content"], encoding='utf-8')
            file_count += 1
            print(f"  Created: {file_info['path']}")
        
        print(f"\n✅ Generated {file_count} files in {code_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Code generation failed: {e}")
        return
    
    print(f"\n✅ Compilation complete!")
    print(f"Output directory: {output_dir}")
    
    # 保存报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "psm_generation_time": psm_time,
        "code_generation_time": code_time,
        "total_time": psm_time + code_time,
        "output_directory": str(output_dir),
        "files_generated": file_count
    }
    
    report_file = output_dir / "compilation_report.json"
    report_file.write_text(json.dumps(report, indent=2), encoding='utf-8')

if __name__ == "__main__":
    compile_user_management()