# Agent知识库

## 成功模式
### 防御式编程模式
- **适用场景**：处理用户输入、外部数据、边界情况
- **解决方案**：
  ```python
  # 1. 空值检查
  if not data:
      return safe_default
  
  # 2. 类型检查
  if isinstance(item, dict) and 'key' in item:
      return item['key']
  
  # 3. 异常安全
  try:
      return risky_operation()
  except SpecificException:
      return fallback_value
  ```
- **效果**：防止运行时错误，提高代码健壮性
- **注意事项**：不要过度防御，保持代码简洁

### 边界情况处理模式
- **适用场景**：列表操作、字典访问、数值计算
- **解决方案**：
  - 空列表：检查长度或使用默认值
  - 字典键访问：使用 `in` 检查或 `.get()` 方法
  - 数值计算：检查除数是否为零
- **效果**：消除 IndexError、KeyError、ZeroDivisionError
- **注意事项**：为边界情况定义清晰的行为契约

## 错误模式
### ZeroDivisionError
- **表现**："division by zero"
- **原因**：除法运算中除数为零
- **解决**：计算前检查除数 `if denominator == 0`
- **预防**：对所有除法操作进行保护

### TypeError - NoneType 键访问
- **表现**："'NoneType' object is not subscriptable"
- **原因**：对 None 值使用字典访问语法
- **解决**：访问前检查 `item is not None and isinstance(item, dict)`
- **预防**：建立数据验证层

## 最佳实践
### 修复策略
- **原则**：先理解错误根本原因，再实施修复
- **步骤**：
  1. 重现错误场景
  2. 分析错误堆栈
  3. 确定边界条件
  4. 实施防御式修复
  5. 全面测试边界情况
- **示例**：修复除零错误时，考虑空列表的合理返回值

### 测试验证
- **边界测试**：空集合、None值、无效数据
- **回归测试**：确保修复不破坏现有功能
- **文档更新**：添加清晰的文档字符串说明行为

---
更新时间：2024-12-19 10:05:00