# Agent知识库

## 成功模式
### Python边界条件处理模式
- **适用场景**：处理用户输入、API数据、文件读取等外部数据源
- **解决方案**：
  1. 空值检查：使用`if not variable`检查空列表/空字符串
  2. None值检查：显式检查`item is not None`
  3. 类型检查：使用`isinstance(item, dict)`验证类型
  4. 键存在检查：使用`'key' in dict`避免KeyError
  5. 异常处理：使用try-except处理类型转换错误
- **效果**：代码健壮性显著提升，避免运行时错误
- **注意事项**：过度检查可能影响性能，需权衡

### 防御性编程最佳实践
- **原则**："永不信任外部输入"
- **示例**：
  ```python
  def safe_process(data):
      if not data:
          return []
      result = []
      for item in data:
          if item and isinstance(item, dict) and 'value' in item:
              try:
                  value = float(item['value'])
                  result.append(value)
              except (ValueError, TypeError):
                  continue  # 或记录日志
      return result
  ```
- **收益**：减少生产环境bug，提升用户体验

## 错误模式
### 常见Python运行时错误
- **ZeroDivisionError**：除零错误
  - **表现**：division by zero
  - **原因**：除数可能为零
  - **解决**：检查除数不为零或使用try-except
  - **预防**：添加空值检查

- **TypeError**：NoneType对象无属性
  - **表现**：'NoneType' object has no attribute 'xxx'
  - **原因**：对象为None时访问属性或方法
  - **解决**：访问前检查对象是否为None
  - **预防**：使用防御性编程

- **KeyError**：字典键不存在
  - **表现**：KeyError: 'key_name'
  - **原因**：访问不存在的字典键
  - **解决**：使用dict.get()或检查键存在
  - **预防**：使用'key' in dict检查

## 最佳实践
### 输入验证层次
1. **存在性检查**：变量是否存在
2. **类型检查**：变量类型是否正确
3. **值域检查**：值是否在合理范围内
4. **业务规则检查**：是否符合业务逻辑

### 测试策略
- **边界值测试**：测试空值、极值、特殊值
- **异常输入测试**：None、错误类型、格式错误的数据
- **正常流程测试**：确保修复不破坏正常功能

---
更新时间：2024-12-19 10:31:00