# Agent CLI - 命令行界面

类似Claude Code的交互式命令行界面，用于与Agent对话。

## 快速开始

```bash
# 基本启动
./agent

# 指定Agent和模型
./agent -a myagent -m claude

# 开启调试模式
./agent -d

# 指定工作目录
./agent -w /path/to/project
```

## 安装依赖

```bash
pip install rich
```

## 功能特性

### 1. 交互式对话
- 直接输入文本与Agent对话
- 支持Markdown格式输出
- 实时显示思考状态

### 2. 命令系统

| 命令 | 描述 | 示例 |
|------|------|------|
| `/help` | 显示帮助信息 | `/help` |
| `/exit` | 退出CLI | `/exit` |
| `/clear` | 清屏 | `/clear` |
| `/status` | 查看Agent状态 | `/status` |
| `/model [name]` | 切换模型 | `/model claude` |
| `/agent [name]` | 切换Agent | `/agent debugger` |
| `/list` | 列出所有Agent | `/list` |
| `/create <name>` | 创建新Agent | `/create helper` |
| `/switch <name>` | 切换到其他Agent | `/switch helper` |
| `/compact` | 压缩历史记录 | `/compact` |
| `/learning` | 执行学习函数 | `/learning` |
| `/memory <text>` | 记住信息 | `/memory 端口是8080` |
| `/knowledge` | 显示知识库 | `/knowledge` |
| `/tools` | 列出可用工具 | `/tools` |
| `/history [n]` | 显示历史命令 | `/history 20` |
| `/config` | 显示配置 | `/config` |
| `/debug` | 开关调试模式 | `/debug` |
| `/multi` | 多行输入模式 | `/multi` |

### 3. 模型支持

内置模型配置：
- `deepseek` - DeepSeek Chat（默认）
- `kimi` - Kimi K2 Turbo
- `claude` - Claude 3.5 Sonnet（通过OpenRouter）
- `grok` - Grok Code Fast（通过OpenRouter）
- `qwen` - Qwen3 Coder（通过OpenRouter）

### 4. 多行输入

使用`/multi`命令进入多行输入模式：

```
assistant> /multi
进入多行输入模式，输入'###'结束
... 第一行
... 第二行
... 第三行
... ###
```

### 5. 快捷键

- `Tab` - 命令自动补全
- `↑/↓` - 历史命令导航
- `Ctrl+C` - 取消当前输入
- `Ctrl+D` - 退出（同`/exit`）

## 环境变量

确保设置了对应的API密钥：

```bash
export DEEPSEEK_API_KEY="your-key"
export MOONSHOT_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"
```

## 使用示例

### 基本对话

```bash
$ ./agent
╔═══════════════════════════════════════╗
║     Agent CLI - Powered by MDA       ║
║   Interactive Agent Command Line     ║
╚═══════════════════════════════════════╝

欢迎使用Agent CLI v1.0.0
输入 /help 查看可用命令

Agent 'assistant' 已就绪

assistant> 你好，请介绍一下自己
Agent思考中...

Agent:
你好！我是一个基于React Agent架构的AI助手...

assistant> /status
╭─────────────── 状态信息 ───────────────╮
│                                        │
│ Agent状态                              │
│ ────────────────────                  │
│ 名称: assistant                        │
│ 模型: deepseek-chat                    │
│ 工作目录: /home/user/project           │
│ 会话开始: 2025-10-08 10:30:00         │
│ 消息数: 1                              │
│ 调试模式: 关闭                         │
│                                        │
╰────────────────────────────────────────╯
```

### 创建和管理Agent

```bash
# 创建新Agent
assistant> /create debugger
成功创建Agent: debugger

# 切换到新Agent
assistant> /switch debugger
已切换到Agent: debugger

# 列出所有Agent
debugger> /list
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ 名称        ┃ 路径                 ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ assistant   │ ~/.agent/assistant   │
│ debugger    │ ~/.agent/debugger    │
└─────────────┴──────────────────────┘
```

### 学习和记忆

```bash
# 让Agent学习本次会话
assistant> /learning
Agent思考中...
学习完成：
已从本次会话中提取并保存了3条经验...

# 让Agent记住重要信息
assistant> /memory 服务器地址是192.168.1.100
已记住

# 查看Agent知识
assistant> /knowledge
[显示knowledge.md内容]
```

### 模型切换

```bash
# 查看可用模型
assistant> /model
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ 名称     ┃ 模型ID                  ┃ 状态    ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ deepseek │ deepseek-chat           │ ✓ 当前  │
│ kimi     │ kimi-k2-turbo-preview   │         │
│ claude   │ anthropic/claude-3.5... │         │
│ grok     │ x-ai/grok-code-fast-1   │         │
└──────────┴─────────────────────────┴─────────┘

# 切换到Claude
assistant> /model claude
已切换到模型: claude
需要重新初始化Agent以应用更改
```

## 高级功能

### 调试模式

开启调试模式查看详细错误信息：

```bash
# 通过命令开启
assistant> /debug
调试模式已开启

# 或启动时开启
./agent -d
```

### 会话管理

```bash
# 保存当前会话
assistant> /save my_session
会话已保存到: my_session.json

# 加载之前的会话
assistant> /load my_session.json
已加载会话: my_session.json
```

## 架构设计

```
agent_cli.py
├── AgentCLI类
│   ├── 命令处理器
│   ├── 消息处理器
│   ├── Agent管理器
│   └── 历史管理器
├── 模型配置
├── Rich UI组件
└── 主循环
```

## 扩展开发

### 添加新命令

在`AgentCLI.__init__()`中添加命令映射：

```python
self.commands = {
    '/mycommand': self.cmd_mycommand,
    ...
}

def cmd_mycommand(self, args: str = ""):
    """我的新命令"""
    # 实现命令逻辑
    console.print("执行我的命令")
```

### 添加新模型

在`model_configs`中添加配置：

```python
self.model_configs = {
    'mymodel': {
        'model': 'model-id',
        'base_url': 'https://api.example.com/v1',
        'api_key_env': 'MYMODEL_API_KEY'
    },
    ...
}
```

## 注意事项

1. **API密钥安全**：不要在代码中硬编码API密钥
2. **历史文件**：命令历史保存在`~/.agent_cli_history`
3. **Agent状态**：Agent状态保存在`~/.agent/[name]/`
4. **并发限制**：同一Agent不支持多个CLI实例同时运行

## 故障排查

### Agent初始化失败
- 检查API密钥环境变量
- 确认网络连接
- 使用`-d`开启调试模式查看详细错误

### 命令不工作
- 使用`/help`确认命令格式
- 检查是否需要参数
- 确认Agent已初始化

### 响应缓慢
- 检查网络延迟
- 考虑切换到更快的模型
- 使用本地模型（如deepseek）

## 版本历史

- v1.0.0 - 初始版本，基本CLI功能

## License

MIT