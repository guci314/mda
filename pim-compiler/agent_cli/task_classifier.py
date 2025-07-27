"""
任务分类器 - 识别任务类型并采用适当的执行策略
"""

import re
from typing import Tuple, Dict, Any
from enum import Enum


class TaskType(Enum):
    """任务类型枚举"""
    QUERY = "query"           # 查询/分析类任务
    CREATE = "create"         # 创建/实现类任务
    MODIFY = "modify"         # 修改/优化类任务
    DEBUG = "debug"           # 调试/修复类任务
    EXPLAIN = "explain"       # 解释/文档类任务


class TaskClassifier:
    """任务分类器 - 基于关键词和模式识别任务类型"""
    
    def __init__(self):
        # 定义任务类型的关键词模式
        self.patterns = {
            TaskType.QUERY: {
                'keywords': ['是什么', '有哪些', '查找', '分析', '了解', '查看', '流程是什么'],
                'patterns': [
                    r'.*的(执行)?流程是什么',
                    r'分析.*结构',
                    r'了解.*实现',
                    r'查看.*代码',
                ]
            },
            TaskType.CREATE: {
                'keywords': ['创建', '实现', '编写', '生成', '开发', '构建'],
                'patterns': [
                    r'创建.*程序',
                    r'实现.*功能',
                    r'编写.*代码',
                    r'生成.*文件',
                ]
            },
            TaskType.MODIFY: {
                'keywords': ['修改', '优化', '重构', '改进', '更新'],
                'patterns': [
                    r'修改.*代码',
                    r'优化.*性能',
                    r'重构.*模块',
                ]
            },
            TaskType.DEBUG: {
                'keywords': ['调试', '修复', '解决', '错误', 'bug'],
                'patterns': [
                    r'修复.*错误',
                    r'解决.*问题',
                    r'调试.*代码',
                ]
            },
            TaskType.EXPLAIN: {
                'keywords': ['解释', '说明', '文档', '注释', '描述'],
                'patterns': [
                    r'解释.*原理',
                    r'说明.*功能',
                    r'添加.*注释',
                ]
            }
        }
    
    def classify(self, task: str) -> Tuple[TaskType, float]:
        """
        对任务进行分类
        
        Args:
            task: 任务描述
            
        Returns:
            (任务类型, 置信度)
        """
        task_lower = task.lower()
        scores = {}
        
        for task_type, config in self.patterns.items():
            score = 0.0
            
            # 检查关键词
            for keyword in config['keywords']:
                if keyword in task:
                    score += 0.3
            
            # 检查正则模式
            for pattern in config['patterns']:
                if re.search(pattern, task):
                    score += 0.5
            
            scores[task_type] = min(score, 1.0)
        
        # 选择得分最高的类型
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        # 如果置信度太低，默认为查询类型
        if confidence < 0.3:
            return TaskType.QUERY, 0.5
        
        return best_type, confidence
    
    def get_execution_strategy(self, task_type: TaskType) -> Dict[str, Any]:
        """
        根据任务类型返回执行策略
        
        Args:
            task_type: 任务类型
            
        Returns:
            执行策略配置
        """
        strategies = {
            TaskType.QUERY: {
                'max_steps': 3,
                'focus': 'understanding',
                'tools_priority': ['read_file', 'list_files', 'search'],
                'avoid_actions': ['write_file', 'create_directory'],
                'planning_hint': '专注于理解和分析现有代码，不要创建新文件'
            },
            TaskType.CREATE: {
                'max_steps': 10,
                'focus': 'implementation',
                'tools_priority': ['write_file', 'create_directory', 'python_repl'],
                'avoid_actions': [],
                'planning_hint': '按照里程碑方式规划实现步骤'
            },
            TaskType.MODIFY: {
                'max_steps': 5,
                'focus': 'refactoring',
                'tools_priority': ['read_file', 'write_file', 'search'],
                'avoid_actions': [],
                'planning_hint': '先理解现有代码，再进行修改'
            },
            TaskType.DEBUG: {
                'max_steps': 7,
                'focus': 'troubleshooting',
                'tools_priority': ['read_file', 'python_repl', 'search'],
                'avoid_actions': [],
                'planning_hint': '定位问题根源，逐步修复'
            },
            TaskType.EXPLAIN: {
                'max_steps': 3,
                'focus': 'documentation',
                'tools_priority': ['read_file', 'write_file'],
                'avoid_actions': ['python_repl'],
                'planning_hint': '清晰解释代码逻辑和设计思路'
            }
        }
        
        return strategies.get(task_type, strategies[TaskType.QUERY])


# 使用示例
if __name__ == "__main__":
    classifier = TaskClassifier()
    
    test_tasks = [
        "pim-compiler的执行流程是什么？",
        "创建一个 Python 程序 hello.py",
        "优化代码性能",
        "修复登录功能的bug",
        "解释这段代码的工作原理"
    ]
    
    for task in test_tasks:
        task_type, confidence = classifier.classify(task)
        strategy = classifier.get_execution_strategy(task_type)
        print(f"\n任务: {task}")
        print(f"类型: {task_type.value} (置信度: {confidence:.2f})")
        print(f"策略: 最大步骤={strategy['max_steps']}, 焦点={strategy['focus']}")