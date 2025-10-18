#!/usr/bin/env python3
"""
生成知识函数索引并保存为JSON文件
用于调试和查看所有可用的知识函数
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/Users/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.knowledge_function_loader import KnowledgeFunctionLoader

def generate_index():
    """生成知识函数索引"""

    # 知识目录列表
    knowledge_dirs = [
        '/Users/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge'
    ]

    # 创建加载器
    loader = KnowledgeFunctionLoader(knowledge_dirs)

    # 构建索引数据
    index_data = {
        "total_functions": len(loader.function_index),
        "functions": {}
    }

    # 填充函数信息
    for func_name, func_info in sorted(loader.function_index.items()):
        index_data["functions"][func_name] = {
            "type": func_info.func_type,
            "file": str(func_info.path.name),
            "path": str(func_info.path),
            "description": func_info.docstring
        }

    # 保存为JSON文件
    output_file = Path('/Users/guci/aiProjects/mda/knowledge_function_index.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 知识函数索引已生成")
    print(f"📄 文件位置: {output_file}")
    print(f"📊 共找到 {len(loader.function_index)} 个知识函数")

    # 打印函数列表
    print("\n知识函数列表：")
    for func_name in sorted(loader.function_index.keys()):
        func_info = loader.function_index[func_name]
        print(f"  @{func_name:30} ({func_info.func_type:8}) - {func_info.path.name}")

    return output_file

if __name__ == "__main__":
    output_file = generate_index()
    print(f"\n使用以下命令在VS Code中打开：")
    print(f"code {output_file}")