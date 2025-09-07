#!/usr/bin/env python3
"""
张三李四工作流演示 - 使用工作流文档防止死循环
"""

import os
import sys
import time
import threading
from pathlib import Path
from datetime import datetime

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.react_agent_minimal import ReactAgentMinimal
from core.workflow_document import WorkflowManager, WorkflowDocument, WorkflowStatus

def setup_environment():
    """设置环境"""
    # 创建必要的目录
    Path(".workflows").mkdir(exist_ok=True)
    
    # 清理旧文件
    for f in Path(".workflows").glob("*.md"):
        f.unlink()
    
    print("环境已准备就绪")

def run_zhangsan_with_workflow():
    """运行张三Agent - 工作流版本"""
    print("\n[张三] 启动...")
    
    # 创建工作流管理器
    workflow_manager = WorkflowManager(".workflows")
    
    # 创建初始工作流 - 询问李四
    initial_workflow = workflow_manager.create_workflow(
        task="请计算：2+2等于几？",
        owner="李四",
        workflow_type="calc"
    )
    
    # 张三添加历史记录
    initial_workflow.add_history(
        agent="张三",
        action="创建并分配任务",
        old_status=WorkflowStatus.PENDING,
        new_status=WorkflowStatus.PENDING
    )
    
    workflow_manager.save_workflow(initial_workflow)
    
    print(f"[张三] 创建工作流: {initial_workflow.workflow_id}")
    print(f"[张三] 任务: {initial_workflow.task}")
    print(f"[张三] 分配给: {initial_workflow.current_owner}")
    
    # 创建张三Agent处理可能的后续
    zhangsan = ReactAgentMinimal(
        work_dir=".",
        model="x-ai/grok-code-fast-1",
        knowledge_files=["knowledge/roles/zhangsan_workflow.md"],
        minimal_mode=False  # 使用文件系统模式以便能更新工作流
    )
    
    # 定期检查工作流状态
    for i in range(10):  # 检查10次
        time.sleep(3)
        
        # 检查是否有分配给张三的工作流
        workflows = workflow_manager.get_pending_workflows("张三")
        if workflows:
            print(f"[张三] 发现{len(workflows)}个待处理工作流")
            for workflow in workflows:
                print(f"[张三] 处理工作流: {workflow.workflow_id}")
                # 让Agent处理
                response = zhangsan.execute(task=f"处理工作流: {workflow.workflow_id}")
                print(f"[张三] 响应: {response}")
    
    print("[张三] 已停止")

def run_lisi_with_workflow():
    """运行李四Agent - 工作流版本"""
    print("\n[李四] 启动...")
    
    # 创建李四Agent
    lisi = ReactAgentMinimal(
        work_dir=".",
        model="x-ai/grok-code-fast-1",
        knowledge_files=["knowledge/roles/lisi_workflow.md"],
        minimal_mode=False  # 使用文件系统模式以便能更新工作流
    )
    
    # 创建工作流管理器
    workflow_manager = WorkflowManager(".workflows")
    
    # 定期检查工作流
    for i in range(10):  # 检查10次
        time.sleep(3)
        
        # 检查分配给李四的工作流
        workflows = workflow_manager.get_pending_workflows("李四")
        if workflows:
            print(f"[李四] 发现{len(workflows)}个待处理工作流")
            for workflow in workflows:
                print(f"[李四] 处理工作流: {workflow.workflow_id}")
                print(f"[李四] 任务: {workflow.task}")
                
                # 让Agent处理工作流
                prompt = f"""检查并处理工作流 {workflow.workflow_id}:
- 当前状态: {workflow.status.value}
- 任务: {workflow.task}
- 你需要：
  1. 接受任务（更新状态为in_progress）
  2. 执行计算
  3. 完成任务（更新状态为completed）
  4. 在Next_Action中写入答案"""
                
                response = lisi.execute(task=prompt)
                print(f"[李四] 响应: {response}")
                
                # 检查工作流是否已完成
                updated_workflow = workflow_manager.load_workflow(workflow.workflow_id)
                if updated_workflow and updated_workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.TERMINATED]:
                    print(f"[李四] 工作流已完成: {workflow.workflow_id}")
                    break
    
    print("[李四] 已停止")

