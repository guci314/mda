#!/usr/bin/env python3
"""
使用React Agent + JSON笔记本实现Sequential Thinking

这个实现展示了如何仅使用React Agent的标准工具（read_file, write_file）
和JSON笔记本来实现Sequential Thinking的所有功能。
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel


def create_sequential_thinking_agent(work_dir: str) -> GenericReactAgent:
    """创建使用JSON笔记本实现Sequential Thinking的Agent"""
    
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=[],
        enable_project_exploration=False,
        llm_model="deepseek-chat",
        llm_base_url="https://api.deepseek.com/v1",
        llm_api_key_env="DEEPSEEK_API_KEY",
        llm_temperature=0
    )
    
    # 只使用默认工具，无需自定义工具！
    agent = GenericReactAgent(config, name="sequential_thinking_agent")
    
    agent.interface = """使用JSON笔记本实现Sequential Thinking的Agent
    
我通过维护 thought_chain.json 文件来实现结构化思考：
- 每个思考步骤都记录在JSON中
- 支持修正、分支、回溯
- 完全可追溯的思维过程
"""
    
    # 核心：通过系统提示定义Sequential Thinking的实现
    agent._system_prompt = (agent._system_prompt or "") + """

## Sequential Thinking 实现协议

你需要通过维护 thought_chain.json 文件来实现Sequential Thinking。

### JSON结构
```json
{
  "session_id": "thinking_session_20240809_123456",
  "created_at": "2024-08-09T12:34:56",
  "total_thoughts_estimate": 5,
  "current_thought": 3,
  "status": "thinking|completed|paused",
  "thoughts": [
    {
      "id": 1,
      "content": "思考内容",
      "timestamp": "2024-08-09T12:34:56",
      "type": "initial|continuation|revision|branch|conclusion",
      "revises": null,  // 如果是revision，指向被修正的thought id
      "branch_from": null,  // 如果是branch，指向分支起点
      "branch_id": null,  // 分支标识
      "confidence": 0.8,  // 置信度
      "tags": ["hypothesis", "verified"]  // 标签
    }
  ],
  "branches": {
    "branch_name": {
      "from_thought": 2,
      "thoughts": [...]
    }
  },
  "conclusions": {
    "main": "主要结论",
    "alternatives": ["备选方案1", "备选方案2"]
  }
}
```

### 使用流程

1. **初始化思维链**
   - 首次思考时，创建 thought_chain.json
   - 设置 session_id 和初始参数

2. **添加思考步骤**
   每次思考：
   - 读取 thought_chain.json
   - 添加新的 thought 对象
   - 更新 current_thought
   - 写回文件

3. **修正思考**
   发现错误时：
   - 添加 type="revision" 的thought
   - 设置 revises 指向要修正的thought id
   - 解释修正原因

4. **分支探索**
   需要并行探索时：
   - 添加 type="branch" 的thought
   - 设置 branch_from 和 branch_id
   - 在 branches 部分记录分支详情

5. **得出结论**
   - 添加 type="conclusion" 的thought
   - 更新 conclusions 部分
   - 设置 status="completed"

### 高级功能

1. **思维回溯**
   - 可以查看任何历史thought
   - 分析思维演进过程

2. **置信度追踪**
   - 为每个thought设置confidence
   - 低置信度的thought可能需要revision

3. **标签系统**
   - 使用tags标记thought类型
   - 便于后续分析和检索

4. **多分支合并**
   - 比较不同分支的结论
   - 选择最优方案

### 示例工作流

对于复杂问题，按以下模式思考：

1. 初始化thought_chain.json
2. 添加问题分析thought (type="initial")
3. 添加假设生成thought
4. 如需验证，调用其他工具（execute_command等）
5. 根据结果添加验证thought
6. 如发现问题，添加revision thought
7. 得出结论，添加conclusion thought
8. 更新status为completed

记住：thought_chain.json就是你的"思维大脑"，所有推理都要记录在其中。
"""
    
    return agent


def demo_architecture_design():
    """演示：使用JSON笔记本设计系统架构"""
    
    print("=" * 80)
    print("React Agent + JSON笔记本 实现 Sequential Thinking")
    print("=" * 80)
    
    work_dir = Path("output/react_sequential_thinking")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    agent = create_sequential_thinking_agent(str(work_dir))
    
    task = """
