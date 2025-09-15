# 代码转RDF知识图谱指南

## 核心本体定义

```turtle
@prefix code: <http://example.org/code#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# 基础类定义
code:Module rdf:type rdfs:Class .
code:Class rdf:type rdfs:Class .
code:Function rdf:type rdfs:Class .
code:Method rdf:type rdfs:Class ;
    rdfs:subClassOf code:Function .
code:Parameter rdf:type rdfs:Class .
code:Import rdf:type rdfs:Class .

# 基础属性定义
code:hasName rdf:type rdf:Property .
code:hasPath rdf:type rdf:Property .
code:hasLineNumber rdf:type rdf:Property .
code:hasDocstring rdf:type rdf:Property .
code:hasParameter rdf:type rdf:Property .
code:hasReturnType rdf:type rdf:Property .

# 关系定义
code:defines rdf:type rdf:Property .
code:imports rdf:type rdf:Property .
code:calls rdf:type rdf:Property .
code:inheritsFrom rdf:type rdf:Property .
code:belongsTo rdf:type rdf:Property .
code:uses rdf:type rdf:Property .
```

## 转换函数定义

### 函数：扫描Python代码库(directory_path)
"""扫描指定目录下的所有Python文件"""
步骤：
1. 递归遍历directory_path下所有.py文件
2. 对每个文件：
   - 记录文件路径
   - 调用 解析Python文件(file_path)
3. 收集所有解析结果
返回：文件解析结果列表

### 函数：解析Python文件(file_path)
"""解析单个Python文件的AST结构"""
步骤：
1. 读取文件内容
2. 使用ast.parse()解析为AST树
3. 调用 提取模块信息(ast_tree, file_path)
4. 调用 提取导入信息(ast_tree)
5. 调用 提取类定义(ast_tree)
6. 调用 提取函数定义(ast_tree)
返回：文件的结构化信息

### 函数：提取模块信息(ast_tree, file_path)
"""从AST提取模块级信息"""
步骤：
1. 获取模块名（从file_path提取）
2. 获取模块文档字符串（如果存在）
3. 创建模块实体
返回：模块信息字典

### 函数：提取导入信息(ast_tree)
"""提取所有import语句"""
步骤：
1. 遍历AST找到所有Import和ImportFrom节点
2. 对每个导入：
   - 记录被导入的模块名
   - 记录导入的具体项（如果有）
   - 记录别名（如果有）
返回：导入信息列表

### 函数：提取类定义(ast_tree)
"""提取所有类定义"""
步骤：
1. 遍历AST找到所有ClassDef节点
2. 对每个类：
   - 获取类名
   - 获取基类列表
   - 获取类文档字符串
   - 获取行号
   - 调用 提取方法定义(class_node)
返回：类定义列表

### 函数：提取函数定义(ast_tree)
"""提取模块级函数定义"""
步骤：
1. 遍历AST找到所有FunctionDef节点（顶层）
2. 对每个函数：
   - 获取函数名
   - 获取参数列表
   - 获取返回类型注解（如果有）
   - 获取文档字符串
   - 获取行号
   - 调用 分析函数调用(function_node)
返回：函数定义列表

### 函数：提取方法定义(class_node)
"""提取类中的方法定义"""
步骤：
1. 遍历类体中的所有FunctionDef节点
2. 对每个方法：
   - 获取方法名
   - 获取参数列表（排除self）
   - 识别特殊方法（__init__, __str__等）
   - 获取装饰器列表
返回：方法定义列表

### 函数：分析函数调用(function_node)
"""分析函数体中的函数调用"""
步骤：
1. 遍历函数体中的所有Call节点
2. 对每个调用：
   - 识别被调用的函数/方法名
   - 记录调用位置（行号）
   - 尝试解析调用目标（本地/导入/内置）
返回：函数调用列表

### 函数：生成RDF三元组(parsed_data)
"""将解析的数据转换为RDF三元组"""
步骤：
1. 初始化三元组列表
2. 对每个模块：
   - 调用 生成模块三元组(module_data)
3. 对每个类：
   - 调用 生成类三元组(class_data)
4. 对每个函数：
   - 调用 生成函数三元组(function_data)
5. 对每个导入：
   - 调用 生成导入三元组(import_data)
6. 对每个调用关系：
   - 调用 生成调用三元组(call_data)
返回：完整的三元组列表

### 函数：生成模块三元组(module_data)
"""生成模块相关的RDF三元组"""
步骤：
1. 创建模块URI: code:{module_name}
2. 生成基础三元组：
   - {module_uri} rdf:type code:Module
   - {module_uri} code:hasName "{module_name}"
   - {module_uri} code:hasPath "{file_path}"
