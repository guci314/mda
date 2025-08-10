# 调试验证增强策略

## 核心原则：严格验证，不容失败

### 成功判定标准（必须全部满足）

```python
def is_truly_successful(test_output):
    """
    只有满足所有条件才能声称成功
    """
    conditions = [
        "exit code: 0" in test_output,
        "failed" not in test_output or "0 failed" in test_output,
        "passed" in test_output and int(extract_passed_count(test_output)) > 0,
        "error" not in test_output.lower() or "0 errors" in test_output,
        "%" in test_output and "100%" in test_output  # pytest的百分比显示
    ]
    return all(conditions)
```

### 失败分类与处理策略

#### 🚨 Level 0: 404错误（最高优先级 - 缺失功能）
- HTTP 404 Not Found
- 路由不存在
- 功能未实现

**策略**：
✅ **创建缺失的路由和服务文件**
✅ **实现完整功能**
❌ **绝对不要修改测试来"适应"404**

```python
# 404错误的正确处理
if status_code == 404:
    # 不要修改测试！
    # 要创建缺失的功能！
    create_router_file()
    create_service_file()
    register_route_in_main()
    implement_crud_operations()
```

#### Level 1: 基础错误（必须修复）
- 语法错误（SyntaxError, IndentationError）
- 导入错误（ImportError, ModuleNotFoundError）
- 类型错误（TypeError基础版）

**策略**：使用专门工具快速修复

#### Level 2: 结构错误（系统性修复）
- Pydantic版本兼容性
- 方法名不匹配
- 字段映射错误

**策略**：批量搜索替换，统一规范

#### Level 3: 业务逻辑错误（深度理解）
- 业务规则不满足
- 数据验证失败
- 断言错误（非404相关）

**策略**：理解需求，修复逻辑

### 防止过早退出的机制

#### 1. 强制完整验证
```python
# 每次修复后必须运行完整测试
pytest tests/ -v --tb=short

# 解析必须包含具体数字
if "11 failed, 2 passed" in output:
    return "还有11个测试失败，继续修复"
```

#### 2. 分阶段目标
```python
milestones = {
    "phase1": "所有语法错误修复（0 syntax errors）",
    "phase2": "所有导入错误修复（0 import errors）",
    "phase3": "Pydantic兼容性修复（0 pydantic errors）",
    "phase4": "所有方法实现（0 AttributeError）",
    "phase5": "所有测试通过（0 failed）"
}
```

#### 3. 详细失败分析
```python
def analyze_failures(test_output):
    """
    分析每个失败的具体原因
    """
    failures = {
        "pydantic_errors": [],
        "attribute_errors": [],
        "assertion_errors": [],
        "http_errors": []
    }
    
    # 解析并分类每个错误
    for line in test_output.split('\n'):
        if "PydanticUserError" in line:
            failures["pydantic_errors"].append(line)
        elif "AttributeError" in line:
            failures["attribute_errors"].append(line)
        # ... 继续分类
    
    return failures
```

### 退出条件严格化

#### 只允许在以下情况退出：

1. **真正成功**
   ```python
   exit_code == 0 AND failed == 0 AND errors == 0
   ```

2. **达到硬限制**
   ```python
   iteration >= 20 AND 连续3次无进展
   ```

3. **需要人工介入**
   ```python
   遇到无法自动修复的架构问题
   ```

### 进度追踪机制

```json
{
  "progress_tracking": {
    "total_tests": 13,
    "initial_failures": 13,
    "current_failures": 11,
    "fixed_count": 2,
    "success_rate": "15.4%",
    "remaining_work": "84.6%"
  }
}
```

### 失败后的强制行动

```python
if test_failures > 0:
    actions = [
        "1. 列出所有失败测试的名称",
        "2. 分析每个失败的根本原因",
        "3. 按优先级排序修复计划",
        "4. 执行修复直到该类错误消失",
        "5. 重新验证并更新进度"
    ]
    
    # 不允许声称成功
    NEVER_SAY_SUCCESS_WHEN_FAILURES_EXIST = True
```

## 关键规则

### 🚫 绝对禁止

1. **禁止在有失败时声称成功**
2. **禁止忽略具体的失败数字**
3. **禁止基于部分成功就停止**
4. **禁止不验证就假设修复成功**

### ✅ 必须执行

1. **必须解析具体的 passed/failed 数量**
2. **必须追踪每个测试的状态变化**
3. **必须在每次修复后完整验证**
4. **必须记录未解决的问题列表**

## 实施示例

### 404错误的处理示例

```python
# 错误的做法 ❌ - 修改测试来"修复"404
# test_reservations.py
def test_get_reservations(client):
    response = client.get("/reservations/")
    # assert response.status_code == 200  # 注释掉原期望
    assert response.status_code == 404  # 改成接受404

# 正确的做法 ✅ - 创建缺失的功能
# 1. 创建 app/routers/reservations.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_reservations():
    return []

# 2. 创建 app/services/reservation_service.py
def get_all_reservations():
    # 实现预约查询逻辑
    pass

# 3. 在 app/main.py 注册路由
from app.routers import reservations
app.include_router(reservations.router, prefix="/reservations")
```

### 验证结果的示例

```python
# 错误的做法 ❌
if "passed" in output:
    return "测试通过"

# 正确的做法 ✅
import re
match = re.search(r'(\d+) failed, (\d+) passed', output)
if match:
    failed = int(match.group(1))
    passed = int(match.group(2))
    if failed == 0:
        return f"真正成功：{passed}个测试全部通过"
    else:
        return f"仍需努力：{failed}个测试失败，{passed}个通过"
```

## 调试Agent必读契约

> 我承诺：
> 1. 只有当 **所有测试都通过** 时才说成功
> 2. 会 **诚实报告** 每个失败的测试
> 3. 会 **持续修复** 直到真正完成
> 4. 会 **详细记录** 未解决的问题
> 5. **绝不** 在有失败时假装成功

记住：部分成功不是成功，99%通过不是100%通过！