# 知识文档RDF本体论设计

## 1. 核心理念
为Knowledge和Docs设计的本体论，捕捉知识的结构、语义和关系。

## 2. 本体论定义

### 2.1 知识类型（Classes）

```turtle
@prefix kd: <http://example.org/knowledge-docs#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ========== 顶层类 ==========
kd:Knowledge rdf:type rdfs:Class ;
    rdfs:comment "所有知识的基类" .

kd:Document rdf:type rdfs:Class ;
    rdfs:comment "文档基类" .

# ========== 知识子类 ==========
kd:Concept rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Knowledge ;
    rdfs:comment "概念性知识，如理论、原理" .

kd:Procedure rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Knowledge ;
    rdfs:comment "流程性知识，如步骤、工作流" .

kd:Function rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Knowledge ;
    rdfs:comment "自然语言函数" .

kd:Principle rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Knowledge ;
    rdfs:comment "原则和最佳实践" .

kd:Pattern rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Knowledge ;
    rdfs:comment "模式和范式" .

kd:Example rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Knowledge ;
    rdfs:comment "示例和案例" .

kd:Configuration rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Knowledge ;
    rdfs:comment "配置和设置知识" .

# ========== 文档子类 ==========
kd:Guide rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Document ;
    rdfs:comment "指南类文档" .

kd:Tutorial rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Document ;
    rdfs:comment "教程类文档" .

kd:Reference rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Document ;
    rdfs:comment "参考文档" .

kd:Specification rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Document ;
    rdfs:comment "规范文档" .

kd:DesignDoc rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Document ;
    rdfs:comment "设计文档" .

# ========== 结构元素 ==========
kd:Section rdf:type rdfs:Class ;
    rdfs:comment "文档章节" .

kd:Subsection rdf:type rdfs:Class ;
    rdfs:subClassOf kd:Section ;
    rdfs:comment "子章节" .

kd:CodeBlock rdf:type rdfs:Class ;
    rdfs:comment "代码块" .

kd:Table rdf:type rdfs:Class ;
    rdfs:comment "表格" .

kd:List rdf:type rdfs:Class ;
    rdfs:comment "列表" .

# ========== 知识分类 ==========
kd:Domain rdf:type rdfs:Class ;
    rdfs:comment "知识领域" .

kd:Topic rdf:type rdfs:Class ;
    rdfs:comment "主题" .

kd:Tag rdf:type rdfs:Class ;
    rdfs:comment "标签" .
```

### 2.2 属性（Properties）

```turtle
# ========== 基本属性 ==========
kd:hasTitle rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge, kd:Document ;
    rdfs:range xsd:string ;
    rdfs:comment "标题" .

kd:hasDescription rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range xsd:string ;
    rdfs:comment "描述" .

kd:hasContent rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge, kd:Document ;
    rdfs:range xsd:string ;
    rdfs:comment "内容" .

kd:hasPath rdf:type rdf:Property ;
    rdfs:domain kd:Document ;
    rdfs:range xsd:string ;
    rdfs:comment "文件路径" .

kd:createdDate rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge, kd:Document ;
    rdfs:range xsd:date ;
    rdfs:comment "创建日期" .

kd:modifiedDate rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge, kd:Document ;
    rdfs:range xsd:date ;
    rdfs:comment "修改日期" .

kd:author rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge, kd:Document ;
    rdfs:range xsd:string ;
    rdfs:comment "作者" .

# ========== 结构关系 ==========
kd:contains rdf:type rdf:Property ;
    rdfs:domain kd:Document ;
    rdfs:range kd:Section ;
    rdfs:comment "包含章节" .

kd:hasSubsection rdf:type rdf:Property ;
    rdfs:domain kd:Section ;
    rdfs:range kd:Subsection ;
    rdfs:comment "有子章节" .

kd:hasCodeBlock rdf:type rdf:Property ;
    rdfs:domain kd:Section ;
    rdfs:range kd:CodeBlock ;
    rdfs:comment "包含代码块" .

kd:hasExample rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range kd:Example ;
    rdfs:comment "有示例" .

# ========== 知识关系 ==========
kd:prerequisite rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range kd:Knowledge ;
    rdfs:comment "前置知识" .

kd:relatedTo rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range kd:Knowledge ;
    rdfs:comment "相关知识" .

kd:extends rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range kd:Knowledge ;
    rdfs:comment "扩展" .

kd:implements rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range kd:Concept ;
    rdfs:comment "实现概念" .

kd:references rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range kd:Document ;
    rdfs:comment "引用文档" .

kd:uses rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range kd:Function ;
    rdfs:comment "使用函数" .

# ========== 分类属性 ==========
kd:belongsToDomain rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range kd:Domain ;
    rdfs:comment "属于领域" .

kd:hasTopic rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range kd:Topic ;
    rdfs:comment "主题" .

kd:hasTag rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range kd:Tag ;
    rdfs:comment "标签" .

# ========== 函数特有属性 ==========
kd:hasParameters rdf:type rdf:Property ;
    rdfs:domain kd:Function ;
    rdfs:range xsd:string ;
    rdfs:comment "参数" .

kd:hasSteps rdf:type rdf:Property ;
    rdfs:domain kd:Function ;
    rdfs:range rdf:List ;
    rdfs:comment "执行步骤" .

kd:hasReturnValue rdf:type rdf:Property ;
    rdfs:domain kd:Function ;
    rdfs:range xsd:string ;
    rdfs:comment "返回值" .

# ========== 质量属性 ==========
kd:complexity rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range xsd:string ;
    rdfs:comment "复杂度：简单/中等/复杂" .

kd:importance rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range xsd:integer ;
    rdfs:comment "重要性评分1-10" .

kd:completeness rdf:type rdf:Property ;
    rdfs:domain kd:Document ;
    rdfs:range xsd:float ;
    rdfs:comment "完整度0-1" .
```

