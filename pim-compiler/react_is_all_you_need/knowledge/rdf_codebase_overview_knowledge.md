# RDF图谱代码库概览生成指南

## 1. 核心理念
通过分析RDF知识图谱的结构和语义信息，生成代码库的高层次架构理解和概览。

## 2. 统计分析函数

### 函数：分析代码库基础统计(ttl_file)
"""统计代码库的基本组成"""
步骤：
1. 加载RDF图谱
2. 执行统计查询：
   ```sparql
   # 统计各类实体数量
   SELECT (COUNT(DISTINCT ?module) as ?modules)
          (COUNT(DISTINCT ?class) as ?classes)
          (COUNT(DISTINCT ?method) as ?methods)
          (COUNT(DISTINCT ?concept) as ?concepts)
   WHERE {
     { ?module rdf:type kg:PythonModule } UNION
     { ?class rdf:type kg:Class } UNION
     { ?method rdf:type kg:Method } UNION
     { ?concept rdf:type kg:Concept }
   }
   ```
3. 统计关系数量：
   - 继承关系：`kg:extends`、`kg:inheritsFrom`
   - 导入关系：`kg:imports`
   - 使用关系：`kg:uses`
   - 定义关系：`kg:defines`
4. 计算代码规模指标：
   - 平均每个类的方法数
   - 模块间的耦合度
   - 继承深度
返回：统计报告

### 函数：识别核心模块(ttl_file)
"""识别代码库的核心模块"""
步骤：
1. 加载RDF图谱
2. 计算模块的重要性分数：
   ```sparql
   SELECT ?module (COUNT(?import) as ?import_count)
   WHERE {
     ?other kg:imports ?module .
   }
   GROUP BY ?module
   ORDER BY DESC(?import_count)
   ```
3. 识别枢纽模块（被多个模块依赖）
4. 识别基础模块（不依赖其他模块）
5. 识别应用模块（依赖多个其他模块）
返回：核心模块列表及其角色

### 函数：分析架构模式(ttl_file)
"""识别代码库的架构模式"""
步骤：
1. 加载RDF图谱
2. 识别设计模式：
   - 工厂模式：查找名称包含Factory的类
   - 单例模式：查找Singleton相关
   - 观察者模式：查找Observer/Listener
   - 装饰器模式：查找Wrapper/Decorator
3. 分析继承层次：
   ```sparql
   SELECT ?base (COUNT(?derived) as ?subclass_count)
   WHERE {
     ?derived kg:extends ?base .
   }
   GROUP BY ?base
   HAVING(?subclass_count > 2)
   ```
4. 识别接口和抽象类
5. 分析组件间的交互模式
返回：架构模式报告

## 3. 概念提取函数

### 函数：提取核心概念(ttl_file)
"""从RDF图谱提取核心概念"""
步骤：
1. 查询所有概念实体：
   ```sparql
   SELECT ?concept ?name ?description
   WHERE {
     ?concept rdf:type kg:Concept .
     ?concept kg:hasName ?name .
     OPTIONAL { ?concept kg:hasDescription ?description }
   }
   ```
2. 分析概念之间的关系
3. 识别概念的实现位置：
   ```sparql
   SELECT ?concept ?implementation
   WHERE {
     ?implementation kg:implements ?concept .
   }
   ```
4. 构建概念层次结构
返回：核心概念及其关系

### 函数：分析领域模型(ttl_file)
"""理解代码库的领域模型"""
步骤：
1. 提取所有类和其docstring
2. 基于docstring识别业务概念
3. 分析类名模式识别领域实体
4. 构建领域概念图：
   - 实体类（名词）
   - 服务类（动词+Service/Manager）
   - 工具类（Tool/Util/Helper）
5. 识别领域边界
返回：领域模型描述

## 4. 依赖分析函数

### 函数：生成依赖关系图(ttl_file)
"""生成模块间的依赖关系"""
步骤：
1. 查询所有导入关系：
   ```sparql
   SELECT ?from ?to
   WHERE {
     ?from kg:imports ?to .
   }
   ```
2. 构建依赖矩阵
3. 识别循环依赖
4. 计算依赖深度
5. 生成依赖关系的文本描述
返回：依赖关系图（文本格式）

### 函数：分析模块耦合度(ttl_file)
"""分析模块间的耦合程度"""
步骤：
1. 统计每个模块的：
   - 传入耦合（被依赖数）
   - 传出耦合（依赖其他模块数）
2. 计算耦合度指标
3. 识别高耦合模块
4. 提供解耦建议
返回：耦合度分析报告

## 5. 功能理解函数

### 函数：提取功能模块(ttl_file)
"""基于方法和类的docstring理解功能模块"""
步骤：
1. 查询所有包含docstring的实体：
   ```sparql
   SELECT ?entity ?name ?docstring ?type
   WHERE {
     ?entity kg:hasModuleDocstring|kg:hasClassDocstring|kg:hasMethodDocstring ?docstring .
     ?entity kg:hasName ?name .
     ?entity rdf:type ?type .
   }
   ```
2. 基于docstring进行功能分类：
   - 数据处理功能
   - 网络通信功能
   - 文件操作功能
   - 用户界面功能
   - 业务逻辑功能
