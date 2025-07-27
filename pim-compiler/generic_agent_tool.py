#!/usr/bin/env python3
"""GenericReactAgent Tool Wrapper - 简单的工具封装"""

import os
import sys
from pathlib import Path
from typing import Optional
import tempfile
import shutil

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置环境变量
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)
os.environ['DISABLE_TOKEN_PATCH'] = '1'

from langchain_core.tools import tool
from direct_react_agent_v4_generic import GenericReactAgent, GeneratorConfig, MemoryLevel


class GenericAgentTool:
    """GenericReactAgent 的工具封装"""
    
    def __init__(
        self,
        memory_level: str = "none",
        knowledge_file: str = "先验知识.md",
        output_dir: Optional[str] = None
    ):
        """
        初始化工具
        
        Args:
            memory_level: 记忆级别 ("none", "smart", "pro")
            knowledge_file: 先验知识文件路径
            output_dir: 输出目录，如果为 None 则使用临时目录
        """
        # 使用临时目录或指定目录
        if output_dir is None:
            self.temp_dir = tempfile.mkdtemp(prefix="generic_agent_")
            self.output_dir = self.temp_dir
            self.cleanup_on_exit = True
        else:
            self.output_dir = output_dir
            self.temp_dir = None
            self.cleanup_on_exit = False
        
        # 映射记忆级别
        memory_mapping = {
            "none": MemoryLevel.NONE,
            "smart": MemoryLevel.SMART,
            "pro": MemoryLevel.PRO
        }
        
        # 创建配置
        self.config = GeneratorConfig(
            output_dir=self.output_dir,
            memory_level=memory_mapping.get(memory_level, MemoryLevel.NONE),
            knowledge_file=knowledge_file
        )
        
        # 创建 Agent
        self.agent = GenericReactAgent(self.config)
    
    def execute(self, task: str) -> str:
        """
        执行任务
        
        Args:
            task: 任务描述
            
        Returns:
            执行结果的字符串描述
        """
        try:
            # 执行任务
            self.agent.execute_task(task)
            
            # 收集输出文件信息
            output_files = []
            output_path = Path(self.output_dir)
            
            if output_path.exists():
                for file_path in output_path.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(output_path)
                        output_files.append(str(relative_path))
            
            # 构建结果字符串
            result = f"✅ 任务执行成功！\n"
            result += f"输出目录: {self.output_dir}\n"
            
            if output_files:
                result += f"\n生成的文件:\n"
                for file in sorted(output_files):
                    result += f"  - {file}\n"
            else:
                result += "\n没有生成文件。"
            
            return result
            
        except Exception as e:
            return f"❌ 任务执行失败: {str(e)}"
        
    def cleanup(self):
        """清理临时目录"""
        if self.cleanup_on_exit and self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def __del__(self):
        """析构时清理"""
        self.cleanup()


# 创建 LangChain 工具
@tool
def execute_generic_task(task: str) -> str:
    """
    使用 GenericReactAgent 执行通用任务
    
    Args:
        task: 要执行的任务描述
        
    Returns:
        执行结果
    """
    tool = GenericAgentTool(memory_level="none")
    try:
        return tool.execute(task)
    finally:
        tool.cleanup()


# 便捷函数
def create_generic_agent_tool(
    memory_level: str = "none",
    knowledge_file: str = "先验知识.md",
    output_dir: Optional[str] = None
) -> GenericAgentTool:
    """
    创建 GenericAgentTool 实例
    
    Args:
        memory_level: 记忆级别
        knowledge_file: 先验知识文件
        output_dir: 输出目录
        
    Returns:
        GenericAgentTool 实例
    """
    return GenericAgentTool(
        memory_level=memory_level,
        knowledge_file=knowledge_file,
        output_dir=output_dir
    )


if __name__ == "__main__":
    # 测试代码
    print("=== GenericAgentTool 测试 ===\n")
    
    # 1. 使用临时目录
    print("1. 使用临时目录:")
    tool1 = GenericAgentTool()
    result1 = tool1.execute("创建一个计算两数之和的 Python 函数")
    print(result1)
    tool1.cleanup()
    
    print("\n" + "="*50 + "\n")
    
    # 2. 使用指定目录
    print("2. 使用指定目录:")
    tool2 = GenericAgentTool(output_dir="output/tool_test")
    result2 = tool2.execute("创建一个简单的 README.md 文件，说明这是一个测试项目")
    print(result2)
    
    print("\n" + "="*50 + "\n")
    
    # 3. 作为 LangChain 工具使用
    print("3. 作为 LangChain 工具:")
    result3 = execute_generic_task("创建一个 hello.py 文件，打印当前时间")
    print(result3)