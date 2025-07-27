"""
编译器工厂 - 创建合适的编译器实例
"""
from pathlib import Path
from typing import Optional

from .config import CompilerConfig
from .core.pure_gemini_compiler import PureGeminiCompiler
from .core.configurable_compiler import ConfigurableCompiler
from utils.logger import get_logger

logger = get_logger(__name__)


class CompilerFactory:
    """编译器工厂类"""
    
    @staticmethod
    def create_compiler(config: Optional[CompilerConfig] = None) -> PureGeminiCompiler:
        """创建编译器实例
        
        Args:
            config: 编译器配置，如果为 None 则使用默认配置
            
        Returns:
            编译器实例
        """
        if config is None:
            config = CompilerConfig()
        
        # 检查是否指定了 generator_type
        if hasattr(config, 'generator_type') and config.generator_type and config.generator_type != 'gemini-cli':
            logger.info(f"Creating Configurable compiler with generator: {config.generator_type}")
            logger.info(f"  - Target platform: {config.target_platform}")
            logger.info(f"  - Output directory: {config.output_dir}")
            logger.info(f"  - Generator type: {config.generator_type}")
            logger.info(f"  - Auto test: {config.auto_test}")
            logger.info(f"  - Auto fix lint: {config.auto_fix_lint}")
            logger.info(f"  - Auto fix tests: {config.auto_fix_tests}")
            
            # 使用可配置编译器（支持多种生成器）
            return ConfigurableCompiler(config)
        else:
            logger.info(f"Creating Pure Gemini compiler with configuration:")
            logger.info(f"  - Target platform: {config.target_platform}")
            logger.info(f"  - Output directory: {config.output_dir}")
            logger.info(f"  - Gemini model: {config.gemini_model}")
            logger.info(f"  - Auto test: {config.auto_test}")
            logger.info(f"  - Auto fix lint: {config.auto_fix_lint}")
            logger.info(f"  - Auto fix tests: {config.auto_fix_tests}")
            
            # 默认使用纯 Gemini 编译器
            return PureGeminiCompiler(config)
    
    @staticmethod
    def compile_file(
        pim_file: Path,
        output_dir: Optional[Path] = None,
        target_platform: str = "fastapi",
        **kwargs
    ) -> bool:
        """便捷方法：直接编译文件
        
        Args:
            pim_file: PIM 文件路径
            output_dir: 输出目录
            target_platform: 目标平台
            **kwargs: 其他配置参数
            
        Returns:
            是否编译成功
        """
        # 创建配置
        config_dict = {
            "target_platform": target_platform,
            **kwargs
        }
        
        if output_dir:
            config_dict["output_dir"] = output_dir
            
        config = CompilerConfig(**config_dict)
        
        # 创建编译器并编译
        compiler = CompilerFactory.create_compiler(config)
        result = compiler.compile(pim_file)
        
        return result.success