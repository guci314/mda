# /pim2FastapiPsm Slash Command for Claude Code

## 命令定义
```
/pim2FastapiPsm pim=<PIM文件名> psm=<PSM文件名> [features=<特性列表>]
```

## 执行指令

当用户执行此命令时，请按以下步骤操作：

### 1. 读取和分析PIM模型

```
1. 读取 models/domain/{pim}.md 文件
2. 深入理解：
   - 业务概念的本质含义
   - 实体之间的关系语义
   - 业务规则的真实意图
   - 业务流程的关键环节
   - 非功能需求的优先级
3. 自动检测可调试方法：
   - 扫描所有的mermaid flowchart块
   - 提取ServiceName.methodName模式
   - 记录流程图内容和描述
```

### 2. 可调试性分析

自动执行以下检测逻辑：

```python
# 伪代码示例
def analyze_debuggability(pim_content):
    debuggable_methods = {}
    
    # 查找所有流程图部分
    # 例如："### UserService.注册用户 流程"
    flow_sections = find_sections_with_pattern(
        pim_content, 
        r'### (\w+Service)\.(\w+) 流程'
    )
    
    for section in flow_sections:
        service_name = section.service_name
        method_name = section.method_name
        
        # 查找flowchart
        flowchart = extract_mermaid_block(
            section.content, 
            type='flowchart'
        )
        
        if flowchart:
            debuggable_methods[f"{service_name}.{method_name}"] = {
                "has_flowchart": True,
                "flowchart_content": flowchart,
                "description": section.description,
                "steps_count": count_flow_steps(flowchart),
                "decision_points": count_decision_nodes(flowchart)
            }
    
    return debuggable_methods
```

### 3. 技术决策推理

基于PIM分析和可调试性检测，进行智能技术选型：

#### 3.1 认证机制选择
```
分析因素：
- 用户规模和并发量
- 安全级别要求
- 是否需要第三方集成
- 会话管理复杂度

决策逻辑：
- 简单内部系统 → API Key
- 标准Web应用 → JWT
- 需要SSO → OAuth2
- 需要实时会话控制 → Redis Session
```

#### 2.2 数据存储优化
```
分析因素：
- 数据关系复杂度
- 查询模式
- 性能要求
- 扩展性需求

决策逻辑：
- 强关系型 → PostgreSQL + 优化索引
- 需要缓存 → Redis
- 全文搜索 → ElasticSearch
- 时序数据 → TimescaleDB
```

#### 2.3 性能架构设计
```
分析因素：
- 并发用户数
- 响应时间要求
- 数据量级
- 实时性需求

决策逻辑：
- 高并发 → 连接池 + 缓存层
- 实时推送 → WebSocket
- 大数据量 → 分页 + 流式处理
- 异步任务 → Celery/RabbitMQ
```

### 4. PSM模型生成

#### 4.1 自动添加可调试标记

基于可调试性分析结果，在PSM中标记方法：

```markdown
### UserService 服务

**方法**：
- `注册用户(用户信息)` ⚡ 可调试 - 处理新用户注册的完整流程，包含数据验证、唯一性检查、状态初始化
- `创建用户(用户信息)` - 创建新用户记录
- `查询用户(查询条件)` - 根据条件查找用户
- `更新用户(标识符, 用户信息)` - 修改用户信息
- `删除用户(标识符)` - 从系统中移除用户

**调试器配置**：
- 可调试方法：1个
- 调试入口：`/debug/flows/user-service/register-user`
- 流程步骤：12个
- 决策点：5个
```

#### 4.2 实体转换示例

**PIM实体**：
```markdown
### 用户 (User)
**属性**：
- 标识符：唯一识别用户
- 登录名：用户登录时使用的名称
```

**转换为PSM**：
```markdown
### User实体

\```mermaid
classDiagram
    class User {
        +UUID id
        +String username
        +String email
        +String password_hash
        +UserStatus status
        +DateTime created_at
        +DateTime updated_at
        +DateTime last_login_at
        +login()
        +logout()
        +updateProfile()
        +changePassword()
        +resetPassword()
        +deactivate()
    }
\```

**技术实现细节**：
- **主键**: UUID (增强安全性，避免ID枚举攻击)
- **索引**: username (UNIQUE), email (UNIQUE), created_at (BTREE)
- **密码存储**: bcrypt with cost factor 12
- **状态管理**: PostgreSQL ENUM type
- **时间戳**: 自动管理 (created_at, updated_at)
```

#### 4.3 业务规则转换

**PIM规则**：
```
用户注册规则：
1. 登录名必须唯一
2. 新注册用户需要验证邮箱
```

**转换为PSM**：
```markdown
### 用户注册规则

**技术实现**：
1. **登录名唯一性**：
   - 数据库唯一约束：`UNIQUE INDEX idx_username ON users(username)`
   - API层预检查：防止数据库异常泄露信息
   - 错误处理：返回友好的"用户名已存在"消息

2. **邮箱验证流程**：
   - 生成验证令牌：`secrets.token_urlsafe(32)`
   - Redis存储：`email_verify:{token}` → user_id (TTL: 24h)
   - 发送邮件：使用异步任务队列
   - 验证端点：`POST /auth/verify-email`
   - 状态转换：PENDING → ACTIVE
```

