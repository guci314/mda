# Ask Claude 知识函数

直接调用Claude（通过OpenRouter），获得高质量的回答。比Claude Code CLI更可靠、更快速。

**重要**：当看到 `@ask_claude` 时，必须使用 `ask_claude` 工具调用Claude API，而不是用自身知识直接回答。

## 为什么需要这个函数？

1. **Claude Code CLI不稳定**：环境问题、Node.js错误
2. **直接API更可靠**：通过OpenRouter调用Claude API
3. **更好的模型选择**：可以选择Claude 3.5 Sonnet、Opus等
4. **Agent间协作**：让Agent能调用更强大的Claude

## @ask_claude 知识函数

当你看到 `@ask_claude` 命令时，**必须执行以下步骤**（不要直接用自己的知识回答）：

### 执行前检查

1. **确认OpenRouter API密钥**：
   ```bash
   # 从.env文件加载
   export OPENROUTER_API_KEY="$(grep OPENROUTER_API_KEY .env | cut -d'=' -f2)"

   # 或检查环境变量
   echo $OPENROUTER_API_KEY
   ```

2. **评估是否需要Claude**：
   - 简单问题：使用Agent自身知识
   - 复杂问题：调用Claude
   - 最新信息：调用Claude

### 执行步骤

1. **使用ask_claude工具**（如果可用）：
   ```
   调用工具: ask_claude
   参数:
   - question: "用户的问题"
   - model: "anthropic/claude-sonnet-4" (默认，Claude Sonnet 4最新版)
   ```

2. **备选方案：准备Python脚本调用Claude**（如果ask_claude工具不可用）：
   ```python
   import os
   import json
   import requests

   def ask_claude(question, model="anthropic/claude-sonnet-4"):
       """通过OpenRouter调用Claude"""

       api_key = os.getenv("OPENROUTER_API_KEY")
       if not api_key:
           return "❌ 未设置OPENROUTER_API_KEY"

       headers = {
           "Authorization": f"Bearer {api_key}",
           "Content-Type": "application/json",
           "HTTP-Referer": "http://localhost",
           "X-Title": "Agent System"
       }

       data = {
           "model": model,
           "messages": [
               {"role": "user", "content": question}
           ],
           "temperature": 0,
           "max_tokens": 4000
       }

       try:
           response = requests.post(
               "https://openrouter.ai/api/v1/chat/completions",
               headers=headers,
               json=data,
               timeout=30
           )

           if response.status_code == 200:
               result = response.json()
               return result["choices"][0]["message"]["content"]
           else:
               return f"❌ API错误: {response.status_code} - {response.text}"

       except Exception as e:
           return f"❌ 请求失败: {e}"
   ```

2. **创建临时脚本执行**：
   ```python
   # 写入临时文件
   write_file("/tmp/ask_claude.py", script_content)

   # 执行脚本
   result = execute_command(
       f'python /tmp/ask_claude.py "{question}"'
   )

   # 清理
   execute_command("rm /tmp/ask_claude.py")
   ```

3. **处理响应**：
   - 检查是否成功
   - 解析Claude的回答
   - 如果失败，使用Agent自身知识

### 实用示例

#### 1. 复杂代码分析
```python
@ask_claude("分析这段React代码的性能问题：[代码]")
```

#### 2. 架构设计
```python
@ask_claude("设计一个支持100万并发的消息队列架构")
```

#### 3. 深度推理
```python
@ask_claude("比较函数式编程和面向对象编程在大型项目中的优劣")
```

#### 4. 最新技术
```python
@ask_claude("介绍2024年最新的前端框架趋势")
```

### 模型选择

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| `anthropic/claude-sonnet-4` | Claude Sonnet 4，最新最强 | **默认选择** |
| `anthropic/claude-3.5-sonnet` | 上一代Sonnet | 备选 |
| `anthropic/claude-3-opus` | 深度推理 | 复杂任务 |
| `anthropic/claude-3-haiku` | 最快速度、低成本 | 简单查询 |

