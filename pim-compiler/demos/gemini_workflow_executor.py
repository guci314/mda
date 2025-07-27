#!/usr/bin/env python3
"""
gemini_workflow_executor.py - 实用的 Gemini CLI 工作流执行器
通过单次调用完成多步骤任务，避免上下文丢失问题
"""

import subprocess
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


class GeminiWorkflowExecutor:
    """Gemini 工作流执行器 - 通过构建完整提示来保持上下文"""
    
    def __init__(self, workflow_name: str = "default"):
        self.workflow_name = workflow_name
        self.steps: List[Dict[str, Any]] = []
        self.results: List[Dict[str, Any]] = []
        
    def add_step(self, name: str, prompt: str, depends_on: Optional[List[int]] = None):
        """添加工作流步骤"""
        step = {
            'id': len(self.steps),
            'name': name,
            'prompt': prompt,
            'depends_on': depends_on or []
        }
        self.steps.append(step)
        return self
    
    def build_workflow_prompt(self) -> str:
        """构建包含所有步骤的工作流提示"""
        prompt_parts = [
            "请按照以下步骤完成任务。每个步骤都要基于前面步骤的结果。\n"
        ]
        
        for i, step in enumerate(self.steps):
            prompt_parts.append(f"\n步骤{i+1} - {step['name']}:")
            prompt_parts.append(step['prompt'])
            
            if step['depends_on']:
                deps = ", ".join([f"步骤{d+1}" for d in step['depends_on']])
                prompt_parts.append(f"（基于 {deps} 的结果）")
        
        prompt_parts.append("\n\n请按顺序完成所有步骤，并清晰地标记每个步骤的输出。")
        
        return "\n".join(prompt_parts)
    
    def execute(self) -> str:
        """执行整个工作流"""
        workflow_prompt = self.build_workflow_prompt()
        
        try:
            result = subprocess.run(
                ['gemini', '-p', workflow_prompt],
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            return f"错误: {e.stderr}"
        except Exception as e:
            return f"错误: {str(e)}"
    
    def execute_sequential(self) -> List[str]:
        """顺序执行每个步骤（带累积上下文）"""
        results = []
        accumulated_context = []
        
        for i, step in enumerate(self.steps):
            # 构建带上下文的提示
            context_prompt = ""
            
            if accumulated_context:
                context_prompt = "基于之前的结果：\n"
                for j, prev_result in enumerate(accumulated_context):
                    context_prompt += f"\n步骤{j+1}的结果:\n{prev_result[:500]}...\n"
                context_prompt += "\n现在，"
            
            full_prompt = context_prompt + step['prompt']
            
            # 执行步骤
            try:
                result = subprocess.run(
                    ['gemini', '-p', full_prompt],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                response = result.stdout.strip()
                results.append(response)
                accumulated_context.append(response)
                
                print(f"\n✅ 步骤{i+1} - {step['name']} 完成")
                
            except Exception as e:
                error_msg = f"步骤{i+1}失败: {str(e)}"
                results.append(error_msg)
                print(f"\n❌ {error_msg}")
        
        return results


def demo_fibonacci_workflow():
    """演示：斐波那契函数开发工作流"""
    print("=== 斐波那契函数开发工作流 ===\n")
    
    workflow = GeminiWorkflowExecutor("fibonacci_development")
    
    # 定义工作流步骤
    workflow.add_step(
        "创建基础函数",
        "创建一个简单的递归斐波那契函数 fibonacci(n)，返回第n个斐波那契数。"
    ).add_step(
        "优化性能",
        "优化上面的斐波那契函数，使用记忆化（memoization）来提高性能。",
        depends_on=[0]
    ).add_step(
        "添加文档",
        "为优化后的函数添加完整的docstring，包括参数说明、返回值说明和使用示例。",
        depends_on=[1]
    ).add_step(
        "编写测试",
        "为这个函数编写pytest测试用例，包括基本测试和边界情况测试。",
        depends_on=[2]
    ).add_step(
        "创建完整模块",
        "将函数、文档和测试整合成一个完整的Python模块文件。",
        depends_on=[0, 1, 2, 3]
    )
    
    # 方法1：一次性执行整个工作流
    print("方法1：一次性执行整个工作流")
    print("-" * 50)
    result = workflow.execute()
    print(result)
    
    # 保存结果
    with open(f"workflow_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
        f.write(result)
    
    print("\n" + "=" * 50)
    print("工作流执行完成！")


def demo_sequential_workflow():
    """演示：顺序执行工作流（保持上下文）"""
    print("=== API 开发工作流（顺序执行）===\n")
    
    workflow = GeminiWorkflowExecutor("api_development")
    
    # 定义API开发步骤
    workflow.add_step(
        "设计数据模型",
        "设计一个简单的博客系统数据模型，包括User和Post两个实体。"
    ).add_step(
        "创建Pydantic模型",
        "基于上面的数据模型，创建对应的Pydantic模型类。",
        depends_on=[0]
    ).add_step(
        "设计API端点",
        "为博客系统设计RESTful API端点，包括用户和文章的CRUD操作。",
        depends_on=[0]
    ).add_step(
        "实现FastAPI路由",
        "基于上面的API设计和Pydantic模型，实现FastAPI路由代码。",
        depends_on=[1, 2]
    )
    
    # 顺序执行
    print("开始顺序执行工作流...")
    results = workflow.execute_sequential()
    
    # 保存每个步骤的结果
    output_dir = f"workflow_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, (step, result) in enumerate(zip(workflow.steps, results)):
        filename = f"{output_dir}/step_{i+1}_{step['name'].replace(' ', '_')}.txt"
        with open(filename, 'w') as f:
            f.write(f"步骤: {step['name']}\n")
            f.write(f"提示: {step['prompt']}\n")
            f.write(f"\n结果:\n{result}")
        print(f"步骤{i+1}结果已保存到: {filename}")
    
    print("\n工作流执行完成！")


def demo_stateful_conversation():
    """演示：通过文件保持状态的对话"""
    print("=== 基于文件的有状态对话 ===\n")
    
    session_file = "gemini_session_state.json"
    
    def load_session():
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                return json.load(f)
        return {"history": [], "context": {}}
    
    def save_session(session):
        with open(session_file, 'w') as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
    
    def chat_with_history(message: str, session: dict) -> str:
        # 构建带历史的提示
        prompt_parts = []
        
        if session["history"]:
            prompt_parts.append("对话历史：")
            for item in session["history"][-6:]:  # 最近3轮对话
                prompt_parts.append(f"{item['role']}: {item['content']}")
            prompt_parts.append("")
        
        prompt_parts.append(f"用户: {message}")
        prompt_parts.append("\n请基于对话历史回答。")
        
        full_prompt = "\n".join(prompt_parts)
        
        # 调用 Gemini
        result = subprocess.run(
            ['gemini', '-p', full_prompt],
            capture_output=True,
            text=True
        )
        
        response = result.stdout.strip()
        
        # 更新历史
        session["history"].append({"role": "用户", "content": message})
        session["history"].append({"role": "助手", "content": response})
        
        return response
    
    # 测试对话
    session = load_session()
    
    print("测试1: 设置信息")
    response1 = chat_with_history("我叫张三，我是一名Python开发者。", session)
    print(f"Gemini: {response1}\n")
    save_session(session)
    
    print("测试2: 询问信息")
    response2 = chat_with_history("我叫什么名字？我是做什么的？", session)
    print(f"Gemini: {response2}\n")
    save_session(session)
    
    if "张三" in response2 and "Python" in response2:
        print("✅ 成功！通过文件保持了对话状态。")
    else:
        print("⚠️  状态保持可能有问题。")
    
    print(f"\n会话状态已保存到: {session_file}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "sequential":
            demo_sequential_workflow()
        elif sys.argv[1] == "stateful":
            demo_stateful_conversation()
        else:
            print("未知选项。可用选项: sequential, stateful")
    else:
        print("演示选项：")
        print("1. python3 gemini_workflow_executor.py          # 一次性工作流")
        print("2. python3 gemini_workflow_executor.py sequential # 顺序执行")  
        print("3. python3 gemini_workflow_executor.py stateful   # 状态对话")
        print("\n运行默认演示...\n")
        demo_fibonacci_workflow()