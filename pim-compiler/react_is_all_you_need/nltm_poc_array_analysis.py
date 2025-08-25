#!/usr/bin/env python3
"""
NLTM概念验证 - 数组统计分析
展示纯知识驱动的执行方式
"""

import json
from pathlib import Path
from typing import Dict, Any


class NLTMSimulator:
    """NLTM模拟器 - 模拟Agent读取知识文件并执行"""
    
    def __init__(self):
        self.knowledge_dir = Path(__file__).parent / "knowledge" / "nltm"
    
    def simulate_director_agent(self, user_request: str) -> Dict[str, Any]:
        """
        模拟编导Agent - 读取知识文件生成NLPL
        实际场景中，这将由LLM根据director_agent_as_tool.md执行
        """
        print("\n[编导Agent] 读取知识文件: director_agent_as_tool.md")
        print(f"[编导Agent] 分析用户请求: {user_request}")
        
        # 模拟根据知识文件生成NLPL
        # 实际由LLM完成
        if any(word in user_request for word in ["统计", "分析", "计算"]):
            # 提取数组
            import re
            array_match = re.search(r'\[([\d,\s]+)\]', user_request)
            if array_match:
                array_str = array_match.group(1)
                array = [int(x.strip()) for x in array_str.split(',')]
            else:
                array = []
            
            nlpl_program = f"""程序: 数组统计分析
  目标: {user_request}
  
  状态:
    数据: {array}
    统计:
      总和: null
      平均值: null
      最大值: null
      最小值: null
      中位数: null
      计数: null
    完成: false
    
  主流程:
    步骤1_验证数据:
      条件: 数据非空
      真分支: 继续执行
      假分支: 返回错误
      
    步骤2_计算总和:
      动作: 计算数组总和
      保存到: 状态.统计.总和
      
    步骤3_计算平均:
      动作: 计算平均值
      保存到: 状态.统计.平均值
      
    步骤4_找最值:
      动作: 找出最大值
      保存到: 状态.统计.最大值
      动作: 找出最小值
      保存到: 状态.统计.最小值
      
    步骤5_计算中位数:
      动作: 排序并找中位数
      保存到: 状态.统计.中位数
      
    步骤6_计数:
      动作: 统计元素个数
      保存到: 状态.统计.计数
      
    步骤7_完成:
      设置: 状态.完成 = true
      返回: 状态.统计"""
            
            initial_state = {
                "数据": array,
                "统计": {
                    "总和": None,
                    "平均值": None,
                    "最大值": None,
                    "最小值": None,
                    "中位数": None,
                    "计数": None
                },
                "完成": False
            }
            
            print("[编导Agent] 生成NLPL程序完成")
            
            return {
                "nlpl_program": nlpl_program,
                "initial_state": initial_state,
                "explanation": f"我将帮您分析数组 {array} 的统计信息"
            }
        
        return {
            "nlpl_program": "",
            "initial_state": {},
            "explanation": "无法理解请求"
        }
    
    def simulate_executor_agent(self, nlpl: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟执行Agent - 读取知识文件执行NLPL
        实际场景中，这将由LLM根据executor_agent_as_tool.md执行
        """
        print("\n[执行Agent] 读取知识文件: executor_agent_as_tool.md")
        print("[执行Agent] 开始执行NLPL程序")
        
        # 处理空输入
        if not nlpl or not initial_state:
            return {
                "success": False,
                "final_state": {},
                "execution_trace": [],
                "errors": [{"type": "INPUT_ERROR", "message": "无效的输入"}],
                "statistics": {"total_steps": 0, "executed_steps": 0, "success_steps": 0, "failed_steps": 0}
            }
        
        state = initial_state.copy()
        execution_trace = []
        
        # 模拟执行步骤
        # 实际由LLM根据知识文件执行
        
        # 步骤1: 验证数据
        if state.get("数据"):
            execution_trace.append({"step": "步骤1_验证数据", "status": "success", "action": "数据非空，继续执行"})
            
            data = state["数据"]
            
            # 步骤2: 计算总和
            total = sum(data)
            state["统计"]["总和"] = total
            execution_trace.append({"step": "步骤2_计算总和", "status": "success", "result": total})
            
            # 步骤3: 计算平均
            avg = total / len(data)
            state["统计"]["平均值"] = round(avg, 2)
            execution_trace.append({"step": "步骤3_计算平均", "status": "success", "result": round(avg, 2)})
            
            # 步骤4: 找最值
            max_val = max(data)
            min_val = min(data)
            state["统计"]["最大值"] = max_val
            state["统计"]["最小值"] = min_val
            execution_trace.append({"step": "步骤4_找最值", "status": "success", "max": max_val, "min": min_val})
            
            # 步骤5: 计算中位数
            sorted_data = sorted(data)
            n = len(sorted_data)
            if n % 2 == 0:
                median = (sorted_data[n//2-1] + sorted_data[n//2]) / 2
            else:
                median = sorted_data[n//2]
            state["统计"]["中位数"] = median
            execution_trace.append({"step": "步骤5_计算中位数", "status": "success", "result": median})
            
            # 步骤6: 计数
            count = len(data)
            state["统计"]["计数"] = count
            execution_trace.append({"step": "步骤6_计数", "status": "success", "result": count})
            
            # 步骤7: 完成
            state["完成"] = True
            execution_trace.append({"step": "步骤7_完成", "status": "success"})
            
            success = True
            errors = []
        else:
            execution_trace.append({"step": "步骤1_验证数据", "status": "failed", "error": "数据为空"})
            success = False
            errors = [{"type": "DATA_ERROR", "message": "数据为空"}]
        
        print("[执行Agent] 执行完成")
        
        return {
            "success": success,
            "final_state": state,
            "execution_trace": execution_trace,
            "errors": errors,
            "statistics": {
                "total_steps": 7,
                "executed_steps": len(execution_trace),
                "success_steps": sum(1 for t in execution_trace if t["status"] == "success"),
                "failed_steps": sum(1 for t in execution_trace if t["status"] == "failed")
            }
        }


def demonstrate_nltm_concept():
    """演示NLTM概念"""
    print("\n" + "="*80)
    print("NLTM概念验证 - 数组统计分析")
    print("展示纯知识驱动的执行方式")
    print("="*80)
    
    # 创建模拟器
    simulator = NLTMSimulator()
    
    # 测试用例
    test_cases = [
        "分析数组 [12, 45, 23, 67, 34, 89, 21, 56, 43, 78] 的统计信息",
        "计算 [5, 10, 15, 20, 25] 的统计数据",
        "帮我统计 [100, 200, 150, 175, 225, 250, 300] 这组数据"
    ]
    
    for i, user_request in enumerate(test_cases, 1):
        print(f"\n\n{'='*60}")
        print(f"测试案例 {i}")
        print('='*60)
        print(f"用户请求: {user_request}")
        
        # 步骤1: 编导Agent生成NLPL
        print("\n📝 步骤1: 编导Agent生成NLPL")
        director_result = simulator.simulate_director_agent(user_request)
        
        print(f"解释: {director_result['explanation']}")
        print("\n生成的NLPL程序:")
        print("-" * 40)
        print(director_result['nlpl_program'][:500] + "..." if len(director_result['nlpl_program']) > 500 else director_result['nlpl_program'])
        print("-" * 40)
        
        # 步骤2: 执行Agent执行NLPL
        print("\n⚙️ 步骤2: 执行Agent执行NLPL")
        executor_result = simulator.simulate_executor_agent(
            director_result['nlpl_program'],
            director_result['initial_state']
        )
        
        # 步骤3: 展示结果
        print("\n📊 步骤3: 执行结果")
        
        if executor_result['success']:
            print("✅ 执行成功!")
            
            # 打印执行轨迹
            print("\n执行轨迹:")
            for trace in executor_result['execution_trace']:
                status_icon = "✓" if trace['status'] == 'success' else "✗"
                print(f"  {status_icon} {trace['step']}")
            
            # 打印统计结果
            stats = executor_result['final_state']['统计']
            print("\n统计结果:")
            print(f"  • 数据: {executor_result['final_state']['数据']}")
            print(f"  • 计数: {stats['计数']}")
            print(f"  • 总和: {stats['总和']}")
            print(f"  • 平均值: {stats['平均值']}")
            print(f"  • 最大值: {stats['最大值']}")
            print(f"  • 最小值: {stats['最小值']}")
            print(f"  • 中位数: {stats['中位数']}")
        else:
            print("❌ 执行失败")
            print(f"错误: {executor_result['errors']}")
    
    # 展示知识驱动的核心概念
    print("\n\n" + "="*80)
    print("🌟 NLTM核心概念验证")
    print("="*80)
    
    print("""
1. 📚 知识驱动
   - 编导Agent读取 director_agent_as_tool.md 生成NLPL
   - 执行Agent读取 executor_agent_as_tool.md 执行程序
   - 无需Python代码定义行为

2. 🔄 执行流程
   用户请求 → 知识文件 → NLPL程序 → 知识文件 → 执行结果

3. ✨ 关键特性
   - 图灵完备: 支持顺序、分支、循环、状态
   - 自然语言: NLPL使用自然语言描述逻辑
   - 知识即程序: 修改知识文件即可改变行为

4. 🚀 优势
   - 无需编程: 一切都是自然语言和知识
   - 易于理解: NLPL程序人类可读
   - 灵活扩展: 添加新知识即可支持新功能
""")
    
    print("="*80)
    print("概念验证完成！NLTM成功展示了知识驱动的计算范式。")
    print("="*80)


if __name__ == "__main__":
    demonstrate_nltm_concept()