使用thought_chain.json实现Sequential Thinking，设计一个电商推荐系统架构。

需求：
1. 实时个性化推荐
2. 支持千万级用户
3. 推荐延迟<100ms
4. CTR提升20%

工作流程：
1. 创建thought_chain.json初始化思维链
2. 分析需求（thought 1）
3. 探索技术方案（thought 2-4，可以创建分支探索不同方案）
4. 评估各方案优劣（thought 5-6）
5. 如发现之前分析有误，添加revision
6. 综合决策（conclusion）
7. 生成架构文档recommendation_system.md

要求：
- 每个重要决策都要在thought_chain.json中记录
- 使用分支探索不同的技术栈（如：协同过滤 vs 深度学习）
- 包含置信度评估
- 最终结论要有理有据
"""
    
    print("\n任务：设计电商推荐系统")
    print("-" * 40)
    
    result = agent.execute_task(task)
    
    # 读取并展示思维链
    thought_file = work_dir / "thought_chain.json"
    if thought_file.exists():
        with open(thought_file, 'r') as f:
            thought_chain = json.load(f)
        
        print("\n思维链分析：")
        print("-" * 40)
        print(f"会话ID: {thought_chain.get('session_id')}")
        print(f"总思考步骤: {len(thought_chain.get('thoughts', []))}")
        print(f"状态: {thought_chain.get('status')}")
        
        print("\n思考过程：")
        for thought in thought_chain.get('thoughts', []):
            prefix = f"[{thought['type']}]"
            if thought.get('revises'):
                prefix += f" 修正#{thought['revises']}"
            if thought.get('branch_id'):
                prefix += f" 分支:{thought['branch_id']}"
            
            print(f"  {thought['id']}. {prefix} {thought['content'][:80]}...")
            if thought.get('confidence'):
                print(f"     置信度: {thought['confidence']}")
        
        if thought_chain.get('conclusions'):
            print("\n最终结论：")
            print(f"  {thought_chain['conclusions'].get('main')}")
    
    return thought_chain if thought_file.exists() else None


def demo_code_debugging():
    """演示：使用JSON笔记本进行代码调试"""
    
    print("\n" + "=" * 80)
    print("使用JSON思维链调试代码")
    print("=" * 80)
    
    work_dir = Path("output/react_sequential_debugging")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建有bug的代码
    buggy_code = '''
class ShoppingCart:
    def __init__(self):
        self.items = {}
        
    def add_item(self, item_id, quantity, price):
        if item_id in self.items:
            self.items[item_id]['quantity'] += quantity
        else:
            self.items[item_id] = {
                'quantity': quantity,
                'price': price
            }
    
    def calculate_total(self):
        total = 0
        for item in self.items.values():
            total += item['quantity'] * item['price']
        return total * 1.1  # Bug: 税率应该是可配置的
    
    def apply_discount(self, discount_percent):
        # Bug: 没有验证discount_percent的范围
        discount = self.calculate_total() * discount_percent / 100
        return self.calculate_total() - discount  # Bug: 重复计算
    
    def remove_item(self, item_id):
        del self.items[item_id]  # Bug: 没有检查item是否存在
'''
    
    buggy_file = work_dir / "shopping_cart.py"
    with open(buggy_file, 'w') as f:
        f.write(buggy_code)
    
    agent = create_sequential_thinking_agent(str(work_dir))
    
    task = f"""
使用thought_chain.json记录你的调试思考过程，系统地调试shopping_cart.py。

步骤：
1. 初始化thought_chain.json
2. 读取代码，添加初步分析thought
3. 逐个识别潜在问题，每个问题一个thought
4. 设计修复方案（可以用分支探索不同修复策略）
5. 如果发现新问题，用revision修正之前的分析
6. 实施修复，生成fixed_shopping_cart.py
7. 添加conclusion总结所有修复

