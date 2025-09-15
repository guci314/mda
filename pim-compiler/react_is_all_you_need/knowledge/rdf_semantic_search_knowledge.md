# RDF图谱语义搜索指南

## 1. 核心理念
利用已生成的RDF知识图谱进行语义搜索，通过SPARQL查询实现结构化的代码搜索。

## 2. 前置准备

### 函数：加载RDF图谱(ttl_file)
"""加载并准备RDF图谱用于搜索"""
步骤：
1. 使用Python导入rdflib库
2. 创建Graph对象
3. 解析Turtle文件：`g.parse(ttl_file, format="turtle")`
4. 定义命名空间：`kg = Namespace("http://example.org/knowledge#")`
5. 返回准备好的图谱对象
返回：(图谱对象, 命名空间)

## 3. 基础搜索函数

### 函数：搜索包含关键词的代码(keyword, ttl_file)
"""搜索所有包含关键词的代码实体"""
步骤：
1. 调用 加载RDF图谱(ttl_file)
2. 构建SPARQL查询：
   ```sparql
   SELECT ?entity ?name ?docstring ?type
   WHERE {
     ?entity kg:hasName ?name .
     ?entity rdf:type ?type .
     OPTIONAL { 
       ?entity kg:hasModuleDocstring|kg:hasClassDocstring|kg:hasMethodDocstring|kg:hasDescription ?docstring 
     }
     FILTER(
       CONTAINS(LCASE(STR(?name)), LCASE("keyword")) ||
       CONTAINS(LCASE(STR(?docstring)), LCASE("keyword"))
     )
   }
   ```
3. 执行查询：`results = graph.query(sparql_query)`
4. 格式化结果，包含实体名、类型、docstring
5. 按相关度排序（名称匹配优先于docstring匹配）
返回：搜索结果列表

### 函数：查找相关方法(concept, ttl_file)
"""查找与概念相关的所有方法"""
步骤：
1. 调用 加载RDF图谱(ttl_file)
2. 构建SPARQL查询：
   ```sparql
   SELECT ?method ?name ?docstring ?class
   WHERE {
     ?method rdf:type kg:Method .
     ?method kg:hasName ?name .
     OPTIONAL { ?method kg:hasMethodDocstring ?docstring }
     OPTIONAL { ?method kg:belongsTo ?class }
     FILTER(
       CONTAINS(LCASE(STR(?docstring)), LCASE("concept")) ||
       CONTAINS(LCASE(STR(?name)), LCASE("concept"))
     )
   }
   ORDER BY ?class ?name
   ```
3. 执行查询并收集结果
4. 按类分组整理方法
返回：方法列表（按类分组）

### 函数：查找类的继承链(class_name, ttl_file)
"""查找类的完整继承关系"""
步骤：
1. 调用 加载RDF图谱(ttl_file)
2. 向上查找父类：
   ```sparql
   SELECT ?parent WHERE {
     kg:class_name kg:extends|kg:inheritsFrom ?parent .
   }
   ```
3. 递归查找所有祖先类
4. 向下查找子类：
   ```sparql
   SELECT ?child WHERE {
     ?child kg:extends|kg:inheritsFrom kg:class_name .
   }
   ```
5. 构建继承树结构
返回：继承关系树

### 函数：查找模块依赖(module_name, ttl_file)
"""查找模块的导入依赖关系"""
步骤：
1. 调用 加载RDF图谱(ttl_file)
2. 查找模块导入的依赖：
   ```sparql
   SELECT ?import WHERE {
     kg:module_name kg:imports ?import .
   }
   ```
3. 查找依赖此模块的其他模块：
   ```sparql
   SELECT ?module WHERE {
     ?module kg:imports kg:module_name .
   }
   ```
4. 构建依赖关系图
返回：依赖关系（导入的、被导入的）

### 函数：查找使用特定工具的代码(tool_name, ttl_file)
"""查找所有使用特定工具或函数的代码"""
步骤：
1. 调用 加载RDF图谱(ttl_file)
2. 构建查询：
   ```sparql
   SELECT ?entity ?name WHERE {
     ?entity kg:uses|kg:calls kg:tool_name .
     ?entity kg:hasName ?name .
   }
   ```
3. 执行查询
4. 扩展搜索到间接调用（通过其他方法）
返回：使用该工具的实体列表

## 4. 高级搜索函数

### 函数：语义概念搜索(concept, ttl_file)
"""基于概念进行语义搜索"""
步骤：
1. 调用 加载RDF图谱(ttl_file)
2. 首先查找概念实体：
   ```sparql
   SELECT ?concept_entity WHERE {
     ?concept_entity rdf:type kg:Concept .
     ?concept_entity kg:hasName ?name .
     FILTER(CONTAINS(LCASE(STR(?name)), LCASE("concept")))
   }
   ```
3. 查找实现或使用该概念的代码：
   ```sparql
   SELECT ?entity ?relation WHERE {
     ?entity kg:implements|kg:uses|kg:relatedTo ?concept_entity .
   }
   ```
4. 扩展到相关概念和代码
返回：概念相关的所有代码实体

### 函数：查找代码模式(pattern_description, ttl_file)
"""查找符合特定模式的代码结构"""
步骤：
1. 调用 加载RDF图谱(ttl_file)
2. 理解模式描述，识别关键特征：
   - 如果包含"继承"：查找继承关系
   - 如果包含"实现"：查找接口实现
   - 如果包含"调用"：查找调用关系
