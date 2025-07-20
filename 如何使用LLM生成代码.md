# 如何使用基于LLM的MDA生成代码

## 理解两种方法的区别

### ❌ 符号主义方法（传统模板）
```python
# 固定的模板替换
template = "class {entity_name}(BaseModel):\n    {attributes}"
code = template.format(entity_name="User", attributes="name: str")
```

### ✅ 连接主义方法（LLM理解）
```
Claude读取PIM → 理解业务含义 → 推理最佳实现 → 生成定制代码
```

## 使用Claude Code生成代码

### 方法1：直接在Claude Code中使用

1. **打开Claude Code**
2. **输入命令**：
   ```
   /mda-generate-fastapi domain=用户管理_psm service=user-service
   ```

3. **Claude会**：
   - 读取 `models/domain/用户管理_psm.md`
   - 理解业务需求（不是机械解析）
   - 生成适合的FastAPI代码
   - 创建完整项目结构

### 方法2：通过对话引导生成

您可以直接与Claude对话：

```
请基于 models/domain/用户管理_psm.md 生成一个FastAPI服务。
要求：
1. 理解业务规则并实现相应的验证
2. 考虑性能需求（10000并发用户）
3. 实现完整的认证和授权系统
4. 包含用户活动审计功能
```

Claude会理解这些需求并生成相应的代码。

### 方法3：迭代式开发

1. **初始生成**：
   ```
   基于用户管理PIM模型生成基础的CRUD API
   ```

2. **增量需求**：
   ```
   添加邮箱验证功能，发送验证邮件
   ```

3. **优化调整**：
   ```
   为用户查询API添加Redis缓存
   ```

## 实际示例

### 输入：PIM模型描述
```markdown
## 业务规则
- 用户注册需要邮箱验证
- 密码必须包含大小写字母和数字，最少8位
- 登录失败5次锁定账户30分钟
- 支持OAuth2.0第三方登录
```

### Claude的理解和生成

Claude不会简单地将规则转换为if-else语句，而是会：

1. **理解意图**：
   - "需要邮箱验证" → 实现完整的邮件发送流程
   - "登录失败锁定" → 使用Redis实现分布式锁
   - "OAuth2.0" → 集成标准OAuth流程

2. **生成智能代码**：
   ```python
   # 不是模板，而是基于理解生成的代码
   
   class EmailVerificationService:
       """邮箱验证服务 - Claude理解需要验证流程"""
       
       async def send_verification_email(self, user: User):
           token = self.generate_secure_token(user.id)
           await self.cache.set(f"verify:{token}", user.id, expire=3600)
           
           # Claude知道需要异步发送邮件
           await self.email_queue.send({
               "to": user.email,
               "subject": "请验证您的邮箱",
               "template": "verification",
               "context": {"token": token}
           })
   
   class LoginService:
       """登录服务 - Claude理解需要防暴力破解"""
       
       async def login(self, credentials: LoginCredentials):
           # Claude理解需要限流
           attempts = await self.cache.incr(
               f"login_attempts:{credentials.email}"
           )
           
           if attempts > 5:
               raise HTTPException(
                   status_code=429,
                   detail="登录失败次数过多，请30分钟后重试"
               )
   ```

## 生成代码的特点

### 1. 上下文感知
- 理解"用户管理"意味着需要认证系统
- 知道"高并发"需要缓存和优化
- 明白"金融系统"需要审计日志

### 2. 最佳实践
- 自动使用依赖注入
- 实现适当的错误处理
- 添加必要的日志记录
- 考虑安全性

### 3. 可扩展设计
- 分层架构
- 接口抽象
- 易于测试
- 支持插件

## 验证生成的代码

### 运行生成的服务
```bash
cd services/user-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 查看API文档
访问 http://localhost:8000/docs

### 运行测试
```bash
pytest
```

## 常见问题

### Q: 如何让Claude理解特定的业务需求？
A: 在PIM模型中使用清晰的业务描述，Claude会理解上下文并生成合适的实现。

### Q: 生成的代码质量如何保证？
A: Claude基于大量的最佳实践训练，会生成遵循标准的高质量代码。

### Q: 可以生成其他语言的代码吗？
A: 可以，只需在命令中指定目标语言和框架。

### Q: 如何处理复杂的业务逻辑？
A: 通过详细的PIM描述和迭代对话，Claude可以理解并实现复杂逻辑。

## 下一步

1. **尝试生成**：使用 `/mda-generate` 生成您的第一个服务
2. **迭代改进**：通过对话优化生成的代码
3. **集成测试**：将生成的服务集成到您的系统中
4. **反馈优化**：使用 `/mda-update` 持续改进

记住：这不是模板化的代码生成，而是基于AI理解的智能生成！