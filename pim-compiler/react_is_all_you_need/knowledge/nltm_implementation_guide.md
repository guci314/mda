# NLTM实施指南 - Kimi/DeepSeek/Gemini专用

## 快速开始

### 1. 识别NLTM任务

当用户提出以下类型任务时，启动NLTM模式：

```python
NLTM_TRIGGERS = [
    "修复所有测试",
    "生成完整的",
    "自动化",
    "批量处理",
    "迭代优化",
    "直到成功",
    "多步骤",
    "流程化"
]
```

### 2. 快速模板

#### 基础NLTM程序模板

```yaml
程序: [任务名称]
  目标: [一句话描述目标]
  
  状态:
    - 当前步骤: 开始
    - 成功标志: false
    - 错误列表: []
    - 尝试次数: 0
    - 最大尝试: 10
  
  主流程:
    步骤1 初始化:
      执行: [初始化操作]
      继续到: 步骤2
    
    步骤2 主循环:
      循环 当"成功标志 == false 且 尝试次数 < 最大尝试":
        执行: [核心操作]
        如果 "[成功条件]":
          设置: 成功标志 = true
          跳转到: 完成
        否则:
          增加: 尝试次数
          记录: 错误信息
    
    完成:
      生成: 执行报告
      返回: 结果
```

#### 基础执行日志模板

```json
{
  "program": "[程序名]",
  "session_id": "[时间戳]",
  "state": {
    "当前步骤": "开始",
    "成功标志": false,
    "结果": null
  },
  "执行历史": []
}
```

## Kimi专用配置

### 系统提示增强

```python
# 在 kimi_react_agent.py 中添加
NLTM_SYSTEM_PROMPT = """
## 自然语言图灵机模式

当任务需要多步骤执行时，你应该：

1. 创建 `task.nlpl` 程序文件
2. 创建 `execution.json` 状态文件
3. 严格按照程序执行，每步更新状态
4. 使用 write_file 和 read_file 管理状态
5. 错误时更新状态并重试

记住：
- 每个操作后立即更新 execution.json
- 保持状态文件小于4000字符
- 使用append_file记录长历史
"""
```

### Kimi NLTM工具集

```python
class KimiNLTMTools:
    @tool
    def init_nltm(self, task_description: str) -> str:
        """初始化NLTM任务"""
        # 生成NLPL程序
        program = f"""
程序: {task_description}
  目标: 完成{task_description}
  状态:
    - 当前步骤: 步骤1
    - 成功标志: false
  主流程:
    步骤1 开始:
      执行: 初始化任务
        """
        self.write_file("task.nlpl", program)
        
        # 初始化状态
        state = {
            "program": task_description,
            "state": {"当前步骤": "步骤1", "成功标志": False},
            "执行历史": []
        }
        self.write_file("execution.json", json.dumps(state, ensure_ascii=False))
        return "NLTM初始化完成"
    
    @tool
    def execute_nltm_step(self) -> str:
        """执行NLTM的下一步"""
        # 读取状态
        state = json.loads(self.read_file("execution.json"))
        current_step = state["state"]["当前步骤"]
        
        # 执行步骤（根据程序逻辑）
        result = self.execute_step(current_step)
        
        # 更新状态
        state["执行历史"].append({
            "步骤": current_step,
            "结果": result,
            "时间": datetime.now().isoformat()
        })
        
        # 决定下一步
        if result["success"]:
            state["state"]["当前步骤"] = self.get_next_step(current_step)
        else:
            state["state"]["错误"] = result["error"]
        
        # 保存状态
        self.write_file("execution.json", json.dumps(state, ensure_ascii=False))
        return f"执行{current_step}完成"
    
    @tool  
    def check_nltm_status(self) -> dict:
        """检查NLTM执行状态"""
        state = json.loads(self.read_file("execution.json"))
        return {
            "当前步骤": state["state"]["当前步骤"],
            "成功标志": state["state"]["成功标志"],
            "执行次数": len(state["执行历史"])
        }
```

## DeepSeek专用配置

### LangGraph集成

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class NLTMState(TypedDict):
    program: str
    current_step: str
    success: bool
    history: List[dict]
    errors: List[str]

