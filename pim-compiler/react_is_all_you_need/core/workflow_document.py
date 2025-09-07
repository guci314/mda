"""
工作流文档管理器 - 防止Agent死循环的状态控制机制
"""

import os
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

class WorkflowStatus(Enum):
    """工作流状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    TERMINATED = "terminated"

@dataclass
class WorkflowHistory:
    """工作流历史记录"""
    timestamp: str
    agent: str
    action: str
    status_change: str
    
@dataclass
class WorkflowDocument:
    """工作流文档数据类"""
    workflow_id: str
    status: WorkflowStatus
    current_owner: str
    previous_owner: Optional[str]
    created_at: str
    updated_at: str
    task: str
    history: List[WorkflowHistory] = field(default_factory=list)
    next_action: Optional[str] = None
    termination_conditions: List[str] = field(default_factory=lambda: [
        "任务完成",
        "超过最大交互次数(10次)",
        "遇到终止标记[WORKFLOW_END]"
    ])
    interaction_count: int = 0
    
    # 礼貌性回复列表
    COURTESY_PHRASES = {
        "谢谢", "感谢", "thanks", "thank you",
        "不客气", "不用谢", "you're welcome", "youre welcome",
        "好的", "ok", "收到", "明白", "了解", "got it",
        "再见", "拜拜", "goodbye", "bye"
    }
    
    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        lines = [
            f"# Workflow: {self.workflow_id}",
            f"Status: {self.status.value}",
            f"Current_Owner: {self.current_owner}",
            f"Previous_Owner: {self.previous_owner or 'None'}",
            f"Created_At: {self.created_at}",
            f"Updated_At: {self.updated_at}",
            f"Interaction_Count: {self.interaction_count}",
            "",
            "## Task",
            self.task,
            "",
            "## History"
        ]
        
        for h in self.history:
            lines.append(f"- {h.timestamp} {h.agent} {h.action} {h.status_change}")
        
        lines.extend([
            "",
            "## Next_Action",
            self.next_action or "待定",
            "",
            "## Termination_Conditions"
        ])
        
        for condition in self.termination_conditions:
            lines.append(f"- {condition}")
        
        return "\n".join(lines)
    
    @classmethod
    def from_markdown(cls, content: str) -> 'WorkflowDocument':
        """从Markdown内容解析"""
        lines = content.strip().split('\n')
        
        # 解析基本字段
        workflow_id = ""
        status = WorkflowStatus.PENDING
        current_owner = ""
        previous_owner = None
        created_at = ""
        updated_at = ""
        interaction_count = 0
        task = ""
        next_action = None
        history = []
        termination_conditions = []
        
        section = None
        task_lines = []
        next_action_lines = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("# Workflow:"):
                workflow_id = line.replace("# Workflow:", "").strip()
            elif line.startswith("Status:"):
                status_str = line.replace("Status:", "").strip()
                status = WorkflowStatus(status_str)
            elif line.startswith("Current_Owner:"):
                current_owner = line.replace("Current_Owner:", "").strip()
            elif line.startswith("Previous_Owner:"):
                owner = line.replace("Previous_Owner:", "").strip()
                previous_owner = owner if owner != "None" else None
            elif line.startswith("Created_At:"):
                created_at = line.replace("Created_At:", "").strip()
            elif line.startswith("Updated_At:"):
                updated_at = line.replace("Updated_At:", "").strip()
            elif line.startswith("Interaction_Count:"):
                interaction_count = int(line.replace("Interaction_Count:", "").strip())
            elif line == "## Task":
                section = "task"
            elif line == "## History":
                section = "history"
            elif line == "## Next_Action":
                section = "next_action"
            elif line == "## Termination_Conditions":
                section = "termination"
            elif section == "task" and line and not line.startswith("##"):
                task_lines.append(line)
            elif section == "history" and line.startswith("-"):
                parts = line[1:].strip().split(maxsplit=3)
                if len(parts) >= 4:
                    history.append(WorkflowHistory(
                        timestamp=parts[0] + " " + parts[1],
                        agent=parts[2],
                        action=parts[3].split()[0],
                        status_change=" ".join(parts[3].split()[1:])
                    ))
            elif section == "next_action" and line and not line.startswith("##"):
                next_action_lines.append(line)
            elif section == "termination" and line.startswith("-"):
                termination_conditions.append(line[1:].strip())
        
        task = "\n".join(task_lines)
        next_action = "\n".join(next_action_lines) if next_action_lines else None
        
        return cls(
            workflow_id=workflow_id,
            status=status,
            current_owner=current_owner,
            previous_owner=previous_owner,
            created_at=created_at,
            updated_at=updated_at,
            task=task,
            history=history,
            next_action=next_action,
            termination_conditions=termination_conditions or cls.termination_conditions.default_factory(),
            interaction_count=interaction_count
        )
    
    def should_terminate(self, message: str = "") -> bool:
        """判断是否应该终止工作流"""
        # 检查交互次数
        if self.interaction_count >= 10:
            return True
        
        # 检查终止标记
        if "[WORKFLOW_END]" in message:
            return True
        
        # 检查礼貌性回复
        message_lower = message.lower().strip()
        for phrase in self.COURTESY_PHRASES:
            if phrase.lower() in message_lower:
                # 如果整个消息主要是礼貌用语，则终止
                if len(message_lower) < 50:  # 短消息
                    return True
        
        # 检查重复处理无进展
        if self.current_owner == self.previous_owner:
            # 检查最近两次历史是否相同Agent
            if len(self.history) >= 2:
                if self.history[-1].agent == self.history[-2].agent:
                    return True
        
        return False
    
    def add_history(self, agent: str, action: str, old_status: WorkflowStatus, new_status: WorkflowStatus):
        """添加历史记录"""
        self.history.append(WorkflowHistory(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            agent=agent,
            action=action,
            status_change=f"{old_status.value}→{new_status.value}"
        ))
        self.interaction_count += 1
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self, workflow_dir: str = ".workflows"):
        self.workflow_dir = Path(workflow_dir)
        self.workflow_dir.mkdir(exist_ok=True)
        self.lock = threading.Lock()
    
    def create_workflow(self, 
                       task: str,
                       owner: str,
                       workflow_type: str = "general") -> WorkflowDocument:
        """创建新工作流"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workflow_id = f"{workflow_type}_{timestamp}"
        
        workflow = WorkflowDocument(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            current_owner=owner,
            previous_owner=None,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            task=task,
            interaction_count=0
        )
        
        workflow.add_history(
            agent="System",
            action="创建工作流",
            old_status=WorkflowStatus.PENDING,
            new_status=WorkflowStatus.PENDING
        )
        
        self.save_workflow(workflow)
        return workflow
    
    def save_workflow(self, workflow: WorkflowDocument):
        """保存工作流文档"""
        with self.lock:
            file_path = self.workflow_dir / f"{workflow.workflow_id}.md"
            file_path.write_text(workflow.to_markdown(), encoding='utf-8')
    
    def load_workflow(self, workflow_id: str) -> Optional[WorkflowDocument]:
        """加载工作流文档"""
        file_path = self.workflow_dir / f"{workflow_id}.md"
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            return WorkflowDocument.from_markdown(content)
        return None
    
    def get_pending_workflows(self, owner: str) -> List[WorkflowDocument]:
        """获取分配给指定Agent的待处理工作流"""
        workflows = []
        for file_path in self.workflow_dir.glob("*.md"):
            content = file_path.read_text(encoding='utf-8')
            workflow = WorkflowDocument.from_markdown(content)
            if (workflow.current_owner == owner and 
                workflow.status in [WorkflowStatus.PENDING, WorkflowStatus.IN_PROGRESS]):
                workflows.append(workflow)
        return workflows
    
    def transfer_workflow(self, 
                         workflow: WorkflowDocument,
                         from_agent: str,
                         to_agent: str,
                         action: str = "转交任务"):
        """转交工作流给另一个Agent"""
        old_status = workflow.status
        workflow.previous_owner = workflow.current_owner
        workflow.current_owner = to_agent
        workflow.status = WorkflowStatus.PENDING
        
        workflow.add_history(
            agent=from_agent,
            action=action,
            old_status=old_status,
            new_status=WorkflowStatus.PENDING
        )
        
        self.save_workflow(workflow)
    
    def complete_workflow(self, 
                         workflow: WorkflowDocument,
                         agent: str,
                         message: str = ""):
        """完成工作流"""
        old_status = workflow.status
        
        # 检查是否应该终止而不是完成
        if workflow.should_terminate(message):
            workflow.status = WorkflowStatus.TERMINATED
            action = "终止工作流(达到终止条件)"
        else:
            workflow.status = WorkflowStatus.COMPLETED
            action = "完成任务"
        
        workflow.add_history(
            agent=agent,
            action=action,
            old_status=old_status,
            new_status=workflow.status
        )
        
        self.save_workflow(workflow)
    
    def accept_workflow(self, 
                       workflow: WorkflowDocument,
                       agent: str):
        """接受工作流任务"""
        old_status = workflow.status
        workflow.status = WorkflowStatus.IN_PROGRESS
        
        workflow.add_history(
            agent=agent,
            action="接受任务",
            old_status=old_status,
            new_status=WorkflowStatus.IN_PROGRESS
        )
        
        self.save_workflow(workflow)
    
    def cleanup_old_workflows(self, days: int = 7):
        """清理旧的已终止工作流"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for file_path in self.workflow_dir.glob("*.md"):
            content = file_path.read_text(encoding='utf-8')
            workflow = WorkflowDocument.from_markdown(content)
            
            if workflow.status == WorkflowStatus.TERMINATED:
                updated_date = datetime.strptime(workflow.updated_at, "%Y-%m-%d %H:%M:%S")
                if updated_date < cutoff_date:
                    file_path.unlink()
                    print(f"清理旧工作流: {workflow.workflow_id}")


if __name__ == "__main__":
    # 测试代码
    manager = WorkflowManager()
    
    # 创建工作流
    workflow = manager.create_workflow(
        task="计算 2+2 等于几",
        owner="李四",
        workflow_type="calc"
    )
    
    print("创建的工作流:")
    print(workflow.to_markdown())
    print("\n" + "="*50 + "\n")
    
    # 接受任务
    manager.accept_workflow(workflow, "李四")
    
    # 测试礼貌性回复终止
    manager.complete_workflow(workflow, "李四", "答案是4，谢谢")
    
    print("完成后的工作流:")
    workflow = manager.load_workflow(workflow.workflow_id)
    print(workflow.to_markdown())
    print(f"\n最终状态: {workflow.status.value}")