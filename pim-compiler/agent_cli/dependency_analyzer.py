"""
依赖关系分析器 - 确保模块按正确顺序创建
"""
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """依赖类型"""
    IMPORT = "import"          # 导入依赖
    INHERITANCE = "inheritance" # 继承依赖
    REFERENCE = "reference"     # 引用依赖
    SCHEMA = "schema"          # 数据模式依赖


@dataclass
class Dependency:
    """依赖关系"""
    source: str          # 依赖方
    target: str          # 被依赖方
    type: DependencyType # 依赖类型
    details: str         # 具体细节（如导入的类名）


class DependencyAnalyzer:
    """依赖关系分析器
    
    分析代码中的依赖关系，确保：
    1. 基础模块先于依赖模块创建
    2. 数据模型先于使用它们的API创建
    3. 配置文件先于使用配置的模块创建
    """
    
    def __init__(self):
        self.dependencies: List[Dependency] = []
        self.module_graph: Dict[str, Set[str]] = {}  # 模块依赖图
        
    def analyze_code_dependencies(self, code: str, file_path: str) -> List[Dependency]:
        """分析代码中的依赖关系"""
        deps = []
        
        # 1. 分析导入依赖
        import_patterns = [
            r'from\s+(\S+)\s+import\s+(.+)',  # from ... import ...
            r'import\s+(\S+)',                  # import ...
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, code)
            for match in matches:
                if isinstance(match, tuple):
                    module_path = match[0]
                    imported_items = match[1] if len(match) > 1 else ""
                else:
                    module_path = match
                    imported_items = ""
                    
                # 转换相对导入为文件路径
                target_file = self._resolve_import_path(module_path, file_path)
                if target_file:
                    deps.append(Dependency(
                        source=file_path,
                        target=target_file,
                        type=DependencyType.IMPORT,
                        details=imported_items
                    ))
                    
        # 2. 分析继承依赖
        class_patterns = [
            r'class\s+\w+\s*\(\s*(\w+)\s*\)',  # class Child(Parent)
        ]
        
        for pattern in class_patterns:
            matches = re.findall(pattern, code)
            for parent_class in matches:
                # 查找父类定义的位置
                if parent_class not in ['object', 'BaseModel', 'Base', 'ABC']:
                    deps.append(Dependency(
                        source=file_path,
                        target=f"*/{parent_class}.py",  # 需要搜索
                        type=DependencyType.INHERITANCE,
                        details=parent_class
                    ))
                    
        # 3. 分析数据模式依赖（Pydantic/SQLAlchemy）
        schema_patterns = [
            r'(\w+)Create',    # UserCreate -> User
            r'(\w+)Update',    # UserUpdate -> User
            r'(\w+)Response',  # UserResponse -> User
        ]
        
        for pattern in schema_patterns:
            matches = re.findall(pattern, code)
            for base_model in matches:
                deps.append(Dependency(
                    source=file_path,
                    target=f"*/models/{base_model.lower()}.py",
                    type=DependencyType.SCHEMA,
                    details=f"{base_model} model"
                ))
                
        return deps
        
    def _resolve_import_path(self, import_path: str, current_file: str) -> Optional[str]:
        """解析导入路径为实际文件路径"""
        # 处理相对导入
        if import_path.startswith('.'):
            # 计算相对层级
            level = len(import_path) - len(import_path.lstrip('.'))
            module_parts = import_path[level:].split('.')
            
            # 从当前文件路径向上
            current_parts = current_file.split('/')
            if level > 0:
                current_parts = current_parts[:-level]
                
            # 构建目标路径
            target_parts = current_parts[:-1] + module_parts
            return '/'.join(target_parts) + '.py'
            
        # 处理绝对导入（项目内）
        elif not import_path.startswith(('os', 'sys', 'json', 'typing')):
            # 假设是项目内的模块
            return import_path.replace('.', '/') + '.py'
            
        return None
        
    def build_dependency_graph(self, file_dependencies: Dict[str, List[str]]) -> Dict[str, Set[str]]:
        """构建依赖图"""
        graph = {}
        
        for file, deps in file_dependencies.items():
            if file not in graph:
                graph[file] = set()
            graph[file].update(deps)
            
        return graph
        
    def get_creation_order(self, files: List[str]) -> List[str]:
        """获取文件创建顺序（拓扑排序）"""
        # 构建依赖图
        graph = {f: set() for f in files}
        in_degree = {f: 0 for f in files}
        
        # 填充依赖关系
        for dep in self.dependencies:
            if dep.source in files and dep.target in files:
                if dep.target not in graph[dep.source]:
                    graph[dep.source].add(dep.target)
                    in_degree[dep.target] += 1
                    
        # 拓扑排序
        queue = [f for f in files if in_degree[f] == 0]
        result = []
        
        while queue:
            # 优先处理基础模块
            queue.sort(key=lambda x: self._get_module_priority(x))
            current = queue.pop(0)
            result.append(current)
            
            # 更新依赖它的模块
            for dependent in files:
                if current in graph.get(dependent, set()):
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
                        
        # 检查循环依赖
        if len(result) != len(files):
            logger.warning("Detected circular dependencies!")
            # 添加剩余文件
            for f in files:
                if f not in result:
                    result.append(f)
                    
        return result
        
    def _get_module_priority(self, file_path: str) -> int:
        """获取模块优先级（越小越优先）"""
        priorities = {
            'config': 1,      # 配置文件最优先
            'database': 2,    # 数据库连接
            'models': 3,      # 数据模型
            'schemas': 4,     # 数据模式
            'services': 5,    # 业务逻辑
            'api': 6,         # API端点
            'main': 7,        # 主程序
            'tests': 8,       # 测试最后
        }
        
        for key, priority in priorities.items():
            if key in file_path:
                return priority
                
        return 99  # 默认优先级
        
    def suggest_missing_dependencies(self, code: str, file_path: str) -> List[Tuple[str, str]]:
        """建议缺失的依赖文件"""
        suggestions = []
        
        # 检查导入的模块是否应该存在
        import_pattern = r'from\s+(\S+)\s+import\s+(.+)'
        matches = re.findall(import_pattern, code)
        
        for module, items in matches:
            # 检查是否是相对导入
            if module.startswith('..'):
                # 需要创建 schemas 文件
                if 'Create' in items or 'Update' in items or 'Response' in items:
                    base_name = items.split(',')[0].strip()
                    base_name = base_name.replace('Create', '').replace('Update', '').replace('Response', '')
                    suggested_file = f"schemas/{base_name.lower()}.py"
                    suggested_content = f"""\"\"\"
{base_name} 数据模式定义
\"\"\"
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class {base_name}Base(BaseModel):
    \"\"\"基础{base_name}模式\"\"\"
    # TODO: 添加基础字段
    pass


class {base_name}Create({base_name}Base):
    \"\"\"创建{base_name}的模式\"\"\"
    pass


class {base_name}Update({base_name}Base):
    \"\"\"更新{base_name}的模式\"\"\"
    pass


class {base_name}Response({base_name}Base):
    \"\"\"响应{base_name}的模式\"\"\"
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
"""
                    suggestions.append((suggested_file, suggested_content))
                    
        return suggestions


