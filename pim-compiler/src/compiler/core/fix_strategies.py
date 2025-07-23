"""测试修复策略配置"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class FixStrategy(Enum):
    """修复策略类型"""
    TRADITIONAL = "traditional"  # 传统的全量修复
    INCREMENTAL = "incremental"  # 增量修复
    HYBRID = "hybrid"  # 混合策略


@dataclass
class FixStrategyConfig:
    """修复策略配置"""
    strategy: FixStrategy = FixStrategy.INCREMENTAL
    
    # 增量修复配置
    batch_size: int = 2  # 每批处理的文件数
    use_cache: bool = True  # 是否使用缓存
    use_patterns: bool = True  # 是否使用错误模式
    quick_test: bool = True  # 是否运行快速测试验证
    
    # 超时配置
    pattern_fix_timeout: int = 60  # 模式修复超时（秒）
    file_fix_timeout: int = 120  # 单文件修复超时（秒）
    full_fix_timeout: int = 300  # 全量修复超时（秒）
    
    # 重试配置
    max_attempts: int = 5  # 最大尝试次数
    stop_on_no_progress: bool = True  # 无进展时停止
    
    @classmethod
    def traditional(cls) -> "FixStrategyConfig":
        """传统策略配置"""
        return cls(
            strategy=FixStrategy.TRADITIONAL,
            use_cache=False,
            use_patterns=False,
            quick_test=False
        )
    
    @classmethod
    def incremental(cls) -> "FixStrategyConfig":
        """增量策略配置"""
        return cls(
            strategy=FixStrategy.INCREMENTAL,
            batch_size=2,
            use_cache=True,
            use_patterns=True,
            quick_test=True
        )
    
    @classmethod
    def aggressive(cls) -> "FixStrategyConfig":
        """激进策略配置（更快但可能不太稳定）"""
        return cls(
            strategy=FixStrategy.INCREMENTAL,
            batch_size=3,
            use_cache=True,
            use_patterns=True,
            quick_test=True,
            pattern_fix_timeout=30,
            file_fix_timeout=60,
            max_attempts=3
        )