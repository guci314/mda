"""World Overview 检查器

在 Agent 初始化时检查工作目录中是否存在 world_overview.md，
如果不存在则触发生成任务。
"""

import os
from pathlib import Path
from typing import Optional
from datetime import datetime


class WorldOverviewChecker:
    """检查并触发生成 world_overview.md"""
    
    def __init__(self, work_dir: Path):
        """
        Args:
            work_dir: Agent 的工作目录（外部世界）
        """
        self.work_dir = Path(work_dir)
        self.overview_file = self.work_dir / "world_overview.md"
        self._important_files = [
            "README.md", "readme.md", "README.rst",
            "package.json", "requirements.txt", "setup.py", 
            "pyproject.toml", "Cargo.toml", "go.mod",
            "pom.xml", "build.gradle"
        ]
        
    def check_and_generate(self, agent_name: str = "system") -> bool:
        """检查 world_overview.md 是否存在，不存在则生成
        
        Args:
            agent_name: 执行生成的 Agent 名称
            
        Returns:
            是否执行了生成（True=生成了新文件，False=文件已存在）
        """
        if self.overview_file.exists():
            return False
            
        # 生成任务描述
        task = self._create_generation_task()
        
        # 这里返回任务，实际执行需要由 Agent 完成
        # 因为只有 Agent 才能使用工具来分析目录和生成文件
        print(f"[WorldOverviewChecker] 需要生成 world_overview.md")
        print(f"[WorldOverviewChecker] 任务：\n{task}")
        
        return True
        
    def _create_generation_task(self) -> str:
        """创建生成 world_overview.md 的任务描述"""
        return f"""请为当前工作目录生成 world_overview.md 文件。

工作目录：{self.work_dir}

步骤：
1. 扫描目录结构，了解整体布局
2. 读取关键文件（如 README.md）了解项目信息
3. 识别项目类型和主要技术栈
4. 按照 knowledge/world_overview_generation.md 中的模板生成文件

注意：
- 保持客观和简洁
- 重点关注目录的整体概况
- 生成的文件应该帮助快速理解和导航这个"外部世界"
"""
    
    def get_overview_content(self) -> Optional[str]:
        """获取 world_overview.md 的内容
        
        Returns:
            文件内容，如果不存在则返回 None
        """
        if not self.overview_file.exists():
            return None
            
        return self.overview_file.read_text(encoding='utf-8')
    
    def should_update(self) -> Optional[str]:
        """检查是否需要更新 world_overview.md
        
        Returns:
            需要更新的原因，如果不需要更新则返回 None
        """
        if not self.overview_file.exists():
            return None  # 文件不存在应该生成，不是更新
        
        # 获取 overview 文件的修改时间
        overview_mtime = self.overview_file.stat().st_mtime
        overview_age_days = (datetime.now().timestamp() - overview_mtime) / 86400
        
        # 检查重要文件是否有更新
        important_changes = []
        for filename in self._important_files:
            file_path = self.work_dir / filename
            if file_path.exists():
                file_mtime = file_path.stat().st_mtime
                if file_mtime > overview_mtime:
                    important_changes.append(filename)
        
        # 检查顶层目录结构是否变化
        current_dirs = set()
        for item in self.work_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                current_dirs.add(item.name)
        
        # 读取现有 overview 中记录的目录
        try:
            content = self.overview_file.read_text(encoding='utf-8')
            # 简单检查：是否有新的顶层目录
            new_dirs = []
            for dir_name in current_dirs:
                if dir_name not in content:
                    new_dirs.append(dir_name)
        except Exception:
            new_dirs = []
        
        # 决定是否需要更新
        reasons = []
        
        if important_changes:
            reasons.append(f"重要文件已更新：{', '.join(important_changes[:3])}")
        
        if new_dirs:
            reasons.append(f"发现新目录：{', '.join(new_dirs[:3])}")
        
        if overview_age_days > 30:
            reasons.append(f"超过30天未更新（已{int(overview_age_days)}天）")
        
        if reasons:
            return "；".join(reasons)
        
        return None
    
    def update_overview(self, reason: str = "定期更新") -> str:
        """生成更新 world_overview.md 的任务
        
        Args:
            reason: 更新原因
            
        Returns:
            更新任务描述
        """
        return f"""请更新 world_overview.md 文件。

更新原因：{reason}
当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

要求：
1. 保留原有的有效信息
2. 更新发生变化的部分
3. 在更新记录中添加本次更新信息
4. 确保信息的准确性和时效性
"""


def integrate_with_react_agent(agent_class):
    """集成到 GenericReactAgent 的装饰器
    
    使用方法：
    @integrate_with_react_agent
    class MyAgent(GenericReactAgent):
        pass
    """
    original_init = agent_class.__init__
    
    def new_init(self, config, *args, **kwargs):
        # 调用原始初始化
        original_init(self, config, *args, **kwargs)
        
        # 检查 world_overview.md
        checker = WorldOverviewChecker(self.work_dir)
        if checker.check_and_generate(self.name):
            # 将生成任务添加到 Agent 的初始任务队列
            # 注意：这需要 Agent 有相应的任务队列机制
            if hasattr(self, '_pending_tasks'):
                task = checker._create_generation_task()
                self._pending_tasks.insert(0, task)
            else:
                print(f"[Warning] Agent {self.name} 没有任务队列机制")
    
    agent_class.__init__ = new_init
    return agent_class


# 使用示例
if __name__ == "__main__":
    # 测试检查器
    test_dir = Path("output/test_world")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    checker = WorldOverviewChecker(test_dir)
    
    # 检查并生成
    if checker.check_and_generate("test_agent"):
        print("\n需要生成 world_overview.md")
    else:
        print("\nworld_overview.md 已存在")
        content = checker.get_overview_content()
        if content:
            print(f"\n当前内容预览：\n{content[:200]}...")