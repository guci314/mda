#!/usr/bin/env python3
"""最简单的 GenericReactAgent 工具封装"""

import os
import sys
from pathlib import Path
import tempfile
import shutil

# 环境设置
sys.path.insert(0, str(Path(__file__).parent))
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel


class Tool:
    """GenericReactAgent 的极简封装"""
    
    def execute(self, task: str) -> str:
        """执行任务，输入字符串，输出字符串"""
        temp_dir = tempfile.mkdtemp()
        try:
            # 创建 agent
            config = ReactAgentConfig(
                output_dir=temp_dir,
                memory_level=MemoryLevel.NONE
            )
            agent = GenericReactAgent(config)
            
            # 执行任务
            agent.execute_task(task)
            
            # 返回结果
            files = list(Path(temp_dir).rglob("*"))
            file_count = sum(1 for f in files if f.is_file())
            return f"任务完成。生成了 {file_count} 个文件在 {temp_dir}"
            
        except Exception as e:
            return f"执行失败: {str(e)}"
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)


# 测试
if __name__ == "__main__":
    tool = Tool()
    result = tool.execute("创建一个 hello world 程序")
    print(result)