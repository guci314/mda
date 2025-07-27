# PSM 文档章节结构设计

## 建议的章节划分

### 1. Domain（领域模型）
- **内容**：
  - 实体定义（Entity）
  - 数据模型（ORM Models）
  - 数据传输对象（DTOs/Schemas）
  - 枚举和常量
  - 领域规则和约束

- **示例结构**：
```markdown
## Domain Models

### Entities
- User Entity (SQLAlchemy)
- Post Entity (SQLAlchemy)
- Comment Entity (SQLAlchemy)

### Schemas (Pydantic)
- UserCreate, UserUpdate, UserResponse
- PostCreate, PostUpdate, PostResponse

### Enums and Constants
- UserRole, PostStatus
- Business Constants

### Constraints and Rules
- Unique constraints
- Foreign key relationships
- Business rule validations
```

### 2. Service（服务层）
- **内容**：
  - 业务逻辑服务
  - 仓储接口（Repository）
  - 事务管理
  - 业务规则实现
  - 服务间依赖

- **示例结构**：
```markdown
## Service Layer

### Business Services
- UserService (用户管理业务逻辑)
- PostService (文章管理业务逻辑)
- AuthService (认证授权逻辑)

### Repository Layer
- UserRepository (数据访问)
- PostRepository (数据访问)

### Transaction Management
- 事务边界定义
- 事务回滚策略

### Business Rules Implementation
- 具体业务规则代码
```

### 3. REST API（接口层）
- **内容**：
  - RESTful 端点定义
  - 请求/响应格式
  - 路由配置
  - 中间件和过滤器
  - API 文档说明

- **示例结构**：
```markdown
## REST API Design

### Endpoints
- User endpoints (/api/users)
  - GET /api/users (list users)
  - POST /api/users (create user)
  - GET /api/users/{id} (get user)
  - PUT /api/users/{id} (update user)
  - DELETE /api/users/{id} (delete user)

### Request/Response Formats
- Request DTOs
- Response DTOs
- Error responses

### Middleware
- Authentication
- Rate limiting
- CORS configuration
```

### 4. Application（应用配置）
- **内容**：
  - 应用启动配置
  - 依赖注入设置
  - 数据库连接配置
  - 环境变量
  - 日志配置
  - 部署说明

- **示例结构**：
```markdown
## Application Configuration

### Main Application
- FastAPI app initialization
- Dependency injection setup
- Global exception handlers

### Database Configuration
- Connection settings
- Migration setup
- Connection pooling

### Environment Configuration
- Environment variables
- Configuration classes
- Settings management

### Deployment
- Docker configuration
- Requirements
- Startup scripts
```

### 5. Test（测试规范）
- **内容**：
  - 单元测试规范
  - 集成测试设计
  - 测试数据准备
  - Mock 对象设计
  - 测试覆盖要求

- **示例结构**：
```markdown
## Testing Specifications

### Unit Tests
- Service layer tests
- Repository tests
- Utility function tests

### Integration Tests
- API endpoint tests
- Database integration tests
- Full workflow tests

### Test Data
- Fixtures
- Test database setup
- Mock data generation

### Testing Strategy
- Coverage requirements
- CI/CD integration
```

## 优化后的章节顺序

考虑到依赖关系和阅读逻辑，建议按以下顺序生成：

1. **Domain** - 基础数据模型，其他章节都依赖它
2. **Service** - 业务逻辑，依赖 Domain
3. **REST API** - 接口层，依赖 Service 和 Domain
4. **Application** - 整体配置，整合所有组件
5. **Test** - 测试规范，覆盖所有层

## 实现示例

```python
class PSMChapterGenerator:
    
    CHAPTERS = [
        {
            "name": "Domain Models",
            "key": "domain",
            "sections": ["Entities", "Schemas", "Enums", "Constraints"],
            "focus": "数据模型和领域对象定义"
        },
        {
            "name": "Service Layer", 
            "key": "service",
            "sections": ["Business Services", "Repository", "Transactions", "Rules"],
            "focus": "业务逻辑和数据访问"
        },
        {
            "name": "REST API",
            "key": "api",
            "sections": ["Endpoints", "Request/Response", "Middleware", "Documentation"],
            "focus": "RESTful 接口设计"
        },
        {
            "name": "Application Configuration",
            "key": "app",
            "sections": ["Main App", "Database", "Environment", "Deployment"],
            "focus": "应用配置和部署"
        },
        {
            "name": "Testing Specifications",
            "key": "test",
            "sections": ["Unit Tests", "Integration Tests", "Test Data", "Strategy"],
            "focus": "测试设计和规范"
        }
    ]
    
    def generate_psm_by_chapters(self, pim_content, platform="fastapi"):
        psm_document = f"# Platform Specific Model - {platform.upper()}\n\n"
        
        for i, chapter in enumerate(self.CHAPTERS):
            print(f"Generating chapter {i+1}/{len(self.CHAPTERS)}: {chapter['name']}")
            
            # 构建章节提示
            prompt = self._build_chapter_prompt(
                chapter=chapter,
                pim_content=pim_content,
                platform=platform,
                previous_chapters=self.CHAPTERS[:i]
            )
            
            # 生成章节内容
            chapter_content = self._generate_chapter(prompt)
            
            # 添加到文档
            psm_document += f"\n# {chapter['name']}\n\n"
            psm_document += chapter_content
            psm_document += "\n\n" + "-" * 80 + "\n"
        
        return psm_document
    
    def _build_chapter_prompt(self, chapter, pim_content, platform, previous_chapters):
        context = ""
        if previous_chapters:
            context = "已生成的章节：" + ", ".join([ch['name'] for ch in previous_chapters])
        
        return f"""
基于以下 PIM 生成 PSM 的 {chapter['name']} 章节。

目标平台：{platform}
章节重点：{chapter['focus']}
包含部分：{', '.join(chapter['sections'])}

{context}

PIM 内容：
{pim_content}

要求：
1. 生成完整的 {chapter['name']} 章节内容
2. 包含所有必要的技术细节和代码示例
3. 确保与已生成章节的一致性
4. 使用 {platform} 的最佳实践

请直接生成章节内容。
"""
```

## 使用建议

1. **保持章节独立性**：每个章节应该相对独立，减少相互依赖
2. **提供上下文摘要**：生成新章节时，提供已生成章节的摘要
3. **控制章节大小**：每个章节控制在 3000-4000 tokens
4. **支持增量生成**：允许单独重新生成某个章节
5. **版本控制友好**：章节划分清晰，便于版本对比

这种结构既符合软件架构的分层原则，又适合分块生成策略！