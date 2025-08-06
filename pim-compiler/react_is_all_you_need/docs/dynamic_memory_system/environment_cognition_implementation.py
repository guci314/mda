#!/usr/bin/env python3
"""环境认知实现示例

展示如何将环境认知整合到 GenericReactAgent 中，
取代独立的 world_overview.md 生成机制。
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, Optional, List
from collections import defaultdict
import networkx as nx


class EnvironmentCognition:
    """环境认知子系统 - 通过使用来理解工作环境"""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.cognition_dir = workspace_dir / ".agent_cognition"
        self.cognition_dir.mkdir(exist_ok=True)
        
        # 核心数据结构
        self.file_access_log = defaultdict(lambda: {
            'count': 0,
            'last_access': None,
            'contexts': [],
            'inferred_purpose': None,
            'confidence': 0.0
        })
        
        # 文件关系图
        self.file_graph = nx.DiGraph()
        
        # 项目理解
        self.project_insights = {
            'type': None,
            'main_language': None,
            'frameworks': set(),
            'patterns': [],
            'key_files': []
        }
        
        # 加载已有认知
        self._load_cognition()
    
    def learn_from_file_access(self, file_path: Path, action: str, content_preview: str = ""):
        """从文件访问中学习"""
        relative_path = file_path.relative_to(self.workspace_dir)
        
        # 更新访问记录
        record = self.file_access_log[str(relative_path)]
        record['count'] += 1
        record['last_access'] = datetime.now().isoformat()
        record['contexts'].append({
            'action': action,
            'preview': content_preview[:200],
            'timestamp': datetime.now().isoformat()
        })
        
        # 推断文件用途
        if not record['inferred_purpose'] or record['confidence'] < 0.8:
            purpose, confidence = self._infer_file_purpose(file_path, action, content_preview)
            if confidence > record['confidence']:
                record['inferred_purpose'] = purpose
                record['confidence'] = confidence
        
        # 更新项目理解
        self._update_project_understanding(file_path, content_preview)
        
        # 保存认知
        self._save_cognition()
    
    def learn_from_file_relationship(self, from_file: Path, to_file: Path, relationship: str):
        """学习文件之间的关系"""
        from_rel = from_file.relative_to(self.workspace_dir)
        to_rel = to_file.relative_to(self.workspace_dir)
        
        self.file_graph.add_edge(str(from_rel), str(to_rel), relationship=relationship)
        
    def _infer_file_purpose(self, file_path: Path, action: str, content: str) -> tuple[str, float]:
        """推断文件用途，返回 (用途描述, 置信度)"""
        name_lower = file_path.name.lower()
        
        # 基于文件名的强规则
        if name_lower == 'readme.md':
            return "项目说明文档", 1.0
        if name_lower == 'requirements.txt':
            return "Python依赖列表", 1.0
        if name_lower == 'package.json':
            return "Node.js项目配置", 1.0
        
        # 基于扩展名和路径
        if file_path.suffix == '.py':
            if 'test' in name_lower or 'test' in str(file_path):
                return "测试代码", 0.9
            if name_lower == '__init__.py':
                return "Python包标识", 0.95
            if 'setup' in name_lower:
                return "安装配置", 0.85
                
        # 基于内容
        if content:
            content_lower = content.lower()
            if 'def test_' in content or 'class test' in content_lower:
                return "测试代码", 0.95
            if 'router = ' in content or '@app.' in content:
                return "API路由", 0.85
            if 'class.*model' in content_lower:
                return "数据模型", 0.8
                
        # 基于操作
        if action == "execute":
            return "可执行脚本", 0.8
            
        return "待确定", 0.3
    
    def _update_project_understanding(self, file_path: Path, content: str):
        """更新对项目的整体理解"""
        # 语言检测
        if file_path.suffix == '.py':
            self.project_insights['main_language'] = 'Python'
        elif file_path.suffix in ['.js', '.ts']:
            if not self.project_insights['main_language']:
                self.project_insights['main_language'] = 'JavaScript/TypeScript'
                
        # 框架检测
        if content:
            if 'from fastapi' in content or 'import fastapi' in content:
                self.project_insights['frameworks'].add('FastAPI')
            if 'from django' in content:
                self.project_insights['frameworks'].add('Django')
            if 'import react' in content.lower():
                self.project_insights['frameworks'].add('React')
                
        # 识别关键文件
        access_count = self.file_access_log[str(file_path)]['count']
        if access_count > 5:
            self.project_insights['key_files'].append(str(file_path))
            self.project_insights['key_files'] = sorted(
                set(self.project_insights['key_files']),
                key=lambda f: self.file_access_log[f]['count'],
                reverse=True
            )[:10]  # 保留前10个
    
    def get_environment_summary(self) -> str:
        """生成环境理解摘要"""
        total_files = len(self.file_access_log)
        high_confidence_files = sum(1 for f in self.file_access_log.values() if f['confidence'] > 0.8)
        
        summary = f"""# 环境认知摘要

## 探索进度
- 已接触文件：{total_files}
- 高置信度理解：{high_confidence_files} ({high_confidence_files/max(total_files, 1)*100:.1f}%)
- 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 项目理解
- 主要语言：{self.project_insights['main_language'] or '待确定'}
- 使用框架：{', '.join(self.project_insights['frameworks']) or '待发现'}
- 项目类型：{self._infer_project_type()}

