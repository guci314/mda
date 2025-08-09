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
        llm_model="kimi-k2-turbo-preview",
        llm_base_url="https://api.moonshot.cn/v1",
        llm_api_key_env="MOONSHOT_API_KEY",
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

## 任务目标（意图声明）

你的任务是使用thought_chain.json文件实现完整的Sequential Thinking过程。

### 成功条件（必须全部满足）
✅ thought_chain.json包含至少5个思考步骤
✅ 必须包含至少2个分支探索（不同技术方案）
✅ 每个thought都有明确的confidence置信度
✅ 最终conclusions部分包含明确的主要结论
✅ status字段最终为"completed"
✅ 生成对应的架构文档（.md文件）

### 失败条件（出现任何一个即为失败）
❌ 只完成1-2个思考步骤就停止
❌ 没有探索多个技术分支
❌ conclusions部分为空
❌ status仍为"thinking"
❌ 没有生成最终文档

## Sequential Thinking 实现协议

### JSON结构（你必须严格遵守）
```json
{
  "session_id": "唯一会话标识",
  "created_at": "创建时间",
  "total_thoughts_estimate": 8,  // 预估需要8个思考步骤
  "current_thought": 0,  // 当前进行到第几步
  "status": "thinking",  // thinking|completed|paused
  "thoughts": [
    {
      "id": 1,
      "content": "详细的思考内容",
      "timestamp": "时间戳",
      "type": "initial|continuation|revision|branch|conclusion",
      "revises": null,
      "branch_from": null,
      "branch_id": null,
      "confidence": 0.8,
      "tags": ["标签1", "标签2"]
    }
  ],
  "branches": {
    "协同过滤": {
      "from_thought": 2,
      "thoughts": [...]
    },
    "深度学习": {
      "from_thought": 2,
      "thoughts": [...]
    }
  },
  "conclusions": {
    "main": "最终选择的方案及理由",
    "alternatives": ["备选方案1", "备选方案2"]
  }
}
```

## 执行策略（必须按顺序完成）

### 第1步：初始化
- 创建thought_chain.json，设置初始结构
- current_thought: 0, status: "thinking"

### 第2步：需求分析（thought 1）
- type: "initial"
- 分析所有需求，识别关键挑战
- confidence: 0.9+（需求明确）

### 第3步：技术方案探索（thought 2-5）
你必须探索至少2个不同的技术分支：

#### 分支A：协同过滤方案
- thought 2: 创建分支点
- thought 3: 探索协同过滤（branch_id: "collaborative_filtering"）
  - 详细分析UserCF/ItemCF
  - 评估优缺点
  - confidence: 基于方案可行性

#### 分支B：深度学习方案  
- thought 4: 探索深度学习（branch_id: "deep_learning"）
  - 分析DNN/Wide&Deep/DeepFM等模型
  - 评估优缺点
  - confidence: 基于方案可行性

### 第4步：方案评估（thought 5-6）
- thought 5: 性能对比（延迟、吞吐量）
- thought 6: 效果对比（CTR提升潜力）
- 可能需要revision修正之前的分析

### 第5步：综合决策（thought 7-8）
- thought 7: 最终方案选择
- thought 8: type="conclusion"，总结所有分析
- 更新conclusions部分
- 设置status="completed"

### 第6步：生成文档
基于thought_chain.json生成recommendation_system.md

## 重要提醒

⚠️ 你必须完成所有8个思考步骤，不能中途停止
⚠️ 每完成一个thought，立即更新thought_chain.json
⚠️ 使用read_file读取当前状态，write_file保存更新
⚠️ 分支探索要详细，不能敷衍了事
⚠️ 最后必须设置status="completed"

## 强制执行循环

你必须执行以下循环，直到current_thought达到8：

```
while current_thought < 8:
    1. 读取thought_chain.json
    2. 添加下一个thought
    3. 更新current_thought
    4. 写回thought_chain.json
```

不允许在current_thought < 8时返回结果！

## 执行检查清单

在返回结果前，你必须确认ALL条件都满足：
☐ thought_chain.json存在且格式正确
☐ thoughts数组包含至少8个元素（当前只有{current}个，还需{remaining}个）
☐ branches对象包含至少2个分支
☐ conclusions.main不为空
☐ status == "completed"（不是"thinking"）
☐ recommendation_system.md文件已生成

❌ 如果任何检查项未完成，你必须继续工作！
❌ 绝对不允许在未完成时返回！
✅ 只有当所有条件都满足时才能返回结果！

## 当前进度追踪

每次更新thought_chain.json后，检查：
- 当前thought数量：{当前数量}/8
- 分支数量：{当前分支数}/2
- 状态：{当前状态} → 必须是"completed"
- 文档：{是否已生成} → 必须已生成

如果进度不足100%，立即继续下一步！
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
【重要】这是一个强制性任务，你必须完成全部8个思考步骤！

## 任务目标
使用thought_chain.json实现Sequential Thinking，设计一个电商推荐系统架构。

## 需求
1. 实时个性化推荐
2. 支持千万级用户  
3. 推荐延迟<100ms
4. CTR提升20%

## 强制执行步骤（必须全部完成）

### Step 1: 初始化
✅ 创建thought_chain.json，设置initial结构

### Step 2: 需求分析（thought 1）
✅ 添加type="initial"的thought，分析所有需求

### Step 3: 技术分支点（thought 2）
✅ 添加分支决策点thought

### Step 4: 协同过滤分支（thought 3）
✅ 添加branch_id="collaborative_filtering"的thought
✅ 详细分析UserCF/ItemCF的优缺点

### Step 5: 深度学习分支（thought 4）
✅ 添加branch_id="deep_learning"的thought
✅ 详细分析DNN/Wide&Deep模型

### Step 6: 性能对比（thought 5）
✅ 对比两个方案的延迟和吞吐量

### Step 7: 效果评估（thought 6）
✅ 评估CTR提升潜力

### Step 8: 最终决策（thought 7）
✅ 选择最优方案，说明理由

### Step 9: 总结（thought 8）
✅ 添加type="conclusion"的thought
✅ 更新conclusions.main
✅ 设置status="completed"

### Step 10: 生成文档
✅ 创建recommendation_system.md

## 验证清单（返回前必须全部打勾）

当前进度检查：
□ thought_chain.json已创建
□ thoughts数组有8个元素（不是2个或3个！）
□ 包含collaborative_filtering分支
□ 包含deep_learning分支
□ conclusions.main已填写
□ status是"completed"（不是"thinking"！）
□ recommendation_system.md已生成

⚠️ 警告：如果你在完成8个thoughts之前返回，任务将被判定为失败！
⚠️ 当前只完成2个thoughts是不可接受的！必须完成全部8个！

请立即开始，并确保完成所有步骤后再返回。
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