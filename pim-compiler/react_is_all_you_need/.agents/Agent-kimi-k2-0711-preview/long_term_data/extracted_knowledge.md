# 知识库

## 元知识
- **搜索策略**：先用中文关键词获取中文技术博客，再用英文关键词获取官方文档，最后用具体类名精准定位
- **信息验证**：对比官方文档、技术博客、代码示例三方信息，优先使用官方文档和最新API
- **快速评估**：通过URL域名判断信息权威性（*.langchain.com > medium > csdn）
- **版本识别**：注意新旧API对比，官方文档会标注"legacy"或"deprecated"

## 原理与设计
- **记忆设计哲学**：LangChain记忆系统的核心是在token成本和记忆精度之间做权衡
- **分层记忆模型**：从完整存储→窗口截断→token限制→摘要压缩→混合策略的演进路径
- **状态管理范式**：从ConversationChain的隐式状态转向RunnableWithMessageHistory的显式状态管理
- **成本控制策略**：通过不同记忆类型实现从原型到生产的平滑过渡

## 接口与API
- **新API（推荐）**：
  ```python
  from langchain_core.runnables.history import RunnableWithMessageHistory
  from langchain_core.chat_history import InMemoryChatMessageHistory
  ```
- **旧API（legacy）**：
  ```python
  from langchain.memory import ConversationBufferMemory
  from langchain.chains import ConversationChain
  ```
- **记忆类型选择矩阵**：
  - 原型阶段：ConversationBufferMemory
  - 生产环境：ConversationTokenBufferMemory
  - 长对话：ConversationSummaryMemory
  - 平衡方案：ConversationSummaryBufferMemory

## 实现细节（需验证）
- **官方文档位置**：https://python.langchain.com/api_reference/ 下的memory子模块
- **关键类路径**：
  - langchain.memory.buffer.ConversationBufferMemory
  - langchain.memory.summary.ConversationSummaryMemory
  - langchain.memory.token_buffer.ConversationTokenBufferMemory
- **配置参数**：
  - ConversationBufferWindowMemory: `k` (保留消息数)
  - ConversationTokenBufferMemory: `max_token_limit`
  - ConversationSummaryMemory: 依赖LLM配置

## 用户偏好与项目特点
- **信息呈现**：偏好结构化总结（表格、对比矩阵）
- **实用性导向**：关注"何时使用"而非"如何实现"
- **版本敏感**：明确标注新旧API差异和迁移建议
- **决策支持**：提供基于场景的选择建议而非技术细节