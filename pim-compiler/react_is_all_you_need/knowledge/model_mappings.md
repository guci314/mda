# LLM模型切换

## 契约函数 @切换模型(target_model)

当用户要求切换LLM模型时，必须严格执行以下契约。

### 函数签名
```
契约函数 @切换模型(target_model)
```

### 强制要求
⚠️ **必须使用ExecutionContext严格执行每个步骤**

### 参数
- `target_model`: 目标模型（简称或完整名称）

### 常用简称映射
- `grok` → `x-ai/grok-code-fast-1` (代码专长，推荐)
- `claude` → `anthropic/claude-sonnet-4.5` (最新Claude)
- `deepseek` → `deepseek-chat`
- `kimi` → `kimi-k2-turbo-preview`
- `qwen` → `qwen/qwen3-coder`

### 核心规则
- **包含 `/` 的模型** → OpenRouter (`https://openrouter.ai/api/v1`, `OPENROUTER_API_KEY`)
- **不包含 `/` 的模型** → 专用API
  - `deepseek-chat` → `https://api.deepseek.com/v1`, `DEEPSEEK_API_KEY`
  - `kimi-k2-turbo-preview` → `https://api.moonshot.cn/v1`, `MOONSHOT_API_KEY`

### 契约执行步骤

#### 步骤1: 初始化ExecutionContext
```
context(action='set_goal', goal='契约函数 @切换模型')
```

#### 步骤2: 解析目标模型名称
```
context(action='add_step', step='解析目标模型名称')
- 如果是简称，转换为完整名称（参考上面的映射）
- 记录完整模型名称
context(action='complete_step')
```

#### 步骤3: 确定API配置
```
context(action='add_step', step='确定API配置')
- 应用核心规则确定base_url和api_key_name
- 包含 `/` → OpenRouter
- 不包含 `/` → 专用API
context(action='complete_step')
```

#### 步骤4: 读取API密钥
```
context(action='add_step', step='读取API密钥')
- 使用read_file工具读取：/Users/guci/aiProjects/mda/pim-compiler/.env
- 解析找到对应的KEY_NAME=value
- 提取API密钥值
context(action='complete_step')
```

#### 步骤5: 调用update_api_config
```
context(action='add_step', step='调用update_api_config')
- 工具：当前agent名称
- 方法：update_api_config
- 参数：model_name, base_url, api_key
context(action='complete_step')
```

#### 步骤6: 报告结果
```
context(action='add_step', step='报告结果')
- 确认切换成功
- 显示新的模型配置
context(action='set_status', status='completed')
context(action='complete_step')
```

### 触发方式
- `@切换模型 grok`
- `切换到grok` / `切换llm到grok` / `使用grok模型`

## 契约函数 @获取模型配置(model_name)

当需要获取模型的正确配置信息时调用此函数，特别是在创建子Agent时。

### 函数签名
```
契约函数 @获取模型配置(model_name) → {model, base_url, api_key_env}
```

### 参数
- `model_name`: 模型名称（简称或完整名称）

### 返回值
```json
{
  "model": "完整的模型名称",
  "base_url": "API地址",
  "api_key_env": "环境变量名（不是值！）"
}
```

### 执行步骤

#### 步骤1: 解析模型名称
```
如果model_name是简称，转换为完整名称：
- "grok" → "x-ai/grok-code-fast-1"
- "claude" → "anthropic/claude-3.5-sonnet"
- "deepseek" → "deepseek-chat"
- "kimi" → "kimi-k2-turbo-preview"
- "qwen" → "qwen/qwen3-coder"
- "gemini" → "gemini-2.5-flash"

如果不是简称，保持原样
```

#### 步骤2: 确定API配置
```
根据模型名称确定base_url和api_key_env：

如果模型名包含 "/"：
  base_url = "https://openrouter.ai/api/v1"
  api_key_env = "OPENROUTER_API_KEY"

否则，根据具体模型：
  如果是 "deepseek-chat":
    base_url = "https://api.deepseek.com/v1"
    api_key_env = "DEEPSEEK_API_KEY"

  如果是 "kimi-k2-turbo-preview" 或 "kimi-k2-0711-preview":
    base_url = "https://api.moonshot.cn/v1"
    api_key_env = "MOONSHOT_API_KEY"

  如果是 "gemini-2.5-flash" 或 "gemini-2.5-pro":
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    api_key_env = "GEMINI_API_KEY"

  其他情况：
    返回错误："未知的模型配置"
```

#### 步骤3: 返回配置
```json
{
  "model": "{完整模型名}",
  "base_url": "{API地址}",
  "api_key_env": "{环境变量名}"
}
```

### 使用示例

#### 示例1: OpenRouter模型
```
输入: @获取模型配置("grok")
输出: {
  "model": "x-ai/grok-code-fast-1",
  "base_url": "https://openrouter.ai/api/v1",
  "api_key_env": "OPENROUTER_API_KEY"
}
```

#### 示例2: DeepSeek
```
输入: @获取模型配置("deepseek")
输出: {
  "model": "deepseek-chat",
  "base_url": "https://api.deepseek.com/v1",
  "api_key_env": "DEEPSEEK_API_KEY"
}
```

#### 示例3: 完整名称
```
输入: @获取模型配置("anthropic/claude-3.5-sonnet")
输出: {
  "model": "anthropic/claude-3.5-sonnet",
  "base_url": "https://openrouter.ai/api/v1",
  "api_key_env": "OPENROUTER_API_KEY"
}
```

### 在@create_subagent中的使用

```python
# 在创建子Agent时调用@获取模型配置
def create_subagent(agent_type, domain, requirements, model="claude"):
    # 步骤2: 配置LLM模型
    config = @获取模型配置(model)

    # 创建state.json
    state_config = {
        "name": agent_type,
        "description": "专业描述...",
        "model": config["model"],
        "base_url": config["base_url"],
        "api_key_env": config["api_key_env"],  # 使用环境变量名
        "work_dir": work_dir,
        # ... 其他配置
    }

    # 写入state.json
    write_file(f"~/.agent/{agent_type}/state.json", json.dumps(state_config))
```

### 重要原则
1. **绝不返回API密钥值** - 只返回环境变量名
2. **默认使用claude** - 如果未指定模型，使用"anthropic/claude-3.5-sonnet"
3. **验证配置** - 确保base_url和api_key_env正确匹配
4. **支持简称** - 自动转换常用简称为完整名称

### 触发方式
- 在@create_subagent中自动调用
- 手动调用：`@获取模型配置 deepseek`
