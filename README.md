# MDA (Model-Driven Architecture) Implementation with PIM Execution Engine

[中文版本](#中文版本)

## Overview

This project implements a revolutionary approach to Model-Driven Architecture (MDA) by introducing a **PIM Execution Engine** that directly interprets and executes Platform Independent Models (PIM) at runtime, eliminating the need for code generation.

### Evolution Journey

1. **Phase 1**: Traditional MDA with template-based code generation
2. **Phase 2**: PIM Execution Engine - Models run directly without code generation ✅
3. **Phase 3**: AI-Enhanced MDA - LLM generates production code when needed ✅

## 🚀 Key Innovation

**Traditional MDA**: `Business Model → Generate Code → Compile → Deploy → Run`  
**Our Approach**: `Business Model → Direct Execution` ✨

Business users can now define their systems using only PIM models, and the engine provides a complete running system with APIs, database, business rules, and debugging capabilities - all without writing or seeing any code!

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│          Business Users                     │
│    (PIM Models in YAML/Markdown)           │
└────────────────┬───────────────────────────┘
                 │
┌────────────────▼───────────────────────────┐
│         PIM Execution Engine               │
├────────────────────────────────────────────┤
│ • Model Loader    • API Generator          │
│ • Data Engine     • Flow Engine            │
│ • Rule Engine     • Debug Interface        │
└────────────────┬───────────────────────────┘
                 │
┌────────────────▼───────────────────────────┐
│     Infrastructure (PostgreSQL, Redis)     │
└────────────────────────────────────────────┘
```

## 📁 Project Structure

```
mda/
├── 基于大语言模型的mda.md          # MDA concepts with LLM
├── 基于Claude Code的MDA实现方案.md  # Implementation plan v2.0
├── PIM执行引擎架构设计.md          # Engine architecture design
├── PIM执行引擎实施路线图.md        # Implementation roadmap
├── CLAUDE.md                       # Claude Code guidance
├── README.md                       # This file
├── models/                         # PIM model examples
│   ├── user_management.yaml       # User management model
│   └── order_management.yaml      # E-commerce order model
├── pim-engine/                    # PIM Execution Engine
│   ├── src/                       # Source code
│   ├── docker-compose.yml         # Docker setup
│   └── README.md                  # Engine documentation
└── .mda/                          # MDA tools and commands
    └── commands/                  # Slash commands for Claude Code
```

## 🚀 Quick Start

### 1. Start the PIM Engine

```bash
cd pim-engine
docker compose up -d
```

### 2. Access the System

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Debug UI**: http://localhost:8000/debug/ui
- **Model Management**: http://localhost:8000/models
- **Database UI**: http://localhost:8080

### 3. Create a PIM Model

Create `models/my_domain.yaml`:

```yaml
domain: my-domain
version: 1.0.0

entities:
  - name: Customer
    attributes:
      name:
        type: string
        required: true
      email:
        type: string
        unique: true

services:
  - name: CustomerService
    methods:
      - name: registerCustomer
        parameters:
          customerData: Customer
```

### 4. Use the Generated API

The engine automatically creates REST APIs:

```bash
# Create a customer
curl -X POST http://localhost:8000/api/v1/my-domain/customers \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

## 🌟 Features

### For Business Users
- Define systems using natural language and diagrams
- No programming knowledge required
- Visual debugging of business flows
- Instant changes without redeployment

### For Developers
- Zero code generation - maintain models, not code
- Hot reload for rapid iteration
- Extensible architecture
- Full API documentation
- WebSocket support for real-time features

### Technical Capabilities
- Dynamic API generation from models
- Automatic database schema creation
- Business rule execution
- Flow orchestration with visual debugging
- Multi-format support (YAML, Markdown)
- Hot reload without restart
- **AI Code Generation** (NEW) - Generate production code with Gemini AI

## 📚 Documentation

- [Implementation Plan](基于Claude Code的MDA实现方案.md) - Detailed MDA implementation with Claude Code
- [Engine Architecture](PIM执行引擎架构设计.md) - Technical architecture of the PIM engine
- [Implementation Roadmap](PIM执行引擎实施路线图.md) - Development phases and milestones
- [Engine README](pim-engine/README.md) - PIM engine specific documentation

## 🛠️ Slash Commands (Claude Code)

For traditional code generation needs:

```bash
# Generate FastAPI service from PIM
/mda-generate-fastapi domain=user-management service=user-service

# Convert PIM to PSM
/pim2FastapiPsm pim=models/domain/用户管理_pim.md

# Troubleshooting
/mda-troubleshooting issue="API not generated"
```

## 🎯 Use Cases

1. **Rapid Prototyping**: Create working APIs in minutes
2. **Business Process Automation**: Model workflows that execute immediately
3. **No-Code Development**: Business analysts can build systems
4. **Microservice Generation**: Each domain becomes a service
5. **Legacy Modernization**: Model existing systems and regenerate

## 🔮 Future Vision

- AI-assisted model design
- Cloud-native deployment
- Visual model designer
- Industry-specific model templates
- Distributed execution engine

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

<a name="中文版本"></a>

# MDA（模型驱动架构）实现与PIM执行引擎

## 概述

本项目通过引入**PIM执行引擎**，实现了模型驱动架构（MDA）的革命性方法。该引擎能够在运行时直接解释和执行平台无关模型（PIM），无需生成代码。

### 发展历程

1. **第一阶段**：基于模板的传统MDA代码生成
2. **第二阶段**：PIM执行引擎 - 模型直接运行，无需代码生成 ✅
3. **第三阶段**：AI增强的MDA - 需要时使用LLM生成生产级代码 ✅

## 🚀 核心创新

**传统MDA**：`业务模型 → 生成代码 → 编译 → 部署 → 运行`  
**我们的方法**：`业务模型 → 直接执行` ✨

业务用户现在只需使用PIM模型定义系统，引擎就能提供完整的运行系统，包括API、数据库、业务规则和调试功能 - 完全不需要编写或查看任何代码！

## 🚀 快速开始

### 1. 启动PIM引擎

```bash
cd pim-engine
docker compose up -d
```

### 2. 访问系统

- **API接口**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **调试界面**: http://localhost:8000/debug/ui
- **模型管理**: http://localhost:8000/models
- **数据库界面**: http://localhost:8080

### 3. 创建PIM模型

创建 `models/我的领域.yaml`:

```yaml
domain: 我的领域
version: 1.0.0

entities:
  - name: 客户
    attributes:
      姓名:
        type: string
        required: true
      邮箱:
        type: string
        unique: true

services:
  - name: 客户服务
    methods:
      - name: 注册客户
        parameters:
          客户数据: 客户
```

## 🌟 特性

### 面向业务用户
- 使用自然语言和图表定义系统
- 无需编程知识
- 可视化调试业务流程
- 即时更改，无需重新部署

### 面向开发者
- 零代码生成 - 维护模型而非代码
- 热重载实现快速迭代
- 可扩展架构
- 完整的API文档
- WebSocket支持实时功能
- **AI代码生成**（新功能）- 使用Gemini AI生成生产级代码

## 📚 文档

- [业务专家使用手册](业务专家使用手册.md) - 面向业务用户的完整指南
- [基于Claude Code的MDA实现方案](基于Claude Code的MDA实现方案.md)
- [PIM执行引擎架构设计](PIM执行引擎架构设计.md)
- [PIM执行引擎实施路线图](PIM执行引擎实施路线图.md)
- [开发者指南](pim-engine/开发者指南.md)
- [引擎README](pim-engine/README.md)

## 🎯 应用场景

1. **快速原型**：几分钟内创建可用的API
2. **业务流程自动化**：建模后立即执行的工作流
3. **无代码开发**：业务分析师也能构建系统
4. **微服务生成**：每个领域成为一个服务
5. **遗留系统现代化**：建模现有系统并重新生成

---

**记住**：使用PIM引擎，您的模型就是您的应用程序！🚀