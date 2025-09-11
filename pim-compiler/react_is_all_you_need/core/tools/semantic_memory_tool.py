"""语义记忆工具 - 管理 agent.md 文件"""

from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from tool_base import Function

class WriteSemanticMemoryTool(Function):
    """写入语义记忆工具"""
    
    def __init__(self, work_dir: str):
        self.work_dir = Path(work_dir)
        super().__init__(
            name="write_semantic_memory",
            description="写入或更新语义记忆（agent.md）文件，用于存储模块的核心知识、设计模式和注意事项",
            parameters={
                "path": {
                    "type": "string",
                    "description": "目录路径，如果为空则使用当前目录"
                },
                "content": {
                    "type": "string",
                    "description": "要写入的内容，如果为空则生成默认模板"
                },
                "append": {
                    "type": "boolean",
                    "description": "是否追加模式（默认为覆盖模式）",
                    "default": False
                }
            },
            return_type="string"
        )
    
    def execute(self, **kwargs) -> str:
        """执行写入语义记忆"""
        path = kwargs.get("path", None)
        content = kwargs.get("content", None)
        append = kwargs.get("append", False)
        
        # 确定路径
        if path is None or path == "":
            target_path = self.work_dir
        else:
            target_path = Path(path)
            if not target_path.is_absolute():
                target_path = self.work_dir / target_path
            if not target_path.exists():
                return f"❌ 路径不存在: {target_path}"
        
        agent_md_path = target_path / "agent.md"
        
        # 如果没有提供内容，生成默认模板
        if content is None or content == "":
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            content = f"""# 模块知识 - {target_path.name}

## 核心概念
<!-- Agent 学到的关键概念 -->

## 重要模式
<!-- 发现的设计模式或解决方案 -->

## 注意事项
<!-- 踩过的坑或特殊约定 -->

## 相关文件
<!-- 重要的相关文件列表 -->

---
更新时间：{timestamp}
更新原因：Agent 主动记录
"""
        
        # 写入或追加
        if append and agent_md_path.exists():
            # 追加模式
            existing_content = agent_md_path.read_text(encoding='utf-8')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_content = f"{existing_content}\n\n---\n追加于：{timestamp}\n\n{content}"
            agent_md_path.write_text(new_content, encoding='utf-8')
            return f"✅ 已追加语义记忆到: {agent_md_path}"
        else:
            # 覆盖模式
            agent_md_path.write_text(content, encoding='utf-8')
            return f"✅ 已保存语义记忆到: {agent_md_path}"


class ReadSemanticMemoryTool(Function):
    """读取语义记忆工具"""
    
    def __init__(self, work_dir: str):
        self.work_dir = Path(work_dir)
        super().__init__(
            name="read_semantic_memory",
            description="读取语义记忆（agent.md）文件，支持级联读取当前目录和父目录的agent.md",
            parameters={
                "path": {
                    "type": "string",
                    "description": "目录路径，如果为空则使用当前目录"
                }
            },
            return_type="string"
        )
    
    def execute(self, **kwargs) -> str:
        """执行读取语义记忆"""
        path = kwargs.get("path", None)
        
        # 确定路径
        if path is None or path == "":
            target_path = self.work_dir
        else:
            target_path = Path(path)
            if not target_path.is_absolute():
                target_path = self.work_dir / target_path
        
        agent_md_path = target_path / "agent.md"
        
        if not agent_md_path.exists():
            # 尝试上级目录
            parent_agent_md = target_path.parent / "agent.md"
            if parent_agent_md.exists():
                content = parent_agent_md.read_text(encoding='utf-8')
                return f"[上级目录的 agent.md]\n{content}"
            return f"❌ 未找到 agent.md 文件: {agent_md_path}"
        
        content = agent_md_path.read_text(encoding='utf-8')
        return f"[当前目录的 agent.md]\n{content}"


# 保留原有的函数接口以便兼容
def write_semantic_memory(
    path: Optional[str] = None,
    content: Optional[str] = None,
    append: bool = False
) -> str:
    """
    写入或更新语义记忆（agent.md）
    
    Args:
        path: 目录路径，如果为None则使用当前目录
        content: 要写入的内容，如果为None则生成模板
        append: 是否追加模式（默认覆盖）
    
    Returns:
        操作结果消息
    """
    tool = WriteSemanticMemoryTool(Path.cwd())
    return tool.execute(path=path, content=content, append=append)


def read_semantic_memory(path: Optional[str] = None) -> str:
    """
    读取语义记忆（agent.md）
    
    Args:
        path: 目录路径，如果为None则使用当前目录
    
    Returns:
        agent.md 的内容，或错误消息
    """
    tool = ReadSemanticMemoryTool(Path.cwd())
    return tool.execute(path=path)