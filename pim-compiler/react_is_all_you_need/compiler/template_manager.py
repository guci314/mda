"""
模板管理器

负责模板的存储、匹配和重用。
"""

import json
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


@dataclass
class Parameter:
    """参数定义"""
    name: str
    type: str  # number, string, enum等
    description: str
    extraction_hints: List[str] = None
    
    def __post_init__(self):
        if self.extraction_hints is None:
            self.extraction_hints = []


@dataclass
class TaskTemplate:
    """任务模板"""
    id: str
    pattern: str  # 如："列出{metric}大于{threshold}的{resource}"
    parameters: List[Parameter]
    compiled_function: str
    examples: List[str]
    created_at: str
    use_count: int = 0
    last_used: str = None
    
    def to_summary(self) -> Dict[str, Any]:
        """返回模板摘要，用于LLM匹配"""
        return {
            "id": self.id,
            "pattern": self.pattern,
            "parameters": [{"name": p.name, "type": p.type} for p in self.parameters],
            "examples": self.examples[:3]  # 只返回前3个例子
        }


@dataclass
class MatchResult:
    """匹配结果"""
    can_reuse: bool
    template_id: Optional[str] = None
    extracted_parameters: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    reasoning: str = ""


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, storage_path: str = None):
        self.templates: Dict[str, TaskTemplate] = {}
        self.storage_path = storage_path
        if storage_path:
            self.load_templates()
    
    def add_template(self, template: TaskTemplate) -> None:
        """添加新模板"""
        self.templates[template.id] = template
        if self.storage_path:
            self.save_templates()
    
    def get_template(self, template_id: str) -> Optional[TaskTemplate]:
        """获取模板"""
        return self.templates.get(template_id)
    
    def get_templates_summary(self) -> List[Dict[str, Any]]:
        """获取所有模板的摘要"""
        return [template.to_summary() for template in self.templates.values()]
    
    def update_usage(self, template_id: str) -> None:
        """更新模板使用统计"""
        if template_id in self.templates:
            template = self.templates[template_id]
            template.use_count += 1
            template.last_used = datetime.now().isoformat()
            if self.storage_path:
                self.save_templates()
    
    def save_templates(self) -> None:
        """保存模板到文件"""
        if not self.storage_path:
            return
        
        data = {
            template_id: asdict(template)
            for template_id, template in self.templates.items()
        }
        
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_templates(self) -> None:
        """从文件加载模板"""
        if not self.storage_path:
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.templates = {}
            for template_id, template_data in data.items():
                # 重建Parameter对象
                params = [
                    Parameter(**param_data) 
                    for param_data in template_data['parameters']
                ]
                template_data['parameters'] = params
                
                # 创建TaskTemplate
                self.templates[template_id] = TaskTemplate(**template_data)
                
        except FileNotFoundError:
            self.templates = {}
    
    def find_similar_templates(self, task: str, limit: int = 10) -> List[TaskTemplate]:
        """查找可能相关的模板（简单关键词匹配）"""
        # 提取任务中的关键词
        keywords = set(task.lower().split())
        
        # 计算每个模板的相关度
        scores = []
        for template in self.templates.values():
            # 模板模式中的关键词
            pattern_keywords = set(template.pattern.lower().split())
            # 示例中的关键词
            example_keywords = set()
            for example in template.examples:
                example_keywords.update(example.lower().split())
            
            # 计算交集
            pattern_score = len(keywords & pattern_keywords)
            example_score = len(keywords & example_keywords) * 0.5
            total_score = pattern_score + example_score
            
            if total_score > 0:
                scores.append((total_score, template))
        
        # 排序并返回前N个
        scores.sort(key=lambda x: x[0], reverse=True)
        return [template for _, template in scores[:limit]]
    
    def generate_template_id(self, pattern: str) -> str:
        """生成模板ID"""
        # 使用pattern的hash作为ID
        return hashlib.md5(pattern.encode()).hexdigest()[:8]