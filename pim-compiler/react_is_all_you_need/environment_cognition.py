#!/usr/bin/env python3
"""环境认知 - MVP 版本

经验主义的环境认知：
1. 通过使用来理解环境（而非预先扫描）
2. 最简单的实现（先跑起来）
3. 基于反馈改进
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, Optional
from collections import defaultdict


class EnvironmentCognition:
    """最简单的环境认知 - v0.1"""
    
    def __init__(self, agent_name: str, work_dir: Path):
        self.agent_name = agent_name
        self.work_dir = Path(work_dir)
        
        # 核心数据：就这么简单
        self.file_access = defaultdict(int)  # 文件访问次数
        self.file_purposes = {}  # 文件用途推断
        self.learnings = []  # 学到的东西
        
        # 持久化位置
        self.cognition_file = Path(f".agents/{agent_name}/long_term_data/environment_cognition.json")
        self.cognition_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载已有认知
        self._load()
    
    def learn_from_file_access(self, file_path: str, action: str = "read"):
        """从文件访问中学习（最简实现）"""
        # 记录访问
        self.file_access[file_path] += 1
        
        # 简单推断用途（第一次访问时）
        if file_path not in self.file_purposes:
            purpose = self._guess_purpose(file_path)
            if purpose:
                self.file_purposes[file_path] = purpose
                self.learnings.append(f"发现 {file_path} 是{purpose}")
        
        # 保存（每次都保存，简单粗暴）
        self._save()
    
    def _guess_purpose(self, file_path: str) -> Optional[str]:
        """猜测文件用途（基于文件名，最简单的规则）"""
        path = Path(file_path)
        name_lower = path.name.lower()
        
        # 最常见的模式
        if name_lower == "readme.md":
            return "项目说明文档"
        elif name_lower == "requirements.txt":
            return "Python 依赖列表"
        elif name_lower == "package.json":
            return "Node.js 项目配置"
        elif "test" in name_lower:
            return "测试文件"
        elif name_lower.endswith(".py"):
            return "Python 源代码"
        elif name_lower.endswith(".md"):
            return "文档"
        
        return None
    
    def get_summary(self) -> str:
        """获取环境理解摘要"""
        if not self.file_access:
            return "还没有探索过这个环境"
        
        # 找出最常访问的文件
        top_files = sorted(self.file_access.items(), 
                          key=lambda x: x[1], 
                          reverse=True)[:5]
        
        summary = f"## 环境认知摘要\n\n"
        summary += f"已访问 {len(self.file_access)} 个文件\n\n"
        
        if top_files:
            summary += "### 常用文件：\n"
            for file, count in top_files:
                purpose = self.file_purposes.get(file, "未知")
                summary += f"- {file} ({purpose}) - 访问{count}次\n"
        
        if self.learnings:
            summary += f"\n### 最近学到：\n"
            for learning in self.learnings[-3:]:
                summary += f"- {learning}\n"
        
        return summary
    
    def _save(self):
        """保存认知（最简单的 JSON）"""
        data = {
            "file_access": dict(self.file_access),
            "file_purposes": self.file_purposes,
            "learnings": self.learnings,
            "last_update": datetime.now().isoformat()
        }
        
        with open(self.cognition_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load(self):
        """加载已有认知"""
        if self.cognition_file.exists():
            try:
                with open(self.cognition_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.file_access.update(data.get('file_access', {}))
                    self.file_purposes.update(data.get('file_purposes', {}))
                    self.learnings.extend(data.get('learnings', []))
            except:
                pass  # 加载失败就用空的


# 演进版本（基于用户反馈）
class EnvironmentCognitionV2(EnvironmentCognition):
    """v0.2 - 添加了项目类型推断"""
    
    def __init__(self, agent_name: str, work_dir: Path):
        super().__init__(agent_name, work_dir)
        self.project_type = None
        self.frameworks = set()
    
    def learn_from_file_content(self, file_path: str, content_preview: str):
        """从文件内容学习（用户要求的功能）"""
        # 检测框架
        if "from fastapi" in content_preview:
            self.frameworks.add("FastAPI")
            self.project_type = "Web API"
        elif "import react" in content_preview.lower():
            self.frameworks.add("React")
            self.project_type = "前端应用"
        
        # 更新学习
        if self.frameworks:
            self.learnings.append(f"发现使用了 {', '.join(self.frameworks)}")
        
        self._save()
    
    def get_summary(self) -> str:
        """增强的摘要"""
        summary = super().get_summary()
        
        if self.project_type:
            summary += f"\n### 项目类型：{self.project_type}\n"
        
        if self.frameworks:
            summary += f"### 使用框架：{', '.join(self.frameworks)}\n"
        
        return summary


# 使用示例
if __name__ == "__main__":
    # 创建最简单的环境认知
    cognition = EnvironmentCognition("test_agent", ".")
    
    # 模拟文件访问
    cognition.learn_from_file_access("README.md", "read")
    cognition.learn_from_file_access("src/main.py", "read")
    cognition.learn_from_file_access("tests/test_main.py", "read")
    
    # 显示学到的东西
    print(cognition.get_summary())
    
    print("\n经验主义总结：")
    print("1. 最简单的实现：一个字典记录访问次数")
    print("2. 基于文件名猜测用途（够用了）")
    print("3. 每次访问都保存（简单但有效）")
    print("4. 用户要更多功能？再加 V2")