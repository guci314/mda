内存使用: {processor.resource_monitor.get_memory_usage_mb():.1f}MB")
    
    return output_files


# 以下函数与之前的实现相同，为了完整性包含在这里
def create_base_knowledge_graph(directory_path: str) -> Dict[str, Any]:
    """创建基础知识图谱结构"""
    base_graph = {
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
                "@id": "dir:contains",
                "@type": "rdf:Property",
                "rdfs:label": "包含",
                "rdfs:comment": "目录包含文件或子目录",
                "rdfs:domain": "dir:Directory",
                "rdfs:range": ["file:File", "dir:Directory"]
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
    return base_graph


def save_knowledge_graph(knowledge_graph: Dict[str, Any], output_name: str):
    """保存知识图谱"""
    jsonld_path = f"{output_name}.jsonld"
    with open(jsonld_path, 'w', encoding='utf-8') as f:
        json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)


def generate_final_output(knowledge_graph: Dict[str, Any], processor, output_name: str) -> Dict[str, str]:
    """生成最终输出文件"""
    final_jsonld_path = f"{output_name}.jsonld"
    save_knowledge_graph(knowledge_graph, output_name)
    
    summary_path = f"{output_name}_summary.md"
    create_summary_file(knowledge_graph, processor, summary_path)
    
    stats_path = f"{output_name}_stats.json"
    create_stats_file(knowledge_graph, processor, stats_path)
    
    return {
        "jsonld": final_jsonld_path,
        "summary": summary_path,
        "stats": stats_path,
        "errors": processor.errors_file
    }


def create_summary_file(knowledge_graph: Dict[str, Any], processor, summary_path: str):
    """创建可视化摘要"""
    file_count = len([e for e in knowledge_graph["@graph"] if e.get("@type") == "file:File"])
    
    summary_content = f"""# 目录知识图谱摘要（优化增量处理）

## 处理统计
- 总文件数量: {processor.progress['total_files']}
- 成功处理: {processor.progress['processed_files']}
- 错误数量: {len(processor.errors)}
- 知识图谱实体: {len(knowledge_graph['@graph'])}

## 处理信息
- 开始时间: {processor.progress['start_time']}
- 完成时间: {datetime.datetime.now().isoformat()}
- 最后处理的文件: {processor.progress.get('last_processed', 'N/A')}
- 最终批次大小: {processor.progress.get('adaptive_batch_size', 'N/A')}

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
    
    if processor.errors:
        summary_content += f"\n## 错误摘要\n"
        error_types = {}
        for error in processor.errors:
            error_msg = error.get("error", "unknown")
            error_types[error_msg] = error_types.get(error_msg, 0) + 1
        
        for error_type, count in error_types.items():
            summary_content += f"- {error_type}: {count}次\n"
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)


def create_stats_file(knowledge_graph: Dict[str, Any], processor, stats_path: str):
    """创建统计信息文件"""
    stats = {
        "processing": processor.progress,
        "knowledge_graph": {
            "total_entities": len(knowledge_graph["@graph"]),
            "files": len([e for e in knowledge_graph["@graph"] if e.get("@type") == "file:File"]),
            "file_types": {},
        },
        "errors": {
            "total": len(processor.errors),
            "details": processor.errors
        },
        "generated_at": datetime.datetime.now().isoformat()
    }
    
    for entity in knowledge_graph["@graph"]:
        if entity.get("@type") == "file:File":
            file_type = entity.get("file:hasType", "unknown")
            stats["knowledge_graph"]["file_types"][file_type] = stats["knowledge_graph"]["file_types"].get(file_type, 0) + 1
    
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def cleanup_temporary_files(output_name: str):
    """清理临时文件"""
    temp_files = [
        f"{output_name}_progress.json",
        f"{output_name}_incremental.jsonld"
    ]
    
    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"警告: 无法删除临时文件 {temp_file}: {e}")


if __name__ == "__main__":
    # 测试代码
    try:
        result = directory_to_knowledge_graph_optimized(
            directory_path=".",
            output_name="test_optimized",
            include_content=False,
            max_depth=2,
            use_parallel=True
        )
        print("✅ 优化版增量知识图谱生成成功!")
        print("生成的文件:")
        for file_type, file_path in result.items():
            print(f"  - {file_type}: {file_path}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")