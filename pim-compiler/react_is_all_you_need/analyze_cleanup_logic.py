#!/usr/bin/env python3
"""分析清理逻辑的触发时机和执行流程"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel

def main():
    print("=== 清理逻辑分析 ===\n")
    
    # 创建工作目录
    work_dir = Path("output/cleanup_analysis")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建私有数据目录来观察清理行为
    agent_name = "test_agent"
    private_dir = work_dir / f".agent_data/{agent_name}"
    private_dir.mkdir(parents=True, exist_ok=True)
    
    # 在私有目录创建测试文件
    test_files = {
        "TODO.md": "# TODO List\n- Task 1\n- Task 2",
        "workflow.bpmn": "<?xml version='1.0'?><bpmn>...</bpmn>",
        "data.txt": "Some data file",
        "results.json": '{"result": "success"}'
    }
    
    print("1. 创建测试文件...")
    for filename, content in test_files.items():
        file_path = private_dir / filename
        file_path.write_text(content)
        print(f"   - {filename}")
    
    # 创建 Agent
    print("\n2. 创建 Agent...")
    config = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat"
    )
    agent = GenericReactAgent(config, name=agent_name)
    print("   Agent 创建完成（此时不会触发清理）")
    
    # 检查文件状态
    print("\n3. 检查私有目录文件（创建后）:")
    for item in private_dir.iterdir():
        print(f"   - {item.name}")
    
    # 执行第一个任务
    print("\n4. 执行第一个任务...")
    agent.execute_task("创建一个简单的计算器函数")
    
    # 检查文件状态
    print("\n5. 检查私有目录文件（第一次执行后）:")
    if private_dir.exists():
        for item in private_dir.iterdir():
            if item.is_dir():
                print(f"   - {item.name}/ (目录)")
                if item.name == "archive":
                    for archived in item.iterdir():
                        print(f"     - {archived.name}")
            else:
                print(f"   - {item.name}")
    
    # 再次创建文件
    print("\n6. 再次创建测试文件...")
    for filename, content in test_files.items():
        file_path = private_dir / filename
        file_path.write_text(content)
    
    # 执行第二个任务
    print("\n7. 执行第二个任务...")
    agent.execute_task("创建一个字符串处理函数")
    
    # 检查文件状态
    print("\n8. 检查私有目录文件（第二次执行后）:")
    if private_dir.exists():
        for item in private_dir.iterdir():
            if item.is_dir():
                print(f"   - {item.name}/ (目录)")
                if item.name == "archive":
                    for archived in item.iterdir():
                        print(f"     - {archived.name}")
            else:
                print(f"   - {item.name}")
    
    print("\n=== 分析总结 ===")
    print("清理逻辑触发时机：")
    print("1. 在 execute_task() 方法开始时")
    print("2. 每次执行新任务前都会清理")
    print("\n清理逻辑执行流程：")
    print("1. 检查私有数据目录 (.agent_data/{agent_name})")
    print("2. 创建 archive 子目录")
    print("3. TODO.md 和 .bpmn 文件 → 归档到 archive/")
    print("4. 其他文件 → 直接删除")
    print("5. 共享工作目录清理已被注释（不再执行）")


if __name__ == "__main__":
    main()