## 3. 知识抽取函数

### 函数：解析知识文件结构(knowledge_file)
"""解析Markdown知识文件的结构"""
步骤：
1. 读取文件内容
2. 识别文档类型（Guide/Tutorial/Reference等）
3. 解析标题层级（#、##、###）
4. 提取章节结构
5. 识别特殊块：
   - 函数定义（### 函数：xxx）
   - 代码块（```）
   - 示例（示例：）
   - 注意事项（注意：、重要：）
6. 构建文档树结构
返回：文档结构树

### 函数：提取自然语言函数(content)
"""从内容中提取自然语言函数定义"""
步骤：
1. 查找模式："### 函数：函数名(参数)"
2. 提取函数签名
3. 提取docstring（三引号内容）
4. 解析步骤列表
5. 识别返回值说明
6. 创建Function实体
返回：函数列表

### 函数：识别知识类型(content)
"""识别内容的知识类型"""
步骤：
1. 分析内容特征：
   - 包含"原则"、"理念" → Principle
   - 包含"步骤"、"流程" → Procedure
   - 包含"概念"、"定义" → Concept
   - 包含"模式"、"范式" → Pattern
   - 包含"示例"、"案例" → Example
   - 包含"配置"、"设置" → Configuration
2. 可能有多个类型，返回主要类型
返回：知识类型

### 函数：提取知识关系(content)
"""提取知识之间的关系"""
步骤：
1. 识别前置条件（"前提"、"需要先"）
2. 识别引用（"参见"、"详见"）
3. 识别扩展（"基于"、"扩展自"）
4. 识别实现（"实现了"、"体现了"）
5. 识别使用（"调用"、"使用"）
返回：关系三元组列表

## 4. 高层次分析函数

### 函数：构建知识图谱(knowledge_dir, output_file)
"""将知识目录转换为RDF图谱"""
步骤：
1. 扫描目录下所有.md文件
2. 对每个文件：
   - 调用 解析知识文件结构(file)
   - 调用 提取自然语言函数(content)
   - 调用 识别知识类型(content)
   - 调用 提取知识关系(content)
3. 构建RDF三元组
4. 推理隐含关系
5. 输出Turtle格式
返回：知识图谱文件

### 函数：生成知识概览(ttl_file)
"""基于RDF生成知识库概览"""
步骤：
1. 加载知识图谱
2. 统计分析：
   - 知识总量（各类型数量）
   - 文档分布
   - 函数清单
   - 核心概念
3. 结构分析：
   - 知识层次
   - 依赖关系
   - 主题分类
4. 质量评估：
   - 文档完整度
   - 知识覆盖度
   - 更新频率
5. 生成概览报告
返回：Markdown格式概览

### 函数：分析知识体系(ttl_file)
"""分析知识的体系结构"""
步骤：
1. 识别核心概念（高连接度节点）
2. 分析知识层次（从基础到高级）
3. 发现知识集群（相关知识分组）
4. 识别知识路径（学习路径）
5. 评估知识完整性
返回：知识体系报告

### 函数：生成学习路径(ttl_file, target_knowledge)
"""生成到达目标知识的学习路径"""
步骤：
1. 找到目标知识节点
2. 递归查找所有前置知识
3. 构建依赖图
4. 拓扑排序生成学习顺序
5. 标注难度和预计时间
返回：学习路径

## 5. 实际应用示例

### 示例1：分析Agent Builder知识
```python
# 构建知识图谱
调用 构建知识图谱(
    "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge",
    "/tmp/knowledge_graph.ttl"
)

# 生成概览
调用 生成知识概览("/tmp/knowledge_graph.ttl")
```

### 示例2：理解自然语言函数体系
```sparql
# 查询所有自然语言函数
SELECT ?func ?name ?params WHERE {
    ?func rdf:type kd:Function .
    ?func kd:hasTitle ?name .
    ?func kd:hasParameters ?params .
}

# 查询函数依赖关系
SELECT ?func1 ?func2 WHERE {
    ?func1 kd:uses ?func2 .
}
```

### 示例3：发现核心概念
```sparql
# 查询被多次引用的概念
SELECT ?concept (COUNT(?ref) as ?count) WHERE {
    ?ref kd:implements ?concept .
    ?concept rdf:type kd:Concept .
}
GROUP BY ?concept
ORDER BY DESC(?count)
```

## 6. 优势

1. **语义理解**：不仅理解结构，还理解含义
2. **关系发现**：自动发现知识间的隐含关系
3. **体系构建**：构建完整的知识体系
4. **学习支持**：生成个性化学习路径
5. **质量评估**：评估知识库的完整性和质量
6. **可查询性**：支持复杂的SPARQL查询

## 7. 扩展方向

### 多语言支持
```turtle
kd:hasLanguage rdf:type rdf:Property ;
    rdfs:domain kd:Document ;
    rdfs:range xsd:string ;
    rdfs:comment "文档语言" .

kd:translation rdf:type rdf:Property ;
    rdfs:domain kd:Document ;
    rdfs:range kd:Document ;
    rdfs:comment "翻译版本" .
```

### 版本管理
```turtle
kd:version rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range xsd:string ;
    rdfs:comment "版本号" .

kd:previousVersion rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range kd:Knowledge ;
    rdfs:comment "前一版本" .
```

### 使用追踪
```turtle
kd:usageCount rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range xsd:integer ;
    rdfs:comment "使用次数" .

kd:lastAccessed rdf:type rdf:Property ;
    rdfs:domain kd:Knowledge ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "最后访问时间" .
```