def monitor_workflows():
    """监控工作流状态"""
    workflow_manager = WorkflowManager(".workflows")
    
    print("\n=== 工作流监控 ===")
    start_time = time.time()
    max_duration = 60  # 最多监控60秒
    
    completed_workflows = set()
    
    while time.time() - start_time < max_duration:
        # 检查所有工作流
        for workflow_file in Path(".workflows").glob("*.md"):
            workflow_id = workflow_file.stem
            
            if workflow_id not in completed_workflows:
                workflow = workflow_manager.load_workflow(workflow_id)
                
                if workflow:
                    print(f"\n[监控] 工作流 {workflow_id}")
                    print(f"  状态: {workflow.status.value}")
                    print(f"  当前负责人: {workflow.current_owner}")
                    print(f"  交互次数: {workflow.interaction_count}")
                    
                    if workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.TERMINATED]:
                        completed_workflows.add(workflow_id)
                        print(f"  ✓ 工作流已{workflow.status.value}")
                        
                        # 打印完整历史
                        print("\n  历史记录:")
                        for h in workflow.history:
                            print(f"    {h.timestamp} | {h.agent} | {h.action}")
                        
                        if workflow.next_action:
                            print(f"\n  结果: {workflow.next_action}")
                        
                        # 检查是否成功避免了死循环
                        if workflow.interaction_count <= 3:
                            print("  ✅ 成功避免死循环！交互次数合理")
                        elif workflow.interaction_count >= 10:
                            print("  ⚠️ 达到最大交互次数限制")
        
        # 如果所有工作流都完成，提前退出
        if len(completed_workflows) > 0:
            all_done = True
            for workflow_file in Path(".workflows").glob("*.md"):
                workflow = workflow_manager.load_workflow(workflow_file.stem)
                if workflow and workflow.status not in [WorkflowStatus.COMPLETED, WorkflowStatus.TERMINATED]:
                    all_done = False
                    break
            
            if all_done:
                print("\n✅ 所有工作流已完成!")
                break
        
        time.sleep(2)
    
    print("\n=== 监控结束 ===")

def main():
    """主函数"""
    print("="*60)
    print("张三李四工作流演示 - 防止死循环")
    print("="*60)
    
    # 设置环境
    setup_environment()
    
    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_workflows)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # 并行运行两个Agent
    zhangsan_thread = threading.Thread(target=run_zhangsan_with_workflow)
    lisi_thread = threading.Thread(target=run_lisi_with_workflow)
    
    zhangsan_thread.start()
    time.sleep(2)  # 给张三一点时间创建工作流
    lisi_thread.start()
    
    # 等待两个Agent完成
    zhangsan_thread.join()
    lisi_thread.join()
    
    # 等待监控线程完成
    monitor_thread.join(timeout=10)
    
    # 最终统计
    print("\n" + "="*60)
    print("最终统计:")
    print("="*60)
    
    workflow_manager = WorkflowManager(".workflows")
    
    total_workflows = 0
    completed = 0
    terminated = 0
    total_interactions = 0
    
    for workflow_file in Path(".workflows").glob("*.md"):
        workflow = workflow_manager.load_workflow(workflow_file.stem)
        if workflow:
            total_workflows += 1
            total_interactions += workflow.interaction_count
            
            if workflow.status == WorkflowStatus.COMPLETED:
                completed += 1
            elif workflow.status == WorkflowStatus.TERMINATED:
                terminated += 1
    
    print(f"总工作流数: {total_workflows}")
    print(f"已完成: {completed}")
    print(f"已终止: {terminated}")
    print(f"平均交互次数: {total_interactions/total_workflows if total_workflows > 0 else 0:.1f}")
    
    if total_interactions <= 5:
        print("\n✅ 优秀！成功避免了死循环")
    elif total_interactions <= 10:
        print("\n✅ 良好！在合理范围内完成任务")
    else:
        print("\n⚠️ 交互次数较多，但被限制机制阻止了死循环")
    
    print("\n演示完成！")

if __name__ == "__main__":
    main()