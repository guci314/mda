#!/usr/bin/env python3
"""知识文件优化示例"""

from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel

# 方案1：不使用知识文件，直接在任务中提供上下文
def approach1():
    print("=== 方案1：不使用知识文件 ===")
    config = ReactAgentConfig(
        work_dir="output/approach1",
        memory_level=MemoryLevel.NONE,
        knowledge_files=[]  # 不加载知识文件
    )
    agent = GenericReactAgent(config)
    
    # 在任务中直接提供必要的上下文
    task = """
    项目根目录是 /home/guci/aiProjects/mda/pim-compiler。
    请分析这个目录的结构，告诉我主要有哪些子目录和文件。
    """
    agent.execute_task(task)

# 方案2：只加载特定的知识文件
def approach2():
    print("\n=== 方案2：只加载特定知识文件 ===")
    config = ReactAgentConfig(
        work_dir="output/approach2",
        memory_level=MemoryLevel.NONE,
        knowledge_files=["knowledge/programming/编程规范知识.md"]  # 只加载小的知识文件
    )
    agent = GenericReactAgent(config)
    
    task = "创建一个符合编程规范的 Python 函数，用于计算两个数的和"
    agent.execute_task(task)

# 方案3：动态加载知识
def approach3():
    print("\n=== 方案3：动态加载知识 ===")
    config = ReactAgentConfig(
        work_dir="output/approach3",
        memory_level=MemoryLevel.NONE,
        knowledge_files=[]  # 初始不加载
    )
    agent = GenericReactAgent(config)
    
    # 根据任务动态加载相关知识
    task = "我需要创建一个 FastAPI 应用"
    if "fastapi" in task.lower():
        # 动态加载 FastAPI 相关知识
        with open("knowledge/programming/fastapi_generation_knowledge.md", "r") as f:
            fastapi_knowledge = f.read()[:1000]  # 只取前1000字符
        agent.load_knowledge(f"FastAPI 基础知识：\n{fastapi_knowledge}")
    
    agent.execute_task(task)

if __name__ == "__main__":
    # 测试不同方案
    approach1()
    # approach2()
    # approach3()