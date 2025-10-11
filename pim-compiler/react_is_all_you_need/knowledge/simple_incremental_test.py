#!/usr/bin/env python3
"""
简化版增量处理测试
"""

import os
import json
import datetime
import time
from typing import List, Dict, Any


def simple_incremental_processor(directory_path: str, output_name: str = "simple_knowledge_graph"):
    """简化版增量处理器"""
    
    print(f"开始处理目录: {directory_path}")
    
    # 基础知识图谱
    knowledge_graph = {
        "@context": {
            "cns": "http://cnschema.org/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "dir": "http://example.org/directory#",
            "file": "http://example.org/file#"
        },
        "@graph": [
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
                "@id": f"dir:{os.path.basename(directory_path)}",
                "@type": "dir:Directory",
                "rdfs:label": os.path.basename(directory_path),
                "file:hasCreationTime": {
                    "@value": datetime.datetime.now().isoformat(),
                    "@type": "xsd:dateTime"
                },
                "dir:contains": []
            }
        ]
    }
    
    # 发现文件
    all_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
    
    print(f"发现 {len(all_files)} 个文件")
    
    # 分批处理
    batch_size = 20
    total_batches = (len(all_files) + batch_size - 1) // batch_size
    processed_count = 0
    
    for batch_index in range(total_batches):
        start_idx = batch_index * batch_size
        end_idx = min(start_idx + batch_size, len(all_files))
        file_batch = all_files[start_idx:end_idx]
        
        print(f"处理批次 {batch_index + 1}/{total_batches} ({len(file_batch)} 个文件)")
        
        batch_entities = []
        for file_path in file_batch:
            try:
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
                    "file:path": file_path
                }
                
                batch_entities.append(entity)
                processed_count += 1
                
            except Exception as e:
                print(f"处理文件失败 {file_path}: {e}")
        
        # 添加到知识图谱
        knowledge_graph["@graph"].extend(batch_entities)
        
        # 定期保存
        if (batch_index + 1) % 5 == 0 or (batch_index + 1) == total_batches:
            temp_output = f"{output_name}_temp.jsonld"
            with open(temp_output, 'w', encoding='utf-8') as f:
                json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)
            print(f"已保存临时结果 ({processed_count}/{len(all_files)})")
    
    # 最终保存
    final_output = f"{output_name}.jsonld"
    with open(final_output, 'w', encoding='utf-8') as f:
        json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)
    
    # 创建摘要
    summary_path = f"{output_name}_summary.md"
    file_count = len([e for e in knowledge_graph["@graph"] if e.get("@type") == "file:File"])
    
    summary_content = f"""# 目录知识图谱摘要

## 统计信息
- 总文件数量: {len(all_files)}
- 成功处理: {processed_count}
- 知识图谱实体: {len(knowledge_graph['@graph'])}

## 文件类型分布
"""
    
    file_types = {}
    for entity in knowledge_graph["@graph"]:
        if entity.get("@type") == "file:File":
            file_type = entity.get("file:hasType", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
    
    for file_type, count in file_types.items():
        type_name = file_type.replace("file:FileType_", "")
        summary_content += f"- {type_name}: {count}个文件\n"
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    # 清理临时文件
    try:
        os.remove(f"{output_name}_temp.jsonld")
    except:
        pass
    
    print(f"✅ 处理完成!")
    print(f"最终文件: {final_output}")
    print(f"摘要文件: {summary_path}")
    
    return {
        "jsonld": final_output,
        "summary": summary_path
    }


if __name__ == "__main__":
    result = simple_incremental_processor(
        directory_path="large_test_directory",
        output_name="simple_test_result"
    )
    print("生成的文件:", result)