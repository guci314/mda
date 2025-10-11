#!/usr/bin/env python3
"""
目录知识图谱转换实现
基于cnSchema将目录结构转换为知识图谱
"""

import os
import json
import datetime
from pathlib import Path


def directory_to_knowledge_graph(directory_path, output_name="directory_knowledge_graph", 
                                include_content=False, max_depth=3, 
                                file_types=["md", "py", "json", "txt", "yaml", "yml"]):
    """
    将目录结构转换为知识图谱
    
    参数:
    - directory_path: 要分析的目录路径
    - output_name: 输出文件的基础名称
    - include_content: 是否包含文件内容摘要
    - max_depth: 最大目录深度
    - file_types: 要处理的文件类型列表
    
    返回:
    - 包含生成文件路径的字典
    """
    
    # 步骤1: 验证目录存在性
    if not os.path.exists(directory_path):
        raise ValueError(f"目录不存在: {directory_path}")
    
    if not os.path.isdir(directory_path):
        raise ValueError(f"路径不是目录: {directory_path}")
    
    # 获取目录基本信息
    dir_info = {
        "path": directory_path,
        "name": os.path.basename(directory_path),
        "size": 0,
        "file_count": 0,
        "dir_count": 0
    }
    
    # 步骤2: 分析目录结构
    file_entities = []
    dir_entities = []
    
    def analyze_directory(current_path, current_depth=0):
        if current_depth > max_depth:
            return
            
        try:
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                
                if os.path.isdir(item_path):
                    # 目录实体
                    dir_entity = create_directory_entity(item_path, current_path)
                    dir_entities.append(dir_entity)
                    analyze_directory(item_path, current_depth + 1)
                    
                elif os.path.isfile(item_path):
                    # 文件实体
                    file_ext = item.split('.')[-1].lower() if '.' in item else ''
                    if file_ext in file_types:
                        file_entity = create_file_entity(item_path, current_path, include_content)
                        file_entities.append(file_entity)
        except PermissionError:
            print(f"警告: 无权限访问目录: {current_path}")
    
    analyze_directory(directory_path)
    
    # 步骤3: 构建知识图谱
    knowledge_graph = build_knowledge_graph(dir_info, dir_entities, file_entities)
    
    # 步骤4: 生成输出文件
    output_files = generate_output_files(knowledge_graph, output_name)
    
    # 步骤5: 验证结果
    validate_results(output_files)
    
    return output_files


def create_directory_entity(dir_path, parent_path):
    """创建目录实体"""
    stat = os.stat(dir_path)
    dir_name = os.path.basename(dir_path)
    
    return {
        "@id": f"dir:{dir_name}",
        "@type": "dir:Directory",
        "rdfs:label": dir_name,
        "file:hasCreationTime": {
            "@value": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "@type": "xsd:dateTime"
        },
        "file:hasModificationTime": {
            "@value": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "@type": "xsd:dateTime"
        },
        "parent": parent_path
    }


def create_file_entity(file_path, parent_path, include_content):
    """创建文件实体"""
    stat = os.stat(file_path)
    file_name = os.path.basename(file_path)
    file_ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
    
    entity = {
        "@id": f"file:{file_name}",
        "@type": "file:File",
        "rdfs:label": file_name,
        "file:hasType": f"file:FileType_{file_ext.upper()}",
        "file:hasSize": {
            "@value": stat.st_size,
            "@type": "xsd:integer"
        },
        "file:hasModificationTime": {
            "@value": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "@type": "xsd:dateTime"
        },
        "parent": parent_path
    }
    
    if include_content:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()[:1000]  # 限制内容长度
                entity["file:hasContent"] = {
                    "@type": "file:TextContent",
                    "rdfs:value": content
                }
        except Exception as e:
            print(f"警告: 无法读取文件内容 {file_path}: {e}")
    
    return entity