要求：
- thought_chain.json必须完整记录整个调试过程
- 使用confidence字段标记问题的严重程度
- 使用tags标记问题类型（如：["validation", "performance", "logic"]）
- 最终生成修复报告debugging_report.md
"""
    
    print("\n任务：调试购物车代码")
    print("-" * 40)
    
    result = agent.execute_task(task)
    
    # 分析调试思维链
    thought_file = work_dir / "thought_chain.json"
    if thought_file.exists():
        with open(thought_file, 'r') as f:
            debug_chain = json.load(f)
        
        print("\n调试思维链：")
        print("-" * 40)
        
        # 统计不同类型的thoughts
        thought_types = {}
        for thought in debug_chain.get('thoughts', []):
            t_type = thought.get('type', 'unknown')
            thought_types[t_type] = thought_types.get(t_type, 0) + 1
        
        print("思考类型分布：")
        for t_type, count in thought_types.items():
            print(f"  {t_type}: {count}")
        
        # 显示所有revision
        revisions = [t for t in debug_chain.get('thoughts', []) 
                    if t.get('type') == 'revision']
        if revisions:
            print("\n修正记录：")
            for rev in revisions:
                print(f"  修正thought #{rev['revises']}: {rev['content'][:60]}...")
    
    return debug_chain if thought_file.exists() else None


def compare_implementations():
    """对比原生MCP工具和JSON笔记本实现"""
    
    print("\n" + "=" * 80)
    print("对比分析：MCP工具 vs JSON笔记本")
    print("=" * 80)
    
    comparison = """
## 实现方式对比

### Sequential Thinking MCP工具
优势：
- 标准化的API接口
- 简洁的函数调用
- 自动的状态管理
- 跨Agent共享

劣势：
- 需要额外的MCP服务
- 状态不持久化
- 自定义能力受限
- 调试较困难

### React Agent + JSON笔记本
优势：
- 完全自主可控
- 状态自动持久化
- 无限的自定义能力
- 便于调试和分析
- 可以添加任意元数据
- 支持复杂的数据结构
- 可以实现版本控制

劣势：
- 需要手动管理JSON结构
- 没有标准化接口
- 可能产生不一致的格式

## 关键洞察

JSON笔记本方式实际上更符合"自然语言虚拟机"的理念：
1. **数据即程序** - thought_chain.json既是数据也是"程序"
2. **工具闭包** - 只需要read_file/write_file就能实现复杂功能
3. **可组合性** - 多个JSON笔记本可以组合成更复杂的系统
4. **透明性** - 所有状态都是可见、可审计的

## 推荐场景

使用MCP工具：
- 需要标准化接口
- 简单的思维链
- 跨系统集成

使用JSON笔记本：
- 需要持久化思维
- 复杂的元数据管理
- 自定义思维模式
- 调试和分析需求
"""
    
    print(comparison)
    
    # 创建对比文档
    work_dir = Path("output/react_sequential_thinking")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    doc_file = work_dir / "implementation_comparison.md"
    with open(doc_file, 'w') as f:
        f.write(comparison)
    
    print(f"\n✅ 对比文档已保存到: {doc_file}")


def main():
    """主函数"""
    
    print("选择演示：")
    print("1. 架构设计（使用JSON思维链）")
    print("2. 代码调试（使用JSON思维链）")
    print("3. 实现方式对比")
    print("4. 运行所有演示")
    
    choice = input("\n请选择 (1-4): ").strip() or "1"
    
    if choice == "1":
        demo_architecture_design()
    elif choice == "2":
        demo_code_debugging()
    elif choice == "3":
        compare_implementations()
    else:
        thought_chain = demo_architecture_design()
        debug_chain = demo_code_debugging()
        compare_implementations()
        
        # 展示JSON的灵活性
        if thought_chain and debug_chain:
            print("\n" + "=" * 80)
            print("JSON笔记本的额外优势展示")
            print("=" * 80)
            
            print("\n1. 可以轻松合并多个思维链：")
            merged = {
                "sessions": {
                    "architecture": thought_chain,
                    "debugging": debug_chain
                },
                "meta": {
                    "total_thoughts": (
                        len(thought_chain.get('thoughts', [])) + 
                        len(debug_chain.get('thoughts', []))
                    ),
                    "created_at": datetime.now().isoformat()
                }
            }
            print(f"   合并后总思考数: {merged['meta']['total_thoughts']}")
            
            print("\n2. 可以添加任意分析维度：")
            print("   - 时间线分析")
            print("   - 置信度变化追踪")
            print("   - 思维模式识别")
            print("   - 错误修正统计")
    
    print("\n演示完成！")
    print("\n结论：React Agent + JSON笔记本 = 灵活的Sequential Thinking实现")


if __name__ == "__main__":
    main()