3. 构建复合SPARQL查询
4. 执行查询并过滤结果
返回：符合模式的代码结构

### 函数：查找相似功能代码(reference_function, ttl_file)
"""查找功能相似的代码"""
步骤：
1. 调用 加载RDF图谱(ttl_file)
2. 获取参考函数的特征：
   ```sparql
   SELECT ?docstring ?params ?returns WHERE {
     kg:reference_function kg:hasMethodDocstring ?docstring .
     OPTIONAL { kg:reference_function kg:hasParameters ?params }
     OPTIONAL { kg:reference_function kg:returns ?returns }
   }
   ```
3. 提取关键词和功能描述
4. 搜索相似docstring的其他函数：
   - 分词并提取关键动词
   - 匹配相似的描述模式
5. 按相似度评分排序
返回：相似函数列表（带相似度分数）

## 5. 实用搜索组合

### 函数：智能代码搜索(query, ttl_file)
"""根据查询自动选择最佳搜索策略"""
步骤：
1. 分析查询意图：
   - 包含"继承"、"extends"：调用 查找类的继承链
   - 包含"导入"、"import"：调用 查找模块依赖
   - 包含"使用"、"调用"：调用 查找使用特定工具的代码
   - 包含"相似"、"类似"：调用 查找相似功能代码
   - 包含具体类名/方法名：直接查询
   - 其他：调用 搜索包含关键词的代码
2. 执行相应的搜索函数
3. 合并和去重结果
4. 按相关度排序
返回：搜索结果

### 函数：生成代码理解报告(entity_name, ttl_file)
"""生成实体的完整理解报告"""
步骤：
1. 调用 加载RDF图谱(ttl_file)
2. 查询实体的基本信息：
   ```sparql
   SELECT ?type ?name ?docstring ?path WHERE {
     kg:entity_name rdf:type ?type ;
                    kg:hasName ?name .
     OPTIONAL { kg:entity_name kg:hasPath ?path }
     OPTIONAL { kg:entity_name kg:hasModuleDocstring|kg:hasClassDocstring|kg:hasMethodDocstring ?docstring }
   }
   ```
3. 查询实体的关系：
   - 继承关系：`kg:extends`、`kg:inheritsFrom`
   - 包含关系：`kg:defines`、`kg:hasMethod`
   - 使用关系：`kg:uses`、`kg:imports`
4. 查询相关概念
5. 生成结构化报告
返回：Markdown格式的理解报告

## 6. 搜索结果处理

### 函数：格式化搜索结果(results, output_format)
"""格式化SPARQL查询结果"""
步骤：
1. 根据output_format选择格式：
   - "markdown"：生成Markdown表格
   - "json"：生成JSON对象
   - "text"：生成文本列表
2. 提取结果中的关键信息
3. 添加文件路径链接（如果有）
4. 高亮匹配的关键词
返回：格式化的结果

### 函数：排序搜索结果(results, criteria)
"""按指定标准排序搜索结果"""
步骤：
1. 根据criteria确定排序规则：
   - "relevance"：相关度（名称匹配>docstring匹配）
   - "type"：按实体类型（Module>Class>Method）
   - "name"：按名称字母顺序
2. 计算每个结果的排序分数
3. 执行排序
返回：排序后的结果

## 7. 批量搜索

### 函数：批量搜索关键词(keywords_list, ttl_file)
"""批量搜索多个关键词"""
步骤：
1. 对每个关键词：
   - 调用 搜索包含关键词的代码(keyword, ttl_file)
2. 合并所有结果
3. 统计每个实体被匹配的次数
4. 按匹配次数和相关度综合排序
返回：综合搜索结果

## 8. 使用示例

```python
# 示例1：查找所有关于压缩的代码
调用 搜索包含关键词的代码("compact", "/tmp/core_knowledge_graph.ttl")

# 示例2：查找ReactAgentMinimal的继承关系
调用 查找类的继承链("ReactAgentMinimal", "/tmp/core_knowledge_graph.ttl")

# 示例3：查找所有工具类
调用 查找代码模式("继承自Function的工具类", "/tmp/core_knowledge_graph.ttl")

# 示例4：智能搜索
调用 智能代码搜索("如何使用compact memory", "/tmp/core_knowledge_graph.ttl")

# 示例5：生成理解报告
调用 生成代码理解报告("ReactAgentMinimal", "/tmp/core_knowledge_graph.ttl")
```

## 9. 性能优化建议

1. **缓存查询结果**：对频繁查询的结果进行缓存
2. **索引优化**：为常用属性建立索引
3. **查询优化**：使用LIMIT限制结果数量
4. **并行查询**：对独立的查询并行执行
5. **增量更新**：只对变化的部分更新图谱

## 10. 调试和验证

### 函数：验证搜索查询(sparql_query, ttl_file)
"""验证SPARQL查询的正确性"""
步骤：
1. 调用 加载RDF图谱(ttl_file)
2. 尝试执行查询
3. 如果失败，分析错误原因：
   - 语法错误
   - 命名空间问题
   - 属性不存在
4. 提供修复建议
返回：验证结果和建议