"""
文件缓存优化器 - 减少重复文件读取
"""
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class CachedFile:
    """缓存文件信息"""
    path: str
    content: str
    timestamp: float
    size: int
    access_count: int = 1
    
    
class FileCacheOptimizer:
    """文件缓存优化器
    
    功能：
    1. 跟踪已读取的文件
    2. 提供缓存状态摘要
    3. 建议是否需要重新读取
    4. 维护访问统计
    """
    
    def __init__(self, cache_ttl: int = 3600):  # 默认缓存1小时
        self.cache: Dict[str, CachedFile] = {}
        self.cache_ttl = cache_ttl
        
    def add_file(self, path: str, content: str) -> None:
        """添加文件到缓存"""
        if path in self.cache:
            # 更新现有缓存
            self.cache[path].content = content
            self.cache[path].timestamp = time.time()
            self.cache[path].size = len(content)
            # 注意：添加文件时不增加访问计数，只有在 get_file 时才增加
        else:
            # 新增缓存
            self.cache[path] = CachedFile(
                path=path,
                content=content,
                timestamp=time.time(),
                size=len(content),
                access_count=0  # 初始访问次数为0，只在读取时增加
            )
        logger.debug(f"Cached file: {path}")
        
    def get_file(self, path: str) -> Optional[str]:
        """从缓存获取文件内容"""
        if path in self.cache:
            cached = self.cache[path]
            # 检查是否过期
            if time.time() - cached.timestamp < self.cache_ttl:
                cached.access_count += 1
                logger.debug(f"Cache hit: {path} (access count: {cached.access_count})")
                return cached.content
            else:
                logger.debug(f"Cache expired: {path}")
                del self.cache[path]
        return None
        
    def has_file(self, path: str) -> bool:
        """检查文件是否在缓存中"""
        return path in self.cache and (time.time() - self.cache[path].timestamp < self.cache_ttl)
        
    def get_cache_summary(self) -> str:
        """获取缓存状态摘要，用于提示词"""
        if not self.cache:
            return "当前没有缓存的文件。"
            
        summary = "已缓存的文件：\n"
        for path, cached in self.cache.items():
            age = int(time.time() - cached.timestamp)
            summary += f"  - {path} ({cached.size} 字节, {age}秒前缓存, 访问{cached.access_count}次)\n"
        return summary
        
    def get_frequent_files(self, threshold: int = 2) -> List[str]:
        """获取频繁访问的文件列表"""
        return [
            path for path, cached in self.cache.items() 
            if cached.access_count >= threshold
        ]
        
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if not self.cache:
            return {
                "total_files": 0,
                "total_size": 0,
                "frequent_files": [],
                "access_stats": {}
            }
            
        total_size = sum(cached.size for cached in self.cache.values())
        access_stats = {
            path: cached.access_count 
            for path, cached in self.cache.items()
        }
        
        return {
            "total_files": len(self.cache),
            "total_size": total_size,
            "frequent_files": self.get_frequent_files(),
            "access_stats": access_stats
        }
        
    def clear_expired(self) -> int:
        """清理过期缓存，返回清理的文件数"""
        current_time = time.time()
        expired = [
            path for path, cached in self.cache.items()
            if current_time - cached.timestamp >= self.cache_ttl
        ]
        for path in expired:
            del self.cache[path]
        return len(expired)
        
    def suggest_action(self, path: str) -> Dict[str, Any]:
        """建议对文件的操作"""
        if self.has_file(path):
            cached = self.cache[path]
            return {
                "should_read": False,
                "reason": f"文件已缓存，{int(time.time() - cached.timestamp)}秒前读取",
                "cached_content_preview": cached.content[:200] + "..." if len(cached.content) > 200 else cached.content
            }
        else:
            return {
                "should_read": True,
                "reason": "文件未缓存或已过期"
            }


def integrate_cache_with_action_decider(
    action_decider_prompt: str,
    file_cache: FileCacheOptimizer,
    requested_files: Set[str] = None
) -> str:
    """将缓存信息集成到动作决策提示词中"""
    
    cache_section = "\n\n文件缓存状态：\n"
    cache_section += file_cache.get_cache_summary()
    
    # 如果有特定请求的文件，检查是否已缓存
    if requested_files:
        cache_section += "\n请求文件的缓存状态：\n"
        for file_path in requested_files:
            suggestion = file_cache.suggest_action(file_path)
            if not suggestion["should_read"]:
                cache_section += f"  - {file_path}: ✓ 已缓存 ({suggestion['reason']})\n"
            else:
                cache_section += f"  - {file_path}: ✗ 需要读取 ({suggestion['reason']})\n"
    
    # 添加优化建议
    stats = file_cache.get_cache_stats()
    if stats["frequent_files"]:
        cache_section += f"\n注意：以下文件被频繁访问，应优先使用缓存：{', '.join(stats['frequent_files'])}\n"
    
    # 在决策原则后插入缓存信息
    enhanced_prompt = action_decider_prompt.replace(
        "决策原则：",
        f"决策原则：{cache_section}\n决策原则："
    )
    
    return enhanced_prompt