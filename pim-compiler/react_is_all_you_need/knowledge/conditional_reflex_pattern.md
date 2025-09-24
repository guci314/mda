# 条件反射模式

## 核心理念
像生物的条件反射一样，某些模式化的输入可以直接触发响应，无需经过"大脑"（LLM）的复杂推理。

## 实现机制

### 1. 模式识别层
在ReactAgent接收输入后，先进行模式匹配：

```python
def preprocess_input(self, user_input: str):
    """输入预处理 - 条件反射检查"""

    # JSON模式检测
    if self._is_json_command(user_input):
        return self._handle_json_directly(user_input)

    # SQL模式检测
    if user_input.strip().upper().startswith(('SELECT', 'INSERT', 'UPDATE')):
        return self._handle_sql_directly(user_input)

    # 正常LLM处理
    return None
```

### 2. 直接路由规则

#### 库存管理示例
```python
# 输入
{
  "action": "check_inventory",
  "product_id": "001"
}

# 直接路由到
→ inventory_tool.py check 001
# 不经过LLM
```

#### 数据库查询示例
```sql
SELECT * FROM orders WHERE status='pending'
→ 直接执行SQL
# 不经过LLM
```

### 3. 条件反射注册

Agent可以学习并注册新的条件反射：

```python
# 在personal_knowledge.md中记录
conditional_reflexes:
  - pattern: '{"action": "inventory_*"}'
    handler: inventory_tool.py
  - pattern: 'SELECT * FROM'
    handler: sql_executor.py
  - pattern: 'CALCULATE:'
    handler: calculator.py
```

## 优势

1. **性能提升**
   - 跳过LLM推理（节省3-10秒）
   - 降低API成本
   - 减少延迟

2. **准确性提升**
   - 结构化输入直接映射
   - 避免LLM理解偏差
   - 确定性执行

3. **认知负载降低**
   - LLM专注复杂任务
   - 简单任务自动处理
   - 类似人类的"肌肉记忆"

## 实现建议

### 轻量级实现（推荐）
在ReactAgentMinimal中添加一个简单的预处理：

```python
def run(self, task: str):
    # 条件反射检查
    if task.strip().startswith('{'):
        try:
            cmd = json.loads(task)
            if 'action' in cmd and 'inventory' in cmd['action']:
                # 直接调用inventory tool
                return self._call_tool('inventory_tool', cmd)
        except:
            pass  # 不是有效JSON，继续正常流程

    # 正常的LLM处理流程
    return self._normal_run(task)
```

### 知识驱动实现
在知识文件中定义反射规则：

```markdown
## 条件反射规则

当输入匹配以下模式时，直接执行对应动作：

1. **JSON库存命令**
   - 模式: `{"action": "inventory_*", ...}`
   - 动作: 调用inventory_tool.py
   - 示例: `{"action": "inventory_check", "id": "001"}`

2. **数学表达式**
   - 模式: `CALC: <expression>`
   - 动作: 直接计算
   - 示例: `CALC: 2+2*3`

3. **状态查询**
   - 模式: `STATUS: <component>`
   - 动作: 查询组件状态
   - 示例: `STATUS: database`
```

## 演化路径

### 第一阶段：硬编码规则
- 在代码中定义简单模式
- 快速验证概念

### 第二阶段：配置驱动
- 规则写入配置文件
- Agent启动时加载

### 第三阶段：自主学习
- Agent观察自己的行为模式
- 自动提取条件反射
- 示例：发现总是用同样方式处理JSON，就注册为反射

## 注意事项

1. **不要过度使用**
   - 只对真正模式化的任务使用
   - 保留LLM的灵活性

2. **错误处理**
   - 反射失败时降级到LLM
   - 记录反射使用情况

3. **可解释性**
   - 记录为什么触发反射
   - 便于调试和审计

## 生物学启发

人类认知的层次：
1. **反射弧**（最快）：膝跳反射
2. **条件反射**（快）：看到红灯停车
3. **直觉**（中等）：模式识别
4. **理性思考**（慢）：复杂推理

Agent认知的对应：
1. **硬编码反射**：JSON → Tool
2. **学习的反射**：已知模式
3. **快速推理**：简单LLM调用
4. **深度推理**：复杂LLM + 工具链

## 实现示例

```python
class ConditionalReflex:
    """条件反射处理器"""

    def __init__(self):
        self.reflexes = {
            'json_inventory': (
                lambda x: x.strip().startswith('{') and '"action"' in x and 'inventory' in x,
                lambda x: f"python inventory_tool.py {json.loads(x)['action']} {json.loads(x).get('id', '')}"
            ),
            'sql_query': (
                lambda x: x.strip().upper().startswith('SELECT'),
                lambda x: f"python sql_tool.py '{x}'"
            )
        }

    def process(self, input_str: str):
        """尝试条件反射处理"""
        for name, (matcher, handler) in self.reflexes.items():
            if matcher(input_str):
                return handler(input_str), name
        return None, None
```

## 总结

条件反射机制是Agent走向高效的关键一步：
- **快速路径**处理模式化任务
- **慢速路径**处理复杂推理
- 两者结合实现**认知效率**最大化

这不是过早优化，而是**认知架构**的必要组成部分。