#!/usr/bin/env python3
"""
NLTM简单测试 - 展示如何用自然语言编程解决实际问题
"""

import json
from pathlib import Path
from datetime import datetime

def create_calculator_nlpl():
    """创建一个计算器NLPL程序"""
    return """
程序: 智能计算器
  目标: 执行复杂数学运算
  
  状态:
    - 表达式: "((2 + 3) * 4 - 5) / 3"
    - 结果: null
    - 步骤记录: []
  
  主流程:
    步骤1 解析表达式:
      识别: 运算符和操作数
      构建: 表达式树
      验证: 语法正确性
    
    步骤2 计算:
      如果 包含括号:
        先计算: 最内层括号
      遵循: 运算优先级
      记录: 每步计算
    
    步骤3 输出:
      显示: 最终结果
      显示: 计算步骤
"""

def create_text_analyzer_nlpl():
    """创建文本分析器NLPL程序"""
    return """
程序: 文本分析器
  目标: 分析文本特征
  
  状态:
    - 文本: "自然语言图灵机是计算的未来"
    - 统计: {}
  
  主流程:
    步骤1 基础统计:
      计算: 字符数
      计算: 词汇数
      识别: 语言类型
    
    步骤2 深度分析:
      提取: 关键词
      分析: 情感倾向
      识别: 主题
    
    步骤3 生成报告:
      汇总: 所有分析结果
      生成: 可视化图表
"""

def create_game_logic_nlpl():
    """创建游戏逻辑NLPL程序"""
    return """
程序: 猜数字游戏
  目标: 实现猜数字游戏逻辑
  
  状态:
    - 目标数字: 42
    - 猜测历史: []
    - 游戏结束: false
    - 最大尝试: 7
  
  主流程:
    步骤1 初始化:
      生成: 随机数(1-100)
      设置: 尝试次数 = 0
    
    步骤2 游戏循环:
      循环 当"未猜中 且 尝试次数 < 最大尝试":
        获取: 用户猜测
        比较: 猜测与目标
        如果 猜测 > 目标:
          提示: "太大了"
        否则如果 猜测 < 目标:
          提示: "太小了"
        否则:
          设置: 游戏结束 = true
          显示: "恭喜猜中！"
        增加: 尝试次数
    
    步骤3 结束:
      如果 游戏结束:
        显示: 成功信息
      否则:
        显示: 失败信息
"""

def simulate_nltm_execution(program_name: str, nlpl_content: str):
    """模拟NLTM执行"""
    print(f"\n{'='*60}")
    print(f"🚀 执行NLPL程序: {program_name}")
    print(f"{'='*60}")
    
    # 创建工作目录
    work_dir = Path(f"./nltm_{program_name.replace(' ', '_').lower()}")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存NLPL程序
    program_file = work_dir / "program.nlpl"
    program_file.write_text(nlpl_content)
    print(f"📝 程序已保存: {program_file}")
    
    # 初始化执行状态
    state = {
        "program": program_name,
        "session": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "running",
        "steps_completed": [],
        "current_step": "初始化"
    }
    
    # 保存状态
    state_file = work_dir / "state.json"
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"💾 状态已初始化: {state_file}")
    
    # 模拟执行步骤
    print(f"\n📊 执行步骤:")
    
    # 根据程序类型模拟不同的执行结果
    if "计算器" in program_name:
        steps = [
            ("解析表达式", "识别到: 2+3=5, 5*4=20, 20-5=15, 15/3=5"),
            ("执行计算", "结果: 5.0"),
            ("生成输出", "计算完成")
        ]
        final_result = {"结果": 5.0, "步骤": ["2+3=5", "5*4=20", "20-5=15", "15/3=5"]}
        
    elif "文本分析" in program_name:
        steps = [
            ("基础统计", "字符:17, 词汇:5"),
            ("深度分析", "语言:中文, 情感:积极"),
            ("生成报告", "分析完成")
        ]
        final_result = {"字符数": 17, "词汇数": 5, "语言": "中文", "情感": "积极"}
        
    elif "游戏" in program_name:
        steps = [
            ("初始化游戏", "目标数字已生成"),
            ("游戏循环", "等待用户输入..."),
            ("游戏结束", "记录游戏结果")
        ]
        final_result = {"目标": 42, "状态": "等待玩家"}
    else:
        steps = [("执行", "完成")]
        final_result = {"状态": "完成"}
    
    for step_name, step_result in steps:
        print(f"  ✅ {step_name}: {step_result}")
        state["steps_completed"].append(step_name)
        state["current_step"] = step_name
    
    # 更新最终状态
    state["status"] = "completed"
    state["result"] = final_result
    
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    print(f"\n✨ 执行完成!")
    print(f"📈 结果: {json.dumps(final_result, ensure_ascii=False)}")
    
    return state

def main():
    """主函数"""
    print("\n" + "="*70)
    print("🌟 自然语言图灵机 (NLTM) - 简单示例")
    print("="*70)
    print("\n展示如何用自然语言编写程序解决实际问题")
    
    # 定义示例程序
    examples = [
        ("智能计算器", create_calculator_nlpl()),
        ("文本分析器", create_text_analyzer_nlpl()),
        ("猜数字游戏", create_game_logic_nlpl())
    ]
    
    # 执行每个示例
    for name, nlpl in examples:
        simulate_nltm_execution(name, nlpl)
    
    print("\n" + "="*70)
    print("📚 总结")
    print("="*70)
    print("""
NLTM的优势:
1. 📝 自然语言编程 - 无需学习传统编程语言
2. 🧠 语义理解 - LLM理解意图而非语法
3. 🔄 动态执行 - 可以根据结果调整策略
4. 💾 状态管理 - JSON提供持久化存储
5. 🎯 领域无关 - 适用于任何类型的任务

这是编程的未来：人人都能用母语编程！
""")

if __name__ == "__main__":
    main()