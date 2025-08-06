# 项目概览

**React Is All You Need** - 基于 LangGraph 的下一代 React Agent 实现

## 项目定位
这是一个实验性的 AI Agent 框架项目，专注于构建基于 LangGraph 的 React Agent 系统，支持三级记忆、知识管理和多 Agent 协作。

## 架构模式
- **核心架构**: LangGraph-based React Agent
- **记忆系统**: 三级记忆 (NONE/SMART/PRO)
- **知识管理**: 动态知识文件加载
- **工具集成**: 完整的开发工具链
- **协作模式**: Agent-as-Tool 架构

## 目录结构

```
./
├── 📁 docs/                    # 技术文档和指南
├── 📁 examples/                # 使用示例和演示
├── 📁 knowledge/               # 知识库系统
│   ├── best_practices/         # 最佳实践知识
│   ├── coordination/           # 协作知识
│   ├── core/                   # 核心知识
│   ├── experimental/           # 实验性知识
│   ├── output/                 # 输出相关
│   ├── programming/            # 编程知识
│   └── workflow/               # 工作流知识
├── 📁 notebooks/               # Jupyter 笔记本
├── 📁 output/                  # 工作输出目录
├── 🐍 *.py (70个)             # Python 核心文件
├── 📄 *.md (64个)             # 文档和知识文件
└── ⚙️ 配置文件                # requirements.txt, .env 等
```

## 核心文件

### 主要组件
- **react_agent.py**: 核心 Agent 实现
- **tools.py**: 工具集合（文件操作、代码搜索、命令执行等）
- **langchain_agent_tool.py**: LangChain 集成
- **perspective_*.py**: 视角管理相关

### 调试和开发
- **debug_*.py**: 调试工具和演示
- **demo_*.py**: 功能演示
- **test_*.py**: 测试文件

### 配置和启动
- **requirements.txt**: 依赖管理
- **start_jupyter_*.sh**: Jupyter 启动脚本
- **.env**: 环境配置

## 技术栈
- **Python**: 3.8+
- **LangGraph**: 核心 Agent 框架
- **LangChain**: 工具集成
- **SQLite**: 持久化存储
- **Jupyter**: 交互式开发

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 基础使用
```bash
python react_agent.py --task "创建一个 TODO 应用"
```

### 3. 多 Agent 协作演示
```bash
python demo_agent_coordination_langchain.py
```

### 4. Jupyter 开发
```bash
./start_jupyter.sh
```

## 项目规模
- **Python 文件**: 70 个
- **Markdown 文档**: 64 个
- **知识文件**: 分层组织在 knowledge/ 目录
- **示例项目**: examples/ 目录包含完整演示

## 特色功能
1. **三级记忆系统**: 无状态、智能摘要、持久化
2. **知识管理**: 动态加载、文件引用、领域知识
3. **多 Agent 协作**: Agent-as-Tool 模式
4. **完整工具链**: 文件、代码、搜索、命令执行
5. **调试支持**: 详细的执行过程显示
6. **灵活配置**: 支持多种 LLM 和缓存策略

## 使用场景
- **代码生成**: 基于需求生成完整项目
- **项目分析**: 自动分析代码结构和架构
- **知识问答**: 基于知识库的智能回答
- **多 Agent 协作**: 复杂任务的分布式处理
- **实验研究**: AI Agent 架构和协作模式探索