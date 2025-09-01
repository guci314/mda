# 世界状态

## 系统架构
### 架构概览
```
主控制器 (main_controller) ──▶ Python专家Agent ──▶ fib.py
                         └─▶ 文档专家Agent ──▶ fib_docs.md
```

### 核心组件
- **主控制器**：
  - 职责：协调多个Agent执行任务
  - 位置：当前工作目录
  - 依赖：无
  - 接口：直接调用Agent API

- **Python专家Agent**：
  - 职责：编写Python代码
  - 位置：Agent实例
  - 依赖：deepseek-chat模型
  - 接口：execute_agent调用

- **文档专家Agent**：
  - 职责：编写技术文档
  - 位置：Agent实例
  - 依赖：deepseek-chat模型
  - 接口：execute_agent调用

## 项目结构
### 核心目录
- `.notes/main_controller/`: 主控制器的笔记目录
- `fib.py`: Python专家将创建的斐波那契函数文件
- `fib_docs.md`: 文档专家将创建的文档文件

## 技术栈
### 语言和框架
- 主语言：Python 3.x
- Agent框架：DeepSeek Chat模型

---
记录时间：2024-12-19 10:30:00
状态类型：任务开始