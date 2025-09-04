#!/usr/bin/env python3
"""
验证Agent自主学习效果 - 对比实验
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from core.react_agent_minimal import ReactAgentMinimal

class LearningEffectVerifier:
    """验证学习效果的实验框架"""
    
    def __init__(self):
        self.results = {
            "without_learning": [],
            "with_learning": []
        }
        
    def prepare_test_tasks(self):
        """准备测试任务序列（相似但不同的任务）"""
        return [
            {
                "name": "debug_task_1",
                "task": """
                修复以下Python代码错误：
                def add(a, b):
                    return a + b + c  # c未定义
                """,
                "expected_pattern": "未定义变量"
            },
            {
                "name": "debug_task_2", 
                "task": """
                修复以下Python代码错误：
                def multiply(x, y):
                    return x * y * z  # z未定义
                """,
                "expected_pattern": "未定义变量"  # 相同模式
            },
            {
                "name": "debug_task_3",
                "task": """
                修复以下Python代码错误：
                def divide(m, n):
                    result = m / n / p  # p未定义
                    return result
                """,
                "expected_pattern": "未定义变量"  # 又是相同模式
            }
        ]
    
    def run_without_learning(self, tasks):
        """运行不带学习的Agent（不使用agent_knowledge.md）"""
        print("\n" + "="*60)
        print("🔴 测试1：无学习机制的Agent")
        print("="*60)
        
        for i, task_def in enumerate(tasks):
            print(f"\n任务 {i+1}: {task_def['name']}")
            
            # 创建新Agent，不读取知识
            agent = ReactAgentMinimal(
                work_dir=f"output/test_no_learning_{i}",
                name=f"no_learning_{i}",
                model="kimi-k2-turbo-preview",  # 使用kimi
                knowledge_files=["knowledge/structured_notes.md"]  # 只给结构，不给历史知识
            )
            
            start_time = datetime.now()
            
            # 执行任务
            result = agent.execute(task=task_def['task'])
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # 记录结果
            self.results["without_learning"].append({
                "task": task_def['name'],
                "time": elapsed,
                "pattern": task_def['expected_pattern'],
                "learned": False
            })
            
            print(f"  耗时: {elapsed:.1f}秒")
            
            # 清理（不保留知识）
            if Path(f"output/test_no_learning_{i}").exists():
                shutil.rmtree(f"output/test_no_learning_{i}")
    
    def run_with_learning(self, tasks):
        """运行带学习的Agent（使用改进的agent_knowledge.md模板）"""
        print("\n" + "="*60)
        print("🟢 测试2：有学习机制的Agent（SONIC方法论）")
        print("="*60)
        
        # 使用统一的工作目录，让知识自然累积
        work_dir = "output/test_with_learning"
        
        for i, task_def in enumerate(tasks):
            print(f"\n任务 {i+1}: {task_def['name']}")
            
            # 构建知识文件列表
            knowledge_files = ["knowledge/structured_notes.md"]
            
            # 如果存在累积的知识，添加到知识文件列表
            knowledge_path = Path(work_dir) / ".notes/learning_agent/agent_knowledge.md"
            if knowledge_path.exists():
                knowledge_files.append(str(knowledge_path))
                print(f"  📚 检测到已有知识，新Agent会读取...")
            
            # 每个任务创建新Agent实例（避免消息累积），但使用相同的工作目录和名称
            agent = ReactAgentMinimal(
                work_dir=work_dir,  # 统一的工作目录
                name="learning_agent",  # 统一的Agent名称
                model="kimi-k2-turbo-preview",  # 使用kimi
                knowledge_files=knowledge_files  # 包含累积的知识
            )
            
            
            start_time = datetime.now()
            
            # 执行任务
            result = agent.execute(task=f"""
            {task_def['task']}
            
            **执行要求**：
            - 检查是否匹配已知模式（读取agent_knowledge.md）
            - 如果是已知模式，直接应用已知解决方案
            - 动态修改TODO：发现捷径时删除不必要步骤
            
            任务结束时，请更新知识文件：
            - 使用write_file工具写入到: .notes/learning_agent/agent_knowledge.md（相对路径）
            - 如果文件已存在，先用read_file读取，然后更新内容
            - 识别模式并记录频率（这是第{i+1}次任务）
            - 如果是重复模式（未定义变量），更新出现次数为{i+1}次
            - 记录本次实际执行轮数
            """)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # 检查是否学到了模式
            learned = False
            knowledge_path = Path(work_dir) / ".notes/learning_agent/agent_knowledge.md"
            if knowledge_path.exists():
                with open(knowledge_path, "r") as f:
                    content = f.read()
                    if "未定义变量" in content:
                        learned = True
                        # 检查频率
                        if "3次" in content or "第3次" in content or str(i+1) + "次" in content:
                            print(f"  ✅ 识别到重复模式！")
            
            # 记录结果
            self.results["with_learning"].append({
                "task": task_def['name'],
                "time": elapsed,
                "pattern": task_def['expected_pattern'],
                "learned": learned
            })
            
            print(f"  耗时: {elapsed:.1f}秒")
            if learned and i > 0:
                print(f"  📈 相比无学习版本快了: {self.results['without_learning'][i]['time'] - elapsed:.1f}秒")
    
    def analyze_results(self):
        """分析学习效果"""
        print("\n" + "="*60)
        print("📊 学习效果分析")
        print("="*60)
        
        # 计算平均时间
        no_learn_times = [r['time'] for r in self.results['without_learning']]
        learn_times = [r['time'] for r in self.results['with_learning']]
        
        no_learn_avg = sum(no_learn_times) / len(no_learn_times) if no_learn_times else 0
        learn_avg = sum(learn_times) / len(learn_times) if learn_times else 0
        
        print(f"\n⏱️ 执行效率对比：")
        print(f"  无学习平均: {no_learn_avg:.1f}秒")
        print(f"  有学习平均: {learn_avg:.1f}秒")
        print(f"  效率提升: {(no_learn_avg - learn_avg) / no_learn_avg * 100:.1f}%")
        
        # 学习曲线
        print(f"\n📈 学习曲线：")
        print("  任务  无学习  有学习  差值")
        for i in range(len(no_learn_times)):
            diff = no_learn_times[i] - learn_times[i]
            print(f"   {i+1}    {no_learn_times[i]:6.1f}  {learn_times[i]:6.1f}  {diff:+6.1f}")
        
        # 模式识别
        learned_patterns = sum(1 for r in self.results['with_learning'] if r['learned'])
        total_tasks = len(self.results['with_learning'])
        print(f"\n🎯 模式识别：")
        print(f"  识别出的模式数: {learned_patterns}")
        if total_tasks > 0:
            print(f"  模式复用率: {learned_patterns / total_tasks * 100:.1f}%")
        
        # 改进趋势
        if len(learn_times) >= 3:
            first_third = learn_times[0]
            last_third = learn_times[-1]
            improvement = (first_third - last_third) / first_third * 100
            print(f"\n📉 改进趋势：")
            print(f"  第1个任务: {first_third:.1f}秒")
            print(f"  第3个任务: {last_third:.1f}秒")
            print(f"  改进幅度: {improvement:.1f}%")
        
        return {
            "no_learning_avg": no_learn_avg,
            "learning_avg": learn_avg,
            "improvement": (no_learn_avg - learn_avg) / no_learn_avg * 100 if no_learn_avg > 0 else 0,
            "patterns_learned": learned_patterns
        }
    
    def verify_knowledge_evolution(self):
        """验证知识进化质量"""
        print("\n" + "="*60)
        print("🔍 知识质量分析")
        print("="*60)
        
        knowledge_file = Path("output/test_with_learning/.notes/learning_agent/agent_knowledge.md")
        if not knowledge_file.exists():
            print("❌ 未找到知识文件")
            return 0  # 返回0而不是None
        
        with open(knowledge_file, "r") as f:
            content = f.read()
        
        # 检查关键要素
        quality_checks = {
            "频率统计": "次任务中出现" in content or "频率" in content,
            "模式命名": "## 模式识别" in content or "### " in content,
            "抽象原理": "原理" in content or "通用" in content,
            "量化指标": "轮" in content or "%" in content,
            "失败记录": "失败" in content or "错误" in content
        }
        
        print("\n知识质量检查：")
        for check, passed in quality_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        quality_score = sum(quality_checks.values()) / len(quality_checks) * 100
        print(f"\n知识质量得分: {quality_score:.0f}%")
        
        # 展示部分知识内容
        print("\n📝 知识样例：")
        lines = content.split('\n')[:20]  # 前20行
        for line in lines:
            if line.strip() and not line.startswith('#'):
                print(f"  {line}")
        
        return quality_score


def run_verification():
    """运行完整的验证实验"""
    print("="*60)
    print("🧪 Agent自主学习效果验证实验")
    print("="*60)
    
    verifier = LearningEffectVerifier()
    
    # 准备测试任务
    tasks = verifier.prepare_test_tasks()
    print(f"\n准备了 {len(tasks)} 个测试任务")
    
    # 运行对比实验
    verifier.run_without_learning(tasks)
    verifier.run_with_learning(tasks)
    
    # 分析结果
    results = verifier.analyze_results()
    
    # 验证知识质量
    quality = verifier.verify_knowledge_evolution()
    
    # 最终结论
    print("\n" + "="*60)
    print("✅ 实验结论")
    print("="*60)
    
    if results['improvement'] > 20:
        print("🎉 学习效果显著！")
    elif results['improvement'] > 10:
        print("👍 学习效果良好")
    else:
        print("🤔 学习效果有限，需要继续优化")
    
    print(f"\n关键指标：")
    print(f"  - 效率提升: {results['improvement']:.1f}%")
    print(f"  - 模式识别: {results['patterns_learned']}个")
    if quality is not None:
        print(f"  - 知识质量: {quality:.0f}%")
    else:
        print(f"  - 知识质量: 无法评估")
    
    # 保存结果
    with open("learning_verification_results.json", "w") as f:
        json.dump({
            "results": results,
            "quality_score": quality if quality is not None else 0,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📊 详细结果已保存到 learning_verification_results.json")


if __name__ == "__main__":
    run_verification()