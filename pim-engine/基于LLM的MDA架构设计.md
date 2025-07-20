# 基于 LLM 的 MDA 架构设计

## 背景与动机

传统的符号主义 MDA 方法存在根本性缺陷：
- 模板只能生成骨架代码，无法处理复杂业务逻辑
- 规则转换无法覆盖所有情况
- 生成的代码质量差，需要大量手工修改

## 连接主义 MDA 方案

### 核心理念

将 PIM 模型作为**上下文**和**需求描述**，使用 LLM 理解业务意图并生成完整的实现代码。

```
PIM Model (业务描述) 
    ↓ (LLM 理解)
Prompt Engineering (结构化提示)
    ↓ (LLM 生成)
High-Quality Code (完整实现)
```

## 架构设计

### 1. LLM 集成层

```python
# 抽象接口
class LLMProvider(ABC):
    @abstractmethod
    async def generate_code(
        self, 
        context: str, 
        prompt: str,
        constraints: List[str]
    ) -> str:
        pass

# 具体实现
class GeminiProvider(LLMProvider):
    """使用 Gemini CLI"""
    
class ClaudeProvider(LLMProvider):
    """使用 Claude API"""
    
class LocalLLMProvider(LLMProvider):
    """使用本地 LLM (如 CodeLlama)"""
```

### 2. PIM 到 Prompt 转换器

```python
class PIMToPromptConverter:
    """将 PIM 模型转换为结构化的 LLM 提示"""
    
    def convert_entity(self, entity: Entity) -> str:
        """转换实体定义为自然语言描述"""
        
    def convert_service(self, service: Service) -> str:
        """转换服务和方法为需求描述"""
        
    def convert_flow(self, flow: Flow) -> str:
        """将流程图转换为执行步骤描述"""
        
    def convert_rules(self, rules: List[Rule]) -> str:
        """将业务规则转换为约束条件"""
```

### 3. 增强的代码生成器

```python
class LLMCodeGenerator(CodeGenerator):
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.converter = PIMToPromptConverter()
        
    async def generate_service_method(
        self, 
        method: Method,
        context: PIMModel
    ) -> str:
        # 1. 构建上下文
        entity_context = self.converter.convert_entities(context.entities)
        flow_context = self.converter.convert_flow(method.flow)
        rules_context = self.converter.convert_rules(method.rules)
        
        # 2. 构建提示
        prompt = f"""
        基于以下业务模型生成 {method.name} 方法的完整实现：
        
        实体定义：
        {entity_context}
        
        业务流程：
        {flow_context}
        
        业务规则：
        {rules_context}
        
        要求：
        - 使用 FastAPI 和 SQLAlchemy
        - 包含完整的错误处理
        - 实现所有业务规则验证
        - 添加适当的日志记录
        """
        
        # 3. 调用 LLM 生成代码
        return await self.llm.generate_code(
            context=str(context),
            prompt=prompt,
            constraints=["Python", "Type hints", "Async/await"]
        )
```

## Docker 集成方案

### 1. 更新 Dockerfile

```dockerfile
FROM python:3.11-slim

# 安装 Node.js (for Gemini CLI)
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 安装 Gemini CLI
RUN npm install -g @google/gemini-cli

# Python 依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码
COPY . /app
WORKDIR /app

# 配置 Gemini CLI
COPY gemini-config.json /root/.gemini/settings.json

CMD ["python", "-m", "main"]
```

### 2. 环境变量配置

```yaml
# docker-compose.yml
services:
  pim-engine:
    environment:
      # Gemini API 配置
      - GOOGLE_AI_STUDIO_KEY=${GOOGLE_AI_STUDIO_KEY}
      - VERTEX_AI_PROJECT=${VERTEX_AI_PROJECT}
      
      # Claude API 配置 (备选)
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      
      # LLM 提供商选择
      - LLM_PROVIDER=gemini  # gemini | claude | local
```

## 实现示例

### 用户注册方法的 LLM 生成

**输入 (PIM)**：
```yaml
flows:
  UserService.registerUser:
    steps:
      - Validate email format
      - Check email uniqueness
      - Hash password
      - Create user record
      - Send welcome email
      
rules:
  - validate_email_format: Email must be valid RFC 5322 format
  - password_strength: Password must be at least 8 characters with mixed case and numbers
```

**LLM 生成的代码**：
```python
async def registerUser(self, userData: UserCreate) -> User:
    """Register a new user with comprehensive validation"""
    
    # Step 1: Validate email format
    if not self._is_valid_email(userData.email):
        raise HTTPException(
            status_code=400, 
            detail="Invalid email format. Must comply with RFC 5322"
        )
    
    # Step 2: Check email uniqueness
    existing_user = self.db.query(User).filter(
        User.email == userData.email
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
    
    # Step 3: Validate password strength
    if not self._validate_password_strength(userData.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters with mixed case and numbers"
        )
    
    # Step 4: Hash password
    hashed_password = bcrypt.hashpw(
        userData.password.encode('utf-8'), 
        bcrypt.gensalt()
    )
    
    # Step 5: Create user record
    try:
        new_user = User(
            email=userData.email,
            password_hash=hashed_password.decode('utf-8'),
            created_at=datetime.utcnow(),
            status='pending_verification'
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        # Step 6: Send welcome email
        await self._send_welcome_email(new_user.email)
        
        logger.info(f"User registered successfully: {new_user.email}")
        return new_user
        
    except Exception as e:
        self.db.rollback()
        logger.error(f"User registration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Registration failed. Please try again."
        )
```

## 优势

1. **完整的业务逻辑实现**：不再是 TODO 和 NotImplementedError
2. **理解业务意图**：LLM 能理解流程图和规则的含义
3. **高质量代码**：包含错误处理、日志、安全考虑
4. **灵活适配**：可以生成任何框架的代码
5. **持续改进**：随着 LLM 进化，生成质量不断提升

## 挑战与解决方案

### 1. API 成本
- 使用本地 LLM (CodeLlama, DeepSeek)
- 缓存生成结果
- 仅对复杂逻辑使用 LLM

### 2. 生成一致性
- 提供详细的约束和示例
- 使用 few-shot prompting
- 后处理和验证

### 3. 安全性
- 代码审查机制
- 沙箱执行测试
- 静态分析工具集成

## 下一步

1. 实现 LLM Provider 接口
2. 集成 Gemini CLI 到 Docker
3. 创建 Prompt 工程模板
4. 对比测试：模板 vs LLM 生成
5. 优化提示词以提高生成质量