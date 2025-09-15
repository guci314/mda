#!/usr/bin/env python3
"""
RDF知识图谱验证工具
使用rdflib验证生成的Turtle文件的正确性
"""

import sys
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
import json

def validate_rdf_graph(turtle_file: str):
    """验证RDF图谱"""
    print(f"🔍 验证RDF图谱: {turtle_file}")
    print("=" * 60)
    
    # 创建图谱并加载Turtle文件
    g = Graph()
    
    try:
        g.parse(turtle_file, format='turtle')
        print(f"✅ Turtle文件语法正确")
    except Exception as e:
        print(f"❌ Turtle文件解析失败: {e}")
        return False
    
    # 定义命名空间
    CODE = Namespace("http://example.org/code#")
    
    # 1. 基础统计
    print(f"\n📊 图谱规模统计:")
    print(f"   三元组总数: {len(g)}")
    
    # 2. 按类型统计实体
    print(f"\n📈 实体统计:")
    
    # 统计模块
    module_query = """
        PREFIX code: <http://example.org/code#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (COUNT(?module) as ?count)
        WHERE { ?module rdf:type code:Module }
    """
    result = g.query(module_query)
    for row in result:
        print(f"   模块(Module): {row.count}")
    
    # 统计类
    class_query = """
        PREFIX code: <http://example.org/code#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (COUNT(?class) as ?count)
        WHERE { ?class rdf:type code:Class }
    """
    result = g.query(class_query)
    for row in result:
        print(f"   类(Class): {row.count}")
    
    # 统计函数
    function_query = """
        PREFIX code: <http://example.org/code#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (COUNT(?function) as ?count)
        WHERE { ?function rdf:type code:Function }
    """
    result = g.query(function_query)
    for row in result:
        print(f"   函数(Function): {row.count}")
    
    # 统计方法
    method_query = """
        PREFIX code: <http://example.org/code#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (COUNT(?method) as ?count)
        WHERE { ?method rdf:type code:Method }
    """
    result = g.query(method_query)
    for row in result:
        print(f"   方法(Method): {row.count}")
    
    # 3. 关系统计
    print(f"\n🔗 关系统计:")
    
    # 继承关系
    inherit_query = """
        PREFIX code: <http://example.org/code#>
        SELECT (COUNT(*) as ?count)
        WHERE { ?child code:inheritsFrom ?parent }
    """
    result = g.query(inherit_query)
    for row in result:
        print(f"   继承关系(inheritsFrom): {row.count}")
    
    # 调用关系
    calls_query = """
        PREFIX code: <http://example.org/code#>
        SELECT (COUNT(*) as ?count)
        WHERE { ?caller code:calls ?callee }
    """
    result = g.query(calls_query)
    for row in result:
        print(f"   调用关系(calls): {row.count}")
    
    # 导入关系
    import_query = """
        PREFIX code: <http://example.org/code#>
        SELECT (COUNT(*) as ?count)
        WHERE { ?module code:imports ?imported }
    """
    result = g.query(import_query)
    for row in result:
        print(f"   导入关系(imports): {row.count}")
    
    # 4. 数据完整性检查
    print(f"\n✔️ 数据完整性检查:")
    
    # 检查所有类都有名称
    unnamed_class_query = """
        PREFIX code: <http://example.org/code#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?class
        WHERE {
            ?class rdf:type code:Class .
            FILTER NOT EXISTS { ?class code:hasName ?name }
        }
    """
    result = list(g.query(unnamed_class_query))
    if result:
        print(f"   ⚠️ 发现 {len(result)} 个没有名称的类")
    else:
        print(f"   ✅ 所有类都有名称")
    
    # 检查所有函数都属于某个模块
    orphan_function_query = """
        PREFIX code: <http://example.org/code#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?function
        WHERE {
            ?function rdf:type code:Function .
            FILTER NOT EXISTS { ?function code:belongsTo ?module }
        }
    """
    result = list(g.query(orphan_function_query))
    if result:
        print(f"   ⚠️ 发现 {len(result)} 个不属于任何模块的函数")
    else:
        print(f"   ✅ 所有函数都属于某个模块")
    
    # 5. 示例查询
    print(f"\n🔍 示例查询:")
    
    # 查找最复杂的类（方法最多）
    complex_class_query = """
        PREFIX code: <http://example.org/code#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?class ?name (COUNT(?method) as ?method_count)
        WHERE {
            ?class rdf:type code:Class ;
                   code:hasName ?name ;
                   code:defines ?method .
        }
        GROUP BY ?class ?name
        ORDER BY DESC(?method_count)
        LIMIT 5
    """
    print("\n   📌 方法最多的5个类:")
    result = g.query(complex_class_query)
    for row in result:
        print(f"      {row.name}: {row.method_count} 个方法")
    
    # 查找调用最多的函数
    popular_function_query = """
        PREFIX code: <http://example.org/code#>
        SELECT ?callee (COUNT(?caller) as ?call_count)
        WHERE {
            ?caller code:calls ?callee .
        }
        GROUP BY ?callee
        ORDER BY DESC(?call_count)
        LIMIT 5
    """
    print("\n   📌 被调用最多的5个函数:")
    result = g.query(popular_function_query)
    for row in result:
        callee = str(row.callee).split('#')[-1]
        print(f"      {callee}: 被调用 {row.call_count} 次")
    
    # 查找导入最多的模块
    import_stats_query = """
        PREFIX code: <http://example.org/code#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?module ?name (COUNT(?import) as ?import_count)
        WHERE {
            ?module rdf:type code:Module ;
                    code:hasName ?name ;
                    code:imports ?import .
        }
        GROUP BY ?module ?name
        ORDER BY DESC(?import_count)
        LIMIT 5
    """
    print("\n   📌 导入最多的5个模块:")
    result = g.query(import_stats_query)
    for row in result:
        print(f"      {row.name}: 导入 {row.import_count} 个模块")
    
    # 6. 检查循环继承
    print(f"\n🔄 循环依赖检查:")
    
    # 简单的循环继承检查（2层）
    cycle_query = """
        PREFIX code: <http://example.org/code#>
        SELECT ?class1 ?class2
        WHERE {
            ?class1 code:inheritsFrom ?class2 .
            ?class2 code:inheritsFrom ?class1 .
        }
    """
    result = list(g.query(cycle_query))
    if result:
        print(f"   ⚠️ 发现循环继承关系:")
        for row in result:
            print(f"      {row.class1} <-> {row.class2}")
    else:
        print(f"   ✅ 没有发现循环继承")
    
    # 7. 导出统计报告
    print(f"\n📄 生成验证报告...")
    
    report = {
        "file": turtle_file,
        "valid": True,
        "statistics": {
            "total_triples": len(g),
            "modules": get_count(g, "Module"),
            "classes": get_count(g, "Class"),
            "functions": get_count(g, "Function"),
            "methods": get_count(g, "Method"),
            "inheritance_relations": get_relation_count(g, "inheritsFrom"),
            "call_relations": get_relation_count(g, "calls"),
            "import_relations": get_relation_count(g, "imports")
        }
    }
    
    report_file = turtle_file.replace('.ttl', '_validation_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ 验证报告已保存到: {report_file}")
    
    print("\n" + "=" * 60)
    print("✅ RDF图谱验证完成！")
    return True

def get_count(graph, entity_type):
    """获取实体数量"""
    query = f"""
        PREFIX code: <http://example.org/code#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (COUNT(?entity) as ?count)
        WHERE {{ ?entity rdf:type code:{entity_type} }}
    """
    result = graph.query(query)
    for row in result:
        return int(row.count)
    return 0

def get_relation_count(graph, relation):
    """获取关系数量"""
    query = f"""
        PREFIX code: <http://example.org/code#>
        SELECT (COUNT(*) as ?count)
        WHERE {{ ?s code:{relation} ?o }}
    """
    result = graph.query(query)
    for row in result:
        return int(row.count)
    return 0

def main():
    if len(sys.argv) != 2:
        print("用法: python validate_rdf.py <turtle文件.ttl>")
        sys.exit(1)
    
    turtle_file = sys.argv[1]
    
    # 检查rdflib是否安装
    try:
        import rdflib
    except ImportError:
        print("错误: 需要安装rdflib")
        print("请运行: pip install rdflib")
        sys.exit(1)
    
    validate_rdf_graph(turtle_file)

if __name__ == "__main__":
    main()