def build_knowledge_graph(dir_info, dir_entities, file_entities):
    """构建完整的知识图谱"""
    
    # 基础模板
    template = {
        "@context": {
            "cns": "http://cnschema.org/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "dir": "http://example.org/directory#",
            "file": "http://example.org/file#"
        },
        "@graph": [
            # 模式定义
            {
                "@id": "dir:Directory",
                "@type": "cns:DigitalDocument",
                "rdfs:label": "目录",
                "rdfs:comment": "文件系统中的目录"
            },
            {
                "@id": "file:File",
                "@type": "cns:DigitalDocument",
                "rdfs:label": "文件",
                "rdfs:comment": "文件系统中的文件"
            },
            {
                "@id": "dir:contains",
                "@type": "rdf:Property",
                "rdfs:label": "包含",
                "rdfs:comment": "目录包含文件或子目录",
                "rdfs:domain": "dir:Directory",
                "rdfs:range": ["file:File", "dir:Directory"]
            }
        ]
    }
    
    # 添加文件类型定义
    file_types = set()
    for entity in file_entities:
        file_type = entity.get("file:hasType")
        if file_type:
            file_types.add(file_type)
    
    for file_type in file_types:
        type_name = file_type.replace("file:FileType_", "")
        template["@graph"].append({
            "@id": file_type,
            "@type": "rdfs:Class",
            "rdfs:label": f"{type_name}文件",
            "rdfs:comment": f"{type_name}格式的文件"
        })
    
    # 添加根目录
    root_dir = {
        "@id": f"dir:{dir_info['name']}",
        "@type": "dir:Directory",
        "rdfs:label": dir_info['name'],
        "file:hasCreationTime": {
            "@value": datetime.datetime.now().isoformat(),
            "@type": "xsd:dateTime"
        },
        "dir:contains": []
    }
    template["@graph"].append(root_dir)
    
    # 添加所有目录和文件
    for entity in dir_entities + file_entities:
        template["@graph"].append(entity)
        
        # 建立包含关系
        parent_id = f"dir:{os.path.basename(entity['parent'])}"
        if parent_id == f"dir:{dir_info['name']}":
            root_dir["dir:contains"].append({"@id": entity["@id"]})
    
    return template


def generate_output_files(knowledge_graph, output_name):
    """生成输出文件"""
    
    # JSON-LD文件
    jsonld_path = f"{output_name}.jsonld"
    with open(jsonld_path, 'w', encoding='utf-8') as f:
        json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)
    
    # 摘要文件
    summary_path = f"{output_name}_summary.md"
    create_summary_file(knowledge_graph, summary_path)
    
    # 统计文件
    stats_path = f"{output_name}_stats.json"
    create_stats_file(knowledge_graph, stats_path)
    
    return {
        "jsonld": jsonld_path,
        "summary": summary_path,
        "stats": stats_path
    }


def create_summary_file(knowledge_graph, summary_path):
    """创建可视化摘要"""
    # 统计信息
    dir_count = len([e for e in knowledge_graph["@graph"] if e.get("@type") == "dir:Directory"])
    file_count = len([e for e in knowledge_graph["@graph"] if e.get("@type") == "file:File"])
    
    summary_content = f"""# 目录知识图谱摘要

## 统计信息
- 目录数量: {dir_count}
- 文件数量: {file_count}
- 总实体数量: {len(knowledge_graph['@graph'])}

## 文件类型分布
"""
    
    # 文件类型统计
    file_types = {}
    for entity in knowledge_graph["@graph"]:
        if entity.get("@type") == "file:File":
            file_type = entity.get("file:hasType", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
    
    for file_type, count in file_types.items():
        type_name = file_type.replace("file:FileType_", "")
        summary_content += f"- {type_name}: {count}个文件\n"
    
    summary_content += f"\n## 生成时间\n- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)


def create_stats_file(knowledge_graph, stats_path):
    """创建统计信息文件"""
    stats = {
        "total_entities": len(knowledge_graph["@graph"]),
        "directories": len([e for e in knowledge_graph["@graph"] if e.get("@type") == "dir:Directory"]),
        "files": len([e for e in knowledge_graph["@graph"] if e.get("@type") == "file:File"]),
        "file_types": {},
        "generated_at": datetime.datetime.now().isoformat()
    }
    
    # 文件类型统计
    for entity in knowledge_graph["@graph"]:
        if entity.get("@type") == "file:File":
            file_type = entity.get("file:hasType", "unknown")
            stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1
    
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def validate_results(output_files):
    """验证生成结果"""
    for file_type, file_path in output_files.items():
        if not os.path.exists(file_path):
            raise RuntimeError(f"输出文件不存在: {file_path}")
        
        if os.path.getsize(file_path) == 0:
            raise RuntimeError(f"输出文件为空: {file_path}")


if __name__ == "__main__":
    # 测试代码
    try:
        result = directory_to_knowledge_graph(
            directory_path="./test_directory",
            output_name="test_knowledge_graph",
            include_content=True,
            max_depth=3
        )
        print("✅ 知识图谱生成成功!")
        print("生成的文件:")
        for file_type, file_path in result.items():
            print(f"  - {file_type}: {file_path}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")