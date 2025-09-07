# 实现方案

## 1. 当前状态分析

### 1.1 已有功能
- ✅ 基础React循环
- ✅ 工具系统（read_file, write_file, execute_command）
- ✅ 知识文件加载
- ✅ 滑动窗口管理
- ✅ minimal_mode开关
- ✅ 基础的笔记系统

### 1.2 需要改进
- ❌ 滑动窗口改为Compact
- ❌ 添加压缩模型调用
- ❌ 统一记忆注入机制

## 2. 实现步骤

### Phase 1: Compact记忆实现（优先级：高）

#### Step 1.1: 添加压缩配置
```python
# 在 __init__ 方法中添加
self.compress_config = {
    "model": "google/gemini-2.0-flash-001",
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "threshold": 70000  # 触发压缩的token数
}
```

#### Step 1.2: 实现压缩方法
```python
def _compact_messages(self, messages: List[Dict]) -> List[Dict]:
    """智能压缩对话历史"""
    # 调用Gemini Flash进行压缩
    # 返回压缩后的消息列表
```

#### Step 1.3: 替换滑动窗口
```python
# 在 _execute_task_impl 中
# 删除滑动窗口逻辑
# 添加压缩检查
if self.count_tokens(messages) > self.compress_config["threshold"]:
    messages = self._compact_messages(messages)
```

### Phase 2: Session记录策略（优先级：中）

#### Step 2.1: 完整模式Session记录
```python
def _write_session(self, task: str, result: str, metadata: Dict):
    """完整模式下写入详细session记录"""
    if not self.minimal_mode:
        session_data = {
            "timestamp": datetime.now(),
            "request": task,
            "response": result,
            "metadata": metadata,
            "rounds": self.round_count,
            "tools_used": self.tools_history
        }
        self._persist_session(session_data)
```

#### Step 2.2: 极简模式无需Session文件
```python
# 极简模式依赖Compact记忆
# Compact本身就是注意力机制，自动选择性记忆重要事件
# 无需额外的session文件
```

### Phase 3: 记忆注入优化（优先级：中）

#### Step 3.1: 统一注入接口
```python
def _inject_memory(self, prompt: str) -> str:
    """统一的记忆注入接口"""
    if self.minimal_mode:
        return self._inject_compact_memory(prompt)
    else:
        return self._inject_external_memory(prompt)
```

#### Step 3.2: 分离注入逻辑
```python
def _inject_compact_memory(self, prompt: str) -> str:
    """注入压缩记忆（极简模式）"""
    # Compact包含状态和选择性事件
    # 无需额外的session注入
    if hasattr(self, 'compact_memory'):
        return prompt + f"\n## 压缩记忆\n{self.compact_memory}"
    return prompt
    
def _inject_external_memory(self, prompt: str) -> str:
    """注入外部记忆（完整模式）"""
    # 注入task_process + recent_sessions
    memory = ""
    if self.task_process_file.exists():
        memory += self.task_process_file.read_text()
    memory += self._load_recent_sessions(limit=5)
    return prompt + memory
```

## 3. 代码修改位置

### 3.1 主要修改文件
```
core/react_agent_minimal.py
├── __init__()          # 添加压缩配置
├── _execute_task_impl() # 替换滑动窗口为压缩
├── _compact_messages()  # 新增：压缩方法
├── _count_tokens()      # 新增：token计数
├── _write_session()     # 优化：session记录
└── _build_minimal_prompt() # 优化：记忆注入
```

### 3.2 知识文件更新
```
knowledge/
└── minimal/
    └── system_prompt_minimal.md  # 更新：添加压缩记忆说明

# 注：mandatory_protocol.md无需修改
# 极简模式不加载mandatory_protocol，使用独立的知识文件
```

## 4. 测试方案

### 4.1 功能测试
```python
def test_compact_memory():
    """测试压缩记忆功能"""
    agent = ReactAgentMinimal(minimal_mode=True)
    
    # 执行长任务触发压缩
    result = agent.execute(task="生成100个文件的任务")
    
    # 验证压缩发生
    assert "压缩对话历史" in logs
    
    # 验证记忆保留
    result2 = agent.execute(task="刚才创建了哪些文件？")
    assert "file" in result2
```

### 4.2 性能测试
```python
def test_performance():
    """对比滑动窗口vs压缩的性能"""
    
    # 测试1：滑动窗口版本
    time_sliding = measure_time(old_version)
    
    # 测试2：压缩版本
    time_compact = measure_time(new_version)
    
    # 验证性能提升
    assert time_compact < time_sliding * 1.2
```


## 5. 风险评估

### 5.1 技术风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 压缩质量差 | 中 | 高 | 优化prompt，多次测试 |
| 压缩延迟高 | 低 | 中 | 使用快速模型，异步压缩 |

### 5.2 实施风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 改动过大 | 中 | 中 | 分阶段实施 |
| 测试不足 | 低 | 高 | 完整测试套件 |

## 6. 时间估算

### 6.1 开发时间
- Phase 1 (Compact): 4小时
- Phase 2 (Session策略): 1小时  
- Phase 3 (注入优化): 2小时
- 测试: 2小时
- **总计**: 9小时

### 6.2 里程碑
1. **M1**: Compact基础实现（Day 1）
2. **M2**: Session优化完成（Day 2）
3. **M3**: 全部完成并测试（Day 3）

## 7. 成功标准

### 7.1 功能标准
- ✅ 70k tokens自动触发压缩
- ✅ 压缩后保留关键信息
- ✅ 极简模式通过Compact实现选择性记忆
- ✅ 完整模式保留详细session记录
- ✅ 记忆注入正常工作

### 7.2 性能标准
- ✅ 压缩延迟 < 2秒
- ✅ 压缩比 > 10:1
- ✅ 整体性能不降低

### 7.3 质量标准
- ✅ 所有测试通过
- ✅ 代码行数 < 600

## 8. 后续优化

### 8.1 短期（1个月）
- 优化压缩prompt
- 添加压缩缓存
- 支持更多压缩模型

### 8.2 长期（3个月）
- 分布式记忆
- 多Agent共享记忆
- 增量学习机制

## 9. 注意事项

### 9.1 保持简洁
- 不要过度工程化
- 优先使用知识文件
- 代码改动最小化

### 9.2 实施原则
- 直接替换，不保留旧代码
- 默认值合理
- 错误处理完善

### 9.3 核心洞察
- **Compact即注意力机制**：压缩过程本身就是选择性注意
- **无需重复记录**：极简模式的Compact已包含事件选择
- **双模式互补**：极简快速响应，完整图灵完备

### 9.4 文档更新
- 更新README说明双模式差异
- 更新API文档关于Compact
- 添加使用示例展示两种模式