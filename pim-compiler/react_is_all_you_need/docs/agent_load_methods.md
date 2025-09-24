# Agent加载方法说明

## 当前ReactAgentMinimal中的加载方法

### 1. create_from_template（从模板创建）
```python
@classmethod
def create_from_template(cls, template_file: str, work_dir: str, **kwargs):
    """从模板文件创建新Agent实例"""
```

用于从保存的模板创建新Agent。

### 2. restore_instance（恢复实例）
```python
@classmethod
def restore_instance(cls, instance_file: str, new_work_dir: Optional[str] = None):
    """恢复完整的Agent实例，包含状态和消息历史"""
```

用于恢复之前保存的Agent完整状态。

## 基于Home目录的简单load方法

根据我们讨论的"Agent就是home目录"理念，应该实现一个简单的load方法：

```python
@classmethod
def load(cls, name: str):
    """
    根据名字加载Agent
    如果~/.agent/{name}存在，加载其状态
    如果不存在，创建新Agent
    """
    home = Path(f"~/.agent/{name}").expanduser()

    if home.exists():
        # 从home目录加载
        agent = cls(
            work_dir=".",  # 或从home/config.json读取
            name=name
        )
        # Agent的__init__会自动加载home目录中的文件
        return agent
    else:
        # 创建新Agent
        return cls(
            work_dir=".",
            name=name
        )
```

## 使用方式对比

### 当前方式（复杂）
```python
# 保存
agent.save_instance("agent.json")

# 加载
agent, messages = ReactAgentMinimal.restore_instance("agent.json")
```

### 理想方式（简单）
```python
# 创建或加载
agent = ReactAgentMinimal.load("alice")

# 不需要显式保存，一切都在home目录
```

## 实现建议

1. **添加简单的load方法**
```python
@classmethod
def load(cls, name: str, **kwargs):
    """加载Agent，如果不存在则创建"""
    # 直接用name初始化，__init__会处理一切
    return cls(name=name, work_dir=".", **kwargs)
```

2. **__init__已经做了大部分工作**
- 检查home目录
- 加载agent_knowledge.md
- 加载experience.md
- 加载compact.md

3. **可能需要的补充**
- 从home/config.json恢复配置
- 从home/state.json恢复状态
- 从home/messages.json恢复对话历史

## 为什么当前没有简单的load方法？

可能是因为：
1. 设计时考虑了template vs instance的区分
2. 想要支持灵活的保存/加载位置
3. 没有完全采用"Agent就是home目录"的理念

## 结论

当前的ReactAgentMinimal有：
- `create_from_template()` - 从模板创建
- `restore_instance()` - 恢复实例

但缺少一个简单的：
- `load(name)` - 根据名字加载或创建Agent

这个简单的load方法更符合"Agent活在文件系统"的理念。