def create_nltm_graph():
    """创建NLTM执行图"""
    
    workflow = StateGraph(NLTMState)
    
    # 定义节点
    def init_node(state):
        """初始化节点"""
        return {
            **state,
            "current_step": "步骤1",
            "success": False,
            "history": [],
            "errors": []
        }
    
    def execute_node(state):
        """执行节点"""
        step = state["current_step"]
        # 执行逻辑
        result = execute_step(step)
        state["history"].append(result)
        
        if result["success"]:
            state["current_step"] = get_next_step(step)
        else:
            state["errors"].append(result["error"])
        
        return state
    
    def check_node(state):
        """检查节点"""
        if state["success"]:
            return "end"
        elif len(state["errors"]) >= 10:
            return "error"
        else:
            return "execute"
    
    # 构建图
    workflow.add_node("init", init_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("check", check_node)
    
    # 添加边
    workflow.set_entry_point("init")
    workflow.add_edge("init", "execute")
    workflow.add_edge("execute", "check")
    workflow.add_conditional_edges(
        "check",
        lambda x: x,
        {
            "execute": "execute",
            "end": END,
            "error": END
        }
    )
    
    return workflow.compile()
```

### DeepSeek NLTM Agent

```python
class DeepSeekNLTMAgent(GenericReactAgent):
    """DeepSeek NLTM Agent"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nltm_graph = create_nltm_graph()
    
    async def run_nltm(self, task: str):
        """运行NLTM任务"""
        
        # 生成NLPL程序
        program = await self.generate_program(task)
        
        # 初始化状态
        initial_state = {
            "program": program,
            "current_step": "开始",
            "success": False,
            "history": [],
            "errors": []
        }
        
        # 执行图
        final_state = await self.nltm_graph.ainvoke(initial_state)
        
        # 返回结果
        return final_state
```

## Gemini专用配置

### Gemini NLTM提示

```python
GEMINI_NLTM_PROMPT = """
You are a Natural Language Turing Machine executing in Gemini mode.

Key behaviors:
1. Create structured NLPL programs in YAML format
2. Maintain JSON execution state meticulously  
3. Execute step-by-step with state updates
4. Handle errors gracefully with retries
5. Generate comprehensive execution reports

Gemini-specific optimizations:
- Use parallel processing when possible
- Leverage Gemini's speed for rapid iterations
- Keep state files concise (under 4KB)
- Use structured outputs for clarity
"""
```

### Gemini快速执行器

```python
class GeminiNLTMExecutor:
    """Gemini优化的NLTM执行器"""
    
    def __init__(self, client):
        self.client = client
        self.state_cache = {}
    
    async def rapid_execute(self, program: str):
        """快速执行NLTM程序"""
        
        # 解析程序
        steps = self.parse_nlpl(program)
        
        # 并行执行独立步骤
        independent_steps = self.identify_independent(steps)
        results = await asyncio.gather(*[
            self.execute_step(step) for step in independent_steps
        ])
        
        # 顺序执行依赖步骤
        for step in self.get_dependent_steps(steps):
            result = await self.execute_step(step)
            if not result["success"]:
                # 快速重试
                for _ in range(3):
                    result = await self.execute_step(step)
                    if result["success"]:
                        break
        
        return self.generate_report()
```

## 实际案例

### 案例1: 自动修复测试 (Kimi)

```python
# Kimi执行
agent = KimiReactAgent()

# 用户: "修复所有单元测试"
response = agent.run("""
我将使用NLTM模式修复所有测试。

首先创建NLPL程序：
""")

# Kimi会自动：
# 1. 创建 fix_tests.nlpl
# 2. 初始化 execution.json
# 3. 逐步执行修复
# 4. 更新状态文件
# 5. 生成最终报告
```

### 案例2: 批量代码生成 (DeepSeek)

```python
# DeepSeek执行
agent = DeepSeekNLTMAgent()

# 用户: "为所有模型生成CRUD API"
result = await agent.run_nltm("generate_crud_apis")

# DeepSeek会：
# 1. 分析模型结构
# 2. 生成执行图
# 3. 并行生成代码
# 4. 验证生成结果
# 5. 自动修复问题
```

### 案例3: 文档自动化 (Gemini)

```python
# Gemini执行
executor = GeminiNLTMExecutor(gemini_client)

# 用户: "生成完整项目文档"
docs = await executor.rapid_execute("""
程序: 文档生成
  步骤1: 扫描代码库
  步骤2: 提取API信息
  步骤3: 生成Markdown
  步骤4: 创建示例代码
  步骤5: 构建索引
""")

# Gemini会高速并行执行所有独立任务
```

## 调试技巧

### 1. 状态检查点

```yaml
调试步骤:
  记录: 当前状态快照
  保存到: checkpoint_{步骤号}.json
  如果 "需要回滚":
    恢复: checkpoint_{上一步骤}.json
```

### 2. 错误追踪

```json
{
  "错误追踪": {
    "步骤": "步骤3.2",
    "错误类型": "ValidationError",
    "错误信息": "详细错误",
    "堆栈": [],
    "重试次数": 2,
    "解决方案": "已尝试的方案"
  }
}
```

### 3. 性能监控

```python
def monitor_nltm_performance(state):
    """监控NLTM性能"""
    metrics = {
        "总步骤数": len(state["执行历史"]),
        "成功率": calculate_success_rate(state),
        "平均执行时间": calculate_avg_time(state),
        "错误恢复次数": count_error_recoveries(state)
    }
    return metrics
```

## 优化建议

### 1. 状态压缩
- 定期归档历史记录
- 只保留关键状态
- 使用引用而非复制

### 2. 并行化
- 识别独立任务
- 使用异步执行
- 批量处理相似操作

### 3. 缓存策略
- 缓存中间结果
- 避免重复计算
- 实现智能失效

### 4. 错误恢复
- 实现断点续传
- 自动回滚机制
- 降级处理策略

## 总结

NLTM让每个LLM都成为图灵完备的计算机：

1. **Kimi** - 擅长长文本处理，适合复杂流程
2. **DeepSeek** - 利用LangGraph，适合图状流程
3. **Gemini** - 速度最快，适合大规模并行

选择合适的Agent和策略，让自然语言编程成为现实！