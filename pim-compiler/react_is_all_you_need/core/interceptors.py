"""
拦截器实现 - 条件反射的处理器
当前实现JSONInterceptor，未来可扩展为TinyLLMInterceptor
"""

import json
import re
from typing import Optional, Dict, Any, List
from pathlib import Path


class JSONInterceptor:
    """JSON格式的快速路径拦截器"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化拦截器

        Args:
            config_file: 配置文件路径，包含拦截规则
        """
        self.rules = {}
        if config_file and Path(config_file).exists():
            self.load_config(config_file)

    def __call__(self, task: str) -> Optional[str]:
        """
        拦截器主函数

        Args:
            task: 输入任务

        Returns:
            如果匹配返回结果，否则返回None
        """
        try:
            # 尝试JSON解析
            data = json.loads(task)

            # 检查action字段
            if 'action' in data:
                return self.handle_action(data)

            # 检查query字段
            if 'query' in data:
                return self.handle_query(data)

            # 检查command字段
            if 'command' in data:
                return self.handle_command(data)

        except json.JSONDecodeError:
            # 不是JSON格式，不处理
            pass

        return None

    def handle_action(self, data: Dict[str, Any]) -> Optional[str]:
        """处理action类型的请求"""
        action = data.get('action')

        # 查找对应的处理器
        if action in self.rules.get('actions', {}):
            handler = self.rules['actions'][action]
            if isinstance(handler, str):
                return handler
            elif callable(handler):
                return handler(data)

        return None

    def handle_query(self, data: Dict[str, Any]) -> Optional[str]:
        """处理query类型的请求"""
        query = data.get('query')

        # 简单的查询处理
        if query in self.rules.get('queries', {}):
            return self.rules['queries'][query]

        return None

    def handle_command(self, data: Dict[str, Any]) -> Optional[str]:
        """处理command类型的请求"""
        command = data.get('command')

        if command in self.rules.get('commands', {}):
            return self.rules['commands'][command]

        return None

    def load_config(self, config_file: str):
        """加载配置文件"""
        with open(config_file, 'r', encoding='utf-8') as f:
            self.rules = json.load(f)

    def register_rule(self, rule_type: str, key: str, response: str):
        """动态注册规则"""
        if rule_type not in self.rules:
            self.rules[rule_type] = {}
        self.rules[rule_type][key] = response


class RegexInterceptor:
    """正则表达式拦截器"""

    def __init__(self, patterns_file: Optional[str] = None):
        """
        初始化正则拦截器

        Args:
            patterns_file: 模式文件路径
        """
        self.patterns = []
        if patterns_file and Path(patterns_file).exists():
            self.load_patterns(patterns_file)

    def __call__(self, task: str) -> Optional[str]:
        """
        拦截器主函数

        Args:
            task: 输入任务

        Returns:
            如果匹配返回结果，否则返回None
        """
        for pattern in self.patterns:
            if pattern['regex'].search(task):
                return pattern['response']

        return None

    def load_patterns(self, patterns_file: str):
        """加载模式文件"""
        with open(patterns_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                self.patterns.append({
                    'regex': re.compile(item['pattern']),
                    'response': item['response'],
                    'priority': item.get('priority', 50)
                })

        # 按优先级排序
        self.patterns.sort(key=lambda x: -x['priority'])

    def register_pattern(self, pattern: str, response: str, priority: int = 50):
        """动态注册模式"""
        self.patterns.append({
            'regex': re.compile(pattern),
            'response': response,
            'priority': priority
        })
        # 重新排序
        self.patterns.sort(key=lambda x: -x['priority'])


class CompositeInterceptor:
    """组合拦截器 - 支持多种策略"""

    def __init__(self):
        """初始化组合拦截器"""
        self.interceptors = []

    def __call__(self, task: str) -> Optional[str]:
        """
        依次尝试所有拦截器

        Args:
            task: 输入任务

        Returns:
            第一个匹配的结果，或None
        """
        for interceptor in self.interceptors:
            result = interceptor(task)
            if result is not None:
                return result

        return None

    def add_interceptor(self, interceptor):
        """添加拦截器"""
        self.interceptors.append(interceptor)

    def remove_interceptor(self, interceptor):
        """移除拦截器"""
        if interceptor in self.interceptors:
            self.interceptors.remove(interceptor)


# 未来的拦截器接口（占位）
class TinyLLMInterceptor:
    """
    轻量级LLM拦截器（未来实现）
    当有合适的轻量级模型时实现
    """

    def __init__(self, model: str = 'phi-3-mini'):
        # TODO: 加载轻量级模型
        raise NotImplementedError("等待轻量级LLM可用")

    def __call__(self, task: str) -> Optional[str]:
        # TODO: 使用轻量级LLM进行模式匹配
        pass