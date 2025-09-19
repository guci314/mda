# 验证知识 - 程序正义版本

## 核心原则：程序正义优先

**理念**：正义不仅要实现，而且要以看得见的方式实现。

## 验证策略

### 必须创建验证脚本的场景

所有验证操作都**必须**创建独立的Python验证脚本：

1. **结构化输出验证**
   - JSON/XML格式验证
   - 数据结构完整性检查
   - 字段存在性验证

2. **业务逻辑验证**
   - 计算结果正确性
   - 状态转换合法性
   - 约束条件满足性

3. **文件操作验证**
   - 文件存在性检查
   - 内容格式验证
   - 编码正确性验证

### 验证脚本模板

```python
#!/usr/bin/env python3
"""
验证脚本：{验证目标}
创建时间：{时间戳}
验证类型：{符号主义验证}
"""

def validate_{function_name}(output):
    """
    验证函数输出是否符合预期

    Args:
        output: 待验证的输出

    Returns:
        bool: True表示验证通过，False表示失败
    """
    try:
        # 步骤1：解析输出
        # 步骤2：检查必要条件
        # 步骤3：验证业务规则
        # 步骤4：返回验证结果

        return True
    except Exception as e:
        print(f"验证失败: {e}")
        return False

if __name__ == "__main__":
    # 执行验证
    import sys
    import json

    # 读取输入
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        with open(input_file, 'r') as f:
            output = json.load(f)
    else:
        # 默认测试数据
        output = {}

    # 执行验证
    result = validate_{function_name}(output)

    # 输出结果
    if result:
        print("✅ 验证通过")
        sys.exit(0)
    else:
        print("❌ 验证失败")
        sys.exit(1)
```

### 验证报告格式

每次验证必须生成验证报告：

```json
{
    "validation_type": "symbolic",
    "script_path": "/path/to/validate.py",
    "execution_time": "2024-01-01T00:00:00",
    "result": "passed/failed",
    "details": {
        "checks_performed": [...],
        "errors_found": [...],
        "suggestions": [...]
    }
}
```

## 执行要求

1. **强制执行**
   - 所有验证都必须创建脚本
   - 脚本必须实际执行
   - 必须捕获执行输出

2. **透明追溯**
   - 脚本文件必须保存
   - 执行日志必须记录
   - 验证结果必须可重现

3. **异常处理**
   - 脚本必须有异常处理
   - 失败必须有明确原因
   - 提供改进建议

## 退化条件

只有在以下情况才能退化到脑内验证：
1. 输出是纯自然语言（无法形式化）
2. 创意内容（主观判断）
3. 用户体验（需要人类感知）

即使退化，也必须：
- 记录为什么无法创建脚本
- 说明采用的验证方法
- 提供验证的理由

## 质量标准

验证脚本必须满足：
- ✅ 可独立运行
- ✅ 有清晰的输入输出
- ✅ 包含完整的错误处理
- ✅ 提供详细的失败信息
- ✅ 支持批量验证
- ✅ 生成验证报告

## 记住

**程序正义 = 透明 + 可追溯 + 可重复**

每个验证决策都应该有据可查，每个验证过程都应该可以重现。