3. 将相关功能聚类
4. 识别功能边界
返回：功能模块清单

### 函数：分析核心工作流(ttl_file)
"""识别主要的执行流程"""
步骤：
1. 查找入口点（main函数、execute方法）
2. 追踪方法调用链：
   ```sparql
   SELECT ?caller ?callee
   WHERE {
     ?caller kg:calls ?callee .
   }
   ```
3. 识别关键执行路径
4. 分析控制流转移
5. 生成工作流描述
返回：核心工作流程

## 6. 高层次概览生成函数

### 函数：生成架构概览(ttl_file)
"""生成完整的架构概览"""
步骤：
1. 调用 分析代码库基础统计(ttl_file)
2. 调用 识别核心模块(ttl_file)
3. 调用 分析架构模式(ttl_file)
4. 调用 提取核心概念(ttl_file)
5. 整合所有信息生成概览：
   ```markdown
   # 代码库架构概览
   
   ## 基本信息
   - 模块数量：X
   - 类数量：Y
   - 核心概念：Z
   
   ## 架构特征
   - 设计模式：...
   - 架构风格：...
   
   ## 核心组件
   - 核心模块：...
   - 关键类：...
   
   ## 主要功能
   - ...
   ```
返回：架构概览文档

### 函数：生成执行摘要(ttl_file)
"""为管理层生成执行摘要"""
步骤：
1. 提取关键指标
2. 识别技术栈
3. 总结核心功能
4. 评估代码质量指标
5. 生成一页纸摘要：
   - 项目规模
   - 技术架构
   - 核心能力
   - 关键组件
   - 质量指标
返回：执行摘要

### 函数：生成技术文档大纲(ttl_file)
"""基于RDF生成技术文档的大纲"""
步骤：
1. 按模块组织内容
2. 按功能分类
3. 按概念层次组织
4. 生成文档结构：
   ```markdown
   1. 系统概述
      1.1 核心概念
      1.2 架构设计
   2. 模块说明
      2.1 模块A
      2.2 模块B
   3. API参考
      3.1 类参考
      3.2 方法参考
   4. 设计决策
   5. 扩展指南
   ```
返回：文档大纲

## 7. 可视化辅助函数

### 函数：生成ASCII架构图(ttl_file)
"""生成文本格式的架构图"""
步骤：
1. 识别主要组件
2. 分析组件关系
3. 生成ASCII图：
   ```
   ┌─────────────┐
   │   Module A  │──imports──▶
   └─────────────┘            │
          │                   ▼
      extends           ┌─────────────┐
          │             │   Module B  │
          ▼             └─────────────┘
   ┌─────────────┐            │
   │   Class X   │◀───uses────┘
   └─────────────┘
   ```
返回：ASCII架构图

### 函数：生成组件关系表(ttl_file)
"""生成组件关系的表格"""
步骤：
1. 提取所有组件
2. 分析组件间关系
3. 生成关系矩阵表：
   ```
   | Component | Depends On | Used By | Type |
   |-----------|------------|---------|------|
   | Module A  | Module B   | Main    | Core |
   | Class X   | Function   | Module A| Tool |
   ```
返回：关系表格

## 8. 洞察生成函数

### 函数：识别改进机会(ttl_file)
"""基于RDF分析识别改进机会"""
步骤：
1. 识别代码异味：
   - 过长的继承链
   - 循环依赖
   - 高耦合模块
   - 缺少文档的关键组件
2. 识别重构机会
3. 发现模式违反
4. 提出改进建议
返回：改进机会列表

### 函数：评估代码库健康度(ttl_file)
"""评估代码库的整体健康状况"""
步骤：
1. 计算健康指标：
   - 文档覆盖率（有docstring的实体比例）
   - 模块化程度
   - 继承深度合理性
   - 耦合度
2. 与最佳实践对比
3. 生成健康报告
返回：健康度评估报告

## 9. 智能概览生成

### 函数：生成智能代码库概览(ttl_file, focus_area=None)
"""根据需求生成定制化概览"""
步骤：
1. 如果指定focus_area：
   - "architecture"：调用 生成架构概览
   - "dependencies"：调用 生成依赖关系图
   - "concepts"：调用 提取核心概念
   - "quality"：调用 评估代码库健康度
2. 否则生成综合概览：
   - 调用 生成架构概览(ttl_file)
   - 调用 提取核心概念(ttl_file)
   - 调用 分析核心工作流(ttl_file)
   - 调用 识别改进机会(ttl_file)
3. 整合所有信息
4. 生成结构化报告
返回：定制化概览

## 10. 使用示例

```python
# 生成完整概览
调用 生成智能代码库概览("/tmp/core_knowledge_graph.ttl")

# 生成架构视图
调用 生成架构概览("/tmp/core_knowledge_graph.ttl")

# 分析依赖关系
调用 生成依赖关系图("/tmp/core_knowledge_graph.ttl")

# 提取核心概念
调用 提取核心概念("/tmp/core_knowledge_graph.ttl")

# 生成执行摘要
调用 生成执行摘要("/tmp/core_knowledge_graph.ttl")

# 评估代码质量
调用 评估代码库健康度("/tmp/core_knowledge_graph.ttl")
```