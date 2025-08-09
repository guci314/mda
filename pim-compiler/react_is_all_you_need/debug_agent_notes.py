"""
Debug Agent笔记管理系统
实现结构化的调试笔记维护
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field, asdict
import hashlib


class StrategyCategory(Enum):
    """修复策略类别"""
    IMPORT_FIX = "import_fix"
    PATH_FIX = "path_fix"
    SYNTAX_FIX = "syntax_fix"
    LOGIC_FIX = "logic_fix"
    CONFIG_FIX = "config_fix"
    DEPENDENCY_FIX = "dependency_fix"


class FixStatus(Enum):
    """修复状态"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    MADE_WORSE = "made_worse"


@dataclass
class TestResults:
    """测试结果数据"""
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    exit_code: Optional[int] = None
    
    @property
    def success_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100
    
    @property
    def is_success(self) -> bool:
        return self.exit_code == 0 and self.failed == 0 and self.errors == 0


class DebugAgentNotes:
    """Debug Agent的笔记管理器"""
    
    def __init__(self, notes_path: str = None):
        self.notes_path = Path(notes_path) if notes_path else Path("debug_notes.json")
        self.notes = self._load_or_create_notes()
    
    def _load_or_create_notes(self) -> Dict[str, Any]:
        """加载或创建笔记"""
        if self.notes_path.exists():
            with open(self.notes_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._create_new_notes()
    
    def _create_new_notes(self) -> Dict[str, Any]:
        """创建新笔记结构"""
        return {
            "session_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "project_context": {},
            "error_patterns": {},
            "fix_attempts": [],
            "knowledge_base": {
                "successful_fixes": [],
                "failed_strategies": [],
                "dependencies_map": {}
            },
            "current_state": {
                "active_errors": [],
                "blocked_errors": [],
                "priority_queue": [],
                "iteration_count": 0,
                "stuck_detection": {
                    "same_error_count": 0,
                    "last_progress_iteration": 0,
                    "is_stuck": False,
                    "suggested_action": None
                }
            },
            "insights": [],
            "communication_log": [],
            "statistics": {
                "total_errors_encountered": 0,
                "errors_fixed": 0,
                "errors_remaining": 0,
                "total_attempts": 0,
                "successful_attempts": 0,
                "average_attempts_per_error": 0,
                "time_spent_minutes": 0,
                "most_common_error_type": None,
                "most_effective_strategy": None
            }
        }
    
    def save(self):
        """保存笔记到文件"""
        self.notes["updated_at"] = datetime.now().isoformat()
        with open(self.notes_path, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, indent=2, ensure_ascii=False)
    
    def record_error(self, error_type: str, error_message: str, 
                     file_path: str = None, line: int = None) -> str:
        """记录新错误"""
        error_id = hashlib.md5(f"{error_type}:{error_message}".encode()).hexdigest()[:8]
        
        if error_id not in self.notes["error_patterns"]:
            self.notes["error_patterns"][error_id] = {
                "error_type": error_type,
                "pattern": error_message,
                "first_seen": datetime.now().isoformat(),
                "occurrence_count": 1,
                "locations": [],
                "root_cause": None,
                "related_errors": []
            }
            self.notes["statistics"]["total_errors_encountered"] += 1
        else:
            self.notes["error_patterns"][error_id]["occurrence_count"] += 1
        
        # 记录位置
        if file_path:
            location = {"file": file_path}
            if line:
                location["line"] = line
            self.notes["error_patterns"][error_id]["locations"].append(location)
        
        # 添加到活跃错误列表
        if error_id not in self.notes["current_state"]["active_errors"]:
            self.notes["current_state"]["active_errors"].append(error_id)
        
        self.save()
        return error_id
    
    def record_fix_attempt(self, error_id: str, strategy_name: str, 
                          category: StrategyCategory, confidence: float = 0.5) -> str:
        """记录修复尝试"""
        attempt_id = str(uuid.uuid4())[:8]
        
        attempt = {
            "attempt_id": attempt_id,
            "timestamp": datetime.now().isoformat(),
            "error_id": error_id,
            "strategy": {
                "name": strategy_name,
                "category": category.value,
                "description": "",
                "confidence": confidence
            },
            "actions_taken": [],
            "result": None,
            "lessons_learned": None
        }
        
        self.notes["fix_attempts"].append(attempt)
        self.notes["statistics"]["total_attempts"] += 1
        self.notes["current_state"]["iteration_count"] += 1
        
        self.save()
        return attempt_id
    
    def add_action_to_attempt(self, attempt_id: str, action_type: str, 
                             target: str, details: Dict = None):
        """添加操作到修复尝试"""
        for attempt in self.notes["fix_attempts"]:
            if attempt["attempt_id"] == attempt_id:
                action = {
                    "action_type": action_type,
                    "target": target,
                    "details": details or {}
                }
                attempt["actions_taken"].append(action)
                self.save()
                break
    
    def record_attempt_result(self, attempt_id: str, status: FixStatus, 
                             test_results: TestResults = None,
                             new_errors: List[str] = None,
                             fixed_errors: List[str] = None,
                             lesson: str = None):
        """记录修复尝试的结果"""
        for attempt in self.notes["fix_attempts"]:
            if attempt["attempt_id"] == attempt_id:
                attempt["result"] = {
                    "status": status.value,
                    "test_results": asdict(test_results) if test_results else None,
                    "new_errors": new_errors or [],
                    "fixed_errors": fixed_errors or []
                }
                
                if lesson:
                    attempt["lessons_learned"] = lesson
                
                # 更新统计
                if status == FixStatus.SUCCESS:
                    self.notes["statistics"]["successful_attempts"] += 1
                    if fixed_errors:
                        self.notes["statistics"]["errors_fixed"] += len(fixed_errors)
                        # 从活跃错误中移除
                        for error_id in fixed_errors:
                            if error_id in self.notes["current_state"]["active_errors"]:
                                self.notes["current_state"]["active_errors"].remove(error_id)
                
                # 检测是否卡住
                self._check_stuck_status()
                
                self.save()
                break
    
    def _check_stuck_status(self):
        """检测是否卡住"""
        current_iteration = self.notes["current_state"]["iteration_count"]
        stuck_detection = self.notes["current_state"]["stuck_detection"]
        
        # 检查最近5次尝试是否都失败了
        recent_attempts = self.notes["fix_attempts"][-5:]
        if len(recent_attempts) >= 5:
            all_failed = all(
                attempt.get("result", {}).get("status") in ["failed", "made_worse"]
                for attempt in recent_attempts
            )
            
            if all_failed:
                stuck_detection["is_stuck"] = True
                stuck_detection["suggested_action"] = "考虑更换策略或寻求人工帮助"
            else:
                stuck_detection["is_stuck"] = False
                stuck_detection["last_progress_iteration"] = current_iteration
    
    def add_insight(self, insight_type: str, description: str, 
                   confidence: float = 0.7, evidence: List[str] = None):
        """添加调试洞察"""
        insight = {
            "timestamp": datetime.now().isoformat(),
            "type": insight_type,
            "description": description,
            "confidence": confidence,
            "evidence": evidence or []
        }
        self.notes["insights"].append(insight)
        self.save()
    
    def get_strategy_blacklist(self, error_id: str) -> List[str]:
        """获取某个错误的失败策略黑名单"""
        blacklist = []
        for attempt in self.notes["fix_attempts"]:
            if (attempt["error_id"] == error_id and 
                attempt.get("result", {}).get("status") in ["failed", "made_worse"]):
                strategy_signature = f"{attempt['strategy']['category']}:{attempt['strategy']['name']}"
                if strategy_signature not in blacklist:
                    blacklist.append(strategy_signature)
        return blacklist
    
    def get_successful_strategies(self, error_type: str) -> List[Dict]:
        """获取某类错误的成功策略"""
        successful = []
        for attempt in self.notes["fix_attempts"]:
            error_id = attempt["error_id"]
            if error_id in self.notes["error_patterns"]:
                pattern = self.notes["error_patterns"][error_id]
                if (pattern["error_type"] == error_type and
                    attempt.get("result", {}).get("status") == "success"):
                    successful.append(attempt["strategy"])
        return successful
    
    def should_skip_error(self, error_id: str, max_attempts: int = 5) -> bool:
        """判断是否应该跳过某个错误"""
        attempts = [a for a in self.notes["fix_attempts"] if a["error_id"] == error_id]
        return len(attempts) >= max_attempts
    
    def get_priority_error(self) -> Optional[str]:
        """获取优先级最高的错误"""
        priority_queue = self.notes["current_state"]["priority_queue"]
        if priority_queue:
            # 按优先级排序
            sorted_queue = sorted(priority_queue, key=lambda x: x["priority"], reverse=True)
            return sorted_queue[0]["error_id"]
        
        # 如果没有优先级队列，返回第一个活跃错误
        active_errors = self.notes["current_state"]["active_errors"]
        return active_errors[0] if active_errors else None
    
    def log_communication(self, direction: str, message_type: str, 
                         content: str, metadata: Dict = None):
        """记录与生成Agent的通信"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "message_type": message_type,
            "content": content,
            "metadata": metadata or {}
        }
        self.notes["communication_log"].append(log_entry)
        self.save()
    
    def get_summary(self) -> str:
        """获取调试摘要"""
        stats = self.notes["statistics"]
        state = self.notes["current_state"]
        
        summary = f"""
=== 调试摘要 ===
会话ID: {self.notes['session_id']}
创建时间: {self.notes['created_at']}
最后更新: {self.notes['updated_at']}

错误统计:
- 总错误数: {stats['total_errors_encountered']}
- 已修复: {stats['errors_fixed']}
- 剩余: {len(state['active_errors'])}

修复统计:
- 总尝试次数: {stats['total_attempts']}
- 成功次数: {stats['successful_attempts']}
- 成功率: {(stats['successful_attempts'] / stats['total_attempts'] * 100) if stats['total_attempts'] > 0 else 0:.1f}%
- 当前迭代: {state['iteration_count']}

当前状态:
- 活跃错误: {', '.join(state['active_errors'][:3])}{'...' if len(state['active_errors']) > 3 else ''}
- 是否卡住: {'是' if state['stuck_detection']['is_stuck'] else '否'}

洞察发现: {len(self.notes['insights'])} 条
        """
        return summary.strip()


# 使用示例
if __name__ == "__main__":
    # 创建笔记管理器
    notes = DebugAgentNotes("debug_session_001.json")
    
    # 记录错误
    error_id = notes.record_error(
        "ModuleNotFoundError",
        "No module named 'app.db.database'",
        "tests/conftest.py",
        9
    )
    
    # 记录修复尝试
    attempt_id = notes.record_fix_attempt(
        error_id,
        "修改导入路径",
        StrategyCategory.IMPORT_FIX,
        confidence=0.8
    )
    
    # 添加操作
    notes.add_action_to_attempt(
        attempt_id,
        "file_edit",
        "tests/conftest.py",
        {
            "old_content": "from app.db.database import Base",
            "new_content": "from app.models.database import Base",
            "line_range": {"start": 9, "end": 9}
        }
    )
    
    # 记录结果
    test_results = TestResults(total=10, passed=8, failed=2, exit_code=1)
    notes.record_attempt_result(
        attempt_id,
        FixStatus.PARTIAL_SUCCESS,
        test_results,
        fixed_errors=[error_id],
        lesson="导入路径需要与实际文件结构一致"
    )
    
    # 添加洞察
    notes.add_insight(
        "pattern_discovered",
        "项目使用app/models目录而不是app/db目录存放数据库模型",
        confidence=0.9,
        evidence=["find命令显示database.py在app/models/目录"]
    )
    
    # 打印摘要
    print(notes.get_summary())