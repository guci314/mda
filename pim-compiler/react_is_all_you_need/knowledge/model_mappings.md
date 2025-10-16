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