3. 如果有文档字符串：
   - {module_uri} code:hasDocstring "{docstring}"
返回：模块三元组列表

### 函数：生成类三元组(class_data)
"""生成类相关的RDF三元组"""
步骤：
1. 创建类URI: code:{module_name}.{class_name}
2. 生成基础三元组：
   - {class_uri} rdf:type code:Class
   - {class_uri} code:hasName "{class_name}"
   - {class_uri} code:belongsTo {module_uri}
   - {class_uri} code:hasLineNumber {line_number}
3. 对每个基类：
   - {class_uri} code:inheritsFrom code:{base_class}
4. 对每个方法：
   - {class_uri} code:defines {method_uri}
返回：类三元组列表

### 函数：生成函数三元组(function_data)
"""生成函数相关的RDF三元组"""
步骤：
1. 创建函数URI: code:{module_name}.{function_name}
2. 生成基础三元组：
   - {function_uri} rdf:type code:Function
   - {function_uri} code:hasName "{function_name}"
   - {function_uri} code:belongsTo {module_uri}
   - {function_uri} code:hasLineNumber {line_number}
3. 对每个参数：
   - {function_uri} code:hasParameter "{param_name}"
4. 如果有返回类型：
   - {function_uri} code:hasReturnType "{return_type}"
返回：函数三元组列表

### 函数：生成导入三元组(import_data)
"""生成导入关系的RDF三元组"""
步骤：
1. 创建导入URI: code:{module_name}_import_{index}
2. 生成三元组：
   - {import_uri} rdf:type code:Import
   - {module_uri} code:imports "{imported_module}"
3. 如果有具体导入项：
   - {import_uri} code:importsItem "{item_name}"
返回：导入三元组列表

### 函数：生成调用三元组(call_data)
"""生成函数调用关系的RDF三元组"""
步骤：
1. 对每个调用关系：
   - {caller_uri} code:calls {callee_uri}
   - 创建调用实例URI（如果需要记录调用详情）
2. 如果能确定被调用函数的位置：
   - 使用完整URI
3. 否则：
   - 使用函数名作为标识
返回：调用关系三元组列表

### 函数：输出Turtle格式(triplets, output_file)
"""将三元组列表输出为Turtle格式文件"""
步骤：
1. 写入前缀声明
2. 按照主语分组三元组
3. 对每个主语组：
   - 使用简洁的Turtle语法输出
   - 相同主语的属性用分号分隔
   - 相同属性的多个值用逗号分隔
4. 保存到output_file
返回：输出文件路径

## 执行流程

### 主函数：转换代码为RDF(source_dir, output_file)
"""完整的转换流程"""
步骤：
1. 调用 扫描Python代码库(source_dir)
2. 调用 生成RDF三元组(parsed_data)
3. 调用 输出Turtle格式(triplets, output_file)
4. 打印转换统计信息
返回：转换成功状态

## 示例输出

```turtle
@prefix code: <http://example.org/code#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

code:react_agent_minimal rdf:type code:Module ;
    code:hasName "react_agent_minimal" ;
    code:hasPath "/core/react_agent_minimal.py" ;
    code:hasDocstring "极简React Agent实现" .

code:react_agent_minimal.ReactAgentMinimal rdf:type code:Class ;
    code:hasName "ReactAgentMinimal" ;
    code:belongsTo code:react_agent_minimal ;
    code:hasLineNumber 45 ;
    code:inheritsFrom code:Function ;
    code:defines code:react_agent_minimal.ReactAgentMinimal.__init__ ,
                code:react_agent_minimal.ReactAgentMinimal.execute .

code:react_agent_minimal.ReactAgentMinimal.__init__ rdf:type code:Method ;
    code:hasName "__init__" ;
    code:hasParameter "work_dir" ,
                     "name" ,
                     "model" ;
    code:hasLineNumber 92 .

code:react_agent_minimal.ReactAgentMinimal.execute rdf:type code:Method ;
    code:hasName "execute" ;
    code:hasParameter "task" ;
    code:hasReturnType "str" ;
    code:hasLineNumber 280 ;
    code:calls code:react_agent_minimal.ReactAgentMinimal._think ,
              code:react_agent_minimal.ReactAgentMinimal._parse_response .
```

## 验证要点

### 函数：验证RDF图谱(turtle_file)
"""使用rdflib验证生成的RDF图谱"""
步骤：
1. 加载Turtle文件到图谱
2. 检查语法正确性
3. 执行SPARQL查询验证：
   - 所有类都有名称
   - 所有函数都属于某个模块
   - 继承关系没有循环
4. 统计图谱规模：
   - 三元组总数
   - 实体数量（按类型）
   - 关系数量（按类型）
返回：验证报告