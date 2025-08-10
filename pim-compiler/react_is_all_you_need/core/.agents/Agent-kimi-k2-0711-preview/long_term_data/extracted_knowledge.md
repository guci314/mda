# 知识库

## 元知识
- **搜索策略**：先用中文关键词（如"LangChain memory 类型 特点 总结"）获取中文技术博客，再用英文关键词（如"ConversationBufferMemory features"）获取官方/权威文档
- **信息验证**：优先使用官方文档（langchain.com）、知名技术博客（Pinecone、Comet）、GitHub仓库
- **深度阅读**：对于技术概念，先读中文博客获取概览，再读英文原文获取准确细节
- **工具组合**：google_search + read_web_page 组合使用，先用搜索定位关键页面，再用页面阅读获取详细内容

## 原理与设计
- **LangChain Memory 核心设计**：为LLM对话提供上下文记忆能力，通过不同策略管理历史对话信息
- **四种主要记忆类型**：
  - **ConversationBufferMemory**：简单缓存，保留完整对话历史
  - **ConversationSummaryMemory**：生成对话摘要，减少token使用
  - **ConversationKGMemory**：构建知识图谱，存储实体关系
  - **ConversationEntityMemory**：跟踪特定实体信息
- **架构演进**：LangChain 0.0.x的记忆抽象已废弃，迁移到LangGraph的持久化特性

## 接口与API
- **主要Memory类**：
  - `ConversationBufferMemory`：基础对话缓存
  - `ConversationSummaryMemory`：对话摘要记忆
  - `ConversationKGMemory`：知识图谱记忆
  - `ConversationEntityMemory`：实体记忆
- **迁移路径**：从LangChain 0.0.x迁移到LangGraph persistence
- **相关模块**：
  - `langchain.memory`：记忆模块
  - `langchain.chains`：链式调用
  - `langchain.llms`：LLM接口

## 实现细节（需验证）
- **官方文档位置**：https://python.langchain.com/docs/versions/migrating_memory/
- **技术博客参考**：
  - Pinecone教程：https://www.pinecone.io/learn/series/langchain/langchain-conversational-memory/
  - Comet博客：https://www.comet.com/site/blog/advanced-memory-in-langchain/
  - CSDN博客：https://blog.csdn.net/Kiradzy/article/details/145063066
- **代码导入路径**（可能已变化）：
  - `from langchain.memory import ConversationKGMemory`
  - `from langchain.chains import ConversationEntityMemory`

## 用户偏好与项目特点
- 用户需要中文技术博客和英文官方文档的双重验证
- 关注记忆类型的"特点"和"应用场景"而不仅仅是技术定义
- 需要了解从旧版本到新版本的迁移信息