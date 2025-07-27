# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MDA (Model Driven Architecture) implementation project that features a **PIM Execution Engine** - a revolutionary approach that interprets and executes Platform Independent Models (PIM) directly at runtime, enabling true no-code development for business users.

### Architecture Evolution
- **Phase 1**: Traditional MDA with code generation (PIM → PSM → Code)
- **Phase 2**: PIM Execution Engine (PIM → Runtime Execution) ✅ Current
- **Hybrid Mode**: Supports both runtime execution AND code generation via Gemini API

### Current Status (2025-07-21)
- **Engine**: Core implementation completed, runs as standalone Python application
- **Deployment**: No Docker required, uses SQLite by default
- **Models**: 3 example models (user management, order management, library system)
- **Features**: 
  - Hot reload (5-second detection)
  - Dynamic API generation
  - Flow execution with debugging
  - Code generation via Gemini API
  - Web-based debug UI
- **State**: Ready to start with `./start_master.sh`

## Project Structure

```
/home/guci/aiProjects/mda/
├── 基于大语言模型的mda.md                # Original MDA concepts
├── 基于LLM的MDA实现方案.md                # Updated implementation plan v2.0
├── PIM执行引擎架构设计.md                # Engine architecture design
├── PIM执行引擎实施路线图.md              # Implementation roadmap
├── CLAUDE.md                            # This file
├── models/                              # PIM models directory
│   ├── domain/                          # Domain models
│   │   ├── 用户管理_pim.md              # User management PIM (pure business)
│   │   └── 用户管理_psm.md              # User management PSM (FastAPI specific)
│   └── examples/                        # Example models
│       └── 客户管理系统.md               # Customer management example
├── pim-engine/                          # PIM Execution Engine
│   ├── src/                             # Engine source code
│   │   ├── core/                        # Core engine components
│   │   │   ├── engine.py                # Main engine class
│   │   │   ├── models.py                # Core data models
│   │   │   └── config.py                # Configuration
│   │   ├── loaders/                     # Model loaders
│   │   │   ├── yaml_loader.py           # YAML format loader
│   │   │   └── markdown_loader.py       # Markdown format loader
│   │   ├── engines/                     # Execution engines
│   │   │   ├── data_engine.py           # Database operations
│   │   │   ├── flow_engine.py           # Flow execution
│   │   │   └── rule_engine.py           # Rule evaluation
│   │   ├── api/                         # API generator
│   │   │   ├── api_generator.py         # Dynamic API creation
│   │   │   ├── dynamic_router.py        # Route management
│   │   │   └── openapi_manager.py       # OpenAPI spec
│   │   └── debug/                       # Debug components
│   │       ├── flow_debugger.py         # Flow debugging
│   │       └── debug_routes.py          # Debug API endpoints
│   ├── models/                          # Example PIM models
│   │   ├── user_management.yaml         # User management system
│   │   ├── order_management.yaml        # E-commerce orders
│   │   └── 图书管理系统.md               # Library system (Chinese)
│   ├── static/                          # Static files (debug UI)
│   │   ├── debug.html                   # Debug interface
│   │   └── models.html                  # Models management UI
│   ├── requirements.txt                 # Python dependencies
│   ├── start_master.sh                  # Start script
│   ├── stop.sh                          # Stop script
│   └── tests/                           # Test suite
└── services/                            # Generated services (legacy)
```

[... rest of the original content remains unchanged ...]

## API and Secret Management

### Secrets and API Keys
- API key for PIM compiler is located in `pim-compiler/.env` file
- Always use environment variables for sensitive configuration
- Never commit API keys or secrets directly to version control
