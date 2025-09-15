#!/usr/bin/env python3
"""
MDA订单系统工作流Agent
基于React Agent Minimal实现PIM → PSM → Code的自动转换
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.react_agent_minimal import ReactAgentMinimal

def create_mda_agents():
    """创建MDA流程所需的Agent"""
    
    # PIM解析Agent - 读取业务模型
    pim_parser = ReactAgentMinimal(
        name="pim_parser",
        description="解析PIM业务模型文件，提取业务实体和流程",
        knowledge_files=["knowledge/mda_concepts.md"]
    )
    
    # PIM → PSM转换Agent
    psm_transformer = ReactAgentMinimal(
        name="psm_transformer", 
        description="将PIM业务模型转换为FastAPI技术模型(PSM)",
        knowledge_files=["knowledge/pim_to_fastapi_psm.md"]
    )
    
    # PSM → Code生成Agent
    code_generator = ReactAgentMinimal(
        name="code_generator",
        description="将PSM技术模型转换为可运行的FastAPI代码",
        knowledge_files=["knowledge/fastapi_psm_to_code.md"]
    )
    
    return pim_parser, psm_transformer, code_generator

def run_mda_workflow(pim_file_path):
    """执行完整的MDA工作流"""
    
    print("🚀 开始MDA订单系统生成工作流...")
    
    # 创建Agent
    pim_parser, psm_transformer, code_generator = create_mda_agents()
    
    # 阶段1: 解析PIM
    print("📖 阶段1: 解析PIM业务模型...")
    pim_content = read_pim_file(pim_file_path)
    pim_data = pim_parser.run(f"解析以下PIM内容并提取业务实体和流程:\n{pim_content}")
    
    # 阶段2: PIM → PSM转换
    print("🔄 阶段2: PIM → PSM转换...")
    psm_data = psm_transformer.run(f"根据以下PIM数据生成FastAPI PSM:\n{pim_data}")
    
    # 保存PSM
    psm_file = "psm/order_system_fastapi.psm.md"
    save_psm(psm_data, psm_file)
    
    # 阶段3: PSM → Code生成
    print("💻 阶段3: PSM → 代码生成...")
    for service_name in ["product", "order", "inventory", "customer", "payment", "delivery"]:
        print(f"  生成 {service_name}-service...")
        code_result = code_generator.run(f"根据PSM生成{service_name}服务的FastAPI代码:\n{psm_data}")
        
        # 保存生成的代码
        save_generated_code(service_name, code_result)
    
    print("✅ MDA工作流完成！")
    print("生成的代码位于: output/fastapi/")

def read_pim_file(file_path):
    """读取PIM文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ PIM文件不存在: {file_path}")
        return ""

def save_psm(psm_data, file_path):
    """保存PSM数据"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(psm_data)
    print(f"📁 PSM已保存: {file_path}")

def save_generated_code(service_name, code_content):
    """保存生成的代码"""
    output_dir = f"output/fastapi/{service_name}-service"
    os.makedirs(output_dir, exist_ok=True)
    
    # 这里需要根据代码内容解析并保存为多个文件
    # 简化示例：保存为单个文件
    output_file = f"{output_dir}/generated_code.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(code_content)
    
    print(f"  代码已保存: {output_file}")

if __name__ == "__main__":
    # 执行MDA工作流
    pim_file = "pim/order_system.md"
    run_mda_workflow(pim_file)