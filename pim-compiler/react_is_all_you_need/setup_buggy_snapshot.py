#!/usr/bin/env python3
"""
设置buggy代码快照，用于快速强化学习循环
"""

import os
import subprocess
from pathlib import Path
from core.react_agent_minimal import ReactAgentMinimal

class BuggyCodeSnapshot:
    def __init__(self, work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/output/rl_test"):
        self.work_dir = Path(work_dir)
        self.snapshot_branch = "buggy_snapshot"
        
    def setup_initial_buggy_code(self):
        """生成一次buggy代码并保存为Git快照"""
        
        print("📦 步骤1: 清空并初始化工作目录")
        os.makedirs(self.work_dir, exist_ok=True)
        os.chdir(self.work_dir)
        
        # 初始化Git仓库
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"])
        subprocess.run(["git", "config", "user.name", "Test User"])
        
        print("\n📦 步骤2: 生成PSM")
        psm_agent = ReactAgentMinimal(
            work_dir=str(self.work_dir),
            name="psm_generator",
            model="kimi-k2-turbo-preview",
            knowledge_files=["knowledge/mda/pim_to_psm_knowledge.md"]
        )
        
        psm_agent.execute(task="""
        根据/home/guci/aiProjects/mda/pim-compiler/examples/blog.md生成PSM
        文件名: blog_psm.md
        """)
        
        print("\n📦 步骤3: 生成代码（包含bug）")
        gen_agent = ReactAgentMinimal(
            work_dir=str(self.work_dir),
            name="code_generator",
            model="kimi-k2-turbo-preview",
            knowledge_files=["knowledge/mda/generation_knowledge.md"]
        )
        
        gen_agent.execute(task="""
        根据blog_psm.md生成FastAPI代码
        包含app/和tests/目录
        """)
        
        print("\n📦 步骤4: 创建Git快照")
        # 添加所有文件
        subprocess.run(["git", "add", "."], check=True)
        
        # 创建初始提交
        subprocess.run(["git", "commit", "-m", "Initial buggy code snapshot"], check=True)
        
        # 创建快照分支
        subprocess.run(["git", "branch", self.snapshot_branch], check=True)
        
        print(f"\n✅ Buggy代码快照已保存到分支: {self.snapshot_branch}")
        
    def reset_to_buggy_state(self):
        """恢复到buggy状态（超快速）"""
        os.chdir(self.work_dir)
        
        # 强制重置到buggy快照
        subprocess.run(["git", "reset", "--hard", self.snapshot_branch], check=True)
        subprocess.run(["git", "clean", "-fd"], check=True)  # 清理未跟踪文件
        
        print("✅ 已恢复到buggy状态（1秒完成）")
        
    def get_snapshot_info(self):
        """获取快照信息"""
        os.chdir(self.work_dir)
        
        # 获取提交信息
        result = subprocess.run(
            ["git", "log", "--oneline", "-1", self.snapshot_branch],
            capture_output=True,
            text=True
        )
        
        return result.stdout.strip()

# 使用示例
if __name__ == "__main__":
    snapshot = BuggyCodeSnapshot()
    
    # 只需要运行一次
    print("🚀 创建buggy代码快照（只需运行一次）")
    snapshot.setup_initial_buggy_code()
    
    print("\n" + "="*60)
    print("快照创建完成！")
    print("后续可以使用 reset_to_buggy_state() 快速恢复")
    print("="*60)