## 核心文件（按使用频率）
"""
        
        for file in self.project_insights['key_files'][:5]:
            record = self.file_access_log[file]
            summary += f"- `{file}` - {record['inferred_purpose']} (访问{record['count']}次)\n"
            
        # 添加文件关系
        if self.file_graph.number_of_edges() > 0:
            summary += "\n## 发现的文件关系\n"
            for from_f, to_f, data in list(self.file_graph.edges(data=True))[:5]:
                summary += f"- {from_f} → {to_f} ({data.get('relationship', 'imports')})\n"
                
        # 添加使用模式
        summary += "\n## 使用模式\n"
        summary += self._analyze_usage_patterns()
        
        return summary
    
    def _infer_project_type(self) -> str:
        """推断项目类型"""
        frameworks = self.project_insights['frameworks']
        
        if 'FastAPI' in frameworks or 'Django' in frameworks:
            return "Web API 服务"
        if 'React' in frameworks or 'Vue' in frameworks:
            return "前端应用"
        if self.project_insights['main_language'] == 'Python':
            if any('notebook' in f for f in self.file_access_log):
                return "数据分析项目"
            return "Python 项目"
            
        return "类型待确定"
    
    def _analyze_usage_patterns(self) -> str:
        """分析使用模式"""
        patterns = []
        
        # 分析访问时间模式
        access_times = []
        for record in self.file_access_log.values():
            if record['last_access']:
                access_times.append(datetime.fromisoformat(record['last_access']))
                
        if access_times:
            # 这里可以添加更复杂的模式分析
            patterns.append("- 活跃开发中")
            
        # 分析文件类型分布
        file_types = defaultdict(int)
        for file_path in self.file_access_log:
            ext = Path(file_path).suffix
            if ext:
                file_types[ext] += 1
                
        if file_types:
            main_type = max(file_types.items(), key=lambda x: x[1])
            patterns.append(f"- 主要处理 {main_type[0]} 文件")
            
        return '\n'.join(patterns) if patterns else "- 模式分析中..."
    
    def _save_cognition(self):
        """保存认知数据"""
        data = {
            'file_access_log': dict(self.file_access_log),
            'project_insights': {
                **self.project_insights,
                'frameworks': list(self.project_insights['frameworks'])
            },
            'file_graph': nx.node_link_data(self.file_graph)
        }
        
        cognition_file = self.cognition_dir / "environment_cognition.json"
        with open(cognition_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_cognition(self):
        """加载已有认知"""
        cognition_file = self.cognition_dir / "environment_cognition.json"
        if cognition_file.exists():
            try:
                with open(cognition_file) as f:
                    data = json.load(f)
                    
                self.file_access_log.update(data.get('file_access_log', {}))
                
                insights = data.get('project_insights', {})
                self.project_insights.update({
                    **insights,
                    'frameworks': set(insights.get('frameworks', []))
                })
                
                graph_data = data.get('file_graph')
                if graph_data:
                    self.file_graph = nx.node_link_graph(graph_data)
                    
            except Exception as e:
                print(f"加载认知数据失败: {e}")


class EnhancedGenericReactAgent:
    """增强的 GenericReactAgent - 集成环境认知"""
    
    def __init__(self, config, name=None):
        # ... 原有初始化代码 ...
        
        # 初始化环境认知（取代 world_overview）
        self.env_cognition = EnvironmentCognition(Path(config.work_dir))
        
        # 不再检查 world_overview
        # self._check_world_overview()  # 删除这行
    
    def read_file(self, file_path: str) -> str:
        """增强的文件读取 - 带环境学习"""
        content = self._original_read_file(file_path)
        
        # 环境学习
        self.env_cognition.learn_from_file_access(
            Path(file_path),
            action="read",
            content_preview=content[:500]
        )
        
        return content
    
    def write_file(self, file_path: str, content: str):
        """增强的文件写入 - 带环境学习"""
        self._original_write_file(file_path, content)
        
        # 环境学习
        self.env_cognition.learn_from_file_access(
            Path(file_path),
            action="write",
            content_preview=content[:500]
        )
    
    def _update_extracted_knowledge_sync(self, messages):
        """更新知识时包含环境认知"""
        # ... 原有知识提取逻辑 ...
        
        # 获取环境认知摘要
        env_summary = self.env_cognition.get_environment_summary()
        
        # 构建包含环境认知的提示词
        prompt = f"""
## 环境认知
{env_summary}

## 任务执行历史
{task_history}

请基于以上信息更新长期记忆...
"""
        
        # ... 继续原有逻辑 ...


# 使用示例
if __name__ == "__main__":
    # 模拟使用
    workspace = Path("./test_workspace")
    workspace.mkdir(exist_ok=True)
    
    cognition = EnvironmentCognition(workspace)
    
    # 模拟文件访问
    cognition.learn_from_file_access(
        workspace / "src" / "main.py",
        action="read",
        content_preview="from fastapi import FastAPI\napp = FastAPI()"
    )
    
    cognition.learn_from_file_access(
        workspace / "tests" / "test_main.py", 
        action="read",
        content_preview="def test_api():\n    assert True"
    )
    
    # 学习文件关系
    cognition.learn_from_file_relationship(
        workspace / "src" / "routes.py",
        workspace / "src" / "models.py",
        "imports"
    )
    
    # 生成摘要
    print(cognition.get_environment_summary())