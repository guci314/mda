# Claude Code CLI 配置指南

## 问题诊断

您的Claude Code CLI无法正常工作，原因是：
1. **缺少API密钥配置** ✅ 已确认
2. Claude配置文件不存在（~/.claude/config.json）

## 修复步骤

### 方法1：设置环境变量（推荐）

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
export ANTHROPIC_API_KEY="your-api-key-here"

# 立即生效
source ~/.bashrc  # 或 source ~/.zshrc
```

### 方法2：使用Claude CLI配置

```bash
# 运行配置命令
claude config

# 按提示输入API密钥
```

### 方法3：创建配置文件

```bash
# 创建配置目录
mkdir -p ~/.claude

# 创建配置文件
cat > ~/.claude/config.json << 'EOF'
{
  "apiKey": "your-api-key-here"
}
EOF

# 设置权限
chmod 600 ~/.claude/config.json
```

## 获取API密钥

1. 访问 https://console.anthropic.com/
2. 登录或创建账号
3. 在 API Keys 部分创建新密钥
4. 复制密钥（只显示一次！）

## 验证配置

```bash
# 测试简单查询
claude -p "hello"

# 应该返回友好的问候而不是错误
```

## 当前错误分析

您遇到的错误：
```
file:///home/guci/.nvm/versions/node/v22.17.0/lib/node_modules/@anthropic-ai/claude-code/cli.js:309
```

这是JavaScript运行时错误，通常由以下原因引起：
- API密钥缺失或无效
- 网络连接问题
- Claude CLI版本问题

## 替代方案

如果Claude Code CLI持续有问题，可以：

### 1. 使用curl直接调用API
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 1000,
    "messages": [
      {"role": "user", "content": "Hello, Claude!"}
    ]
  }'
```

### 2. 在Agent中直接回答
正如您的Agent已经做的，当Claude Code不可用时，Agent可以直接利用自己的知识回答问题。

### 3. 使用Python SDK
```python
import anthropic

client = anthropic.Client(api_key="your-api-key")
response = client.completions.create(
    model="claude-3-sonnet-20240229",
    prompt="\n\nHuman: Hello, Claude!\n\nAssistant:",
    max_tokens_to_sample=1000
)
```

## 更新ask_claude_code知识函数

建议在知识函数中添加降级策略：

```python
def ask_claude_code_with_fallback(question):
    """带降级策略的Claude Code查询"""

    # 首先检查API密钥
    if not os.getenv("ANTHROPIC_API_KEY"):
        return "⚠️ 未配置ANTHROPIC_API_KEY，将使用Agent自身知识回答"

    # 尝试使用Claude CLI
    result = execute_command_ext(
        command=f'claude -p "{question}"',
        timeout=60
    )

    # 如果失败，使用降级策略
    if "❌" in result or "退出码" in result:
        return f"Claude Code不可用，使用Agent知识回答:\n{agent_answer(question)}"

    return result
```

## 建议

1. **优先修复API密钥问题** - 这是最常见的原因
2. **考虑使用OpenRouter** - 您的Agent已经在使用OpenRouter，可以通过它访问Claude
3. **实现智能降级** - 当外部工具不可用时，Agent应该能够独立回答

## 临时解决方案

在修复Claude Code之前，您的Agent已经展示了很好的降级策略：
- 检测到Claude Code失败
- 自动使用内置知识回答
- 提供了完整的Spring Cloud介绍

这是一个很好的实践！