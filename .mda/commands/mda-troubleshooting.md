# /mda-troubleshooting

## 描述
MDA项目故障排查指南和解决方案，帮助快速定位和解决开发中的常见问题。

## 语法
```
/mda-troubleshooting [topic=<主题>]
```

## 参数
- `topic` (可选): 查看特定主题的经验教训（如：debug, json, docker, mermaid等）

## 经验教训总结

### 1. 模型层次设计

#### 教训
- **明确区分PIM和PSM**：最初将PSM误标为PIM，导致概念混淆
- **PIM应保持平台无关**：PIM不应包含技术细节（如JWT、bcrypt等）

#### 最佳实践
```
PIM (Platform Independent Model)
├── 业务概念和规则
├── 领域对象定义
├── 业务流程（可调试的标记）
└── 不含技术实现细节

PSM (Platform Specific Model)  
├── 技术架构决策
├── 具体技术栈（FastAPI、PostgreSQL等）
├── 实现细节（认证、加密等）
└── 部署配置
```

### 2. 流程调试器设计

#### 教训
- **Mermaid图表渲染**：初始包含markdown包装导致渲染失败
- **WebSocket通信**：需要双向状态同步机制
- **异步执行追踪**：必须有回调机制通知状态变化

#### 解决方案
```python
# 1. Mermaid图表直接生成，不包含```mermaid包装
def generate_mermaid_diagram(flow):
    lines = ["flowchart TD"]  # 直接开始，不要markdown包装
    
# 2. WebSocket状态同步
async def on_state_change(event_type, data):
    await websocket.send_json({
        "type": event_type,
        "data": data,
        "session": session.model_dump(mode='json')
    })

# 3. 执行器回调机制
executor = FlowExecutor(session, flow, on_state_change)
```

### 3. JSON序列化问题

#### 教训
- **datetime对象**：FastAPI WebSocket的send_json不支持datetime
- **Pydantic模型**：需要正确配置JSON编码器

#### 解决方案
```python
# 1. 自定义JSON编码器
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# 2. Pydantic模型配置
class Config:
    json_encoders = {
        datetime: lambda v: v.isoformat()
    }

# 3. 使用model_dump(mode='json')
session.model_dump(mode='json')  # 自动处理datetime
```

### 4. Docker环境问题

#### 教训
- **数据库连接**：容器名解析和认证问题
- **文件挂载**：开发时的热重载配置
- **环境变量**：.env文件的正确加载

#### 解决方案
```yaml
# docker-compose.yml
services:
  postgres:
    container_name: user-postgres  # 固定容器名
    
  user-service:
    volumes:
      - ./app:/app/app  # 代码热重载
      - ./.env:/app/.env  # 环境变量
    depends_on:
      postgres:
        condition: service_healthy  # 等待数据库就绪
```

### 5. MDA代码生成策略

#### 教训
- **标记系统**：需要区分生成代码和自定义代码
- **增量更新**：必须保护用户自定义代码

#### 最佳实践
```python
# MDA-GENERATED-START: section-name
# 生成的代码
# MDA-GENERATED-END: section-name

# MDA-CUSTOM-START: section-name
# 用户自定义代码（更新时保留）
# MDA-CUSTOM-END: section-name
```

### 6. 调试界面集成

#### 教训
- **路由设计**：调试界面应该像/docs一样易于访问
- **静态资源**：正确处理JavaScript和CSS文件路径

#### 解决方案
```python
# 统一的服务端点设计
/docs       # OpenAPI文档
/redoc      # ReDoc文档  
/debug      # 调试器API
/debug/ui   # 调试器界面
```

### 7. 实时通信设计

#### 教训
- **状态管理**：前后端状态需要精确同步
- **事件类型**：需要细粒度的事件分类

#### 事件设计
```javascript
// 细粒度事件类型
- execution_started    // 执行开始
- step_started        // 步骤开始
- step_completed      // 步骤完成  
- execution_completed // 执行完成
- execution_error     // 执行错误
- state_update       // 状态更新
```

### 8. LLM驱动的优势

#### 对比传统模板方式
- **上下文理解**：LLM能理解业务意图，生成更合适的代码
- **灵活性**：可以根据不同场景生成不同风格的代码
- **智能集成**：自动集成调试器等高级功能

#### 示例
```markdown
# PIM中的描述
"用户注册需要验证邮箱唯一性"

# LLM理解后生成
- 异步邮箱检查
- 友好的错误提示
- 事务处理
- 日志记录
```

## 使用建议

### 开发流程
1. **先设计PIM**：专注业务逻辑，不考虑技术
2. **转换PSM**：选择合适的技术栈
3. **生成代码**：利用LLM理解力生成高质量代码
4. **增量开发**：在生成的基础上添加业务逻辑

### 调试策略
1. **使用浏览器控制台**：查看WebSocket消息和执行日志
2. **检查Docker日志**：`docker logs <container>` 查看服务端错误
3. **验证数据流**：在调试界面查看context变化

### 常见问题排查

#### 调试界面无响应
1. 检查是否选择了流程
2. 查看浏览器控制台错误
3. 验证WebSocket连接状态

#### JSON序列化错误
1. 检查是否有datetime对象
2. 使用model_dump(mode='json')
3. 实现自定义JSON编码器

#### Docker连接问题
1. 使用docker compose logs查看日志
2. 检查容器间网络连通性
3. 验证环境变量配置

#### CDN资源加载失败（中国地区）
1. 替换 cdn.jsdelivr.net 为 unpkg.com
2. 或使用国内CDN：
   - bootcdn.net
   - staticfile.org
   - cdnjs.cloudflare.com
3. 下载资源到本地作为静态文件

## 未来改进方向

1. **智能断点**：基于条件自动设置断点
2. **时间旅行调试**：回放执行历史
3. **分布式调试**：跨服务的流程调试
4. **AI辅助调试**：自动发现和修复问题

## 总结

基于LLM的MDA实现展示了AI驱动开发的潜力：
- 从理解到生成的智能化流程
- 自动集成高级功能（如调试器）
- 保持代码的可维护性和可扩展性

关键成功因素：
1. 清晰的模型分层（PIM/PSM）
2. 完善的调试支持
3. 良好的错误处理
4. 实时的状态同步