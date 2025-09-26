#!/usr/bin/env python3
"""
创建tyz_worker的脚本
可以在Jupyter中通过 %run create_tyz_worker.py 来执行
"""

import sys
import os

# 强制清理所有缓存的模块
print("清理缓存模块...")
modules_to_delete = []
for name in list(sys.modules.keys()):
    if any(x in name for x in ['react_agent', 'tool_base', 'core.', 'tools.']):
        modules_to_delete.append(name)

for name in modules_to_delete:
    del sys.modules[name]
    print(f"  删除模块: {name}")

# 设置正确的路径（优先级最高）
react_path = '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need'
if react_path in sys.path:
    sys.path.remove(react_path)
sys.path.insert(0, react_path)

# 移除pim-engine路径
sys.path = [p for p in sys.path if 'pim-engine' not in p]

print(f"\n当前sys.path前3个路径:")
for i, p in enumerate(sys.path[:3]):
    print(f"  {i}: {p}")

# 重新导入
print("\n重新导入ReactAgentMinimal...")
from core.react_agent_minimal import ReactAgentMinimal

# 创建tyz_worker
print("\n创建tyz_worker...")
tyz_worker = ReactAgentMinimal(
    name="tyz_worker",
    description="从事天衍智的工作",
    work_dir="/home/guci/robot_projects/rag_sample/",
    model="x-ai/grok-code-fast-1",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    knowledge_files=[
        "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/minimal/validation/validation_simplicity.md"
    ],
    max_rounds=200
)

# 验证functions
print(f"\n验证functions (共{len(tyz_worker.functions)}个):")
for i, func in enumerate(tyz_worker.functions):
    func_name = func['function']['name']
    print(f"  {i+1}. {func_name}")
    if func_name == 'tyz_worker':
        print(f"     ✅ 找到tyz_worker自己!")
        methods = func['function']['parameters']['properties']['method']['enum']
        print(f"     可用方法: {methods}")

# 测试基本功能
print("\n测试基本功能...")
print(f"tyz_worker.name: {tyz_worker.name}")
print(f"tyz_worker.description: {tyz_worker.description}")
print(f"tyz_worker.model: {tyz_worker.model}")

# 测试直接调用execute方法（模拟self_management）
print("\n测试直接调用update_description...")
try:
    result = tyz_worker.execute(
        method='update_description',
        args={'new_description': '自知者明 自胜者强'}
    )
    print(f"结果: {result}")
    print(f"更新后的description: {tyz_worker.description}")
except Exception as e:
    print(f"直接调用失败: {e}")

print("\n" + "="*60)
print("tyz_worker已创建完成！")
print("在Jupyter中可以直接使用变量 'tyz_worker'")
print("="*60)

# 执行修改description的任务
print("\n" + "="*60)
print("执行修改description任务...")
print("="*60)

task="""
把description修改成"自知者明 自胜者强"
"""
x=tyz_worker.execute(task=task)
print(x)

print("\n最终description:", tyz_worker.description)

# 将tyz_worker添加到全局命名空间，这样Jupyter可以直接访问
import __main__
__main__.tyz_worker = tyz_worker