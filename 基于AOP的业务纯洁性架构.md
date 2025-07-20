# 基于AOP的业务纯洁性架构

## 1. 核心理念

### 1.1 业务纯洁性原则
- **PIM模型**：只包含业务概念、规则和流程，零技术细节
- **斜杠命令**：只描述业务操作意图，不涉及技术实现
- **技术切面**：通过AOP方式动态织入，与业务逻辑完全解耦

### 1.2 架构愿景
```
业务专家 → 纯业务模型 → 执行引擎 → AOP织入技术切面 → 运行系统
```

## 2. 切面（Aspect）设计

### 2.1 核心技术切面
```python
# 日志切面
@log_aspect(level="INFO", format="business_operation")
def register_user(user_data):
    # 纯业务逻辑
    pass

# 安全切面
@security_aspect(
    authentication="jwt",
    authorization="role_based",
    roles=["admin", "user_manager"]
)
def delete_user(user_id):
    # 纯业务逻辑
    pass

# 限流切面
@rate_limit_aspect(
    max_requests=100,
    window="1m",
    by="ip"
)
def query_users():
    # 纯业务逻辑
    pass

# 事务切面
@transaction_aspect(
    isolation="read_committed",
    retry=3
)
def transfer_money(from_account, to_account, amount):
    # 纯业务逻辑
    pass

# 缓存切面
@cache_aspect(
    ttl=300,
    key_pattern="{method_name}:{args}"
)
def get_user_profile(user_id):
    # 纯业务逻辑
    pass

# 监控切面
@monitoring_aspect(
    metrics=["response_time", "error_rate"],
    alerts={"error_rate": ">0.05"}
)
def process_order(order_data):
    # 纯业务逻辑
    pass
```

### 2.2 切面分类

#### 2.2.1 基础设施切面
- **日志记录**：操作日志、审计日志、错误日志
- **性能监控**：响应时间、吞吐量、资源使用
- **错误处理**：异常捕获、错误恢复、降级策略

#### 2.2.2 安全切面
- **认证**：JWT、OAuth2、SSO
- **授权**：RBAC、ABAC、ACL
- **加密**：数据加密、传输加密
- **审计**：操作审计、合规审计

#### 2.2.3 可靠性切面
- **限流**：请求限流、并发控制
- **熔断**：服务熔断、自动恢复
- **重试**：失败重试、退避策略
- **超时**：请求超时、连接超时

#### 2.2.4 数据切面
- **事务**：ACID保证、分布式事务
- **缓存**：结果缓存、查询缓存
- **验证**：输入验证、业务规则验证

## 3. 纯业务PIM模型示例

### 3.1 原始模型（包含技术细节）❌
```yaml
domain: user-management
entities:
  - name: User
    attributes:
      email:
        type: string
        validation: email_format  # 技术细节
        index: true              # 技术细节
    
services:
  - name: UserService
    methods:
      - name: registerUser
        cache: 5min              # 技术细节
        rate_limit: 100/hour     # 技术细节
        transaction: required    # 技术细节
```

### 3.2 纯业务模型（业务纯洁）✅
```yaml
domain: user-management
entities:
  - name: User
    description: 系统用户
    attributes:
      email:
        description: 用户邮箱地址
        business_rules:
          - 必须唯一
          - 用于登录和通知
    
services:
  - name: UserService
    description: 用户管理服务
    methods:
      - name: registerUser
        description: 注册新用户
        business_rules:
          - 邮箱不能重复
          - 必须发送欢迎邮件
        sla:  # 业务级别的服务约定
          response_time: 快速响应
          availability: 高可用
```

## 4. 切面配置方式

### 4.1 默认切面配置
```yaml
# .mda/aspects/default.yaml
default_aspects:
  all_methods:
    - logging:
        level: INFO
    - monitoring:
        metrics: [response_time, error_rate]
    - error_handling:
        strategy: log_and_continue
  
  query_methods:  # 匹配 get*, find*, query*
    - cache:
        ttl: 300
    - rate_limit:
        max: 1000
        window: 1m
  
  mutation_methods:  # 匹配 create*, update*, delete*
    - transaction:
        isolation: read_committed
    - audit:
        level: detailed
```

