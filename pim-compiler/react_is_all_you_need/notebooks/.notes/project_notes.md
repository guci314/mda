# . 项目笔记

## 项目结构
- README.md: ./README.md
- 核心代码: ./core/
- 配置文件: ./.env
- 数据文件: ./orders.json, ./products.json（已迁移到Agent home目录）

## 我的DNA
- Specification: ~/.agent/order_agent/specification.md  # 我的本质定义

## 代码约定
- 使用ReactAgentMinimal框架
- 知识文件在knowledge/目录
- 基于DDD领域驱动设计
- 微服务架构：Share Nothing原则

## 子Agent架构
- customer_manager: ~/.agent/customer_manager/ （客户管理微服务）
- product_manager: ~/.agent/product_manager/ （商品管理微服务）
- 数据隔离：每个子Agent拥有独立的数据存储
- 通信方式：通过集成工具API调用

## 重要发现
### 2025-10-03 [@learning]
- 成功创建product_manager子Agent，实现完整的Share Nothing微服务架构
- 产品数据完全隔离在~/.agent/product_manager/data/products.json
- order_agent通过product_integration_tool调用子Agent服务
- 验证了微服务架构的可行性和数据隔离的有效性

### 2025-10-03 [@learning]
- 创建子Agent的标准9步流程：定义Specification → 创建知识文件 → 实现外部工具 → 使用create_agent创建Agent → 迁移数据 → 测试功能 → 更新集成工具 → 更新知识文件 → 运行一致性检查
- 确保每个步骤完整执行，保证系统一致性