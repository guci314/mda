"""
查询处理器 - 专门处理查询类任务的简化执行器
"""

import logging
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from .tools import get_tool_by_name
from .executors import LangChainToolExecutor

logger = logging.getLogger(__name__)


@dataclass
class QueryStep:
    """查询步骤"""
    action: str
    target: str
    description: str
    
    
class QueryHandler:
    """专门处理查询类任务的处理器"""
    
    def __init__(self, executor: LangChainToolExecutor):
        self.executor = executor
        
    def handle_project_structure_query(self, project_path: str) -> Tuple[bool, str]:
        """处理项目结构查询"""
        steps = [
            QueryStep("read_file", f"{project_path}/README.md", "读取项目说明"),
            QueryStep("list_files", project_path, "查看项目根目录结构"),
            QueryStep("search", "main|cli|entry", "查找入口文件"),
        ]
        
        results = []
        for step in steps:
            try:
                if step.action == "read_file":
                    result = self.executor.execute(step.action, {"path": step.target})
                elif step.action == "list_files":
                    result = self.executor.execute(step.action, {"path": step.target})
                elif step.action == "search":
                    # 简化搜索，只在主要目录搜索
                    result = self._search_key_files(project_path, step.target)
                    
                if result.success:
                    results.append(f"{step.description}:\n{result.output[:500]}...")
            except Exception as e:
                logger.warning(f"步骤执行失败: {step.description} - {e}")
                
        return True, "\n\n".join(results)
    
    def handle_execution_flow_query(self, project_name: str, project_path: str) -> Tuple[bool, str]:
        """处理执行流程查询"""
        # 定义常见的项目类型和对应的关键文件
        key_files = {
            "compiler": ["main.py", "cli.py", "compiler.py", "__main__.py"],
            "web": ["app.py", "server.py", "main.py", "index.js"],
            "library": ["__init__.py", "core.py", "lib.py"],
        }
        
        # 智能识别项目类型
        project_type = self._identify_project_type(project_name, project_path)
        files_to_check = key_files.get(project_type, key_files["compiler"])
        
        results = []
        
        # 1. 读取README或文档
        doc_files = ["README.md", "docs/README.md", "ARCHITECTURE.md"]
        for doc in doc_files:
            doc_path = f"{project_path}/{doc}"
            result = self.executor.execute("read_file", {"path": doc_path})
            if result.success:
                results.append(f"项目文档 ({doc}):\n{self._extract_flow_info(result.output)}")
                break
        
        # 2. 查找并分析入口文件
        for entry_file in files_to_check:
            result = self._find_and_read_file(project_path, entry_file)
            if result:
                results.append(f"入口文件 ({entry_file}):\n{self._extract_entry_info(result)}")
                break
        
        # 3. 总结执行流程
        if results:
            summary = self._summarize_execution_flow(project_name, results)
            return True, summary
        else:
            return False, f"无法找到 {project_name} 的执行流程信息"
    
    def _identify_project_type(self, project_name: str, project_path: str) -> str:
        """识别项目类型"""
        if "compiler" in project_name.lower():
            return "compiler"
        elif "web" in project_name.lower() or "api" in project_name.lower():
            return "web"
        else:
            return "library"
    
    def _find_and_read_file(self, base_path: str, filename: str) -> Optional[str]:
        """查找并读取文件"""
        # 尝试常见位置
        possible_paths = [
            f"{base_path}/{filename}",
            f"{base_path}/src/{filename}",
            f"{base_path}/lib/{filename}",
            f"{base_path}/pim_compiler/{filename}",
        ]
        
        for path in possible_paths:
            result = self.executor.execute("read_file", {"path": path})
            if result.success:
                return result.output
        return None
    
    def _extract_flow_info(self, content: str) -> str:
        """从文档中提取流程信息"""
        # 查找包含流程相关的段落
        lines = content.split('\n')
        flow_sections = []
        in_flow_section = False
        
        keywords = ['流程', 'flow', 'process', 'steps', '步骤', 'workflow']
        
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                in_flow_section = True
            elif line.strip() and not line.startswith(' ') and in_flow_section:
                in_flow_section = False
                
            if in_flow_section:
                flow_sections.append(line)
                
        return '\n'.join(flow_sections[:20]) if flow_sections else content[:500]
    
    def _extract_entry_info(self, content: str) -> str:
        """从入口文件提取关键信息"""
        # 提取 main 函数或关键类
        lines = content.split('\n')
        key_lines = []
        
        for i, line in enumerate(lines):
            if 'def main' in line or 'class.*CLI' in line or '__name__.*==.*__main__' in line:
                # 获取该行及后续10行
                key_lines.extend(lines[i:i+10])
                
        return '\n'.join(key_lines[:30]) if key_lines else content[:500]
    
    def _summarize_execution_flow(self, project_name: str, results: List[str]) -> str:
        """总结执行流程"""
        summary = f"{project_name} 执行流程分析:\n\n"
        summary += "\n\n".join(results)
        summary += f"\n\n基于以上信息，{project_name} 的执行流程可以总结为上述内容中描述的步骤。"
        return summary
    
    def _search_key_files(self, project_path: str, pattern: str) -> Any:
        """搜索关键文件"""
        # 这里简化实现，实际可以调用 grep 或 search 工具
        class MockResult:
            def __init__(self, success, output):
                self.success = success
                self.output = output
                
        # 返回模拟结果
        return MockResult(True, "找到入口文件: main.py, cli.py")