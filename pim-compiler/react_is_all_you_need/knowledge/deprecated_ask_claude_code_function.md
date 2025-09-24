# Claude Code交互知识函数

本文件定义了与Claude Code CLI交互的知识函数，使用ExecuteCommandExtended工具处理长时间运行的命令。

## 为什么需要这个函数？

Claude Code是一个强大的编程助手，但响应时间可能较长（10-60秒）。使用ExecuteCommandExtended工具可以：
- 避免超时错误
- 提供更好的用户体验
- 支持流式输出

## @ask_claude_code 知识函数

当你需要向Claude Code提问或请求帮助时，请执行以下步骤：

### 执行前准备

1. **确认Claude Code已安装**：
   - 运行 `which claude` 检查是否已安装
   - 如未安装，提示用户安装

2. **检查API密钥配置**：
   ```bash
   # 检查环境变量
   echo $ANTHROPIC_API_KEY

   # 或检查配置文件
   cat ~/.claude/config.json
   ```
   - 如果未配置，提醒用户设置API密钥
   - 考虑使用降级策略（直接用Agent知识回答）

3. **准备问题**：
   - 明确、具体的问题效果最好
   - 如果涉及代码，考虑包含相关上下文

### 执行步骤

1. **构建命令（使用完整路径）**：
   ```bash
   # 基本格式（使用完整路径避免PATH问题）
   /home/guci/.nvm/versions/node/v22.17.0/bin/claude -p "你的问题"

   # 带文件上下文
   cat file.py | /home/guci/.nvm/versions/node/v22.17.0/bin/claude -p "解释这段代码"

   # 继续上次对话
   /home/guci/.nvm/versions/node/v22.17.0/bin/claude -c -p "继续之前的讨论..."
   ```

2. **使用ExecuteCommandExtended执行（带环境变量）**：
   ```python
   # 因为Claude Code响应较慢，使用扩展执行
   # 注意：需要显式设置API密钥
   result = ExecuteCommandExtended(
       command='export ANTHROPIC_API_KEY="$(cat ~/.claude/config.json | grep apiKey | cut -d\'"\' -f4)" && claude -p "你的问题"',
       timeout=60000,  # 60秒超时
       stream_output=True  # 流式输出
   )

   # 或者使用配置文件
   result = ExecuteCommandExtended(
       command='claude -p "你的问题"',  # CLI会自动读取~/.claude/config.json
       timeout=60000
   )
   ```

3. **处理响应**：
   - 检查执行状态
   - 解析Claude的回复
   - 如果超时，考虑使用更简单的问题

### 常用模式

#### 1. 快速问答
```bash
claude -p "Python中如何处理异常？"
```

#### 2. 代码审查
```bash
cat script.py | claude -p "审查这段代码，找出潜在问题"
```

#### 3. 解释概念
```bash
claude -p "解释React Hooks的工作原理"
```

#### 4. 生成代码
```bash
claude -p "生成一个Python函数，实现二分查找"
```

#### 5. 调试帮助
```bash
# 包含错误信息
echo "错误信息" | claude -p "帮我解决这个错误"
```

### 高级选项

#### 模型选择
```bash
# 使用特定模型
claude --model sonnet -p "你的问题"  # 默认模型
claude --model haiku -p "你的问题"   # 快速模型
claude --model opus -p "你的问题"    # 强大模型
```

#### 会话管理
```bash
# 继续最近的对话
claude -c

# 恢复特定会话
claude -r "session-id" -p "继续讨论"

# 限制交互轮数
claude --max-turns 3 -p "多轮对话问题"
```

### 执行示例

```python
def ask_claude_code(question, context_file=None, continue_session=False):
    """向Claude Code提问的封装函数"""

    # Claude完整路径（避免PATH问题）
    claude_path = "/home/guci/.nvm/versions/node/v22.17.0/bin/claude"

    # 构建命令
    if context_file:
        cmd = f'cat {context_file} | {claude_path} -p "{question}"'
    elif continue_session:
        cmd = f'{claude_path} -c -p "{question}"'
    else:
        cmd = f'{claude_path} -p "{question}"'

    # 使用ExecuteCommandExtended执行
    try:
        result = ExecuteCommandExtended(
            command=cmd,
            timeout=60000,  # 60秒
            stream_output=True
        )

        if result.exit_code == 0:
            return result.output
        else:
            return f"执行失败: {result.error}"

    except TimeoutError:
        return "Claude Code响应超时，请尝试简化问题"
```

### 注意事项

1. **响应时间**：
   - Claude Code通常需要10-60秒响应
   - 复杂问题可能需要更长时间
   - 使用ExecuteCommandExtended避免超时

2. **上下文管理**：
   - 使用 `-c` 继续之前的对话
   - 会话ID保存在 `~/.claude/` 目录

3. **错误处理**：
   - 检查Claude是否已安装
   - 处理网络连接问题
   - 优雅处理超时

4. **最佳实践**：
   - 问题要具体明确
   - 提供必要的上下文
   - 对于长代码，使用管道输入
   - 考虑分解复杂问题

### 降级策略

当Claude Code不可用时（如API密钥缺失、网络问题），应该采用降级策略：

```python
def handle_claude_failure(question, error_msg):
    """处理Claude Code失败的降级策略"""

    # 检查错误类型
    if "API" in error_msg or "密钥" in error_msg:
        print("⚠️ Claude Code API密钥未配置")
    elif "网络" in error_msg or "timeout" in error_msg:
        print("⚠️ 网络连接问题")
    else:
        print(f"⚠️ Claude Code错误: {error_msg}")

    # 降级策略：使用Agent自身知识
    print("\n将使用Agent自身知识回答您的问题...")
    # 直接用Agent的能力回答，而不依赖外部工具
    return answer_with_agent_knowledge(question)
```

### 常见问题

**Q: Claude Code报错"退出码: 1"怎么办？**
A: 通常是API密钥问题。检查：
- 环境变量 `ANTHROPIC_API_KEY` 是否设置
- 配置文件 `~/.claude/config.json` 是否存在
- 如果都没有，参考 `claude_code_setup_guide.md`

**Q: Claude Code响应很慢怎么办？**
A: 这是正常的，使用ExecuteCommandExtended工具可以避免超时。也可以考虑：
- 使用更快的模型（如haiku）
- 简化问题
- 分步提问

**Q: 如何查看之前的对话历史？**
A: 对话历史保存在 `~/.claude/` 目录，可以使用 `claude -c` 继续最近对话。

**Q: 能否批量处理多个问题？**
A: 可以写脚本循环调用，但要注意：
- 每个请求都需要时间
- 考虑使用会话功能保持上下文
- 注意API限制

**Q: Claude Code完全无法使用怎么办？**
A: 采用降级策略：
1. Agent直接回答（就像你的Agent已经做的）
2. 使用其他LLM服务（如通过OpenRouter）
3. 使用curl直接调用Anthropic API

## 总结

`@ask_claude_code` 函数提供了与Claude Code CLI交互的标准方式，通过ExecuteCommandExtended工具处理长时间运行的命令，确保稳定可靠的交互体验。