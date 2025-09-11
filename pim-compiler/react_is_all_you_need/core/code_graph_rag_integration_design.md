# Code-Graph-RAG 集成设计文档

## 项目概述

本设计文档描述如何将 **Code-Graph-RAG** 系统集成到 **React Agent** 软件中，为Agent提供强大的代码分析和图谱查询能力。

### 设计目标
- ✅ **极简集成**: 保持React Agent的极简哲学
- ✅ **功能完整**: 支持代码分析、查询、编辑、优化全功能
- ✅ **接口统一**: 遵循Function基类规范
- ✅ **易使用**: 自然语言接口，开箱即用

## 架构设计

### 整体架构
```
┌─────────────────────────────────────────────────┐
│                React Agent Minimal              │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  │
│  │ SearchTool  │  │ CreateAgent │  │ 其他工具 │  │
│  └─────────────┘  └─────────────┘  └─────────┘  │
│          │             │              │         │
└──────────┼─────────────┼──────────────┼─────────┘
           │             │              │
           ▼             ▼              ▼
┌─────────────────────────────────────────────────┐
│              CodeAnalysisTool                   │
│  (继承Function基类，统一接口规范)                │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│               适配层 (Adapter)                   │
│  • 参数转换和验证                               │
│  • 错误处理和降级                               │
│  • 结果格式化和缓存                             │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│              Code-Graph-RAG 系统                │
│  • graph_loader.py - 代码分析                   │
│  • main.py - 自然语言查询                       │
│  • graph_updater.py - 代码编辑                  │
│  • parser_loader.py - 多语言解析                │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│                Memgraph 数据库                  │
│  • Docker容器运行                              │
│  • 代码知识图谱存储                             │
│  • Cypher查询引擎                              │
└─────────────────────────────────────────────────┘
```

### 技术栈
- **React Agent**: ReactAgentMinimal + Function基类
- **Code-Graph-RAG**: Tree-sitter + Memgraph + AI模型
- **通信方式**: 函数调用 + 进程间通信
- **数据格式**: JSON + Pydantic模型

## 接口规范

### 核心工具类: CodeAnalysisTool

```python
class CodeAnalysisTool(Function):
    """代码分析和图谱查询工具"""
    
    def __init__(self):
        super().__init__(
            name="code_analysis",
            description="多语言代码分析、图谱查询和编辑工具",
            parameters={
                "action": {
                    "type": "string", 
                    "description": "操作类型: analyze(分析)|query(查询)|edit(编辑)|optimize(优化)"
                },
                "target": {
                    "type": "string", 
                    "description": "目标文件或目录路径"
                },
                "query": {
                    "type": "string", 
                    "description": "自然语言查询或指令"
                },
                "language": {
                    "type": "string", 
                    "description": "编程语言(可选): python, javascript, typescript, cpp, lua, rust, java"
                }
            }
        )
```

### 功能接口

#### 1. 代码结构分析 (analyze)
```python
# 分析Python项目的结构
result = agent.run("""
使用code_analysis工具分析src目录的代码结构
""")

# 等效调用
code_tool.execute(
    action="analyze",
    target="src",
    language="python"
)
```

#### 2. 关系查询 (query)
```python
# 查询类之间的关系
result = agent.run("""
查询User类和Order类之间的关系
""")

# 等效调用  
code_tool.execute(
    action="query",
    target="src/models",
    query="User类和Order类之间的关系"
)
```

#### 3. 代码编辑 (edit)
```python
# 重构代码
result = agent.run("""
将所有的print语句改为logging
""")

# 等效调用
code_tool.execute(
    action="edit", 
    target="src/utils.py",
    query="将所有的print语句改为logging"
)
```

#### 4. 优化建议 (optimize)
```python
# 获取优化建议
result = agent.run("""
分析main.py的性能瓶颈并提供优化建议
""")

# 等效调用
code_tool.execute(
    action="optimize",
    target="main.py", 
    query="性能瓶颈和优化建议"
)
```

## 实施路线图

### 阶段1: 基础集成 (1-2天)
- [ ] 环境准备: Python 3.12+, Docker, cmake, uv
- [ ] 依赖安装: `uv sync --extra treesitter-full`
- [ ] Memgraph启动: Docker Compose配置
- [ ] CodeAnalysisTool骨架实现

