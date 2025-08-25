#!/usr/bin/env python3
"""
基础Agent类
提供Agent的基本结构和配置
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentConfig:
    """Agent配置类"""
    work_dir: str
    name: str = "BaseAgent"
    description: str = ""
    max_retries: int = 3
    timeout: int = 30000
    

class BaseAgent:
    """基础Agent类"""
    
    def __init__(self, config: AgentConfig):
        """初始化基础Agent"""
        self.config = config
        self.name = config.name
        self.description = config.description
        self.work_dir = Path(config.work_dir)
        
        # 确保工作目录存在
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # 执行历史
        self.history = []
        
    def execute_task(self, task: Any) -> Dict[str, Any]:
        """执行任务的接口方法（子类需要实现）"""
        raise NotImplementedError("Subclass must implement execute_task")
    
    def reset(self):
        """重置Agent状态"""
        self.history = []
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.history
    
    def save_to_file(self, filename: str, content: str):
        """保存内容到文件"""
        file_path = self.work_dir / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def read_from_file(self, filename: str) -> Optional[str]:
        """从文件读取内容"""
        file_path = self.work_dir / filename
        if file_path.exists():
            return file_path.read_text(encoding='utf-8')
        return None