# 正确的LLM配置示例

## 问题总结

子Agent的LLM配置经常出现以下错误：
1. **API密钥硬编码** - 安全风险，应使用环境变量
2. **模型与API不匹配** - 如model是grok但base_url是deepseek
3. **缺少api_key_env字段** - 导致无法读取环境变量

## 正确的state.json配置示例

### 示例1：使用OpenRouter的模型（推荐）
```json
{
  "name": "book_management_agent",
  "description": "图书管理专业Agent，负责图书的增删改查、库存管理、分类管理、ISBN管理等核心功能",
  "model": "anthropic/claude-3.5-sonnet",
  "base_url": "https://openrouter.ai/api/v1",
  "api_key_env": "OPENROUTER_API_KEY",
  "work_dir": "/Users/guci/robot_projects/book_app",
  "has_compact": false,
  "message_count": 0,
  "timestamp": "2025-10-17T14:26:55.689313",
  "task_count": 0,
  "children": []
}
```

### 示例2：使用DeepSeek
```json
{
  "name": "customer_management_agent",
  "description": "客户管理专业Agent，负责客户注册、会员管理、信息维护、信用评分等功能",
  "model": "deepseek-chat",
  "base_url": "https://api.deepseek.com/v1",
  "api_key_env": "DEEPSEEK_API_KEY",
  "work_dir": "/Users/guci/robot_projects/book_app",
  "has_compact": false,
  "message_count": 0,
  "timestamp": "2025-10-17T14:06:09.945446",
  "task_count": 0,
  "children": []
}
```

### 示例3：使用Grok（通过OpenRouter）
```json
{
  "name": "borrow_management_agent",
  "description": "借阅管理专业Agent，负责图书借阅、归还、续借、逾期处理、罚款计算等功能",
  "model": "x-ai/grok-code-fast-1",
  "base_url": "https://openrouter.ai/api/v1",
  "api_key_env": "OPENROUTER_API_KEY",
  "work_dir": "/Users/guci/robot_projects/book_app",
  "has_compact": false,
  "message_count": 0,
  "timestamp": "2025-10-17T14:06:22.154456",
  "task_count": 0,
  "children": []
}
```

## 模型配置规则

### 规则1：包含"/"的模型使用OpenRouter
```python
if "/" in model_name:
    base_url = "https://openrouter.ai/api/v1"
    api_key_env = "OPENROUTER_API_KEY"
```

支持的模型：
- `anthropic/claude-3.5-sonnet` ⭐ 推荐
- `anthropic/claude-3-opus`
- `anthropic/claude-3-haiku`
- `x-ai/grok-code-fast-1`
- `qwen/qwen3-coder`
- `meta-llama/llama-3-70b-instruct`

### 规则2：不包含"/"的模型使用专用API
```python
if "/" not in model_name:
    if model_name == "deepseek-chat":
        base_url = "https://api.deepseek.com/v1"
        api_key_env = "DEEPSEEK_API_KEY"
    elif model_name.startswith("kimi"):
        base_url = "https://api.moonshot.cn/v1"
        api_key_env = "MOONSHOT_API_KEY"
    elif model_name.startswith("gemini"):
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        api_key_env = "GEMINI_API_KEY"
```

## 创建子Agent时的正确代码示例

```python
def create_sub_agent_with_correct_llm():
    """正确创建子Agent的LLM配置"""

    agent_type = "book_management_agent"
    model = "anthropic/claude-3.5-sonnet"  # 或从参数传入

    # 1. 根据模型名确定API配置
    if "/" in model:
        base_url = "https://openrouter.ai/api/v1"
        api_key_env = "OPENROUTER_API_KEY"
    else:
        # 根据具体模型设置
        if model == "deepseek-chat":
            base_url = "https://api.deepseek.com/v1"
            api_key_env = "DEEPSEEK_API_KEY"
        # ... 其他模型配置

    # 2. 创建state.json（注意：使用api_key_env而非api_key）
    state_config = {
        "name": agent_type,
        "description": "专业描述...",
        "model": model,
        "base_url": base_url,
        "api_key_env": api_key_env,  # ⚠️ 不是api_key！
        "work_dir": work_dir,
        "has_compact": False,
        "message_count": 0,
        "timestamp": current_time,
        "task_count": 0,
        "children": []
    }

    # 3. 写入state.json
    state_path = f"~/.agent/{agent_type}/state.json"
    write_file(state_path, json.dumps(state_config, indent=2))
```

## 常见错误示例 ❌

### 错误1：硬编码API密钥
```json
{
  "api_key": "sk-or-v1-11927f7b58b969..."  // ❌ 永远不要这样做！
}
```

### 错误2：模型与API不匹配
```json
{
  "model": "x-ai/grok-code-fast-1",
  "base_url": "https://api.deepseek.com/v1"  // ❌ Grok模型用DeepSeek API
}
```

### 错误3：缺少api_key_env
```json
{
  "model": "deepseek-chat",
  "base_url": "https://api.deepseek.com/v1"
  // ❌ 缺少api_key_env字段
}
```

## 验证清单 ✅

创建子Agent后，检查其state.json：
- [ ] 有api_key_env字段（不是api_key）
- [ ] api_key_env的值是环境变量名（如"OPENROUTER_API_KEY"）
- [ ] model和base_url匹配
- [ ] description描述专业准确
- [ ] work_dir路径正确
- [ ] 没有硬编码的密钥

## 环境变量配置

确保在`.env`文件中配置了对应的API密钥：
```bash
# /Users/guci/aiProjects/mda/pim-compiler/.env
OPENROUTER_API_KEY=sk-or-v1-xxxxx
DEEPSEEK_API_KEY=sk-xxxxx
MOONSHOT_API_KEY=sk-xxxxx
GEMINI_API_KEY=AIzxxxxx
```

## 总结

正确的LLM配置是子Agent能够独立运行的关键。@create_subagent契约函数已经更新，明确要求：
1. 使用api_key_env指定环境变量名
2. model和base_url必须匹配
3. 绝对禁止硬编码API密钥

这样可以确保：
- ✅ 安全性（不暴露密钥）
- ✅ 灵活性（可以切换API密钥）
- ✅ 正确性（模型能够正常调用）