### 阶段2: 功能封装 (2-3天)  
- [ ] 封装graph_loader.py分析功能
- [ ] 封装main.py自然语言查询
- [ ] 封装graph_updater.py代码编辑
- [ ] 错误处理和日志系统

### 阶段3: 测试验证 (1-2天)
- [ ] 单元测试: 覆盖所有功能接口
- [ ] 集成测试: React Agent集成测试
- [ ] 性能测试: 响应时间和内存使用
- [ ] 文档: 使用示例和API文档

### 阶段4: 优化部署 (1天)
- [ ] 性能优化: 缓存和异步处理
- [ ] 错误恢复: 自动重连和降级
- [ ] 监控: 健康检查和指标收集
- [ ] 生产部署: 容器化配置

**总计: 5-8个开发日**

## 依赖管理

### 系统依赖
```yaml
# 必需依赖
python: ">=3.12"
docker: "最新版本"
cmake: "构建Tree-sitter"
uv: "Python包管理器"

# 语言支持
完全支持: python, javascript, typescript, cpp, lua, rust, java
开发中: go, scala, csharp
```

### Docker配置
```yaml
# docker-compose.yaml (Code-Graph-RAG)
version: '3.8'
services:
  memgraph:
    image: memgraph/memgraph:latest
    ports:
      - "7687:7687"
    volumes:
      - mg_data:/var/lib/memgraph

volumes:
  mg_data:
```

## 错误处理

### 错误类型
1. **连接错误**: Memgraph数据库连接失败
2. **解析错误**: 代码语法解析失败
3. **查询错误**: Cypher查询执行错误
4. **权限错误**: 文件访问权限不足

### 处理策略
- ✅ 重试机制: 数据库连接自动重试
- ✅ 降级处理: 查询失败时返回简化结果
- ✅ 详细日志: 记录完整的错误上下文
- ✅ 用户提示: 友好的错误消息和建议

## 性能考虑

### 内存管理
- **AST解析**: 分段解析大文件，避免内存溢出
- **图谱查询**: 分页查询大型结果集
- **缓存策略**: 高频查询结果缓存

### 响应时间
- **实时操作**: < 2秒 (分析、简单查询)
- **复杂查询**: < 10秒 (多关系深度查询)
- **批量处理**: 异步后台任务

## 使用示例

### 基础使用
```python
from core import ReactAgentMinimal
from core.tools import CodeAnalysisTool

# 创建Agent并集成代码分析工具
agent = ReactAgentMinimal(
    work_dir="my_project",
    tools=[CodeAnalysisTool()]  # 自动注册工具
)

# 分析代码结构
result = agent.run("""
分析src目录的Python代码，找出所有的类定义和它们之间的关系
""")
```

### 高级查询
```python
# 复杂关系查询
result = agent.run("""
查询UserService类调用了哪些外部API，
并分析这些调用的性能和错误处理
""")

# 代码优化建议
result = agent.run("""
分析data_processor.py的性能瓶颈，
并提供具体的优化建议和重构方案
""")
```

## 扩展性考虑

### 插件架构
1. **解析器插件**: 支持新的编程语言
2. **存储插件**:  alternative图数据库支持
3. **AI模型插件**: 集成不同的AI服务

### 配置化
- 语言支持配置
- AI模型选择配置
- 缓存策略配置
- 性能阈值配置

## 风险评估

### 技术风险
1. **依赖复杂性**: Tree-sitter和Memgraph的依赖较多
   - 缓解: 容器化部署，提供详细安装文档

2. **性能问题**: 大代码库分析可能较慢
   - 缓解: 增量分析，缓存优化，异步处理

3. **兼容性**: 不同Python版本和系统环境
   - 缓解: 严格的版本要求，测试矩阵

### 维护风险
1. **代码更新**: Code-Graph-RAG项目活跃更新
   - 缓解: 接口抽象，版本pin

2. **文档同步**: 多个系统的文档维护
   - 缓解: 自动化文档生成

## 版本历史

- **v1.0** (2024-09-12): 初始设计文档

---

*本文档采用极简设计哲学，专注于核心功能和实际可行性。*