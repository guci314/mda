# Agent 如何理解和使用 Tools

## 核心机制

LangChain 中的 Agent 通过以下信息理解 tool 的用途：

### 1. Tool 的描述信息

```python
@tool
def write_file(file_path: str, content: str) -> str:
    """写入文件"""  # 这个 docstring 就是 tool 的描述
    # 实现代码...
```

Agent 会接收到：
- **名称**: `write_file`
- **描述**: `写入文件`
- **参数**: `file_path` (str), `content` (str)
- **返回值类型**: str

### 2. 参数 Schema 的描述

```python
class FileInput(BaseModel):
    file_path: str = Field(description="文件路径")
    content: str = Field(description="文件内容")

@tool("write_file", args_schema=FileInput)
def write_file(file_path: str, content: str) -> str:
    """写入文件到指定路径"""
    # 实现代码...
```

Agent 额外获得：
- 参数 `file_path` 的含义：文件路径
- 参数 `content` 的含义：文件内容

### 3. 系统提示词的指导

在 `direct_react_agent_v3_fixed.py` 中，系统提示词告诉 Agent：

```python
system_prompt = f"""你是一个专业的 {self.config.platform} 开发专家。

你的任务是根据 PSM（Platform Specific Model）生成完整的 {self.config.platform} 应用代码。

## 工作流程：
1. 创建完整的项目结构（包括所有 __init__.py 文件）
2. 生成所有代码文件
3. 确保测试文件使用正确的导入方式
4. 创建 requirements.txt
5. 使用 install_dependencies 工具安装项目依赖
6. 使用 run_tests 工具运行测试
...
"""
```

这告诉 Agent：
- 什么时候使用 `create_directory`（创建项目结构时）
- 什么时候使用 `write_file`（生成代码文件时）
- 什么时候使用 `install_dependencies`（创建 requirements.txt 后）
- 什么时候使用 `run_tests`（代码生成完成后）

## Agent 的理解过程

### 1. 工具发现
Agent 启动时会收到可用工具列表：
```python
tools = [
    write_file,      # 写入文件
    read_file,       # 读取文件
    create_directory,# 创建目录
    list_directory,  # 列出目录内容
    install_dependencies,  # 安装Python依赖包
    run_tests        # 运行 pytest 测试
]
```

### 2. 任务分解
当 Agent 收到任务时，会：
1. 理解任务目标（生成 FastAPI 应用代码）
2. 根据系统提示词规划步骤
3. 匹配每个步骤需要的工具

### 3. 工具选择
Agent 通过匹配选择工具：

| 任务 | 选择的工具 | 原因 |
|------|-----------|------|
| "需要创建项目目录结构" | `create_directory` | 描述是"创建目录" |
| "写入 main.py 文件" | `write_file` | 描述是"写入文件"，参数匹配需求 |
| "检查文件是否存在" | `read_file` | 描述是"读取文件"，可用于检查 |
| "安装项目依赖" | `install_dependencies` | 描述明确说明功能 |

### 4. 参数推理
Agent 理解参数含义：
```python
# Agent 看到：
# write_file(file_path: str, content: str) -> str
# file_path 的描述是 "文件路径"
# content 的描述是 "文件内容"

# Agent 推理：
# 要写入 main.py，那么：
# - file_path = "main.py"
# - content = <生成的代码内容>
```

## 实际示例

### 示例1：创建项目结构
```
Agent 思考过程：
1. 任务：创建 FastAPI 项目结构
2. 系统提示词说需要创建目录和 __init__.py 文件
3. 可用工具中 create_directory 可以"创建目录"
4. 调用：create_directory("myapp")
5. 调用：create_directory("myapp/models")
6. 可用工具中 write_file 可以"写入文件"
7. 调用：write_file("myapp/__init__.py", "")
```

### 示例2：运行测试
```
Agent 思考过程：
1. 任务：验证生成的代码
2. 系统提示词说要"使用 run_tests 工具运行测试"
3. run_tests 的描述是"运行 pytest 测试"
4. 参数 test_dir 默认是 "tests"
5. 调用：run_tests(test_dir="tests", verbose=True)
```

## 为什么简单描述就够了？

1. **上下文丰富**：系统提示词提供了详细的使用指导
2. **参数自解释**：参数名和类型提供额外信息
3. **工具名称清晰**：`write_file`、`create_directory` 等名称本身就很明确
4. **LLM 的常识**：大语言模型理解常见编程任务

## 最佳实践

### 1. 清晰的工具命名
```python
# 好的命名
@tool
def create_user_in_database(username: str, email: str) -> str:
    """在数据库中创建新用户"""

# 不好的命名
@tool  
def proc_usr(u: str, e: str) -> str:
    """处理用户"""
```

### 2. 描述包含关键信息
```python
# 好的描述
@tool
def compile_sass_to_css(sass_file: str, output_dir: str) -> str:
    """编译 SASS 文件为 CSS。支持 .sass 和 .scss 格式，
    自动处理导入和变量。输出文件名与输入相同但扩展名为 .css"""

# 简单但够用的描述
@tool
def compile_sass_to_css(sass_file: str, output_dir: str) -> str:
    """编译 SASS 文件为 CSS"""
```

### 3. 参数描述要准确
```python
class SearchInput(BaseModel):
    query: str = Field(description="搜索关键词")
    file_type: str = Field(description="文件类型过滤（如 .py, .js）")
    max_results: int = Field(default=10, description="最大返回结果数")
```

### 4. 系统提示词中的使用指导
```python
system_prompt = """
工作流程：
1. 使用 search_files 工具查找所有 Python 文件
2. 使用 analyze_code 工具分析代码质量
3. 使用 generate_report 工具生成报告
"""
```

## 总结

Agent 理解 tool 的机制是多层次的：

1. **工具级别**：通过 name、description、参数说明
2. **系统级别**：通过系统提示词了解何时、如何使用工具
3. **任务级别**：通过任务上下文推理需要哪些工具
4. **经验级别**：LLM 本身的知识帮助理解工具用途

这就是为什么即使工具描述很简单（如"写入文件"），Agent 仍然能够正确使用它们完成复杂任务的原因。