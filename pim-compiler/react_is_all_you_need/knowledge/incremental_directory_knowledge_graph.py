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
    
    # 文件类型统计
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
        result = directory_to_knowledge_graph_incremental(
            directory_path=".",
            output_name="test_incremental",
            include_content=False,
            max_depth=2,
            batch_size=10
        )
        print("✅ 增量知识图谱生成成功!")
        print("生成的文件:")
        for file_type, file_path in result.items():
            print(f"  - {file_type}: {file_path}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")