#!/usr/bin/env python3
"""
智能计算器模块
支持基础运算、科学计算、单位转换等
"""

import re
import math
import operator
from typing import Union, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class CalculationResult:
    """计算结果"""
    expression: str
    result: Union[int, float, str]
    steps: list = None
    error: str = None
    success: bool = True


class SmartCalculator:
    """智能计算器"""

    def __init__(self):
        # 基础运算符
        self.operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '**': operator.pow,
            '^': operator.pow,
        }

        # 数学函数
        self.math_functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'abs': abs,
            'round': round,
            'floor': math.floor,
            'ceil': math.ceil,
        }

        # 常量
        self.constants = {
            'pi': math.pi,
            'e': math.e,
            'π': math.pi,
        }

        # 单位转换
        self.unit_conversions = {
            # 长度
            'km_to_m': 1000,
            'm_to_cm': 100,
            'cm_to_mm': 10,
            'mile_to_km': 1.60934,

            # 重量
            'kg_to_g': 1000,
            'g_to_mg': 1000,
            'pound_to_kg': 0.453592,

            # 温度（特殊处理）
            'celsius_to_fahrenheit': lambda c: c * 9/5 + 32,
            'fahrenheit_to_celsius': lambda f: (f - 32) * 5/9,
        }

    def calculate(self, expression: str) -> CalculationResult:
        """
        计算表达式
        支持：基础运算、科学计算、单位转换、中文数字
        """
        try:
            # 预处理表达式
            processed = self._preprocess_expression(expression)

            # 尝试不同的计算方式

            # 1. 单位转换
            if '转' in expression or 'to' in expression.lower():
                return self._handle_unit_conversion(expression)

            # 2. 百分比计算
            if '%' in expression and '的' in expression:
                return self._handle_percentage(expression)

            # 3. 标准数学表达式
            result = self._evaluate_expression(processed)

            return CalculationResult(
                expression=expression,
                result=result,
                success=True
            )

        except Exception as e:
            return CalculationResult(
                expression=expression,
                result=None,
                error=str(e),
                success=False
            )

    def _preprocess_expression(self, expr: str) -> str:
        """预处理表达式"""
        # 保存原始表达式用于特殊处理
        original = expr

        # 移除空格
        expr = expr.replace(' ', '')

        # 处理特殊数学表达式
        # 根号
        expr = re.sub(r'根号(\d+)', r'sqrt(\1)', expr)
        expr = re.sub(r'√(\d+)', r'sqrt(\1)', expr)

        # 平方和立方
        expr = re.sub(r'(\d+)的平方', r'\1**2', expr)
        expr = re.sub(r'(\d+)的立方', r'\1**3', expr)
        expr = re.sub(r'(\d+)\^(\d+)', r'\1**\2', expr)

        # 中文数字转换
        chinese_to_arabic = {
            '零': '0', '一': '1', '二': '2', '三': '3', '四': '4',
            '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
            '十': '10', '百': '100', '千': '1000', '万': '10000',
            '加': '+', '减': '-', '乘': '*', '除': '/',
            '加上': '+', '减去': '-', '乘以': '*', '除以': '/',
        }

        for ch, ar in chinese_to_arabic.items():
            expr = expr.replace(ch, ar)

        # 处理自然语言
        expr = re.sub(r'等于多少[？?]?', '', expr)
        expr = re.sub(r'是多少[？?]?', '', expr)
        expr = re.sub(r'的结果', '', expr)
        expr = re.sub(r'计算', '', expr)

        # 替换常量
        for name, value in self.constants.items():
            expr = expr.replace(name, str(value))

        return expr

    def _evaluate_expression(self, expr: str) -> float:
        """安全地评估数学表达式"""
        # 构建安全的命名空间
        safe_dict = {
            '__builtins__': {},
            **self.math_functions,
            **self.constants
        }

        # 使用eval计算（已限制命名空间）
        result = eval(expr, safe_dict)

        # 格式化结果
        if isinstance(result, float):
            # 如果是整数，返回整数
            if result.is_integer():
                return int(result)
            # 保留合理的小数位数
            return round(result, 10)

        return result

    def _handle_percentage(self, expr: str) -> CalculationResult:
        """处理百分比计算"""
        # 匹配模式：X的Y%
        pattern = r'(\d+(?:\.\d+)?)\s*的\s*(\d+(?:\.\d+)?)\s*%'
        match = re.search(pattern, expr)

        if match:
            base = float(match.group(1))
            percent = float(match.group(2))
            result = base * percent / 100

            return CalculationResult(
                expression=expr,
                result=result,
                steps=[f"{base} × {percent}% = {base} × {percent/100} = {result}"]
            )

        raise ValueError(f"无法解析百分比表达式: {expr}")

    def _handle_unit_conversion(self, expr: str) -> CalculationResult:
        """处理单位转换"""
        # 简单的单位转换示例
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*公里.*转.*米', 'km_to_m'),
            (r'(\d+(?:\.\d+)?)\s*千克.*转.*克', 'kg_to_g'),
            (r'(\d+(?:\.\d+)?)\s*摄氏.*转.*华氏', 'celsius_to_fahrenheit'),
        ]

        for pattern, conversion in patterns:
            match = re.search(pattern, expr)
            if match:
                value = float(match.group(1))

                if callable(self.unit_conversions[conversion]):
                    result = self.unit_conversions[conversion](value)
                else:
                    result = value * self.unit_conversions[conversion]

                return CalculationResult(
                    expression=expr,
                    result=result,
                    steps=[f"转换: {value} → {result}"]
                )

        raise ValueError(f"无法识别的单位转换: {expr}")

    def parse_natural_language(self, text: str) -> Optional[str]:
        """
        解析自然语言数学问题
        返回可计算的表达式
        """
        # 模式匹配常见数学问题
        patterns = [
            # 基础运算
            (r'(\d+)\s*加\s*(\d+)', r'\1+\2'),
            (r'(\d+)\s*减\s*(\d+)', r'\1-\2'),
            (r'(\d+)\s*乘\s*(\d+)', r'\1*\2'),
            (r'(\d+)\s*除以?\s*(\d+)', r'\1/\2'),

            # 英文
            (r'(\d+)\s*plus\s*(\d+)', r'\1+\2'),
            (r'(\d+)\s*minus\s*(\d+)', r'\1-\2'),
            (r'(\d+)\s*times\s*(\d+)', r'\1*\2'),
            (r'(\d+)\s*divided\s*by\s*(\d+)', r'\1/\2'),

            # 平方/立方
            (r'(\d+)\s*的平方', r'\1**2'),
            (r'(\d+)\s*的立方', r'\1**3'),
            (r'(\d+)\s*squared', r'\1**2'),
            (r'(\d+)\s*cubed', r'\1**3'),

            # 根号
            (r'根号\s*(\d+)', r'sqrt(\1)'),
            (r'square\s*root\s*of\s*(\d+)', r'sqrt(\1)'),
        ]

        processed = text.lower()
        for pattern, replacement in patterns:
            processed = re.sub(pattern, replacement, processed)

        # 如果处理后包含数学运算符，返回表达式
        if any(op in processed for op in ['+', '-', '*', '/', '**', 'sqrt']):
            return processed

        return None


