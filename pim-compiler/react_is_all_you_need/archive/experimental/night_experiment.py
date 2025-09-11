#!/usr/bin/env python3
"""
夜间自动实验脚本 - 测试不同LLM模型的debug性能
运行方式: nohup python night_experiment.py > experiment.log 2>&1 &
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent_minimal import ReactAgentMinimal


class ModelExperiment:
    """模型实验器"""
    
    def __init__(self, work_dir: str, pim_file: str):
        self.work_dir = Path(work_dir)
        self.pim_file = pim_file
        self.results = []
        
    def test_model(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """测试单个模型配置"""
        model_name = model_config["name"]
        print(f"\n{'='*60}")
        print(f"🧪 测试模型: {model_name}")
        print(f"开始时间: {datetime.now()}")
        print(f"{'='*60}")
        
        # 清理工作目录
        experiment_dir = self.work_dir / f"experiment_{model_name.replace('/', '_')}"
        if experiment_dir.exists():
            subprocess.run(f"rm -rf {experiment_dir}", shell=True)
        experiment_dir.mkdir(parents=True, exist_ok=True)
        
        # 记录开始时间
        start_time = time.time()
        rounds_used = 0
        success = False
        error_msg = None
        
        try:
            # 创建各个专家Agent（保持不变，只改debug_agent）
            general_agent = ReactAgentMinimal(
                work_dir=str(experiment_dir),
                name="general_agent",
                description="通用任务处理专家 - 处理文件操作等基础任务",
                model="x-ai/grok-code-fast-1",
                minimal_mode=True
            )
            
            psm_generation_agent = ReactAgentMinimal(
                work_dir=str(experiment_dir),
                name="psm_generation_agent",
                description="PSM生成专家 - 根据PIM生成平台特定模型文档",
                model="x-ai/grok-code-fast-1",
                knowledge_files=["knowledge/mda/pim_to_psm_knowledge.md"],
                minimal_mode=True
            )
            
            code_generation_agent = ReactAgentMinimal(
                work_dir=str(experiment_dir),
                name="code_generation_agent",
                description="代码生成专家 - 根据PSM生成FastAPI代码",
                model="x-ai/grok-code-fast-1",
                knowledge_files=["knowledge/mda/generation_knowledge.md"],
                minimal_mode=True,
                max_rounds=300
            )
            
            # 使用实验模型作为debug_agent
            debug_agent = ReactAgentMinimal(
                work_dir=str(experiment_dir),
                name="debug_agent",
                description="调试修复专家 - 修复代码和测试问题",
                model=model_config["model"],
                base_url=model_config.get("base_url"),
                knowledge_files=["knowledge/mda/debugging_unified.md"],
                minimal_mode=True,
                max_rounds=model_config.get("max_rounds", 300)
            )
            
            # 创建Project Manager
            project_manager = ReactAgentMinimal(
                work_dir=str(experiment_dir),
                name="project_manager",
                description="项目经理 - 协调其他Agent完成MDA工作流",
                model="x-ai/grok-code-fast-1",
                minimal_mode=True
            )
            
            # 添加Agent作为Function
            project_manager.add_function(general_agent)
            project_manager.add_function(psm_generation_agent)
            project_manager.add_function(code_generation_agent)
            project_manager.add_function(debug_agent)
            
            # 执行任务
            task = f"""
# MDA完整工作流任务

## 需求
从零开始，基于PIM文件生成一个完整的博客系统，包括代码实现和测试。

## 执行步骤
1. **清空工作目录** - 删除所有现有文件，从干净环境开始
2. **生成PSM文档** - 基于PIM生成平台特定模型
3. **生成代码** - 根据PSM生成完整实现
4. **修复测试** - 确保所有测试通过

## 输入
- PIM文件: {self.pim_file}

## 期望输出
1. PSM文档 (blog_psm.md)
2. 代码实现 - FastAPI应用
3. 测试用例 - 单元测试100%通过
4. 项目文档 - README文件

