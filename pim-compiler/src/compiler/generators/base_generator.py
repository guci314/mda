"""
代码生成器抽象基类
定义了所有代码生成器必须实现的接口
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging


@dataclass
class GeneratorConfig:
    """生成器配置"""
    name: str
    model: str = ""
    api_key: str = ""
    api_base: str = ""
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 300  # 超时时间（秒）
    extra_params: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}


@dataclass
class GenerationResult:
    """生成结果"""
    success: bool
    output_path: Path
    psm_content: Optional[str] = None
    code_files: Optional[Dict[str, str]] = None  # 文件路径 -> 内容
    error_message: Optional[str] = None
    generation_time: float = 0.0
    logs: str = ""
    
    def __post_init__(self):
        if self.code_files is None:
            self.code_files = {}


class BaseGenerator(ABC):
    """代码生成器抽象基类"""
    
    def __init__(self, config: GeneratorConfig):
        """
        初始化生成器
        
        Args:
            config: 生成器配置
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self.setup()
    
    def setup(self):
        """初始化设置，子类可覆盖"""
        pass
    
    @abstractmethod
    def generate_psm(
        self, 
        pim_content: str, 
        platform: str = "fastapi",
        output_dir: Optional[Path] = None
    ) -> GenerationResult:
        """
        从 PIM 生成 PSM
        
        Args:
            pim_content: PIM 内容
            platform: 目标平台
            output_dir: 输出目录
            
        Returns:
            GenerationResult: 生成结果
        """
        pass
    
    @abstractmethod
    def generate_code(
        self, 
        psm_content: str, 
        output_dir: Path,
        platform: str = "fastapi"
    ) -> GenerationResult:
        """
        从 PSM 生成代码
        
        Args:
            psm_content: PSM 内容
            output_dir: 输出目录
            platform: 目标平台
            
        Returns:
            GenerationResult: 生成结果
        """
        pass
    
    def generate_from_pim(
        self,
        pim_content: str,
        output_dir: Path,
        platform: str = "fastapi"
    ) -> Tuple[GenerationResult, GenerationResult]:
        """
        从 PIM 完整生成代码（先生成 PSM，再生成代码）
        
        Args:
            pim_content: PIM 内容
            output_dir: 输出目录
            platform: 目标平台
            
        Returns:
            Tuple[GenerationResult, GenerationResult]: PSM生成结果, 代码生成结果
        """
        # 先生成 PSM
        psm_result = self.generate_psm(pim_content, platform, output_dir)
        if not psm_result.success:
            return psm_result, GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=f"PSM generation failed: {psm_result.error_message}"
            )
        
        # 再生成代码
        if psm_result.psm_content is None:
            return psm_result, GenerationResult(
                success=False,
                output_path=output_dir,
                error_message="PSM content is None"
            )
        code_result = self.generate_code(psm_result.psm_content, output_dir, platform)
        return psm_result, code_result
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.config.name:
            self.logger.error("Generator name is required")
            return False
        return True
    
    def _save_files(self, files: Dict[str, str], output_dir: Path) -> bool:
        """
        保存生成的文件
        
        Args:
            files: 文件路径到内容的映射
            output_dir: 输出目录
            
        Returns:
            bool: 是否成功
        """
        try:
            for file_path, content in files.items():
                full_path = output_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                self.logger.debug(f"Saved file: {full_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save files: {e}")
            return False
    
    def __str__(self):
        return f"{self.__class__.__name__}(name={self.config.name})"
    
    def __repr__(self):
        return f"{self.__class__.__name__}(config={self.config})"