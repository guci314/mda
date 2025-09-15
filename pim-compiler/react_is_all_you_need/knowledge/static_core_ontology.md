# 静态核心本体论

## 1. 最小认知原语（仅10个核心概念）

这是人类定义的稳定核心，所有Agent扩展都必须基于这些原语。

### 1.1 存在层（What exists）
```turtle
@prefix core: <http://ontology.core#> .

core:Thing           # 万物之源，所有概念的根
core:Entity          # 具体实体（可识别的事物）
core:Concept         # 抽象概念（思维构造）
```

### 1.2 关系层（How related）
```turtle
core:Relation        # 关系本身（所有关系的基类）
core:partOf          # 部分关系（组成关系）
core:instanceOf      # 实例关系（类型关系）
core:relatedTo       # 一般关联（最弱的关联）
```

### 1.3 过程层（What happens）
```turtle
core:Process         # 过程/变化（动态行为）
core:causes          # 因果关系（导致）
core:transformsTo    # 转换关系（变成）
```

## 2. 扩展规则

### 函数：扩展本体到新概念(concept_name, parent_concept, nl_description, nl_context, nl_example)
"""Agent扩展本体时必须遵循的规则"""
步骤：
1. 验证parent_concept必须是10个核心概念之一或已有扩展
2. 生成自然语言说明（必需）：
   - nl_description: 20-200字符的概念定义
   - nl_context: 10-100字符的使用语境
   - nl_example: 5-150字符的具体示例
3. 计算语义向量embedding（768维）
4. 创建RDF三元组：
   ```turtle
   new:Concept rdfs:subClassOf core:ParentConcept ;
       onto:nlDescription "..." ;
       onto:nlContext "..." ;
       onto:nlExample "..." ;
       onto:embedding [...] ;
       onto:createdBy "AgentName" ;
       onto:confidence 0.XX .
   ```
5. 验证逻辑一致性
6. 如果confidence < 0.8，标记需要人类审核
返回：扩展的RDF定义

## 3. 语义向量计算

### 函数：计算概念语义向量(nl_description, nl_context, nl_example)
"""生成概念的语义向量用于对齐"""
步骤：
1. 组合文本：full_text = f"{nl_description} {nl_context} {nl_example}"
2. 使用句子编码模型（如sentence-transformers）
3. 生成768维归一化向量
4. 存储为onto:embedding属性
返回：768维浮点数组

## 4. 概念对齐

### 函数：对齐相似概念(concept_a, concept_b, threshold=0.85)
"""发现不同Agent创建的相同概念"""
步骤：
1. 计算余弦相似度：sim = cosine_similarity(concept_a.embedding, concept_b.embedding)
2. 如果sim > threshold：
   - 标记为等价概念（owl:equivalentClass）
3. 如果0.75 < sim < threshold：
   - 标记为相似概念（onto:similarTo）
4. 记录对齐关系
返回：对齐类型和相似度分数

## 5. 示例扩展

### Agent发现的"自然语言函数"概念
```turtle
ag:NaturalLanguageFunction rdfs:subClassOf core:Process ;
    onto:nlDescription "A function defined in natural language that describes a process or procedure to be executed" ;
    onto:nlContext "Used in knowledge-driven development where behavior is defined by markdown files" ;
    onto:nlExample "函数：监控agent(agent_name, task) - 步骤：1.创建Agent 2.测试 3.分析日志" ;
    onto:embedding [0.23, 0.45, -0.12, ...] ;
    onto:createdBy "KnowledgeAnalysisAgent" ;
    onto:confidence 0.93 .
```

### Agent发现的"SOP"概念
```turtle
ag:SOP rdfs:subClassOf core:Concept ;
    onto:nlDescription "Standard Operating Procedure that defines a repeatable sequence of steps to accomplish a task" ;
    onto:nlContext "Used to standardize complex workflows in agent systems" ;
    onto:nlExample "Agent监控SOP: 1.编写知识 2.创建Agent 3.测试 4.分析 5.修复" ;
    onto:embedding [0.31, 0.52, -0.08, ...] ;
    onto:createdBy "WorkflowAnalysisAgent" ;
    onto:confidence 0.91 .
```

## 6. 动态扩展工作流

1. **Agent分析新领域**
   - 识别频繁出现的模式
   - 提取候选概念

2. **映射到核心本体**
   - 确定最合适的父类
   - 生成自然语言说明

3. **创建扩展定义**
   - 包含所有必需字段
   - 计算语义向量

4. **检查概念对齐**
   - 与已有概念比较
   - 发现等价或相似概念

5. **注册新概念**
   - 如果是新概念，添加到本体
   - 如果是已有概念，建立对齐关系

## 7. 质量控制

### 置信度阈值
- confidence > 0.9: 自动接受
- 0.8 < confidence < 0.9: 标记为待确认
- confidence < 0.8: 需要人类审核

### 使用频率追踪
- 记录每个扩展概念的使用次数
- 高频概念提升为准核心概念
- 低频概念标记为候选删除

## 8. 人机协作点

- **人类**：定义10个核心概念（一次性）
- **Agent**：基于核心概念扩展（持续性）
- **人类**：审核低置信度扩展（偶尔）
- **系统**：自动对齐和演化（自动）