请从清空目录开始，完成整个MDA工作流。
"""
            
            result = project_manager.execute(task=task)
            success = True
            
            # 分析debug_agent的执行轮数（从日志文件中提取）
            log_file = experiment_dir / ".agent" / "debug_agent" / "output.log"
            if log_file.exists():
                log_content = log_file.read_text(encoding='utf-8')
                # 统计"思考第X轮"的出现次数
                import re
                rounds = re.findall(r'思考第(\d+)轮', log_content)
                if rounds:
                    rounds_used = max(int(r) for r in rounds)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 错误: {e}")
        
        # 记录结束时间
        end_time = time.time()
        elapsed = end_time - start_time
        
        # 记录结果
        result = {
            "model": model_name,
            "model_id": model_config["model"],
            "success": success,
            "total_time": elapsed,
            "total_time_minutes": elapsed / 60,
            "debug_rounds": rounds_used,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"\n📊 {model_name} 实验结果:")
        print(f"  - 成功: {success}")
        print(f"  - 总时间: {elapsed/60:.1f}分钟")
        print(f"  - Debug轮数: {rounds_used}")
        if error_msg:
            print(f"  - 错误: {error_msg}")
        
        return result
    
    def run_all_experiments(self, models: List[Dict[str, Any]]):
        """运行所有模型实验"""
        print(f"\n🚀 开始夜间实验")
        print(f"测试 {len(models)} 个模型")
        print(f"预计时间: {len(models) * 30}分钟")
        
        for model_config in models:
            try:
                result = self.test_model(model_config)
                self.results.append(result)
                
                # 保存中间结果（防止中断丢失）
                self.save_results()
                
                # 休息一下，避免API限制
                print(f"⏸️ 休息30秒...")
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n⚠️ 用户中断")
                break
            except Exception as e:
                print(f"❌ 实验失败: {e}")
                self.results.append({
                    "model": model_config["name"],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        # 最终报告
        self.generate_report()
    
    def save_results(self):
        """保存实验结果"""
        results_file = Path("experiment_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已保存到 {results_file}")
    
    def generate_report(self):
        """生成实验报告"""
        print("\n" + "="*60)
        print("📊 实验报告")
        print("="*60)
        
        if not self.results:
            print("没有实验结果")
            return
        
        # 创建markdown报告
        report = ["# 夜间LLM Debug性能实验报告", ""]
        report.append(f"实验时间: {datetime.now()}")
        report.append("")
        report.append("## 实验结果")
        report.append("")
        report.append("| 模型 | 成功 | 总时间(分钟) | Debug轮数 | 备注 |")
        report.append("|------|------|-------------|-----------|------|")
        
        baseline_time = 35  # 原始deepseek-chat的时间
        
        for r in self.results:
            success = "✅" if r.get("success") else "❌"
            time_min = r.get("total_time_minutes", 0)
            rounds = r.get("debug_rounds", 0)
            
            # 计算相对性能
            if time_min > 0:
                speedup = baseline_time / time_min
                note = f"{speedup:.1f}x速度"
            else:
                note = r.get("error", "未完成")
            
            report.append(f"| {r['model']} | {success} | {time_min:.1f} | {rounds} | {note} |")
        
        # 找出最佳模型
        successful_results = [r for r in self.results if r.get("success")]
        if successful_results:
            best = min(successful_results, key=lambda x: x.get("total_time", float('inf')))
            report.append("")
            report.append(f"## 🏆 最佳模型: {best['model']}")
            report.append(f"- 时间: {best['total_time_minutes']:.1f}分钟")
            report.append(f"- Debug轮数: {best['debug_rounds']}")
            report.append(f"- 相比baseline提升: {baseline_time/best['total_time_minutes']:.1f}倍")
        
        report_text = "\n".join(report)
        
        # 保存报告
        report_file = Path("experiment_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(report_text)
        print(f"\n📄 报告已保存到 {report_file}")


def main():
    """主函数"""
    # 配置要测试的模型
    models_to_test = [
        {
            "name": "DeepSeek-Chat(Baseline)",
            "model": "deepseek-chat",
            "base_url": "https://api.deepseek.com/v1",
            "max_rounds": 300
        },
        {
            "name": "DeepSeek-Reasoner",
            "model": "deepseek-reasoner",  
            "base_url": "https://api.deepseek.com/v1",
            "max_rounds": 300
        },
        {
            "name": "glm-4.5",
            "model": "z-ai/glm-4.5",
            "base_url": "https://openrouter.ai/api/v1",
            "max_rounds": 300
        },
        {
            "name": "qwen3-coder",
            "model": "qwen/qwen3-coder",
            "base_url": "https://openrouter.ai/api/v1", 
            "max_rounds": 300
        }
    ]
    
    # 配置
    work_dir = "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/experiments"
    pim_file = "/home/guci/aiProjects/mda/pim-compiler/examples/blog.md"
    
    # 创建实验器
    experimenter = ModelExperiment(work_dir, pim_file)
    
    # 运行实验
    print("🌙 夜间实验开始")
    print(f"预计完成时间: {len(models_to_test) * 30}分钟")
    print("你可以去睡觉了，明天早上看结果！")
    print("\n提示: 使用 'tail -f experiment.log' 查看实时进度")
    
    experimenter.run_all_experiments(models_to_test)
    
    print("\n✨ 夜间实验完成！")
    print("查看 experiment_report.md 获取详细报告")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 实验被中断")
    except Exception as e:
        print(f"\n❌ 实验失败: {e}")
        import traceback
        traceback.print_exc()