### 完整实现

```python
def ask_claude_with_fallback(question, use_opus=False):
    """带降级的Claude调用"""

    # 选择模型
    model = "anthropic/claude-3-opus" if use_opus else "anthropic/claude-3.5-sonnet"

    # 创建临时Python脚本
    script = f'''
import os
import json
import requests

question = """{question}"""

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("❌ 未设置OPENROUTER_API_KEY")
    exit(1)

headers = {{
    "Authorization": f"Bearer {{api_key}}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Agent System"
}}

data = {{
    "model": "{model}",
    "messages": [{{"role": "user", "content": question}}],
    "temperature": 0,
    "max_tokens": 4000
}}

try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )

    if response.status_code == 200:
        result = response.json()
        print(result["choices"][0]["message"]["content"])
    else:
        print(f"❌ API错误: {{response.status_code}}")
        print(response.text)
except Exception as e:
    print(f"❌ 请求失败: {{e}}")
'''

    # 写入并执行
    write_file("/tmp/ask_claude_temp.py", script)
    result = execute_command("python /tmp/ask_claude_temp.py", timeout=60)
    execute_command("rm -f /tmp/ask_claude_temp.py")

    # 检查结果
    if "❌" in result or not result.strip():
        # 降级到Agent自身知识
        print("⚠️ Claude不可用，使用Agent知识回答")
        return answer_with_agent_knowledge(question)

    return result
```

### 使用场景对比

| 场景 | 使用Agent自身 | 调用Claude |
|------|--------------|------------|
| 基础编程知识 | ✅ | ❌ 浪费 |
| 简单代码生成 | ✅ | ❌ 不必要 |
| 复杂架构设计 | ⚠️ 可以尝试 | ✅ 推荐 |
| 深度代码分析 | ❌ 能力不足 | ✅ 必须 |
| 最新技术趋势 | ❌ 知识过时 | ✅ 必须 |
| 哲学性讨论 | ⚠️ 基础 | ✅ 更深入 |

### 成本考虑

通过OpenRouter调用Claude的价格（参考）：
- Claude 3.5 Sonnet: $3/1M输入，$15/1M输出
- Claude 3 Opus: $15/1M输入，$75/1M输出
- Claude 3 Haiku: $0.25/1M输入，$1.25/1M输出

建议：
1. 默认使用Sonnet（性价比最高）
2. 复杂任务才用Opus
3. 简单查询可以用Haiku

### 错误处理

```python
def handle_claude_errors(error_msg):
    """处理各种错误情况"""

    if "rate limit" in error_msg.lower():
        print("⚠️ 达到速率限制，等待后重试")
        time.sleep(5)
        return retry_once()

    elif "401" in error_msg or "unauthorized" in error_msg:
        print("❌ API密钥无效")
        return use_agent_knowledge()

    elif "timeout" in error_msg.lower():
        print("⚠️ 请求超时，简化问题")
        return ask_simpler_question()

    else:
        print(f"⚠️ 未知错误：{error_msg}")
        return use_agent_knowledge()
```

### 注意事项

1. **API密钥管理**：
   - 确保OPENROUTER_API_KEY已设置
   - 不要在代码中硬编码密钥

2. **成本控制**：
   - 监控API使用量
   - 优先使用Agent自身能力
   - 合理选择模型

3. **降级策略**：
   - 始终准备降级方案
   - 不要依赖外部API
   - Agent自身能力是基础

4. **响应时间**：
   - Claude通常需要5-15秒
   - 设置合理的超时
   - 考虑用户体验

## 总结

`@ask_claude`函数提供了直接访问Claude强大能力的途径，通过OpenRouter API实现稳定可靠的调用。结合智能降级策略，确保系统始终能够提供价值。

**核心原则**：
- 简单问题用Agent自己解决
- 复杂问题调用Claude
- 始终有降级方案
- 成本效益优先