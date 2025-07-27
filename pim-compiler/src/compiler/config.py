"""
编译器配置
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class CompilerConfig:
    """编译器配置类"""
    
    # 基本配置
    target_platform: str = "fastapi"  # 目标平台: fastapi, django, flask, spring, express
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    
    # 生成器配置
    generator_type: str = field(default_factory=lambda: os.getenv("CODE_GENERATOR_TYPE", "gemini-cli"))  # 生成器类型: gemini-cli, react-agent, autogen
    
    # Gemini 配置
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"))
    gemini_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    
    # 编译选项
    enable_cache: bool = True  # 是否启用缓存
    verbose: bool = True  # 是否输出详细日志
    
    # 测试和修复选项
    auto_test: bool = True  # 是否自动运行测试
    enable_lint: bool = False  # 是否启用 lint 检查（默认禁用以避免超时）
    auto_fix_lint: bool = True  # 是否自动修复 lint 错误
    auto_fix_tests: bool = True  # 是否自动修复测试错误
    lint_fix_mode: str = "critical"  # lint 修复模式: "all" (修复所有), "critical" (只修复关键错误), "skip" (跳过修复)
    fail_on_test_failure: bool = True  # 测试失败时是否让编译失败（默认True）
    min_test_pass_rate: float = 1.0  # 最低测试通过率（0.0-1.0），低于此值编译失败
    enable_coverage: bool = False  # 是否启用测试覆盖率（默认False）
    
    # 代码生成选项
    generate_tests: bool = True  # 是否生成单元测试
    generate_docs: bool = True  # 是否生成文档
    
    # 高级选项
    max_retries: int = 3  # 最大重试次数
    timeout: int = 600  # 超时时间（秒）
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保输出目录存在
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查 Gemini API key（虽然 Gemini CLI 可能使用其他认证方式）
        if not self.gemini_api_key and not os.getenv("GOOGLE_API_KEY"):
            logger.warning("Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set. Gemini CLI might use other authentication methods.")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "target_platform": self.target_platform,
            "output_dir": str(self.output_dir),
            "generator_type": self.generator_type,
            "gemini_model": self.gemini_model,
            "enable_cache": self.enable_cache,
            "verbose": self.verbose,
            "auto_test": self.auto_test,
            "enable_lint": self.enable_lint,
            "auto_fix_lint": self.auto_fix_lint,
            "auto_fix_tests": self.auto_fix_tests,
            "lint_fix_mode": self.lint_fix_mode,
            "fail_on_test_failure": self.fail_on_test_failure,
            "min_test_pass_rate": self.min_test_pass_rate,
            "enable_coverage": self.enable_coverage,
            "generate_tests": self.generate_tests,
            "generate_docs": self.generate_docs,
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }