# 工作目录安全保证

## 核心原则

1. **工作目录 = 外部世界**
   - 工作目录代表 Agent 与外部世界交互的空间
   - 可能是用户的项目代码库、数据目录或任何重要目录
   - Agent 只是这个世界的"访客"，不是"管理者"

2. **只能修改，永不清理**
   - Agent 可以在工作目录中创建新文件
   - Agent 可以修改现有文件（通过工具）
   - Agent **永远不能**清理或删除工作目录
   - Agent **永远不能**批量删除文件

3. **工作目录必须预先存在**
   - Agent 不会创建工作目录
   - 如果工作目录不存在，Agent 初始化时会报错
   - 这确保用户明确知道 Agent 将在哪里操作

## 实现保证

### 1. 初始化检查
```python
# 在 GenericReactAgent.__init__ 中
if not self.work_dir.exists():
    raise ValueError(
        f"工作目录 '{self.work_dir}' 不存在。\n"
        "工作目录代表外部世界（如项目代码库），必须预先存在。\n"
        "Agent 不能创建工作目录，只能在其中操作文件。"
    )
```

### 2. 清理逻辑隔离
- 所有清理操作仅限于 Agent 的私有数据目录（`.agents/data/{agent_name}`）
- 工作目录的清理代码已被永久注释掉：
```python
# 注释掉清理共享工作目录的代码，以支持多 Agent 文件共享
# 在多 Agent 协作场景下，不应该清理共享工作目录
# 每个 Agent 应该只管理自己的私有数据目录 (.agent_data/{agent_name})
```

### 3. 目录结构分离
```
用户的项目/              # 工作目录（外部世界）
├── src/
├── tests/
├── README.md
└── ... 用户的文件

.agents/                # Agent 内部存储（独立位置）
├── memory/             # 提取的知识
│   └── {agent_name}/
└── data/              # 私有数据
    └── {agent_name}/
```

## 安全测试

我们通过以下测试验证了这些保证：

1. **不存在的工作目录** - Agent 初始化时会报错 ✓
2. **只读文件保护** - 只读文件不会被删除 ✓
3. **系统目录保护** - 不会清理系统目录 ✓
4. **多 Agent 协作** - 共享文件不会被清理 ✓

## 使用指南

### 正确用法
```python
# 工作目录必须已存在
project_dir = Path("~/my_project").expanduser()
if not project_dir.exists():
    print("请先创建项目目录")
    exit(1)

config = ReactAgentConfig(
    work_dir=str(project_dir),
    # ... 其他配置
)
agent = GenericReactAgent(config)
```

### 错误用法
```python
# ❌ 不要让 Agent 在不存在的目录工作
config = ReactAgentConfig(
    work_dir="/some/nonexistent/path"  # 会抛出 ValueError
)

# ❌ 不要让 Agent 在系统关键目录工作
config = ReactAgentConfig(
    work_dir="/"  # 极其危险！
)
```

## 总结

这些保证确保了：
- 用户的文件永远安全
- Agent 只能做被明确允许的操作
- 工作目录与 Agent 内部状态完全隔离
- 符合"最小权限原则"