# 使用 AI 生成代码指南

## 概述

PIM Engine 现在支持使用 AI（Gemini、Claude 等）来生成高质量的业务代码，而不仅仅是模板化的 CRUD 操作。

## 快速开始

### 1. 配置环境

创建 `.env` 文件：
```bash
cp .env.llm.example .env
```

编辑 `.env` 文件，添加你的 API Key：
```env
# Gemini API Key (从 https://aistudio.google.com/app/apikey 获取)
GOOGLE_AI_STUDIO_KEY=your-api-key-here

# 代理设置（如果在中国需要）
PROXY_HOST=host.docker.internal  # Docker Desktop
# PROXY_HOST=172.17.0.1  # Linux Docker
PROXY_PORT=7890  # 你的代理端口
```

### 2. 启动服务

对于 Linux 用户：
```bash
./start-with-gemini-linux.sh
```

对于 Mac/Windows Docker Desktop 用户：
```bash
./start-with-gemini.sh
```

### 3. 使用 Web 界面

1. 访问 http://localhost:8001/models
2. 确保模型已加载（点击"刷新列表"）
3. 在代码生成区域：
   - 选择目标平台（如 FastAPI）
   - **勾选"使用 AI"选项**
   - 点击"生成代码"

## AI 生成 vs 模板生成

### 模板生成（传统方式）
```python
async def registerUser(self, userData: User) -> Any:
    """Register a new user with validation"""
    # TODO: Implement business logic
    raise NotImplementedError("registerUser not implemented")
```

### AI 生成（新方式）
```python
async def registerUser(self, userData: UserCreate) -> User:
    """Register a new user with comprehensive validation"""
    
    # Validate email format
    if not self._is_valid_email(userData.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check email uniqueness
    existing_user = self.db.query(User).filter(User.email == userData.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Validate password strength
    if not self._validate_password_strength(userData.password):
        raise HTTPException(status_code=400, detail="Password too weak")
    
    # Hash password
    hashed_password = bcrypt.hashpw(userData.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user record
    try:
        new_user = User(
            email=userData.email,
            password_hash=hashed_password.decode('utf-8'),
            created_at=datetime.utcnow()
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        # Send welcome email
        await self._send_welcome_email(new_user.email)
        
        logger.info(f"User registered: {new_user.email}")
        return new_user
        
    except Exception as e:
        self.db.rollback()
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")
```

## 支持的 AI 提供商

### 1. Gemini (推荐)
- 免费额度：60 请求/分钟，1000 请求/天
- 需要代理（在中国）
- 支持超长上下文（1M tokens）

### 2. Claude (Anthropic)
- 需要付费 API Key
- 生成质量高
- 不需要代理

### 3. 本地 LLM (Ollama)
- 完全免费
- 不需要网络
- 质量可能较低

## API 使用

### 检查 LLM 提供商状态
```bash
curl http://localhost:8001/api/v1/codegen/llm/providers
```

### 使用 API 生成代码
```bash
curl -X POST http://localhost:8001/api/v1/codegen/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "user_management",
    "platform": "fastapi",
    "use_llm": true,
    "llm_provider": "gemini",
    "options": {
      "use_llm_for_all": true
    }
  }'
```

## 故障排除

### 1. Gemini 连接失败
- 检查代理设置是否正确
- 确认 API Key 有效
- 查看容器日志：`docker compose -f docker-compose.llm.yml logs pim-engine`

### 2. 代理配置
- Docker Desktop：使用 `host.docker.internal`
- Linux Docker：使用 `docker0` 网桥 IP（通常是 `172.17.0.1`）
- 可以通过 `ip addr show docker0` 查看

### 3. 生成速度慢
- AI 生成比模板慢是正常的
- 复杂业务逻辑可能需要 30-60 秒
- 可以考虑使用本地 LLM 加速

## 最佳实践

1. **PIM 模型质量**：AI 生成的代码质量取决于 PIM 模型的详细程度
   - 详细描述业务规则
   - 明确定义流程步骤
   - 提供清晰的实体关系

2. **混合使用**：
   - 简单 CRUD 使用模板（快速）
   - 复杂业务逻辑使用 AI（高质量）

3. **代码审查**：
   - AI 生成的代码应该审查
   - 可能需要小幅调整
   - 但基本结构和逻辑通常是正确的

## 示例项目

1. 用户管理系统：包含注册、认证、权限管理
2. 订单管理系统：包含库存检查、支付流程、状态管理
3. 工作流系统：包含审批流程、状态机、通知

每个示例都展示了 AI 如何理解业务规则并生成相应的实现代码。