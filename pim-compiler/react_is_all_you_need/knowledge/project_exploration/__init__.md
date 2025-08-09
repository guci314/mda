# Project Exploration 知识包

项目探索和理解相关的知识，帮助Agent分析和理解项目结构。

## 包含的知识模块

### 4+1架构视图探索

#### 4plus1_exploration_prompt.md
- **用途**: 使用4+1架构视图方法探索项目
- **适用对象**: 项目分析Agent、架构理解Agent
- **主要内容**: 
  - 逻辑视图：类、接口、组件关系
  - 开发视图：代码组织、模块结构
  - 进程视图：运行时进程、线程
  - 物理视图：部署架构、硬件映射
  - 场景视图：用例、业务流程

### UML建模探索

#### uml_exploration_prompt.md
- **用途**: 使用UML建模方法理解项目
- **适用对象**: 建模Agent、文档生成Agent
- **主要内容**:
  - 结构图：类图、组件图、部署图
  - 行为图：序列图、活动图、状态图
  - 交互图：通信图、时序图
  - 用例图：参与者、用例关系

## 使用建议

### 1. 项目初始分析
```python
# 全面的项目理解
knowledge_files = [
    "knowledge/project_exploration/4plus1_exploration_prompt.md",
    "knowledge/project_exploration/uml_exploration_prompt.md"
]
```

### 2. 架构理解专注
```python
# 仅关注架构视图
knowledge_files = [
    "knowledge/project_exploration/4plus1_exploration_prompt.md"
]
```

### 3. 建模文档生成
```python
# UML建模为主
knowledge_files = [
    "knowledge/project_exploration/uml_exploration_prompt.md"
]
```

## 探索流程

### 标准探索步骤

1. **项目扫描**
   - 识别主要编程语言
   - 分析目录结构
   - 检测框架和依赖

2. **架构分析** (4+1视图)
   - 逻辑架构：识别核心组件
   - 开发架构：理解代码组织
   - 进程架构：分析运行时行为
   - 物理架构：理解部署结构
   - 场景：提取关键用例

3. **建模提取** (UML)
   - 静态结构：类关系、组件依赖
   - 动态行为：交互序列、状态转换
   - 用例建模：业务流程理解

4. **知识整合**
   - 生成项目概览文档
   - 创建架构决策记录
   - 更新项目理解笔记

## 输出格式

### 项目理解报告
```markdown
# 项目名称

## 概览
- 语言：Python/Java/...
- 框架：FastAPI/Spring/...
- 架构风格：微服务/单体/...

## 4+1架构视图
### 逻辑视图
...
### 开发视图
...

## UML模型
### 核心类图
...
### 主要序列图
...
```

### 探索笔记
```json
{
  "project_name": "...",
  "exploration_date": "2024-08-10",
  "languages": ["Python"],
  "frameworks": ["FastAPI"],
  "architecture_style": "RESTful API",
  "key_components": [...],
  "main_workflows": [...],
  "dependencies": [...]
}
```

## 与其他知识包的协作

### 与MDA知识包
- 项目探索结果可作为PIM输入
- 理解现有代码以生成PSM

### 与Workflow知识包
- 识别项目中的工作流程
- 提取任务依赖关系

### 与Core知识包
- 使用系统提示模板
- 遵循数据管理规范

## 最佳实践

### DO ✅
1. 从整体到细节逐步探索
2. 记录所有重要发现
3. 生成可视化文档
4. 保持探索笔记更新
5. 验证理解的准确性

### DON'T ❌
1. 不要忽略配置文件
2. 不要跳过测试代码分析
3. 不要假设架构风格
4. 不要遗漏依赖分析
5. 不要忽视文档注释

## 工具支持

### 推荐工具
- **代码分析**: ast模块、静态分析工具
- **依赖分析**: pip、npm、maven等包管理器
- **可视化**: PlantUML、Mermaid
- **文档生成**: Sphinx、MkDocs

### 命令示例
```bash
# Python项目分析
find . -name "*.py" | xargs grep -h "^class\|^def" 

# 依赖分析
pip freeze > requirements.txt
npm list --depth=0

# 目录结构
tree -I "__pycache__|*.pyc|node_modules"
```

## 注意事项

1. **隐私保护**: 不要在探索笔记中包含敏感信息
2. **性能考虑**: 大型项目探索可能耗时较长
3. **增量探索**: 支持渐进式项目理解
4. **版本跟踪**: 记录探索时的代码版本

## 扩展可能

- 添加更多架构模式识别
- 支持更多编程语言
- 集成自动化文档生成
- 添加代码质量评估
- 支持架构演进跟踪