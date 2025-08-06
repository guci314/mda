```markdown
# 知识库

## 元知识
- 通过`list_directory`工具探索项目目录结构
- 通过`read_file`工具读取关键文档（如README.md）获取架构信息
- 使用目录结构和关键文件作为架构分析的切入点
- 通过UML四视图分析法快速理解系统架构

## 原理与设计
- 项目采用LangGraph的React Agent架构
- 核心设计理念：模块化Agent系统+工具生态系统+知识管理
- 三级记忆系统设计：
  - NONE：无状态执行
  - SMART：智能摘要缓冲
  - PRO：SQLite持久化存储
- 多Agent协作机制：
  - Agent as Tool模式
  - 任务依赖处理系统
- 分层架构设计：
  - 核心层/Agent层/应用层/知识层分离
- 调试支持设计：
  - 可视化工具和条件断点

## 接口与API
- 核心组件接口：
  - `GenericReactAgent`：主Agent类
  - `ReactAgentConfig`：配置管理
  - `MemoryManager`：记忆系统管理
  - `KnowledgeManager`：知识动态加载
- 工具集接口：
  - 文件操作类工具
  - 代码搜索/修改工具
  - 命令执行工具
  - `GenericAgentTool`：Agent包装工具
- 知识管理接口：
  - `@include`语法引用
  - 动态加载机制

## 实现细节（需验证）
- 核心实现文件：
  - `react_agent.py`（主实现）
  - `tools.py`（工具集合）
  - `langchain_agent_tool.py`（集成工具）
- 目录结构特征：
  - `core/`目录可能包含核心实现
  - `.agents/`存放独立Agent配置
  - `examples/`包含应用示例
  - `knowledge/`存储共享知识
  - 演示文件以`demo_`或`debug_`前缀命名
  - 文档类文件集中在根目录或`docs/`

## 用户偏好与项目特点
- 偏好模块化设计：Agent/工具/知识分离
- 强调执行过程可视化（显示思考过程）
- 重视调试支持（NotebookDebugger）
- 项目约定：
  - 使用SQLite作为持久化存储
  - 通过`.env`文件管理配置
  - 维护详细的README文档
  - 记忆数据分散存储在`.agents/*/long_term_data`和`short_term_data`
```