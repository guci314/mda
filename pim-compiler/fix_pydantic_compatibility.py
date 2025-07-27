#!/usr/bin/env python3
"""修复 Pydantic v1/v2 兼容性问题"""

import sys

# 猴子补丁 - 在导入 langchain 之前修复 pydantic
import pydantic

# 为 pydantic v1 添加 v2 的兼容性
if not hasattr(pydantic, 'field_validator'):
    # 创建一个虚拟的 field_validator 装饰器
    def field_validator(*fields, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    pydantic.field_validator = field_validator

if not hasattr(pydantic, 'ConfigDict'):
    # 创建一个虚拟的 ConfigDict
    pydantic.ConfigDict = dict

print("✅ Pydantic兼容性补丁已应用")