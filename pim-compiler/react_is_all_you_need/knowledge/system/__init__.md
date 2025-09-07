# System Knowledge Package

## 包描述
系统级核心知识，定义了Agent的基础行为模式和强制协议。

## 导出模块
- `memory_protocol.md` - 三维记忆框架协议（原mandatory_protocol.md）
- `memory_structure.md` - 记忆结构规范（原structured_notes.md）  
- `system_prompt.md` - 系统基础提示词

## 理论基础：三维记忆框架

### 三个维度
1. **主体/世界**：Agent自身 vs 外部环境
2. **状态/事件流**：静态快照 vs 动态过程
3. **类型层/实例层**：抽象模式 vs 具体执行

### 映射关系
| | 世界(World) | 主体(Subject) |
|---|---|---|
| **类型层** | 隐式（提示词） | 显式（知识文件） |
| **实例层** | world_state.md + sessions | task_process.md |

## 核心原则
1. **图灵完备性**：task_process.md提供无限状态存储
2. **Event Sourcing**：sessions提供不可变事件日志
3. **三元分离**：世界、任务、主体记忆独立管理

## 使用方式
```python
knowledge_files = [
    "knowledge/system/*.md",  # 加载所有系统知识
    # 或
    "knowledge/system/memory_protocol.md",  # 选择性加载
]
```