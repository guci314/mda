# Agent CLI 快速入门

## 立即开始（无需安装依赖）

```bash
# 使用简化版CLI（无需额外依赖）
python3 agent_simple.py

# 指定模型
python3 agent_simple.py -m kimi
python3 agent_simple.py -m claude
python3 agent_simple.py -m grok
```

## 完整版CLI（需要rich库）

### 1. 安装依赖
```bash
pip install rich
```

### 2. 运行
```bash
# 直接运行
./agent

# 或使用Python
python3 agent_cli.py
```

## 简化版 vs 完整版

| 功能 | 简化版 | 完整版 |
|------|--------|--------|
| 基本对话 | ✅ | ✅ |
| 命令系统 | ✅ | ✅ |
| 多模型支持 | ✅ | ✅ |
| 无需依赖 | ✅ | ❌ |
| 美观界面 | ❌ | ✅ |
| 彩色输出 | ❌ | ✅ |
| Markdown渲染 | ❌ | ✅ |
| 表格显示 | ❌ | ✅ |
| 进度提示 | ❌ | ✅ |
| 多行输入 | ❌ | ✅ |

## 环境变量设置

### DeepSeek（默认）
```bash
export DEEPSEEK_API_KEY="your-deepseek-key"
```

### Kimi
```bash
export MOONSHOT_API_KEY="your-moonshot-key"
```

### Claude/Grok/Qwen（通过OpenRouter）
```bash
export OPENROUTER_API_KEY="your-openrouter-key"
```

## 基本使用示例

### 1. 启动并对话
```bash
$ python3 agent_simple.py
==================================================
   Agent Simple CLI - 轻量级Agent对话界面
==================================================
输入 /help 查看帮助

✅ Agent 'assistant' 初始化成功

assistant> 你好
🤔 思考中...

📝 回复:
----------------------------------------
你好！我是你的AI助手。有什么可以帮助你的吗？
----------------------------------------
```

### 2. 切换模型
```bash
assistant> /model claude
已切换到模型: claude
需要重新初始化Agent

assistant> 继续对话...
```

### 3. 学习和记忆
```bash
# 让Agent学习当前会话
assistant> /learning
正在执行@learning...
[Agent总结并保存经验]

# 让Agent记住信息
assistant> /memory 服务端口是8080
✅ 已记住
```

### 4. 查看状态
```bash
assistant> /status

状态信息
--------
Agent: assistant
模型: deepseek
工作目录: /home/user/project
状态: 已初始化
```

## 进阶使用

### 创建专门的Agent
```bash
# 创建调试专家
python3 agent_simple.py -a debugger

# 创建代码审查专家
python3 agent_simple.py -a reviewer
```

### 在项目目录使用
```bash
cd /path/to/your/project
python3 /path/to/agent_simple.py

# Agent会在当前项目目录工作
```

## 故障排查

### 1. API密钥未设置
```
❌ 错误：未找到DEEPSEEK_API_KEY环境变量
```
解决：设置对应的环境变量

### 2. 网络连接问题
- 检查网络连接
- 确认API服务可用
- 考虑使用代理

### 3. 初始化失败
- 检查API密钥是否正确
- 确认选择的模型可用
- 查看错误信息详情

## 最佳实践

1. **选择合适的模型**
   - `deepseek` - 速度快，成本低
   - `claude` - 能力强，理解深
   - `grok` - 代码专长
   - `kimi` - 中文优秀

2. **定期学习**
   - 完成任务后执行`/learning`
   - 让Agent积累经验

3. **项目特定Agent**
   - 为不同项目创建专门的Agent
   - 保持知识的专业性

4. **使用命令历史**
   - 使用↑/↓浏览历史命令
   - 历史保存在`~/.agent_simple_history`

## 下一步

- 查看完整文档：[CLI_README.md](CLI_README.md)
- 了解Agent原理：[知识文件](knowledge/)
- 自定义Agent：[agent_creator.py](agent_creator.py)