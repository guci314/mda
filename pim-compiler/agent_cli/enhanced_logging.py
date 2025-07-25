"""
增强的日志功能，用于诊断 Agent CLI 问题
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import os


@dataclass
class PerformanceMetrics:
    """性能指标"""
    step_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    action_count: int = 0
    llm_calls: int = 0
    files_read: List[str] = None
    files_written: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.files_read is None:
            self.files_read = []
        if self.files_written is None:
            self.files_written = []
        if self.errors is None:
            self.errors = []
    
    def complete(self):
        """完成步骤，计算耗时"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        

class DiagnosticLogger:
    """诊断日志器"""
    
    def __init__(self, log_file: str = "agent_cli_diagnostics.log"):
        self.log_file = log_file
        self.start_time = time.time()
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.llm_call_count = 0
        self.file_read_count = {}  # 文件读取次数统计
        self.current_step: Optional[str] = None
        
        # 设置专门的诊断日志器
        self.logger = logging.getLogger("agent_cli.diagnostics")
        self.logger.setLevel(logging.DEBUG)
        
        # 创建文件处理器
        if not self.logger.handlers:
            fh = logging.FileHandler(log_file, mode='a')
            fh.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            
        self.log_session_start()
    
    def log_session_start(self):
        """记录会话开始"""
        self.logger.info("=" * 80)
        self.logger.info(f"Agent CLI Diagnostic Session Started at {datetime.now()}")
        self.logger.info("=" * 80)
    
    def log_task(self, task: str):
        """记录任务"""
        self.logger.info(f"\n[TASK] {task}")
    
    def log_step_start(self, step_name: str, description: str, expected_output: str):
        """记录步骤开始"""
        self.current_step = step_name
        self.metrics[step_name] = PerformanceMetrics(
            step_name=step_name,
            start_time=time.time()
        )
        self.logger.info(f"\n[STEP START] {step_name}")
        self.logger.info(f"  Description: {description}")
        self.logger.info(f"  Expected: {expected_output}")
    
    def log_step_end(self, step_name: str, status: str):
        """记录步骤结束"""
        if step_name in self.metrics:
            self.metrics[step_name].complete()
            metrics = self.metrics[step_name]
            self.logger.info(f"\n[STEP END] {step_name}")
            self.logger.info(f"  Status: {status}")
            self.logger.info(f"  Duration: {metrics.duration:.2f}s")
            self.logger.info(f"  Actions: {metrics.action_count}")
            self.logger.info(f"  LLM Calls: {metrics.llm_calls}")
            self.logger.info(f"  Files Read: {metrics.files_read}")
            self.logger.info(f"  Files Written: {metrics.files_written}")
            if metrics.errors:
                self.logger.info(f"  Errors: {metrics.errors}")
    
    def log_action(self, action_number: int, tool_name: str, description: str, params: Dict[str, Any]):
        """记录动作"""
        if self.current_step and self.current_step in self.metrics:
            self.metrics[self.current_step].action_count += 1
            
        self.logger.info(f"\n[ACTION {action_number}] {tool_name}")
        self.logger.info(f"  Description: {description}")
        self.logger.info(f"  Parameters: {json.dumps(params, indent=2)}")
        
        # 统计文件操作
        if tool_name == "read_file" and "path" in params:
            file_path = params.get("path") or params.get("file_path")
            if file_path:
                self.file_read_count[file_path] = self.file_read_count.get(file_path, 0) + 1
                if self.current_step and self.current_step in self.metrics:
                    self.metrics[self.current_step].files_read.append(file_path)
                    
        elif tool_name == "write_file" and "path" in params:
            file_path = params.get("path") or params.get("file_path")
            if file_path and self.current_step and self.current_step in self.metrics:
                self.metrics[self.current_step].files_written.append(file_path)
    
    def log_action_result(self, success: bool, result: Optional[str] = None, error: Optional[str] = None):
        """记录动作结果"""
        if success:
            self.logger.info(f"  Result: SUCCESS")
            if result and len(result) > 200:
                self.logger.info(f"  Output: {result[:200]}... (truncated)")
            elif result:
                self.logger.info(f"  Output: {result}")
        else:
            self.logger.error(f"  Result: FAILED")
            if error:
                self.logger.error(f"  Error: {error}")
                if self.current_step and self.current_step in self.metrics:
                    self.metrics[self.current_step].errors.append(error)
    
    def log_llm_call(self, call_type: str, prompt_length: int, response_length: int):
        """记录 LLM 调用"""
        self.llm_call_count += 1
        if self.current_step and self.current_step in self.metrics:
            self.metrics[self.current_step].llm_calls += 1
            
        self.logger.debug(f"\n[LLM CALL] {call_type}")
        self.logger.debug(f"  Call #: {self.llm_call_count}")
        self.logger.debug(f"  Prompt Length: {prompt_length} chars")
        self.logger.debug(f"  Response Length: {response_length} chars")
    
    def log_step_decision(self, completed: bool, reason: str, missing: Optional[str] = None):
        """记录步骤决策"""
        self.logger.info(f"\n[STEP DECISION]")
        self.logger.info(f"  Completed: {completed}")
        self.logger.info(f"  Reason: {reason}")
        if missing:
            self.logger.info(f"  Missing: {missing}")
    
    def log_context_compression(self, original_size: int, compressed_size: int, saved_percentage: float):
        """记录上下文压缩"""
        self.logger.info(f"\n[CONTEXT COMPRESSION]")
        self.logger.info(f"  Original Size: {original_size} bytes")
        self.logger.info(f"  Compressed Size: {compressed_size} bytes")
        self.logger.info(f"  Saved: {saved_percentage:.1f}%")
    
    def log_warning(self, message: str):
        """记录警告"""
        self.logger.warning(f"\n[WARNING] {message}")
    
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """记录错误"""
        self.logger.error(f"\n[ERROR] {message}")
        if exception:
            self.logger.error(f"  Exception: {type(exception).__name__}: {str(exception)}")
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成执行摘要"""
        total_duration = time.time() - self.start_time
        
        summary = {
            "total_duration": total_duration,
            "total_llm_calls": self.llm_call_count,
            "steps": len(self.metrics),
            "total_actions": sum(m.action_count for m in self.metrics.values()),
            "files_read_count": self.file_read_count,
            "repeated_reads": {f: count for f, count in self.file_read_count.items() if count > 1},
            "performance_by_step": {
                name: {
                    "duration": m.duration,
                    "actions": m.action_count,
                    "llm_calls": m.llm_calls,
                    "files_read": len(m.files_read),
                    "files_written": len(m.files_written),
                    "errors": len(m.errors)
                } for name, m in self.metrics.items() if m.duration
            }
        }
        
        return summary
    
    def log_summary(self):
        """记录执行摘要"""
        summary = self.generate_summary()
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("EXECUTION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Total Duration: {summary['total_duration']:.2f}s")
        self.logger.info(f"Total LLM Calls: {summary['total_llm_calls']}")
        self.logger.info(f"Total Steps: {summary['steps']}")
        self.logger.info(f"Total Actions: {summary['total_actions']}")
        
        if summary['repeated_reads']:
            self.logger.warning("\nRepeated File Reads:")
            for file, count in summary['repeated_reads'].items():
                self.logger.warning(f"  {file}: {count} times")
        
        self.logger.info("\nPerformance by Step:")
        for step, metrics in summary['performance_by_step'].items():
            self.logger.info(f"\n  {step}:")
            self.logger.info(f"    Duration: {metrics['duration']:.2f}s")
            self.logger.info(f"    Actions: {metrics['actions']}")
            self.logger.info(f"    LLM Calls: {metrics['llm_calls']}")
            if metrics['errors'] > 0:
                self.logger.warning(f"    Errors: {metrics['errors']}")
        
        # 保存详细的 JSON 摘要
        summary_file = self.log_file.replace('.log', '_summary.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        self.logger.info(f"\nDetailed summary saved to: {summary_file}")


# 全局诊断日志器实例
_diagnostic_logger: Optional[DiagnosticLogger] = None


def get_diagnostic_logger() -> Optional[DiagnosticLogger]:
    """获取诊断日志器实例"""
    return _diagnostic_logger


def init_diagnostic_logger(log_file: str = "agent_cli_diagnostics.log") -> DiagnosticLogger:
    """初始化诊断日志器"""
    global _diagnostic_logger
    _diagnostic_logger = DiagnosticLogger(log_file)
    return _diagnostic_logger