# DeepSeek Reasoner 文件写入问题修复方案

## 问题根因

DeepSeek Reasoner 在生成工具调用参数时，有时候会遗漏 `content` 参数，只传递 `file_path` 参数，导致 `WriteFileTool` 执行时抛出 `KeyError: 'content'`。

## 解决方案

### 方案1：修复 WriteFileTool 添加参数验证（推荐）

修改 `/Users/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/core/tool_base.py` 的 WriteFileTool：

```python
class WriteFileTool(Function):
    """写入文件工具"""

    def execute(self, **kwargs) -> str:
        # 参数验证
        if "file_path" not in kwargs:
            return "错误：缺少必需参数 'file_path'"
        if "content" not in kwargs:
            return "错误：缺少必需参数 'content'。请提供要写入文件的完整内容。"

        path_str = kwargs["file_path"]
        content = kwargs["content"]

        # 处理绝对路径和~路径
        if path_str.startswith('~') or path_str.startswith('/'):
            file_path = Path(path_str).expanduser()
        else:
            file_path = self.work_dir / path_str

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"文件已写入: {path_str}"
        except Exception as e:
            return f"写入文件失败: {str(e)}"
```

### 方案2：在系统提示中强调参数要求

在 Agent 的系统提示中添加：

```python
# 在 ReactAgentMinimal.__init__ 中添加
system_prompt_addon = """
重要工具使用说明：
- write_file 工具必须同时提供 file_path 和 content 两个参数
- content 参数必须包含完整的文件内容，不能为空
- 如果内容较长，也必须完整生成在 content 参数中
"""
```

### 方案3：修改工具参数定义，标记为必需

```python
def __init__(self, work_dir):
    super().__init__(
        name="write_file",
        description="创建或覆盖文件内容",
        parameters={
            "file_path": {
                "type": "string",
                "description": "文件路径",
                "required": True  # 标记为必需
            },
            "content": {
                "type": "string",
                "description": "完整的文件内容",
                "required": True  # 标记为必需
            }
        }
    )
```

### 方案4：在 Agent 中添加重试逻辑

检测到 content 参数缺失时，提示模型重新生成：

```python
def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
    """执行工具 - 添加参数验证"""

    # 特殊处理 write_file
    if tool_name == "write_file" and "content" not in arguments:
        return "错误：write_file 工具缺少 content 参数。请重新调用，确保同时提供 file_path 和 content 参数。"

    # 继续正常执行
    for tool in self.function_instances:
        if tool.name == tool_name:
            return tool.execute(**arguments)
```

## 为什么会发生？

1. **Token限制**：DeepSeek Reasoner 可能在生成长内容时遇到token限制
2. **JSON格式问题**：生成复杂JSON时格式不完整
3. **模型特性**：某些情况下模型倾向于省略大段内容

## 建议的实施步骤

1. **立即修复**：实施方案1，添加参数验证，返回友好错误信息
2. **测试验证**：测试不同长度的文件内容写入
3. **长期优化**：考虑将大文件分段写入，或使用 append_file 增量写入

## 测试代码

```python
# test_write_file.py
from core.react_agent_minimal import ReactAgentMinimal

agent = ReactAgentMinimal(
    work_dir="/tmp/test",
    model="deepseek-reasoner"
)

# 测试写入Python脚本
result = agent.execute("""
创建一个 uuid_generator.py 文件，内容是：
```python
#!/usr/bin/env python3
import uuid

def generate_uuid():
    return str(uuid.uuid4())

if __name__ == "__main__":
    print(generate_uuid())
```
""")

print(result)
```