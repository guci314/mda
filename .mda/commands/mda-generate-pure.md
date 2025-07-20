# /mda-generate-pure

基于业务纯洁性原则的模型代码生成命令。

## 命令格式

```bash
/mda-generate-pure domain=<领域名> purpose=<业务目的> [sla=<服务等级>] [profile=<技术配置>]
```

## 参数说明

### 必需参数
- `domain`: 业务领域名称（如：用户管理、订单处理、库存管理）
- `purpose`: 业务目的描述（如：用户注册与认证、订单全流程管理）

### 可选参数
- `sla`: 服务等级要求（如：高可用、快速响应、强一致性）
- `profile`: 技术配置文件（默认：default）

## 业务纯洁性原则

### ❌ 错误示例（包含技术细节）
```bash
/mda-generate-pure domain=用户管理 db=postgresql cache=redis auth=jwt
```

### ✅ 正确示例（纯业务描述）
```bash
/mda-generate-pure domain=用户管理 purpose=用户注册与认证 sla=高可用
```

## 技术配置分离

技术细节通过配置文件管理，不出现在命令中：

### 配置文件位置
```
.mda/
├── profiles/
│   ├── default.yaml          # 默认技术栈
│   ├── high-availability.yaml # 高可用配置
│   ├── high-performance.yaml  # 高性能配置
│   └── cost-optimized.yaml    # 成本优化配置
└── aspects/
    ├── default.yaml          # 默认切面配置
    ├── financial.yaml        # 金融领域切面
    └── healthcare.yaml       # 医疗领域切面
```

### 示例配置：high-availability.yaml
```yaml
profile: high-availability
description: 高可用性技术栈配置

technology_stack:
  api:
    framework: fastapi
    features:
      - async
      - openapi
      - websocket
  
  database:
    primary: postgresql
    config:
      - replication: master-slave
      - connection_pool: 20
      - failover: automatic
  
  cache:
    provider: redis
    config:
      - mode: cluster
      - persistence: yes
  
  message_queue:
    provider: rabbitmq
    config:
      - cluster: yes
      - durable: yes

aspects:
  - logging:
      level: INFO
      format: json
      
  - monitoring:
      provider: prometheus
      metrics:
        - response_time
        - error_rate
        - throughput
        
  - security:
      authentication: jwt
      authorization: rbac
      encryption: tls
      
  - reliability:
      circuit_breaker:
        threshold: 50%
        timeout: 30s
      retry:
        max_attempts: 3
        backoff: exponential
      rate_limit:
        default: 1000/min
        
  - transaction:
      default: read_committed
      timeout: 30s
```

## 执行流程

1. **解析业务意图**
   ```python
   # Claude理解业务目的
   purpose = "用户注册与认证"
   business_features = extract_business_features(purpose)
   # 结果：["用户创建", "邮箱验证", "密码管理", "登录认证"]
   ```

2. **加载技术配置**
   ```python
   # 根据SLA选择配置
   sla = "高可用"
   profile = load_profile(sla_to_profile(sla))
   aspects = load_aspects(domain)
   ```

3. **生成纯业务代码**
   ```python
   # 生成的服务类（纯业务逻辑）
   class UserService:
       async def register_user(self, user_data: UserData) -> User:
           """注册新用户 - 纯业务逻辑"""
           # 验证用户数据完整性
           self._validate_user_data(user_data)
           
           # 检查邮箱是否已存在
           if await self._email_exists(user_data.email):
               raise BusinessError("邮箱已被注册")
           
           # 创建用户
           user = User.from_registration_data(user_data)
           
           # 发送欢迎邮件
           await self._send_welcome_email(user)
           
           return user
   ```

4. **应用技术切面**
   ```python
   # 通过装饰器添加技术关注点
   from aspects import apply_domain_aspects
   
   @apply_domain_aspects("user-management")
   class UserService:
       # 自动应用：日志、监控、安全、事务等切面
       pass
   ```

## 生成的项目结构

```
generated-service/
├── domain/                    # 纯业务逻辑
│   ├── models/               # 业务实体
│   ├── services/             # 业务服务
│   ├── rules/                # 业务规则
│   └── flows/                # 业务流程
├── aspects/                   # 技术切面（自动生成）
│   ├── logging.py
│   ├── security.py
│   ├── monitoring.py
│   └── config.yaml
├── infrastructure/            # 技术实现（自动生成）
│   ├── api/                  # API层
│   ├── persistence/          # 持久化层
│   └── messaging/            # 消息层
└── main.py                   # 启动入口
```

## 示例用法

### 1. 简单业务系统
```bash
/mda-generate-pure domain=产品目录 purpose=产品信息管理
```

### 2. 高可用系统
```bash
/mda-generate-pure domain=支付处理 purpose=在线支付与对账 sla=高可用
```

### 3. 特定行业系统
```bash
/mda-generate-pure domain=病历管理 purpose=电子病历存储与查询 profile=healthcare
```

## 生成代码示例

### 纯业务服务
```python
# domain/services/user_service.py
class UserService:
    """用户服务 - 纯业务逻辑，无技术细节"""
    
    async def register_user(self, registration_data: RegistrationData) -> User:
        """
        注册新用户
        
        业务规则：
        1. 邮箱必须唯一
        2. 密码需要符合强度要求
        3. 需要发送验证邮件
        """
        # 纯业务实现
        user = User.create_from_registration(registration_data)
        await self.notification_service.send_verification_email(user)
        return user
```

### 自动生成的切面应用
```python
# infrastructure/api/user_api.py
from aspects import auto_apply_aspects
from domain.services import UserService

# 自动应用所有配置的切面
@auto_apply_aspects
class UserAPI:
    def __init__(self):
        self.service = UserService()
    
    async def register_user(self, request: RegistrationRequest):
        # 切面自动处理：认证、授权、日志、监控、限流等
        user = await self.service.register_user(request.to_domain())
        return UserResponse.from_domain(user)
```

## 优势总结

1. **业务专家友好**：命令中只有业务概念
2. **技术灵活性**：通过配置文件随时调整技术栈
3. **关注点分离**：业务逻辑和技术实现完全解耦
4. **易于测试**：可以单独测试纯业务逻辑
5. **统一管理**：所有技术切面集中配置

这种方式真正实现了"业务驱动开发"，让业务专家能够直接参与系统设计！