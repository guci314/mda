# Agent知识库

## 成功模式
### Python边界条件处理模式
- **适用场景**：处理列表、字典等数据结构时
- **解决方案**：
  ```python
  # 列表操作前检查
  if not my_list:
      return default_value
  
  # 字典操作前检查
  if item is not None and isinstance(item, dict) and 'key' in item:
      value = item['key']
  
  # 使用get方法安全获取字典值
  value = item.get('key', default_value)
  ```
- **效果**：防止IndexError、KeyError、TypeError等运行时错误
- **注意事项**：考虑所有可能的边界情况（空、None、类型错误）

### 防御式编程最佳实践
- **适用场景**：处理外部输入或不可靠数据源
- **解决方案**：
  1. 输入验证：检查类型、范围、格式
  2. 边界条件：空列表、None值、异常值
  3. 优雅降级：提供默认值或跳过无效数据
  4. 错误日志：记录异常情况便于调试
- **效果**：提高代码健壮性，减少运行时崩溃
- **注意事项**：平衡健壮性与性能，避免过度检查

## 错误模式
### ZeroDivisionError
- **表现**：division by zero
- **原因**：除数为0（通常是空列表长度）
- **解决**：
  ```python
  if denominator == 0:
      return 0  # 或 raise ValueError
  ```
- **预防**：所有除法操作前检查除数

### TypeError: NoneType object is not subscriptable
- **表现**：尝试对None值使用[]操作符
- **原因**：变量为None却按字典/列表方式访问
- **解决**：
  ```python
  if item is not None and isinstance(item, dict):
      value = item.get('key')
  ```
- **预防**：访问属性/元素前验证对象类型和存在性

## 调试技巧
### 快速定位运行时错误
1. **阅读错误信息**：关注错误类型和行号
2. **最小复现**：创建最小测试用例重现错误
3. **边界测试**：测试空值、None、边界条件
4. **逐步验证**：print/log关键变量值

### 代码修复验证
1. **修复原错误**：确保原测试用例通过
2. **边界测试**：测试各种边界情况
3. **回归测试**：确保没有引入新错误
4. **文档更新**：更新函数文档说明行为

---
更新时间：2024-12-19 10:33:00