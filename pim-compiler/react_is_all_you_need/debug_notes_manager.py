"""调试笔记管理器 - 防止笔记文件过大影响性能"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class DebugNotesManager:
    """管理调试笔记，防止文件过大"""
    
    def __init__(self, work_dir: str, max_size_kb: int = 50):
        self.work_dir = Path(work_dir)
        self.notes_path = self.work_dir / "debug_notes.json"
        self.summary_path = self.work_dir / "debug_summary.json"
        self.archive_dir = self.work_dir / "debug_archive"
        self.max_size = max_size_kb * 1024  # 转换为字节
        
        # 确保归档目录存在
        self.archive_dir.mkdir(exist_ok=True)
        
    def check_and_compress(self) -> bool:
        """检查并压缩调试笔记"""
        if not self.notes_path.exists():
            return False
            
        size = self.notes_path.stat().st_size
        if size > self.max_size:
            print(f"📦 调试笔记超过{self.max_size//1024}KB，正在压缩...")
            self._compress_notes()
            return True
        return False
    
    def _compress_notes(self):
        """压缩调试笔记"""
        with open(self.notes_path, 'r') as f:
            notes = json.load(f)
        
        # 1. 归档当前完整版本
        archive_name = f"debug_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        archive_path = self.archive_dir / archive_name
        shutil.copy(self.notes_path, archive_path)
        print(f"   已归档到: {archive_path}")
        
        # 2. 提取和更新摘要
        self._update_summary(notes)
        
        # 3. 创建压缩版本
        compressed = {
            "session_id": f"debug_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "current_iteration": 0,
            "error_history": {},  # 清空，从摘要中学习
            "fix_attempts": [],    # 清空
            "successful_strategies": self._get_top_strategies(notes, 10),
            "failed_strategies": notes.get('failed_strategies', [])[-5:],
            "test_results_history": []  # 清空
        }
        
        # 4. 保存压缩版本
        with open(self.notes_path, 'w') as f:
            json.dump(compressed, f, indent=2)
        print(f"   压缩完成: {size//1024}KB -> {len(json.dumps(compressed))//1024}KB")
    
    def _update_summary(self, notes: Dict):
        """更新长期摘要"""
        summary = {}
        
        if self.summary_path.exists():
            with open(self.summary_path, 'r') as f:
                summary = json.load(f)
        
        # 初始化摘要结构
        if 'error_patterns' not in summary:
            summary['error_patterns'] = {}
        if 'solution_success_rate' not in summary:
            summary['solution_success_rate'] = {}
        if 'total_sessions' not in summary:
            summary['total_sessions'] = 0
        
        # 更新错误模式统计
        for error in notes.get('error_history', {}).values():
            pattern = error['type']
            summary['error_patterns'][pattern] = \
                summary['error_patterns'].get(pattern, 0) + 1
        
        # 更新解决方案成功率
        for strategy in notes.get('successful_strategies', []):
            pattern = strategy['error_pattern']
            solution = strategy['solution']
            key = f"{pattern}|{solution}"
            
            if key not in summary['solution_success_rate']:
                summary['solution_success_rate'][key] = {
                    'success': 0,
                    'total': 0,
                    'confidence': 0
                }
            
            summary['solution_success_rate'][key]['success'] += \
                strategy.get('success_count', 1)
            summary['solution_success_rate'][key]['total'] += 1
            summary['solution_success_rate'][key]['confidence'] = \
                strategy.get('confidence', 0.95)
        
        summary['total_sessions'] += 1
        summary['last_updated'] = datetime.now().isoformat()
        
        # 保存摘要
        with open(self.summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"   摘要已更新: {self.summary_path}")
    
    def _get_top_strategies(self, notes: Dict, limit: int = 10) -> List[Dict]:
        """获取最有效的策略"""
        strategies = notes.get('successful_strategies', [])
        
        # 按成功率和置信度排序
        sorted_strategies = sorted(
            strategies,
            key=lambda x: (x.get('confidence', 0), x.get('success_count', 0)),
            reverse=True
        )
        
        return sorted_strategies[:limit]
    
    def get_learning_context(self) -> str:
        """获取学习上下文（用于初始化Agent）"""
        context = []
        
        # 1. 加载摘要
        if self.summary_path.exists():
            with open(self.summary_path, 'r') as f:
                summary = json.load(f)
            
            # 添加最常见的错误模式
            top_errors = sorted(
                summary.get('error_patterns', {}).items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            if top_errors:
                context.append("## 常见错误模式")
                for error, count in top_errors:
                    context.append(f"- {error}: {count}次")
            
            # 添加最有效的解决方案
            top_solutions = sorted(
                summary.get('solution_success_rate', {}).items(),
                key=lambda x: x[1]['confidence'] * x[1]['success'],
                reverse=True
            )[:5]
            
            if top_solutions:
                context.append("\n## 最有效的解决方案")
                for key, stats in top_solutions:
                    pattern, solution = key.split('|')
                    success_rate = stats['success'] / max(stats['total'], 1) * 100
                    context.append(
                        f"- {pattern} → {solution} "
                        f"(成功率: {success_rate:.0f}%)"
                    )
        
        # 2. 加载当前笔记的成功策略
        if self.notes_path.exists():
            try:
                with open(self.notes_path, 'r') as f:
                    notes = json.load(f)
                
                if notes.get('successful_strategies'):
                    context.append("\n## 最近成功的策略")
                    for strategy in notes['successful_strategies'][:3]:
                        context.append(
                            f"- {strategy['error_pattern']} → "
                            f"{strategy['solution']}"
                        )
            except:
                pass
        
        return '\n'.join(context) if context else "暂无历史学习记录"
    
    def cleanup_old_archives(self, keep_days: int = 7):
        """清理旧的归档文件"""
        if not self.archive_dir.exists():
            return
        
        cutoff = datetime.now().timestamp() - (keep_days * 24 * 3600)
        cleaned = 0
        
        for archive_file in self.archive_dir.glob("*.json"):
            if archive_file.stat().st_mtime < cutoff:
                archive_file.unlink()
                cleaned += 1
        
        if cleaned > 0:
            print(f"🗑️ 清理了 {cleaned} 个旧归档文件")


# 使用示例
if __name__ == "__main__":
    manager = DebugNotesManager("output/mda_dual_agent_demo")
    
    # 检查并压缩
    manager.check_and_compress()
    
    # 获取学习上下文
    context = manager.get_learning_context()
    print("\n学习上下文：")
    print(context)
    
    # 清理旧归档
    manager.cleanup_old_archives(keep_days=7)