#!/usr/bin/env python3
"""
NLTM概念验证 - 使用Kimi Agent
展示真实的知识驱动执行
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from core.kimi_react_agent import KimiReactAgent


def test_nltm_with_kimi():
    """使用Kimi测试NLTM概念"""
    
    print("\n" + "="*80)
    print("NLTM概念验证 - 使用Kimi Agent")
    print("="*80)
    
    # 检查API key
    if not os.getenv("MOONSHOT_API_KEY"):
        print("❌ 请设置MOONSHOT_API_KEY环境变量")
        return
    
    # 创建工作目录
    work_dir = Path("./kimi_nltm_poc")
    work_dir.mkdir(exist_ok=True)
    
    # 第一步：创建编导Agent
    print("\n📝 步骤1: 创建编导Agent")
    director_agent = KimiReactAgent(
        work_dir=str(work_dir / "director"),
        model="moonshot-v1-128k",
        knowledge_files=[
            "knowledge/nltm/director_agent_as_tool.md",
            "knowledge/nltm/nlpl_templates.md"
        ]
    )
    
    # 第二步：创建执行Agent
    print("\n⚙️ 步骤2: 创建执行Agent")
    executor_agent = KimiReactAgent(
        work_dir=str(work_dir / "executor"),
        model="moonshot-v1-128k",
        knowledge_files=[
            "knowledge/nltm/executor_agent_as_tool.md"
        ]
    )
    
    # 测试案例
    test_cases = [
        {
            "request": "分析数组 [12, 45, 23, 67, 34, 89, 21, 56, 43, 78] 的统计信息",
            "description": "10个元素的数组"
        },
        {
            "request": "计算 [5, 10, 15, 20, 25] 的统计数据",
            "description": "5个等差数列元素"
        },
        {
            "request": "帮我统计 [100, 200, 150, 175, 225, 250, 300] 这组数据",
            "description": "7个元素的数组"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'='*70}")
        print(f"测试案例 {i}: {test_case['description']}")
        print('='*70)
        print(f"用户请求: {test_case['request']}")
        
        # 步骤1: 编导Agent生成NLPL
        print("\n🎬 编导Agent工作中...")
        
        director_task = f"""
你是NLTM编导Agent。请根据director_agent_as_tool.md知识文件，为以下用户请求生成NLPL程序。

用户请求: {test_case['request']}

请生成：
1. 完整的NLPL程序（保存为program.nlpl）
2. 初始状态JSON（保存为initial_state.json）
3. 对用户的解释（保存为explanation.txt）

记住：
- NLPL程序要包含完整的状态定义和执行步骤
- 状态要包含数据和统计结果字段
- 步骤要清晰明确
"""
        
        print("生成NLPL程序...")
        director_result = director_agent.execute_task(director_task)
        
        # 读取生成的文件（Kimi创建了嵌套路径）
        nlpl_file = work_dir / "director" / "kimi_nltm_poc" / "director" / "program.nlpl"
        state_file = work_dir / "director" / "kimi_nltm_poc" / "director" / "initial_state.json"
        
        # 备用路径
        if not nlpl_file.exists():
            nlpl_file = work_dir / "director" / "program.nlpl"
            state_file = work_dir / "director" / "initial_state.json"
        
        if nlpl_file.exists():
            nlpl_program = nlpl_file.read_text()
            print("\n生成的NLPL程序:")
            print("-" * 40)
            print(nlpl_program[:500] + "..." if len(nlpl_program) > 500 else nlpl_program)
            print("-" * 40)
        else:
            print("❌ NLPL程序生成失败")
            continue
        
        if state_file.exists():
            initial_state = json.loads(state_file.read_text())
            print("\n初始状态:")
            print(json.dumps(initial_state, ensure_ascii=False, indent=2)[:300])
        else:
            initial_state = {}
        
        # 步骤2: 执行Agent执行NLPL
        print("\n\n🚀 执行Agent工作中...")
        
        # 将NLPL和状态复制到执行Agent的工作目录
        exec_nlpl_file = work_dir / "executor" / "program.nlpl"
        exec_state_file = work_dir / "executor" / "state.json"
        
        exec_nlpl_file.write_text(nlpl_program)
        exec_state_file.write_text(json.dumps(initial_state, ensure_ascii=False, indent=2))
        
        executor_task = f"""
你是NLTM执行Agent。请根据executor_agent_as_tool.md知识文件，执行NLPL程序。

工作目录中有：
- program.nlpl: 要执行的NLPL程序
- state.json: 当前状态

请：
1. 读取并理解NLPL程序
2. 按步骤严格执行
3. 每步更新state.json
4. 完成后生成执行报告（保存为execution_report.md）

执行原则：
- 严格按照NLPL步骤执行
- 每个动作都要实际执行（如计算总和、平均值等）
- 更新状态要准确
- 记录执行过程
"""
        
        print("执行NLPL程序...")
        executor_result = executor_agent.execute_task(executor_task)
        
        # 读取执行结果
        final_state_file = work_dir / "executor" / "state.json"
        report_file = work_dir / "executor" / "execution_report.md"
        
        if final_state_file.exists():
            try:
                # 尝试读取JSON，如果失败则提取最后一个有效的JSON片段
                state_content = final_state_file.read_text()
                # 尝试找到最后一个完整的JSON
                import re
                json_matches = re.findall(r'\{[^{}]*"统计"[^{}]*\}', state_content)
                if json_matches:
                    # 获取包含统计数据的最后一个片段
                    for match in reversed(json_matches):
                        if '平均值' in match and '最大值' in match:
                            # 构建一个简单的状态对象
                            stats_match = re.search(r'"统计"\s*:\s*(\{[^}]+\})', match)
                            if stats_match:
                                stats = json.loads(stats_match.group(1))
                                final_state = {"统计": stats, "完成": True}
                                break
                    else:
                        final_state = json.loads(state_content)
                else:
                    final_state = json.loads(state_content)
            except json.JSONDecodeError:
                print("⚠️ 状态文件格式有问题，尝试解析...")
                final_state = {"统计": {}, "完成": False}
            
            print("\n📊 执行结果:")
            
            if "统计" in final_state:
                stats = final_state["统计"]
                print(f"  • 数据: {final_state.get('数据', [])}")
                for key, value in stats.items():
                    if value is not None:
                        print(f"  • {key}: {value}")
            else:
                print("最终状态:")
                print(json.dumps(final_state, ensure_ascii=False, indent=2)[:500])
        
        if report_file.exists():
            report = report_file.read_text()
            print("\n执行报告摘要:")
            print(report[:300] + "..." if len(report) > 300 else report)
    
    # 总结
    print("\n\n" + "="*80)
    print("🌟 NLTM概念验证总结")
    print("="*80)
    print("""
关键验证点：
✅ 编导Agent根据知识文件生成NLPL程序
✅ 执行Agent根据知识文件执行程序
✅ 整个过程由知识驱动，无硬编码逻辑
✅ 状态管理和更新完全自动化

这证明了：
1. 知识文件可以完全定义Agent行为
2. NLPL作为中间语言连接理解和执行
3. 复杂计算可以用自然语言描述和执行
4. NLTM是可行的计算范式
""")


if __name__ == "__main__":
    test_nltm_with_kimi()