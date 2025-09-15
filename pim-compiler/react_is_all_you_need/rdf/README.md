# RDF知识图谱与动态本体系统

本目录包含了使用**静态核心 + 动态扩展**模式构建知识图谱的完整实现。

## 核心文件

### 1. Python脚本

#### 直接转换工具
- `code_to_rdf_converter.py` - **代码库RDF转换器**（将Python代码转为知识图谱）
- `knowledge_to_rdf_with_extension.py` - 知识文档RDF生成器（动态扩展）

#### Agent智能生成
- `agent_rdf_generator.py` - **Agent智能RDF生成器**（让Agent理解并生成RDF）
- `agent_rdf_converter.py` - Agent调用自然语言函数生成RDF

#### 验证和分析
- `validate_extended_ontology.py` - 扩展本体验证工具
- `validate_knowledge_rdf.py` - 知识图谱验证工具
- `generate_knowledge_overview.py` - 高层次概览生成器

### 2. 理论文档
- `universal_ontology_challenge.md` - 通用本体论的挑战与解决方案
- `human_agent_hybrid_ontology.md` - 人机协作本体构建模式
- `agent_ontology_alignment.md` - 多Agent概念对齐机制

### 3. 生成结果
- `knowledge_extended.ttl` - 扩展后的知识图谱（Turtle格式）
- `ontology_extension_report.md` - 本体扩展报告
- `knowledge_overview.md` - 知识体系概览

## 核心创新

### 静态核心（人类定义）
仅10个最小认知原语：
- **存在层**：Thing, Entity, Concept
- **关系层**：Relation, partOf, instanceOf, relatedTo
- **过程层**：Process, causes, transformsTo

### 动态扩展（Agent自主）
Agent分析Knowledge目录后自动发现：
- NaturalLanguageFunction (0.93) - 自然语言函数
- Agent (0.95) - 自主软件实体
- Knowledge (0.94) - 结构化知识
- Memory (0.92) - 记忆系统
- SOP (0.91) - 标准操作流程
- Tool (0.89) - 可复用工具

## 使用方法

### 方式1：直接转换（快速）

#### 转换代码库为RDF
```bash
# 转换Python代码目录
python code_to_rdf_converter.py /path/to/code/dir output.ttl

# 默认转换core目录
python code_to_rdf_converter.py
```

#### 转换知识文档为RDF
```bash
python knowledge_to_rdf_with_extension.py
```

### 方式2：Agent智能生成（深度理解）

#### 使用Agent生成代码RDF
```bash
# Agent分析代码并生成RDF
python agent_rdf_generator.py --mode code --source /path/to/code

# Agent分析知识文档
python agent_rdf_generator.py --mode knowledge

# 同时分析代码和知识
python agent_rdf_generator.py --mode both

# 对比分析一致性
python agent_rdf_generator.py --mode compare
```

### 验证本体结构
```bash
python validate_extended_ontology.py
```

### 生成高层次概览
```bash
python generate_knowledge_overview.py
```

## 关键特性

1. **自然语言说明**：每个概念都有人类可读的描述
2. **语义向量**：用于跨Agent概念对齐
3. **置信度评分**：自动质量控制
4. **继承层次**：清晰的概念分类

## 推荐的语义向量模型

- **通用**：sentence-transformers/all-MiniLM-L6-v2
- **高质量**：sentence-transformers/all-mpnet-base-v2
- **中文**：BAAI/bge-small-zh-v1.5
- **多语言**：intfloat/multilingual-e5-small

## 意义

这个系统展示了**人机协作构建知识体系**的新范式：
- 人类提供框架
- Agent填充细节
- 通过语义理解实现概念对齐
- 最终形成活的、会成长的认知系统