class CalculatorService:
    """计算器服务，提供简单的接口"""

    def __init__(self):
        self.calculator = SmartCalculator()
        self.history = []

    def execute(self, command: str) -> Dict[str, Any]:
        """
        执行计算命令
        返回标准格式的结果
        """
        # 记录历史
        self.history.append(command)

        # 执行计算
        result = self.calculator.calculate(command)

        # 格式化输出
        if result.success:
            response = {
                'status': 'success',
                'input': command,
                'result': result.result,
                'display': f"{command} = {result.result}",
                'steps': result.steps
            }

            # 添加单位或说明
            if '转' in command:
                response['display'] = f"转换结果: {result.result}"
            elif '%' in command:
                response['display'] = f"计算结果: {result.result}"

        else:
            response = {
                'status': 'error',
                'input': command,
                'error': result.error,
                'display': f"计算错误: {result.error}"
            }

        return response

    def can_handle(self, text: str) -> bool:
        """判断是否能处理该文本"""
        # 检查是否包含数学相关的关键词
        math_keywords = [
            # 运算符
            '+', '-', '*', '/', '=', '^',
            '加', '减', '乘', '除', '等于',
            'plus', 'minus', 'times', 'divided',

            # 数学函数
            '根号', 'sqrt', 'sin', 'cos', 'log',
            '平方', '立方', 'square', 'cube',

            # 数字
            r'\d+',

            # 单位转换
            '转', 'to', '换算',

            # 百分比
            '%', '百分之',
        ]

        text_lower = text.lower()

        # 检查是否包含关键词
        for keyword in math_keywords:
            if keyword.startswith('\\'):  # 正则表达式
                if re.search(keyword, text_lower):
                    return True
            else:
                if keyword in text_lower:
                    return True

        # 尝试解析自然语言
        if self.calculator.parse_natural_language(text):
            return True

        return False


# 便捷函数
def calculate(expression: str) -> Union[float, str]:
    """快速计算函数"""
    service = CalculatorService()
    result = service.execute(expression)

    if result['status'] == 'success':
        return result['result']
    else:
        return result['error']


# 测试代码
if __name__ == "__main__":
    # 创建计算器服务
    service = CalculatorService()

    # 测试用例
    test_cases = [
        "1+1",
        "100 - 50",
        "12 * 15",
        "144 / 12",
        "2 ** 10",
        "sqrt(16)",
        "sin(3.14159/2)",
        "一加一等于多少",
        "五乘以六",
        "100的20%",
        "10公里转换成米",
        "25摄氏度转华氏度",
        "2的平方",
        "根号9",
        "这不是数学问题"
    ]

    print("="*50)
    print("智能计算器测试")
    print("="*50)

    for test in test_cases:
        print(f"\n输入: {test}")

        # 检查是否能处理
        if service.can_handle(test):
            result = service.execute(test)
            print(f"结果: {result['display']}")
            if result.get('steps'):
                print(f"步骤: {result['steps']}")
        else:
            print("结果: 无法识别为数学问题")