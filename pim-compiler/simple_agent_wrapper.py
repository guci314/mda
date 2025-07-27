#!/usr/bin/env python3
"""Simple wrapper for GenericReactAgent"""

import os
import sys
from pathlib import Path
import tempfile
import shutil
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置环境变量
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)
os.environ['DISABLE_TOKEN_PATCH'] = '1'

from direct_react_agent_v4_generic import GenericReactAgent, GeneratorConfig, MemoryLevel


class SimpleAgentWrapper:
    """极简的 GenericReactAgent 封装"""
    
    def __init__(self):
        """初始化，使用默认配置"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="agent_output_")
        
        # 使用最简配置
        self.config = GeneratorConfig(
            output_dir=self.temp_dir,
            memory_level=MemoryLevel.NONE,  # 无记忆
            knowledge_file="先验知识.md"
        )
        
        # 创建 Agent
        self.agent = GenericReactAgent(self.config)
    
    def execute(self, task: str) -> str:
        """
        执行任务并返回结果
        
        Args:
            task: 任务描述字符串
            
        Returns:
            执行结果字符串
        """
        # 捕获所有输出
        output_buffer = StringIO()
        error_buffer = StringIO()
        
        try:
            # 重定向输出
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                self.agent.execute_task(task)
            
            # 获取输出内容
            output = output_buffer.getvalue()
            errors = error_buffer.getvalue()
            
            # 检查生成的文件
            files_created = []
            output_path = Path(self.temp_dir)
            for file_path in output_path.rglob("*"):
                if file_path.is_file():
                    files_created.append(str(file_path.relative_to(output_path)))
            
            # 构建结果
            result = f"Task completed successfully!\n"
            if files_created:
                result += f"Files created: {', '.join(files_created)}\n"
            if output:
                result += f"\nAgent output:\n{output}"
            if errors:
                result += f"\nWarnings/Errors:\n{errors}"
                
            return result
            
        except Exception as e:
            return f"Task failed: {str(e)}"
        finally:
            # 清理临时目录
            if Path(self.temp_dir).exists():
                shutil.rmtree(self.temp_dir)
            output_buffer.close()
            error_buffer.close()


# 单例模式的全局函数
def execute(task: str) -> str:
    """
    执行任务的全局函数
    
    Args:
        task: 任务描述
        
    Returns:
        执行结果
    """
    wrapper = SimpleAgentWrapper()
    return wrapper.execute(task)


# 最简单的类封装
class AgentTool:
    """最简单的工具类"""
    
    @staticmethod
    def execute(task: str) -> str:
        """执行任务"""
        return execute(task)


if __name__ == "__main__":
    # 测试
    print("=== Simple Agent Wrapper Test ===\n")
    
    # 方式1: 使用全局函数
    print("Test 1 - Global function:")
    result1 = execute("创建一个 Python 函数，计算斐波那契数列的第 n 项")
    print(result1)
    
    print("\n" + "="*50 + "\n")
    
    # 方式2: 使用类的静态方法
    print("Test 2 - Static method:")
    result2 = AgentTool.execute("创建一个简单的 TODO 列表类")
    print(result2)
    
    print("\n" + "="*50 + "\n")
    
    # 方式3: 使用实例
    print("Test 3 - Instance method:")
    wrapper = SimpleAgentWrapper()
    result3 = wrapper.execute("写一个函数，将摄氏度转换为华氏度")
    print(result3)