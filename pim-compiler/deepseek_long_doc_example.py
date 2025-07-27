#!/usr/bin/env python3
"""
DeepSeek 长文档生成示例
展示如何处理输出长度限制
"""

import os
from openai import OpenAI

# 简化的长文档生成策略

def strategy_1_chunked_generation():
    """策略1：分块生成"""
    print("策略1：分块生成")
    print("-" * 40)
    
    # 定义文档章节
    chapters = [
        {"title": "数据模型", "prompt": "生成 User 和 Post 实体的 SQLAlchemy 模型"},
        {"title": "API端点", "prompt": "生成用户管理的 FastAPI 路由"},
        {"title": "服务层", "prompt": "生成 UserService 的业务逻辑"}
    ]
    
    full_doc = ""
    for chapter in chapters:
        # 每个章节单独生成
        response = f"## {chapter['title']}\n\n[这里是 {chapter['title']} 的内容]\n\n"
        full_doc += response
    
    print(f"生成了 {len(chapters)} 个章节")
    return full_doc


def strategy_2_continuation():
    """策略2：续写模式"""
    print("\n策略2：续写模式")
    print("-" * 40)
    
    # 初始生成（限制 token 数）
    initial = "Python 装饰器是一种特殊的函数，它可以修改其他函数的行为。装饰器的基本语法是..."
    
    # 检测截断
    if initial.endswith("..."):
        # 请求续写
        continuation_prompt = f"继续：{initial[-50:]}"
        continuation = "使用 @ 符号，例如 @decorator_name。装饰器本质上是一个高阶函数。"
        full_text = initial + continuation
        print("检测到截断，已续写")
        return full_text
    
    return initial


def strategy_3_outline_driven():
    """策略3：大纲驱动"""
    print("\n策略3：大纲驱动")
    print("-" * 40)
    
    # 1. 先生成大纲
    outline = {
        "title": "用户管理系统 PSM",
        "sections": [
            "1. 数据模型定义",
            "2. API 接口设计", 
            "3. 业务逻辑实现",
            "4. 错误处理机制"
        ]
    }
    
    # 2. 基于大纲逐节生成
    doc = f"# {outline['title']}\n\n"
    for section in outline['sections']:
        doc += f"\n## {section}\n\n[{section} 的详细内容]\n"
    
    print(f"基于大纲生成了 {len(outline['sections'])} 个章节")
    return doc


def strategy_4_function_calls():
    """策略4：函数调用（工具使用）"""
    print("\n策略4：函数调用模式")
    print("-" * 40)
    
    # 模拟使用 append_to_file 函数逐步构建文档
    file_operations = [
        {"action": "write", "content": "# PSM 文档\n\n## 概述\n"},
        {"action": "append", "content": "\n## 数据模型\n...模型定义..."},
        {"action": "append", "content": "\n## API 设计\n...接口定义..."},
        {"action": "append", "content": "\n## 实现细节\n...代码实现..."}
    ]
    
    doc = ""
    for op in file_operations:
        if op["action"] == "write":
            doc = op["content"]
        elif op["action"] == "append":
            doc += op["content"]
    
    print(f"通过 {len(file_operations)} 次操作构建文档")
    return doc


def strategy_5_streaming():
    """策略5：流式生成"""
    print("\n策略5：流式生成")
    print("-" * 40)
    
    # 模拟流式接收
    chunks = [
        "FastAPI 是一个现代化的",
        " Python Web 框架，",
        "它基于 Starlette 和 Pydantic，",
        "提供了高性能和类型安全的特性。"
    ]
    
    full_text = ""
    for i, chunk in enumerate(chunks):
        full_text += chunk
        print(f"接收块 {i+1}: {len(chunk)} 字符")
    
    print(f"总共接收: {len(full_text)} 字符")
    return full_text


# 实际使用示例
def practical_example():
    """实际使用示例：生成长 PSM 文档"""
    print("\n" + "=" * 50)
    print("实际示例：生成长 PSM 文档")
    print("=" * 50)
    
    class PSMGenerator:
        def __init__(self):
            self.max_tokens_per_request = 4000
            
        def generate_psm(self, pim_content):
            # 1. 分析 PIM，确定章节结构
            chapters = self._analyze_pim(pim_content)
            
            # 2. 逐章生成，避免单次输出过长
            psm_doc = "# Platform Specific Model\n\n"
            
            for i, chapter in enumerate(chapters):
                print(f"\n生成章节 {i+1}/{len(chapters)}: {chapter['name']}")
                
                # 生成章节内容
                content = self._generate_chapter(chapter, pim_content)
                
                # 如果内容被截断，续写
                if self._is_truncated(content):
                    continuation = self._continue_chapter(content, chapter)
                    content += continuation
                
                psm_doc += f"\n## {chapter['name']}\n\n{content}\n"
            
            return psm_doc
        
        def _analyze_pim(self, pim_content):
            # 模拟分析结果
            return [
                {"name": "数据模型定义", "focus": "entities"},
                {"name": "API 端点设计", "focus": "endpoints"},
                {"name": "服务层设计", "focus": "business_logic"},
                {"name": "数据访问层", "focus": "repository"}
            ]
        
        def _generate_chapter(self, chapter, pim_content):
            # 模拟生成内容
            return f"{chapter['name']} 的详细内容..."
        
        def _is_truncated(self, content):
            # 检查是否被截断
            return content.endswith("...")
        
        def _continue_chapter(self, content, chapter):
            # 模拟续写
            return " (续写内容)"
    
    # 使用生成器
    generator = PSMGenerator()
    pim = "简单的 PIM 内容"
    psm = generator.generate_psm(pim)
    
    print(f"\n生成的 PSM 文档长度: {len(psm)} 字符")
    print("\nPSM 预览:")
    print(psm[:200] + "...")


# 主函数
def main():
    print("DeepSeek 长文档生成策略演示")
    print("=" * 50)
    
    # 演示各种策略
    strategy_1_chunked_generation()
    strategy_2_continuation()
    strategy_3_outline_driven()
    strategy_4_function_calls()
    strategy_5_streaming()
    
    # 实际使用示例
    practical_example()
    
    print("\n" + "=" * 50)
    print("总结：")
    print("1. 分块生成：适合结构化文档")
    print("2. 续写模式：适合连续文本")
    print("3. 大纲驱动：适合复杂文档")
    print("4. 函数调用：适合精确控制")
    print("5. 流式生成：适合实时输出")
    print("\n选择合适的策略可以有效突破输出长度限制！")


if __name__ == "__main__":
    main()