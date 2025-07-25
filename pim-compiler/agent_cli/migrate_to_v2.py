#!/usr/bin/env python3
"""
迁移脚本 - 将 Agent CLI 切换到 v2 架构

使用方法：
    python migrate_to_v2.py          # 切换到 v2
    python migrate_to_v2.py --revert # 恢复到 v1
"""

import os
import shutil
import argparse
from pathlib import Path


def backup_file(file_path: Path, backup_suffix: str = ".backup"):
    """备份文件"""
    backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
    if not backup_path.exists():
        shutil.copy2(file_path, backup_path)
        print(f"✓ 备份: {file_path} -> {backup_path}")
    else:
        print(f"- 备份已存在: {backup_path}")


def switch_to_v2():
    """切换到 v2 架构"""
    print("切换到 Agent CLI v2 (动态执行架构)...")
    
    base_dir = Path(__file__).parent
    
    # 1. 备份原始文件
    init_file = base_dir / "__init__.py"
    main_file = base_dir / "__main__.py"
    
    backup_file(init_file)
    backup_file(main_file)
    
    # 2. 使用 v2 版本替换
    init_v2 = base_dir / "__init___v2.py"
    main_v2 = base_dir / "__main___v2.py"
    
    if init_v2.exists():
        shutil.copy2(init_v2, init_file)
        print(f"✓ 更新: {init_file}")
    else:
        print(f"✗ 找不到: {init_v2}")
        
    if main_v2.exists():
        shutil.copy2(main_v2, main_file)
        print(f"✓ 更新: {main_file}")
    else:
        print(f"✗ 找不到: {main_v2}")
    
    print("\n✅ 已切换到 v2 架构！")
    print("\n新功能：")
    print("- 支持一个步骤执行多个动作")
    print("- 双决策器模型（动作决策器 + 步骤决策器）")
    print("- 动态计划调整能力")
    print("\n运行示例：")
    print("  python -m agent_cli run '你的任务描述'")
    print("  python -m agent_cli run '你的任务描述' --max-actions 20")
    print("  python -m agent_cli run '你的任务描述' --no-dynamic")


def revert_to_v1():
    """恢复到 v1 架构"""
    print("恢复到 Agent CLI v1 (原始架构)...")
    
    base_dir = Path(__file__).parent
    
    # 恢复备份
    for filename in ["__init__.py", "__main__.py"]:
        file_path = base_dir / filename
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        
        if backup_path.exists():
            shutil.copy2(backup_path, file_path)
            print(f"✓ 恢复: {file_path}")
        else:
            print(f"✗ 找不到备份: {backup_path}")
    
    print("\n✅ 已恢复到 v1 架构！")


def check_current_version():
    """检查当前版本"""
    base_dir = Path(__file__).parent
    init_file = base_dir / "__init__.py"
    
    if init_file.exists():
        content = init_file.read_text()
        if "AgentCLI_V2" in content:
            print("当前版本: v2 (动态执行架构)")
        else:
            print("当前版本: v1 (原始架构)")
    else:
        print("无法确定当前版本")


def main():
    parser = argparse.ArgumentParser(
        description="Agent CLI 架构迁移工具"
    )
    parser.add_argument(
        "--revert", 
        action="store_true", 
        help="恢复到 v1 架构"
    )
    parser.add_argument(
        "--check", 
        action="store_true", 
        help="检查当前版本"
    )
    
    args = parser.parse_args()
    
    if args.check:
        check_current_version()
    elif args.revert:
        revert_to_v1()
    else:
        switch_to_v2()


if __name__ == "__main__":
    main()