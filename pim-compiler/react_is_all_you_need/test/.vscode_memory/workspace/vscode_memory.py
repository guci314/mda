#!/usr/bin/env python3
"""
VSCode记忆模式 - 基于VSCode的内存管理模式
模拟人类思维的潜意识(文件系统)和显意识(工作界面)

设计理念：
- 潜意识(文件系统): 持久化存储，完整但访问较慢
- 显意识(界面): 内存中的活跃内容，快速访问但容量有限
- 动态分辨率: 根据注意力焦点动态调整信息清晰度
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

class Resolution(Enum):
    """信息分辨率级别"""
    TITLE = 1      # 仅标题 (~10 tokens)
    OUTLINE = 2    # 大纲 (~50 tokens)  
    PREVIEW = 3    # 预览 (~200 tokens)
    FULL = 4       # 完整内容

class VSCodeMemory:
    """VSCode记忆模式实现"""
    
    def __init__(self, workspace_dir: Path, max_context_tokens: int = 262144):
        """
        初始化VSCode记忆系统
        
        Args:
            workspace_dir: 工作目录(潜意识存储位置)
            max_context_tokens: 最大上下文tokens数 (默认262k for Qwen3-Coder)
        """
        self.workspace_dir = Path(workspace_dir)
        self.memory_dir = self.workspace_dir / ".vscode_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 潜意识层 - 文件系统存储
        self.filesystem = {
            "episodes": self.memory_dir / "episodes",      # 事件记忆
            "states": self.memory_dir / "states",         # 状态快照
            "knowledge": self.memory_dir / "knowledge",   # 知识库
            "workspace": self.memory_dir / "workspace"    # 工作文件
        }
        
        # 创建目录结构
        for dir_path in self.filesystem.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 显意识层 - 工作记忆
        self.consciousness = {
            # 结构认知层
            "resource_outline": [],  # 资源大纲(文件树结构、类/函数列表等)
            "overview": [],         # 全局概览(项目摘要、关键指标等)
            
            # 工作记忆层
            "working_set": [],      # 工作集(当前任务涉及的活跃项目)
            "focus_item": None,     # 焦点项(正在编辑/分析的具体内容)
            "detail_view": None,    # 详细视图(焦点项的完整内容)
            
            # 操作记录层
            "action_history": [],   # 行动历史(最近执行的操作)
            "issues": [],           # 待解决问题(错误、警告、TODO等)
            "findings": []          # 发现(搜索结果、分析洞察等)
        }
        
        # 注意力管理
        self.attention = {
            "focus": None,        # 当前焦点
            "context": [],        # 上下文相关项
            "recent": []          # 最近访问
        }
        
        # Token预算管理 - 根据max_context_tokens动态调整
        self.max_tokens = max_context_tokens
        
        # 为大context模型(>100k)调整预算分配
        if max_context_tokens > 100000:
            # Qwen3-Coder等大模型可以分配更多tokens
            self.token_budget = {
                "resource_outline": 3000,  # 资源大纲预算
                "overview": 2000,          # 全局概览预算
                "working_set": 10000,      # 工作集预算
                "detail": 50000,           # 详细内容预算
                "context": 20000,          # 相关上下文预算
                "history": 10000           # 历史记录预算
            }
        else:
            # 标准模型的预算分配
            self.token_budget = {
                "resource_outline": 800,   # 资源大纲预算
                "overview": 500,           # 全局概览预算
                "working_set": 2000,       # 工作集预算
                "detail": 8000,            # 详细内容预算
                "context": 4000,           # 相关上下文预算
                "history": 2000            # 历史记录预算
            }
        
        # 加载或初始化索引
        self.index_file = self.memory_dir / "index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """加载内存索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "files": {},      # 文件索引
            "episodes": [],   # 事件索引
            "states": [],     # 状态索引
            "access_log": []  # 访问日志
        }
    
    def _save_index(self):
        """保存内存索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def _estimate_tokens(self, text: str) -> int:
        """估算文本的token数"""
        # 简化估算: 中文约1.5字符/token, 英文约4字符/token
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + english_chars / 4)
    
    def _get_file_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def _compress_content(self, content: str, resolution: Resolution) -> str:
        """根据分辨率压缩内容"""
        lines = content.split('\n')
        
        if resolution == Resolution.TITLE:
            # 仅返回第一行或标题
            return lines[0][:100] if lines else ""
        
        elif resolution == Resolution.OUTLINE:
            # 返回关键行(函数定义、类定义、注释等)
            outline = []
            for line in lines[:50]:  # 最多前50行
                stripped = line.strip()
                if any(keyword in stripped for keyword in 
                       ['def ', 'class ', '#', '//', '/*', 'function', 'const ', 'let ', 'var ']):
                    outline.append(line)
            return '\n'.join(outline[:10])  # 最多10行
        
        elif resolution == Resolution.PREVIEW:
            # 返回前200个token的内容
            preview = []
            token_count = 0
            for line in lines:
                line_tokens = self._estimate_tokens(line)
                if token_count + line_tokens > 200:
                    break
                preview.append(line)
                token_count += line_tokens
            return '\n'.join(preview)
        
        else:  # FULL
            return content
    
    def save_episode(self, event: str, data: Dict[str, Any]) -> str:
        """
        保存事件到潜意识
        
        Args:
            event: 事件类型
            data: 事件数据
            
        Returns:
            事件ID
        """
        timestamp = datetime.now().isoformat()
        episode_id = f"{event}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        episode = {
            "id": episode_id,
            "timestamp": timestamp,
            "event": event,
            "data": data
        }
        
        # 保存到文件系统
        episode_file = self.filesystem["episodes"] / f"{episode_id}.json"
        with open(episode_file, 'w', encoding='utf-8') as f:
            json.dump(episode, f, indent=2, ensure_ascii=False)
        
        # 更新索引
        self.index["episodes"].append({
            "id": episode_id,
            "timestamp": timestamp,
            "event": event,
            "summary": data.get("summary", "")
        })
        
        # 保持索引大小
        if len(self.index["episodes"]) > 1000:
            self.index["episodes"] = self.index["episodes"][-500:]
        
        self._save_index()
        return episode_id
    
    def save_state(self, state_name: str, state_data: Dict) -> str:
        """
        保存状态快照
        
        Args:
            state_name: 状态名称
            state_data: 状态数据
            
        Returns:
            状态ID
        """
        state_id = f"{state_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        state = {
            "id": state_id,
            "name": state_name,
            "timestamp": datetime.now().isoformat(),
            "data": state_data
        }
        
        # 保存到文件系统
        state_file = self.filesystem["states"] / f"{state_id}.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        # 更新索引
        self.index["states"].append({
            "id": state_id,
            "name": state_name,
            "timestamp": state["timestamp"]
        })
        
        # 保持最近N个状态
        if len(self.index["states"]) > 100:
            self.index["states"] = self.index["states"][-50:]
        
        self._save_index()
        return state_id
    
    def open_file(self, file_path: str, content: str) -> None:
        """
        在编辑器中打开文件(加载到显意识)
        
        Args:
            file_path: 文件路径
            content: 文件内容
        """
        file_hash = self._get_file_hash(content)
        
        # 保存到潜意识(如果是新内容)
        if file_path not in self.index["files"] or \
           self.index["files"][file_path].get("hash") != file_hash:
            
            workspace_file = self.filesystem["workspace"] / Path(file_path).name
            with open(workspace_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.index["files"][file_path] = {
                "path": str(workspace_file),
                "hash": file_hash,
                "size": len(content),
                "tokens": self._estimate_tokens(content),
                "last_access": datetime.now().isoformat()
            }
            self._save_index()
        
        # 更新显意识
        self.consciousness["focus_item"] = file_path
        self.consciousness["detail_view"] = content
        
        # 添加到工作集
        if file_path not in self.consciousness["working_set"]:
            self.consciousness["working_set"].append(file_path)
        
        # 更新注意力
        self.attention["focus"] = file_path
        
        # 记录访问
        self._log_access(file_path)
    
    def _log_access(self, item: str):
        """记录访问日志"""
        self.index["access_log"].append({
            "item": item,
            "timestamp": datetime.now().isoformat()
        })
        
        # 保持日志大小
        if len(self.index["access_log"]) > 1000:
            self.index["access_log"] = self.index["access_log"][-500:]
    
    def search(self, query: str) -> List[Dict]:
        """
        搜索记忆
        
        Args:
            query: 搜索查询
            
        Returns:
            搜索结果列表
        """
        results = []
        
        # 搜索文件
        for file_path, file_info in self.index["files"].items():
            if query.lower() in file_path.lower():
                results.append({
                    "type": "file",
                    "path": file_path,
                    "relevance": 0.8
                })
        
        # 搜索事件
        for episode in self.index["episodes"]:
            if query.lower() in episode.get("event", "").lower() or \
               query.lower() in episode.get("summary", "").lower():
                results.append({
                    "type": "episode",
                    "id": episode["id"],
                    "event": episode["event"],
                    "relevance": 0.6
                })
        
        # 更新发现到显意识
        self.consciousness["findings"] = results[:10]
        
        return results
    
    def focus_on(self, target: str) -> None:
        """
        聚焦到特定目标
        
        Args:
            target: 目标(文件路径、事件ID等)
        """
        self.attention["focus"] = target
        
        # 动态加载相关上下文
        self.attention["context"] = self._find_related(target)
        
        # 更新最近访问
        if target not in self.attention["recent"]:
            self.attention["recent"].insert(0, target)
        
        # 保持最近访问列表大小
        self.attention["recent"] = self.attention["recent"][:20]
    
    def _find_related(self, target: str, max_items: int = 5) -> List[str]:
        """
        查找相关项
        
        Args:
            target: 目标项
            max_items: 最大返回数量
            
        Returns:
            相关项列表
        """
        related = []
        
        # 基于访问日志找相关项
        target_accesses = [log for log in self.index["access_log"] 
                          if log["item"] == target]
        
        if target_accesses:
            last_access_time = target_accesses[-1]["timestamp"]
            
            # 找时间上接近的访问
            for log in self.index["access_log"]:
                if log["item"] != target and \
                   abs((datetime.fromisoformat(log["timestamp"]) - 
                        datetime.fromisoformat(last_access_time)).total_seconds()) < 300:
                    if log["item"] not in related:
                        related.append(log["item"])
        
        return related[:max_items]
    
    def compress_for_llm(self, extra_tokens: int = 0) -> str:
        """
        为LLM压缩当前记忆状态
        
        Args:
            extra_tokens: 额外需要预留的token数
            
        Returns:
            压缩后的记忆状态文本
        """
        available_tokens = self.max_tokens - extra_tokens
        used_tokens = 0
        compressed = []
        
        # 1. 当前焦点(最高优先级)
        if self.attention["focus"] and self.consciousness["detail_view"]:
            focus_content = self._compress_content(
                self.consciousness["detail_view"],
                Resolution.FULL if available_tokens > 10000 else Resolution.PREVIEW
            )
            focus_tokens = self._estimate_tokens(focus_content)
            
            if used_tokens + focus_tokens < available_tokens:
                compressed.append(f"=== 当前焦点: {self.attention['focus']} ===\n{focus_content}")
                used_tokens += focus_tokens
        
        # 2. 工作集(中优先级)
        if self.consciousness["working_set"]:
            compressed.append("\n=== 工作集 ===")
            for item in self.consciousness["working_set"]:
                if item == self.attention["focus"]:
                    continue
                
                # 从潜意识加载摘要
                if item in self.index["files"]:
                    file_info = self.index["files"][item]
                    item_summary = f"- {item} ({file_info['size']} bytes, {file_info['tokens']} tokens)"
                    item_tokens = self._estimate_tokens(item_summary)
                    
                    if used_tokens + item_tokens < available_tokens:
                        compressed.append(item_summary)
                        used_tokens += item_tokens
        
        # 3. 资源大纲(低优先级)
        if self.consciousness["resource_outline"]:
            compressed.append("\n=== 资源大纲 ===")
            outline_text = "\n".join(self.consciousness["resource_outline"][:30])
            outline_tokens = self._estimate_tokens(outline_text)
            
            if used_tokens + outline_tokens < available_tokens:
                compressed.append(outline_text)
                used_tokens += outline_tokens
        
        # 4. 全局概览
        if self.consciousness["overview"]:
            compressed.append("\n=== 项目概览 ===")
            overview_text = "\n".join(self.consciousness["overview"][:10])
            overview_tokens = self._estimate_tokens(overview_text)
            
            if used_tokens + overview_tokens < available_tokens:
                compressed.append(overview_text)
                used_tokens += overview_tokens
        
        # 5. 最近事件
        if self.index["episodes"]:
            compressed.append("\n=== 最近事件 ===")
            recent_episodes = self.index["episodes"][-5:]
            for episode in recent_episodes:
                episode_text = f"- [{episode['timestamp'][:10]}] {episode['event']}: {episode.get('summary', '')[:50]}"
                episode_tokens = self._estimate_tokens(episode_text)
                
                if used_tokens + episode_tokens < available_tokens:
                    compressed.append(episode_text)
                    used_tokens += episode_tokens
        
        # 6. 发现
        if self.consciousness["findings"]:
            compressed.append("\n=== 发现 ===")
            for result in self.consciousness["findings"][:5]:
                result_text = f"- {result['type']}: {result.get('path', result.get('id', ''))}"
                result_tokens = self._estimate_tokens(result_text)
                
                if used_tokens + result_tokens < available_tokens:
                    compressed.append(result_text)
                    used_tokens += result_tokens
        
        return "\n".join(compressed)
    
    def garbage_collect(self, keep_recent: int = 100):
        """
        垃圾回收 - 清理旧的记忆
        
        Args:
            keep_recent: 保留最近N个项目
        """
        # 清理旧事件
        episode_files = sorted(self.filesystem["episodes"].glob("*.json"))
        if len(episode_files) > keep_recent:
            for f in episode_files[:-keep_recent]:
                f.unlink()
        
        # 清理旧状态
        state_files = sorted(self.filesystem["states"].glob("*.json"))
        if len(state_files) > keep_recent // 2:
            for f in state_files[:-keep_recent//2]:
                f.unlink()
        
        # 更新索引
        self.index["episodes"] = self.index["episodes"][-keep_recent:]
        self.index["states"] = self.index["states"][-keep_recent//2:]
        self.index["access_log"] = self.index["access_log"][-keep_recent*10:]
        
        self._save_index()
    
    def export_session(self) -> Dict:
        """导出当前会话状态"""
        return {
            "timestamp": datetime.now().isoformat(),
            "consciousness": self.consciousness,
            "attention": self.attention,
            "memory_stats": {
                "files": len(self.index["files"]),
                "episodes": len(self.index["episodes"]),
                "states": len(self.index["states"]),
                "working_set_size": len(self.consciousness["working_set"]),
                "current_focus": self.consciousness["focus_item"]
            }
        }
    
    def import_session(self, session_data: Dict):
        """导入会话状态"""
        if "consciousness" in session_data:
            self.consciousness = session_data["consciousness"]
        if "attention" in session_data:
            self.attention = session_data["attention"]