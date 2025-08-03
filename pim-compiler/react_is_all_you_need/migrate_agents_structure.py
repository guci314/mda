#!/usr/bin/env python3
"""
迁移 .agents 目录结构

从旧结构：
.agents/
├── data/{agent_name}/
└── memory/{agent_name}/

迁移到新结构：
.agents/
└── {agent_name}/
    ├── data/
    └── knowledge/
"""

import os
import shutil
from pathlib import Path
import sys


def migrate_agents_structure():
    """执行目录结构迁移"""
    
    # 获取 .agents 目录路径
    agents_dir = Path(__file__).parent / ".agents"
    
    if not agents_dir.exists():
        print(f"错误：.agents 目录不存在: {agents_dir}")
        return False
    
    print(f"开始迁移 .agents 目录结构...")
    print(f"目录位置: {agents_dir}")
    
    # 获取所有需要迁移的 agent
    old_data_dir = agents_dir / "data"
    old_memory_dir = agents_dir / "memory"
    
    agents_to_migrate = set()
    
    # 收集所有 agent 名称
    if old_data_dir.exists():
        for agent_dir in old_data_dir.iterdir():
            if agent_dir.is_dir():
                agents_to_migrate.add(agent_dir.name)
    
    if old_memory_dir.exists():
        for agent_dir in old_memory_dir.iterdir():
            if agent_dir.is_dir():
                agents_to_migrate.add(agent_dir.name)
    
    print(f"\n发现 {len(agents_to_migrate)} 个 agent 需要迁移:")
    for agent_name in sorted(agents_to_migrate):
        print(f"  - {agent_name}")
    
    # 执行迁移
    success_count = 0
    for agent_name in sorted(agents_to_migrate):
        print(f"\n迁移 {agent_name}...")
        
        # 创建新的 agent 目录
        new_agent_dir = agents_dir / agent_name
        new_agent_dir.mkdir(exist_ok=True)
        
        # 迁移 data 目录
        old_data_path = old_data_dir / agent_name
        new_data_path = new_agent_dir / "data"
        
        if old_data_path.exists() and not new_data_path.exists():
            try:
                shutil.move(str(old_data_path), str(new_data_path))
                print(f"  ✓ 迁移 data 目录")
            except Exception as e:
                print(f"  ✗ 迁移 data 目录失败: {e}")
        elif new_data_path.exists():
            print(f"  - data 目录已存在，跳过")
        
        # 迁移 memory 目录到 knowledge
        old_memory_path = old_memory_dir / agent_name
        new_knowledge_path = new_agent_dir / "knowledge"
        
        if old_memory_path.exists() and not new_knowledge_path.exists():
            try:
                shutil.move(str(old_memory_path), str(new_knowledge_path))
                print(f"  ✓ 迁移 memory → knowledge 目录")
            except Exception as e:
                print(f"  ✗ 迁移 memory 目录失败: {e}")
        elif new_knowledge_path.exists():
            print(f"  - knowledge 目录已存在，跳过")
        
        success_count += 1
    
    print(f"\n成功迁移 {success_count}/{len(agents_to_migrate)} 个 agent")
    
    # 清理旧目录（如果为空）
    if old_data_dir.exists():
        try:
            # 检查是否为空
            if not any(old_data_dir.iterdir()):
                old_data_dir.rmdir()
                print(f"\n已删除空的 data 目录")
        except Exception as e:
            print(f"\n无法删除 data 目录: {e}")
    
    if old_memory_dir.exists():
        try:
            # 检查是否为空
            if not any(old_memory_dir.iterdir()):
                old_memory_dir.rmdir()
                print(f"已删除空的 memory 目录")
        except Exception as e:
            print(f"\n无法删除 memory 目录: {e}")
    
    # 显示新的目录结构
    print("\n新的目录结构:")
    for agent_dir in sorted(agents_dir.iterdir()):
        if agent_dir.is_dir() and agent_dir.name not in ["data", "memory"]:
            print(f"  {agent_dir.name}/")
            for sub_dir in sorted(agent_dir.iterdir()):
                if sub_dir.is_dir():
                    print(f"    └── {sub_dir.name}/")
                    # 显示知识文件
                    if sub_dir.name == "knowledge":
                        for file in sub_dir.iterdir():
                            if file.is_file():
                                print(f"        └── {file.name}")
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("Agent 目录结构迁移工具")
    print("=" * 60)
    
    # 确认操作
    response = input("\n是否执行迁移？(y/n): ")
    if response.lower() != 'y':
        print("取消迁移")
        return 1
    
    # 执行迁移
    if migrate_agents_structure():
        print("\n✅ 迁移完成！")
        return 0
    else:
        print("\n❌ 迁移失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())