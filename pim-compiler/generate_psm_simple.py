#!/usr/bin/env python3
"""
使用 ChatOpenAI 直接生成完整 PSM（同步版本）
"""

import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime

def generate_complete_psm(pim_path: str, output_path: str):
    """一次性生成完整的 PSM"""
    
    # 读取 PIM 内容
    pim_content = Path(pim_path).read_text(encoding='utf-8')
    print(f"加载 PIM 文件: {pim_path}")
    print(f"PIM 内容长度: {len(pim_content)} 字符")
    
    # 获取 API 配置
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        try:
            with open('/home/guci/aiProjects/mda/.env', 'r') as f:
                for line in f:
                    if line.startswith('DEEPSEEK_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        except:
            pass
    
    if not api_key:
        raise ValueError("No DEEPSEEK_API_KEY found")
    
    # 创建 LLM
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com",
        temperature=0.7
    )
    
    # 系统提示词
    system_prompt = """你是一个专业的软件架构师，负责根据 PIM（Platform Independent Model）生成完整的 PSM（Platform Specific Model）。

技术栈：
- FastAPI (Web框架)
- SQLAlchemy 2.0 (ORM)
- Pydantic v2 (数据验证)
- PostgreSQL (数据库)
- Python 3.11+

请生成包含以下四个部分的完整 PSM：

1. **Domain Models** - 数据模型
   - SQLAlchemy 模型（使用 mapped_column）
   - Pydantic 模型（Base, Create, Update, Response）
   - 枚举定义

2. **Service Layer** - 业务逻辑
   - 服务类（依赖注入）
   - 仓储模式（接口和实现）
   - 业务规则实现

3. **API Layer** - RESTful API
   - FastAPI 路由
   - 端点实现（CRUD）
   - 请求/响应处理

4. **Tests** - 测试代码
   - 单元测试
   - 集成测试
   - 测试配置

每个部分都要：
- 包含完整可运行的代码
- 使用中文注释
- 遵循 FastAPI 最佳实践
- 包含错误处理
"""
    
    # 用户消息
    human_prompt = f"""请根据以下 PIM 生成完整的 PSM：

{pim_content}

要求：
1. 生成的代码必须可以直接运行
2. 使用 async/await 异步编程
3. 包含完整的类型注解
4. 实现所有业务规则
5. 每个部分用 Markdown 标题分隔
"""
    
    # 调用 LLM
    print("\n开始生成 PSM...")
    start_time = datetime.now()
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]
    
    response = llm.invoke(messages)
    psm_content = response.content
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"PSM 生成完成！耗时: {duration:.2f} 秒")
    print(f"生成内容长度: {len(psm_content)} 字符")
    
    # 保存结果
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(psm_content, encoding='utf-8')
    
    print(f"PSM 已保存到: {output_file}")
    
    return psm_content

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成完整 PSM")
    parser.add_argument("pim_file", help="PIM 文件路径")
    parser.add_argument("-o", "--output", default="./psm_output/complete_psm.md", help="输出文件")
    
    args = parser.parse_args()
    
    generate_complete_psm(args.pim_file, args.output)

if __name__ == "__main__":
    main()