def integrate_dependency_analyzer(agent_cli):
    """将依赖分析器集成到 Agent CLI"""
    
    analyzer = DependencyAnalyzer()
    
    # 在动作决策时考虑依赖关系
    original_action_decider = agent_cli._action_decider
    
    def dependency_aware_action_decider(step):
        """考虑依赖关系的动作决策器"""
        
        # 如果是创建文件的步骤，分析依赖关系
        if hasattr(step, 'deliverables'):
            # 收集已创建的文件
            created_files = agent_cli.context.get('created_files', [])
            
            # 分析待创建文件的依赖关系
            pending_files = []
            for deliverable in step.deliverables:
                if '文件' in deliverable or '.py' in deliverable:
                    # 提取文件路径
                    file_match = re.search(r'(\S+\.py)', deliverable)
                    if file_match:
                        pending_files.append(file_match.group(1))
                        
            # 获取创建顺序
            if pending_files:
                ordered_files = analyzer.get_creation_order(pending_files)
                
                # 找到下一个应该创建的文件
                for file in ordered_files:
                    if file not in created_files:
                        # 修改决策，优先创建这个文件
                        logger.info(f"Dependency analyzer suggests creating: {file}")
                        break
                        
        return original_action_decider(step)
        
    agent_cli._action_decider = dependency_aware_action_decider
    agent_cli.dependency_analyzer = analyzer