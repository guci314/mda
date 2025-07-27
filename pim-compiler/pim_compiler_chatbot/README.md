# PIM Compiler Chatbot

基于 LangChain ReAct Agent 的智能 PIM 编译助手。

## 功能特性

- 🔍 **智能搜索**：根据关键词搜索 PIM 文件
- 🚀 **后台编译**：异步执行编译任务
- 📊 **进度监控**：实时查看编译日志和进度
- 🗂️ **项目管理**：列出和清理编译输出

## 快速开始

### 1. 安装依赖

```bash
cd pim-compiler
pip install -r pim_compiler_chatbot/requirements.txt
```

### 2. 配置已完成！

项目已包含 `.env` 文件，其中配置了 DeepSeek API Key，无需额外设置。

### 3. 运行聊天机器人

#### 最简单的方式：

```bash
# 在 pim-compiler 目录下运行
./run_pim_chatbot.sh
```

选择你想要的模式：
1. 命令行模式（使用 LLM）
2. 简化版模式（无需 LLM）
3. Web UI 模式（使用 LLM）
4. 运行测试

#### 或直接运行：

```bash
# 命令行模式
python pim_compiler_chatbot/chatbot.py

# 简化版（无需 LLM）
python pim_compiler_chatbot/chatbot_simple.py

# Web UI
python pim_compiler_chatbot/chatbot_ui.py
```


## 三种使用模式

### 1. 完整版（需要 LLM）
使用 LangChain ReAct Agent，支持自然语言理解：
```bash
export DEEPSEEK_API_KEY="your-key"
python chatbot.py
```

### 2. 简化版（无需 LLM）
直接使用命令，不需要 API Key：
```bash
python chatbot_simple.py
```

### 3. Web UI 版
提供图形界面（需要 LLM）：
```bash
export DEEPSEEK_API_KEY="your-key"
python chatbot_ui.py
```

## 使用示例

### 基本对话流程

```
你: 编译医院系统
助手: 正在搜索医院相关的 PIM 文件...
      找到 1 个相关的 PIM 文件:
      - examples/smart_hospital_system.md
      
      正在编译 examples/smart_hospital_system.md...
      ✅ 已启动编译任务:
      - 日志文件: smart_hospital_system.log
      - 进程 PID: 12345

你: 查看日志
助手: 📋 smart_hospital_system 编译日志分析
      ⏳ 编译正在进行中...
      
      关键进度信息:
      - Step 1: Generating PSM...
      - Step 2: Generating code...
      - Generated: models.py
      - Generated: api.py
      ...
```

### 支持的命令

1. **搜索和编译**
   - "编译医院系统" - 搜索并编译相关系统
   - "编译 examples/library_system.md" - 直接编译指定文件

2. **监控进度**
   - "查看日志" - 查看活动编译任务的日志
   - "查看医院系统日志" - 查看特定系统的日志

3. **项目管理**
   - "列出所有项目" - 显示已编译的项目
   - "清理医院系统" - 清理指定项目的输出

## 技术架构

### 核心组件

1. **PIMCompilerTools**
   - 封装所有编译相关的工具函数
   - 处理文件搜索、编译执行、日志分析

2. **ReAct Agent**
   - 基于 LangChain 的推理-行动循环
   - 自动选择合适的工具完成任务

3. **工具集**
   - `search_pim_files`: 搜索 PIM 文件
   - `compile_pim`: 执行编译命令
   - `check_log`: 分析编译日志
   - `list_compiled_projects`: 列出项目
   - `clean_output`: 清理输出

### 工作流程

```
用户输入
    ↓
ReAct Agent 分析意图
    ↓
选择合适的工具
    ↓
执行工具获取结果
    ↓
分析结果并决定下一步
    ↓
生成最终回复
```

## 测试

运行测试脚本：

```bash
# 测试所有功能
python test_chatbot.py

# 只测试工具
python test_chatbot.py --tools

# 只测试智能体
python test_chatbot.py --agent

# 模拟完整工作流
python test_chatbot.py --workflow
```

## 扩展开发

### 添加新工具

```python
def my_custom_tool(param: str) -> str:
    """自定义工具的实现"""
    return f"处理结果: {param}"

# 在 create_pim_compiler_agent 中添加
tools.append(
    Tool(
        name="my_custom_tool",
        func=my_custom_tool,
        description="工具的描述，告诉 Agent 何时使用"
    )
)
```

### 自定义 LLM 配置

```python
llm_config = {
    "model": "gpt-4",  # 或其他模型
    "temperature": 0.3,
    "max_tokens": 2000,
    "openai_api_base": "https://api.deepseek.com/v1"  # 自定义端点
}

agent = create_pim_compiler_agent(llm_config)
```

## 注意事项

1. **编译器路径**：确保 `pim-compiler` 可执行文件存在
2. **权限问题**：需要执行权限和写入日志的权限
3. **后台进程**：编译任务在后台运行，关闭聊天机器人不会停止编译
4. **日志清理**：定期清理旧的日志文件

## 故障排除

### LLM 连接失败
- 检查 API Key 是否正确设置
- 确认网络连接正常
- 尝试使用不同的 LLM 提供商

### 编译失败
- 检查 pim-compiler 是否可执行
- 确认 PIM 文件路径正确
- 查看详细的错误日志

### 搜索不到文件
- 确认文件在 examples 目录中
- 尝试不同的搜索关键词
- 直接使用完整路径

## License

MIT