#### 4.4 性能优化方案

基于PIM中的性能要求，生成具体技术方案：

```markdown
### 性能优化策略

**基于需求**："系统应支持大量并发用户"

**技术方案**：
1. **数据库优化**：
   \```sql
   -- 为高频查询添加索引
   CREATE INDEX idx_user_status ON users(status) WHERE status = 'ACTIVE';
   CREATE INDEX idx_user_last_login ON users(last_login_at DESC);
   
   -- 分区表（如果用户量超过100万）
   CREATE TABLE users_2024 PARTITION OF users
   FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
   \```

2. **缓存策略**：
   \```python
   # Redis缓存用户信息
   CACHE_USER_KEY = "user:{user_id}"
   CACHE_USER_TTL = 300  # 5分钟
   
   # 缓存用户权限
   CACHE_PERMISSION_KEY = "user:{user_id}:permissions"
   CACHE_PERMISSION_TTL = 600  # 10分钟
   \```

3. **API限流**：
   \```python
   # 基于Redis的滑动窗口限流
   RATE_LIMIT_WINDOW = 60  # 1分钟
   RATE_LIMIT_MAX_REQUESTS = 100  # 每分钟100次
   \```
```

### 5. 安全增强

自动为PSM添加安全特性：

```markdown
### 安全规格

**认证机制**：
- **算法**：JWT RS256 (非对称加密)
- **Token结构**：
  \```json
  {
    "sub": "user_id",
    "username": "john_doe",
    "role": "user",
    "permissions": ["read:profile", "write:profile"],
    "exp": 1234567890,
    "iat": 1234567890,
    "jti": "unique_token_id"
  }
  \```
- **Refresh Token**：存储在Redis，支持撤销

**防护措施**：
1. **暴力破解防护**：
   - 5次失败后锁定30分钟
   - 使用Redis记录失败次数
   - IP级别的限制

2. **SQL注入防护**：
   - 使用SQLAlchemy ORM
   - 参数化查询
   - 输入验证

3. **XSS防护**：
   - 自动HTML转义
   - Content-Type验证
   - CSP头部设置
```

### 6. 生成完整PSM文档

将所有转换结果组织成完整的PSM文档，包括：

1. **文档头部**：说明这是从PIM生成的PSM
2. **业务描述**：保留PIM的业务描述，添加技术视角
3. **技术架构**：具体的技术选型和理由
4. **实体模型**：包含所有技术细节的Mermaid图
5. **API设计**：RESTful端点规划
6. **数据库设计**：表结构、索引、约束
7. **安全设计**：认证、授权、防护措施
8. **性能设计**：缓存、优化、扩展方案
9. **部署架构**：容器化、监控、日志

### 7. 特性处理

如果用户指定了features参数，相应调整技术方案：

```python
features = features.split(',') if features else []

if 'websocket' in features:
    # 添加WebSocket支持
    # 实时通知、在线状态等
    
if 'oauth2' in features:
    # 使用OAuth2替代JWT
    # 支持第三方登录
    
if 'graphql' in features:
    # 添加GraphQL端点
    # 灵活的数据查询
```

### 8. 输出和保存

1. 将生成的PSM保存到 `models/domain/{psm}.md`
2. 显示转换摘要：
   - 识别的业务概念数量
   - 选择的技术栈
   - 添加的安全特性
   - 性能优化点
   - **可调试方法数量**（自动检测）
   - **调试器配置信息**
3. 提供下一步建议：
   - 使用 `/mda-generate-fastapi` 生成代码
   - 检查技术选型是否符合需求
   - 可能需要调整的配置

## 注意事项

1. **保持业务语义**：技术细节不应掩盖业务本质
2. **合理选型**：不过度设计，根据实际需求选择技术
3. **安全优先**：默认启用所有安全特性
4. **文档完整**：生成的PSM应该是自解释的

## 错误处理

- 如果PIM文件不存在，提示用户检查文件名
- 如果PIM模型不完整，列出缺失的关键信息
- 如果特性冲突（如jwt和oauth2同时指定），询问用户选择

## 自动检测示例

用户输入：
```
/pim2FastapiPsm pim=用户管理_pim psm=用户管理_psm
```

Claude执行流程：
1. 读取 `models/domain/用户管理_pim.md`
2. 发现 `### UserService.注册用户 流程` 部分
3. 检测到该部分包含 `flowchart TD` 图表
4. 自动将 `注册用户` 方法标记为可调试
5. 在PSM中添加 `⚡ 可调试` 标记和调试器配置
6. 生成包含调试器支持的完整PSM

输出摘要：
```
✅ PSM生成成功
- 实体数量：1个（User）
- 服务方法：5个
- 可调试方法：1个（UserService.注册用户 - 自动检测）
- 技术特性：JWT认证, Redis缓存, 审计日志
- 调试器入口：/debug/flows/user-service/register-user
```

## 与其他命令的协作

- 生成PSM后，提示用户使用 `/mda-generate-fastapi` 生成代码
- 支持 `/psm-validate` 验证生成的PSM
- 支持 `/psm-optimize` 进一步优化PSM
- 生成的PSM会被 `/mda-generate-fastapi` 识别并生成相应的调试器代码