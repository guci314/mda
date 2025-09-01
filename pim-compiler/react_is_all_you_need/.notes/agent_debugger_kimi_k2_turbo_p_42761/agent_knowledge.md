# Agent知识库

## 成功模式
### Python边界条件处理模式
- **适用场景**：处理用户输入、列表操作、字典访问等可能出现边界情况的场景
- **解决方案**：
  ```python
  # 空值检查
  if not input_list:
      return default_value
      
  # 类型检查
  if item is not None and isinstance(item, dict):
      # 安全访问
      if 'key' in item:
          value = item['key']
  
  # 异常处理
  try:
      result = risky_operation()
  except SpecificError:
      handle_gracefully()
  ```
- **效果**：防止运行时错误，提高代码健壮性
- **注意事项**：不要过度防御，保持代码简洁

### 调试流程模式
- **适用场景**：修复Python代码中的bug
- **解决方案**：
  1. 读取并理解原始代码
  2. 识别具体的错误类型和位置
  3. 分析错误原因（边界条件、类型错误等）
  4. 实施修复（添加检查、异常处理）
  5. 验证修复结果（运行测试）
- **效果**：系统化地定位和修复bug
- **注意事项**：先理解再修复，避免引入新问题

## 错误模式
### 常见Python错误类型
- **ZeroDivisionError**：除零错误，通常由于空列表或零值除法
  - **表现**：division by zero
  - **原因**：len(list) == 0
  - **解决**：检查列表是否为空
  - **预防**：添加空值检查

- **TypeError**：类型错误，None值或错误类型操作
  - **表现**：NoneType object is not subscriptable
  - **原因**：对None值进行字典访问或列表操作
  - **解决**：添加类型检查和None值验证
  - **预防**：使用isinstance和is not None检查

## 最佳实践
### 防御性编程
- **原则**：假设所有输入都可能是无效的
- **示例**：
  ```python
  def safe_process(data):
      if not isinstance(data, list):
          return []
      return [process_item(item) for item in data if item is not None]
  ```
- **收益**：减少运行时错误，提高用户体验

### 测试验证
- **原则**：修复后必须验证所有边界情况
- **示例**：
  ```python
  # 测试空值、None、无效数据、正常数据
  test_cases = [
      [],
      None,
      [None, {'value': 5}],
      [{'value': 1}, {'value': 2}]
  ]
  ```
- **收益**：确保修复完整，防止回归

---
更新时间：2024-12-19 10:02:00