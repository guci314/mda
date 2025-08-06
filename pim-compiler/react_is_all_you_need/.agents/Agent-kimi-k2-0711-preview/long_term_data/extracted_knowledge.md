# 长期记忆更新

## 用户个性化信息
- **姓名**：谷词
- **交互风格**：直接、简洁，关注项目概览而非细节
- **记忆确认**：已确认姓名记忆，无需再次询问

## 项目识别经验更新

### 1. 实验性工作空间特征
- **结构模式**：根目录包含多个独立实验项目（test_*, demo_*, shared_*）
- **命名约定**：使用数字后缀区分版本（test_project, test_project2, test_project3）
- **功能分区**：测试项目 + 演示项目 + 共享资源 + 核心工具
- **项目规模**：23个Python文件的实验集合 vs 70个Python文件+64个Markdown文档的完整框架

### 2. 架构模式识别
- **微实验架构**：分散式微实验设计，每个子项目独立验证
- **完整框架架构**：基于LangGraph的下一代React Agent框架，三级记忆系统+知识管理+多Agent协作
- **技术栈对比**：
  - 微实验：纯Python，零外部依赖
  - 完整框架：Python 3.8+、LangGraph、LangChain、SQLite

### 3. 快速识别技巧
- **根目录扫描**：优先查看一级目录的命名模式
- **关键词匹配**：test_*, demo_*, shared_*, *_workspace* vs docs/, knowledge/, examples/
- **文件计数**：快速统计Python文件数量判断项目规模
- **架构推断**：通过目录结构和文件命名推断功能分层

## world_overview.md 模板优化

### 1. 实验性工作空间专用模板
```markdown
# 项目概览
**实验性工作空间** - 包含多个测试项目和演示

## 架构模式
微实验架构 (Micro-Experiment Architecture)

## 目录结构
[树状图，最多3层]

## 项目分类
- **测试项目**：test_project*, 功能验证实验
- **演示项目**：demo_project*, 概念验证展示
- **共享资源**：shared_workspace*, 跨项目复用
- **核心工具**：独立实验单元

## 技术特征
- Python ≥3.8，零外部依赖
- 面向对象 + 函数式混合设计
- 单元测试驱动开发
- 渐进式功能演进

## 快速开始
1. 选择对应实验目录
2. 运行 `python <main_file>.py`
3. 执行测试：`python test_*.py`
```

### 2. 完整框架模板
```markdown
# 项目概览
**基于LangGraph的下一代React Agent框架**

## 架构模式
三级记忆系统 + 知识管理 + 多Agent协作

## 目录结构
- docs/：技术文档和指南
- knowledge/：分层组织的知识库系统
- examples/：使用示例和演示
- 核心文件：react_agent.py、tools.py、langchain_agent_tool.py

## 技术特征
- Python 3.8+
- LangGraph、LangChain、SQLite
- 70个Python文件 + 64个Markdown文档

## 快速开始
1. 基础使用：`python react_agent.py`
2. 多Agent协作：`python examples/multi_agent_demo.py`
3. Jupyter环境：`jupyter notebook`
```

## 常见问题解决方案更新

### 1. 无架构文档处理
- **问题**：缺乏architecture.md或design文档
- **解决**：通过代码结构和目录命名推断架构模式
- **工具**：find + wc统计文件数量，list_directory分析结构

### 2. 多项目根目录处理
- **问题**：根目录包含多个独立实验项目
- **解决**：按功能分类（测试/演示/共享/工具），分别概述
- **统计**：使用`find . -name "*.py" | wc -l`快速评估规模

### 3. 实验性项目描述
- **问题**：缺乏标准项目特征（无requirements.txt, README.md等）
- **解决**：通过目录命名、文件结构和代码内容推断项目用途
- **验证**：运行示例代码确认功能

### 4. 完整框架项目描述
- **问题**：项目规模大，功能复杂
- **解决**：按功能模块分层描述，突出核心组件
- **验证**：检查核心文件（react_agent.py, tools.py）确认主要功能

## 复用脚本增强

### 1. 实验项目快速分析
```bash
# 统计实验规模
echo "## 项目规模"
find . -name "*.py" | wc -l  # Python文件总数
find . -maxdepth 1 -type d -name "test_*" | wc -l  # 测试项目数
find . -maxdepth 1 -type d -name "demo_*" | wc -l 