### 4.2 领域特定切面
```yaml
# .mda/aspects/financial.yaml
financial_domain:
  payment_methods:
    - transaction:
        isolation: serializable
    - audit:
        level: complete
        retention: 7years
    - encryption:
        algorithm: AES256
    - compliance:
        standards: [PCI-DSS, SOX]
```

## 5. 斜杠命令的业务纯洁性

### 5.1 改进前（包含技术）❌
```markdown
/mda-generate-fastapi domain=用户管理 service=user-service db=postgresql cache=redis
```

### 5.2 改进后（纯业务）✅
```markdown
/mda-generate domain=用户管理 purpose=用户注册与认证 sla=高可用
```

技术选择由配置文件决定：
```yaml
# .mda/profiles/high-availability.yaml
profile: high-availability
technology_stack:
  api: fastapi
  database: postgresql-cluster
  cache: redis-cluster
  message_queue: rabbitmq
aspects:
  - high_availability
  - distributed_tracing
  - circuit_breaker
```

## 6. 实现示例

### 6.1 装饰器实现
```python
# aspects/logging.py
def log_aspect(level="INFO", format="json"):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 前置日志
            logger.log(level, f"Starting {func.__name__}", 
                      extra={"args": args, "kwargs": kwargs})
            
            try:
                # 执行业务逻辑
                result = await func(*args, **kwargs)
                
                # 后置日志
                logger.log(level, f"Completed {func.__name__}", 
                          extra={"result": result})
                
                return result
            except Exception as e:
                # 错误日志
                logger.error(f"Error in {func.__name__}", 
                           extra={"error": str(e)})
                raise
        
        return wrapper
    return decorator

# aspects/security.py
def security_aspect(authentication=None, authorization=None, roles=None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 认证检查
            if authentication:
                auth_result = await authenticate(authentication)
                if not auth_result.success:
                    raise AuthenticationError()
            
            # 授权检查
            if authorization and roles:
                if not await authorize(auth_result.user, roles):
                    raise AuthorizationError()
            
            # 执行业务逻辑
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
```

### 6.2 引擎集成
```python
class PIMEngine:
    def __init__(self):
        self.aspect_manager = AspectManager()
        self.aspect_manager.load_default_aspects()
    
    async def execute_method(self, service_name, method_name, args):
        # 获取纯业务方法
        method = self.get_business_method(service_name, method_name)
        
        # 动态应用切面
        wrapped_method = self.aspect_manager.apply_aspects(
            method,
            context={
                "service": service_name,
                "method": method_name,
                "domain": self.get_domain(service_name)
            }
        )
        
        # 执行包装后的方法
        return await wrapped_method(*args)
```

## 7. 优势分析

### 7.1 业务优势
- **业务专家友好**：模型中只有业务概念，无技术干扰
- **需求对齐**：模型直接反映业务需求，不含实现细节
- **易于沟通**：业务和技术团队使用同一套纯业务语言

### 7.2 技术优势
- **关注点分离**：业务逻辑和技术实现完全解耦
- **灵活配置**：技术切面可独立配置和更换
- **统一管理**：所有横切关注点集中管理
- **易于测试**：可单独测试业务逻辑，无需关心技术细节

### 7.3 维护优势
- **独立演进**：业务逻辑和技术栈可独立升级
- **复用性高**：切面可跨领域复用
- **配置化**：通过配置而非代码控制技术行为

## 8. 实施路线图

### Phase 1: 基础切面（1-2周）
- [ ] 实现日志切面
- [ ] 实现基础安全切面
- [ ] 实现错误处理切面

### Phase 2: 高级切面（2-4周）
- [ ] 实现事务切面
- [ ] 实现缓存切面
- [ ] 实现限流切面

### Phase 3: 引擎集成（1-2周）
- [ ] 切面管理器
- [ ] 动态织入机制
- [ ] 配置加载器

### Phase 4: 工具支持（2-3周）
- [ ] 切面可视化工具
- [ ] 性能分析工具
- [ ] 切面调试器

## 9. 结论

基于AOP的业务纯洁性架构完全可行，且带来显著优势：

1. **业务模型纯粹**：只包含业务逻辑，易于理解和维护
2. **技术灵活性**：通过切面配置轻松切换技术实现
3. **统一管理**：横切关注点集中处理，避免代码重复
4. **渐进式实施**：可从简单切面开始，逐步完善

这种架构让PIM真正成为"平台无关模型"，实现了业务与技术的完美分离！