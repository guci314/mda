#!/usr/bin/env python3
"""项目探索器 - 主动理解项目结构

经验主义设计：
1. 不预设框架，通过配置的提示词决定探索方式
2. 探索结果存储为单个markdown文件
3. 异步执行，不影响主任务
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class ProjectExplorer:
    """项目探索器 - 生成项目理解文档"""
    
    # 默认的开放式探索提示词
    DEFAULT_EXPLORATION_PROMPT = """# 项目探索任务

请深入探索和理解这个项目，形成你对项目的整体认知。

你可以从任何你认为重要的角度来分析：
- 项目的目的和核心功能
- 代码组织方式和架构设计
- 主要组件及其协作关系
- 技术栈和关键依赖
- 设计模式和编程范式
- 任何有助于理解项目的独特视角

输出要求：
- 使用Markdown格式
- 可以包含mermaid图表（如果有助于理解）
- 可以包含关键代码片段
- 诚实标注不确定或推测的部分
- 结构和组织方式由你决定

请基于提供的项目信息，生成一份全面的项目理解文档。
"""
    
    def __init__(self, agent_name: str, work_dir: Path, llm, config, on_complete_callback=None):
        """初始化项目探索器
        
        Args:
            agent_name: Agent名称
            work_dir: 工作目录
            llm: LLM实例
            config: Agent配置
            on_complete_callback: 探索完成后的回调函数
        """
        self.agent_name = agent_name
        self.work_dir = Path(work_dir)
        self.llm = llm
        self.config = config
        self.on_complete_callback = on_complete_callback
        
        # 存储位置
        self.understanding_file = Path(f".agents/{agent_name}/long_term_data/project_understanding.md")
        self.understanding_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 探索历史
        self.exploration_log = Path(f".agents/{agent_name}/long_term_data/exploration_log.json")
        
    async def explore_project(self) -> None:
        """异步探索项目，生成理解文档"""
        try:
            print("🔍 [项目探索] 开始分析项目结构...")
            start_time = datetime.now()
            
            # 获取探索提示词
            exploration_prompt = self._get_exploration_prompt()
            
            # 收集项目基础信息
            project_info = self._gather_project_info()
            
            # 构建完整提示词
            full_prompt = f"{exploration_prompt}\n\n## 项目基础信息\n\n{project_info}"
            
            # 调用LLM生成项目理解
            if os.environ.get('DEBUG'):
                logger.info(f"开始LLM探索，提示词长度: {len(full_prompt)}")
                
            response = await self.llm.ainvoke(full_prompt)
            understanding = response.content
            
            # 保存探索结果
            self.understanding_file.write_text(understanding, encoding='utf-8')
            
            # 记录探索历史
            self._log_exploration(start_time, len(understanding))
            
            # 预览结果
            preview = understanding.split('\n')[0][:100]
            if len(preview) == 100:
                preview += "..."
                
            print(f"✅ [项目探索] 完成！已生成项目理解文档 ({len(understanding)} 字符)")
            print(f"   📄 {preview}")
            
            # 触发完成回调
            if self.on_complete_callback:
                try:
                    self.on_complete_callback()
                except Exception as callback_error:
                    logger.warning(f"探索完成回调执行失败: {callback_error}")
            
        except Exception as e:
            print(f"⚠️ [项目探索] 探索过程中出错: {e}")
            if os.environ.get('DEBUG'):
                logger.error(f"项目探索失败: {e}", exc_info=True)
    
    def _get_exploration_prompt(self) -> str:
        """获取探索提示词（按优先级）"""
        # 1. 直接配置的提示词
        if hasattr(self.config, 'exploration_prompt') and self.config.exploration_prompt:
            return self.config.exploration_prompt
            
        # 2. 从文件加载的提示词
        if hasattr(self.config, 'exploration_prompt_file') and self.config.exploration_prompt_file:
            prompt_file = Path(self.config.exploration_prompt_file)
            if prompt_file.exists():
                return prompt_file.read_text(encoding='utf-8')
            else:
                print(f"⚠️ 探索提示词文件未找到: {prompt_file}")
                
        # 3. 使用默认提示词
        return self.DEFAULT_EXPLORATION_PROMPT
    
    def _gather_project_info(self) -> str:
        """收集项目基础信息供LLM参考"""
        info_parts = []
        
        # 1. 项目路径
        info_parts.append(f"### 项目路径\n`{self.work_dir}`\n")
        
        # 2. 目录结构
        info_parts.append("### 目录结构")
        info_parts.append("```")
        info_parts.append(self._get_directory_tree(max_depth=3))
        info_parts.append("```\n")
        
        # 3. README内容（如果存在）
        readme_files = ['README.md', 'readme.md', 'README.rst', 'README.txt']
        for readme_name in readme_files:
            readme_path = self.work_dir / readme_name
            if readme_path.exists():
                content = readme_path.read_text(encoding='utf-8')
                # 限制长度，避免过长
                if len(content) > 2000:
                    content = content[:2000] + "\n... (truncated)"
                info_parts.append(f"### {readme_name} 内容")
                info_parts.append(content)
                info_parts.append("")
                break
        
        # 4. 主要文件列表
        info_parts.append("### 主要Python文件")
        py_files = list(self.work_dir.rglob("*.py"))
        # 排除一些常见的无关文件
        py_files = [f for f in py_files if not any(
            skip in str(f) for skip in ['__pycache__', '.git', 'venv', '.env']
        )]
        
        # 限制数量并排序
        py_files = sorted(py_files)[:30]
        for f in py_files:
            rel_path = f.relative_to(self.work_dir)
            info_parts.append(f"- {rel_path}")
            
        # 5. 配置文件
        info_parts.append("\n### 配置文件")
        config_patterns = ['*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '*.conf']
        config_files = []
        for pattern in config_patterns:
            config_files.extend(self.work_dir.rglob(pattern))
        
        config_files = sorted(set(config_files))[:10]
        for f in config_files:
            rel_path = f.relative_to(self.work_dir)
            info_parts.append(f"- {rel_path}")
            
        # 6. 测试文件（了解功能）
        test_files = [f for f in py_files if 'test' in str(f).lower()]
        if test_files:
            info_parts.append("\n### 测试文件")
            for f in test_files[:10]:
                rel_path = f.relative_to(self.work_dir)
                info_parts.append(f"- {rel_path}")
        
        return "\n".join(info_parts)
    
    def _get_directory_tree(self, max_depth: int = 3) -> str:
        """生成目录树（限制深度）"""
        def _tree(path: Path, prefix: str = "", depth: int = 0) -> List[str]:
            if depth >= max_depth:
                return []
                
            lines = []
            try:
                # 获取目录内容并排序
                contents = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
                # 过滤掉一些目录
                contents = [x for x in contents if x.name not in {
                    '.git', '__pycache__', '.pytest_cache', 'node_modules', 
                    '.venv', 'venv', '.idea', '.vscode'
                }]
                
                for i, item in enumerate(contents):
                    is_last = i == len(contents) - 1
                    current_prefix = "└── " if is_last else "├── "
                    next_prefix = "    " if is_last else "│   "
                    
                    lines.append(f"{prefix}{current_prefix}{item.name}")
                    
                    if item.is_dir() and depth < max_depth - 1:
                        lines.extend(_tree(item, prefix + next_prefix, depth + 1))
                        
            except PermissionError:
                lines.append(f"{prefix}├── [Permission Denied]")
                
            return lines
        
        tree_lines = [str(self.work_dir.name)]
        tree_lines.extend(_tree(self.work_dir))
        return "\n".join(tree_lines[:100])  # 限制最多100行
    
    def _log_exploration(self, start_time: datetime, result_size: int) -> None:
        """记录探索历史"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "result_size": result_size,
            "prompt_type": self._get_prompt_type()
        }
        
        # 读取现有日志
        logs = []
        if self.exploration_log.exists():
            try:
                logs = json.loads(self.exploration_log.read_text(encoding='utf-8'))
            except:
                pass
        
        # 添加新记录（保留最近10条）
        logs.append(log_entry)
        logs = logs[-10:]
        
        # 保存
        self.exploration_log.write_text(
            json.dumps(logs, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def _get_prompt_type(self) -> str:
        """识别使用的提示词类型"""
        if hasattr(self.config, 'exploration_prompt') and self.config.exploration_prompt:
            return "custom_direct"
        elif hasattr(self.config, 'exploration_prompt_file') and self.config.exploration_prompt_file:
            return "custom_file"
        else:
            return "default"
    
    def get_last_exploration_time(self) -> Optional[float]:
        """获取上次探索时间戳"""
        if self.exploration_log.exists():
            try:
                logs = json.loads(self.exploration_log.read_text(encoding='utf-8'))
                if logs:
                    last_time = datetime.fromisoformat(logs[-1]['timestamp'])
                    return last_time.timestamp()
            except:
                pass
        return None


# 示例：UML框架提示词
EXAMPLE_UML_PROMPT = """# 项目探索 - UML视角

请使用UML的4个核心视图来理解这个项目：

## 1. Use Case视图（用例视图）
分析系统提供的功能和用户交互方式。
- 识别主要的Actor（用户、外部系统等）
- 列出主要用例及其描述
- 用mermaid画出用例图

## 2. Package视图（包视图）
分析代码的模块组织和依赖关系。
- 识别主要的包/模块
- 分析它们之间的依赖关系
- 用mermaid画出包图

## 3. Class视图（类视图）
分析主要的类、接口及其关系。
- 识别核心类和接口
- 分析继承、实现、关联关系
- 用mermaid画出类图

## 4. Interaction视图（交互视图）
分析运行时对象的协作模式。
- 选择关键的执行流程
- 展示对象间的消息传递
- 用mermaid画出序列图

每个视图都要包含：
1. Mermaid图表
2. 关键发现的文字说明
3. 不确定或推测的部分要标注

基于提供的项目信息，生成完整的UML分析文档。
"""


if __name__ == "__main__":
    # 测试目录树生成
    explorer = ProjectExplorer("test", Path("."), None, None)
    print(explorer._get_directory_tree(max_depth=2))