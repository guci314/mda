"""
可配置的编译器实现
支持使用不同的代码生成器后端
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import shutil

from ..config import CompilerConfig
from ..generators import GeneratorFactory, GeneratorConfig, BaseGenerator
from utils.logger import get_logger

logger = get_logger(__name__)


class ConfigurableCompiler:
    """可配置的编译器
    
    支持多种代码生成器：
    - gemini-cli: 使用 Gemini CLI 命令行工具
    - react-agent: 使用 LangChain React Agent
    - autogen: 使用 Microsoft Autogen
    """
    
    def __init__(self, config: CompilerConfig):
        self.config = config
        self.generator = self._create_generator()
        logger.info(f"Initialized ConfigurableCompiler with generator: {config.generator_type}")
    
    def _create_generator(self) -> BaseGenerator:
        """创建代码生成器"""
        # 创建生成器配置
        generator_config = GeneratorConfig(
            name=self.config.generator_type,
            model=self.config.gemini_model if self.config.generator_type == "gemini-cli" else None,
            timeout=self.config.timeout,
            extra_params={
                "target_platform": self.config.target_platform,
                "generate_tests": self.config.generate_tests,
                "generate_docs": self.config.generate_docs
            }
        )
        
        # 使用工厂创建生成器
        return GeneratorFactory.create_generator(
            self.config.generator_type,
            generator_config
        )
    
    def compile(self, pim_file: Path) -> Dict[str, Any]:
        """编译 PIM 文件
        
        Args:
            pim_file: PIM 文件路径
            
        Returns:
            Dict[str, Any]: 编译结果
        """
        start_time = datetime.now()
        logger.info(f"Starting compilation of {pim_file}")
        logger.info(f"Using generator: {self.config.generator_type}")
        logger.info(f"Target platform: {self.config.target_platform}")
        
        # 确保 PIM 文件存在
        if not pim_file.exists():
            return {
                "success": False,
                "error": f"PIM file not found: {pim_file}",
                "pim_file": str(pim_file)
            }
        
        # 读取 PIM 内容
        try:
            pim_content = pim_file.read_text(encoding='utf-8')
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read PIM file: {e}",
                "pim_file": str(pim_file)
            }
        
        # 创建输出目录
        output_dir = self.config.output_dir / f"{pim_file.stem}_{self.config.generator_type}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 步骤 1: 生成 PSM
        logger.info("Step 1: Generating PSM...")
        psm_start = time.time()
        
        psm_result = self.generator.generate_psm(
            pim_content,
            self.config.target_platform,
            output_dir
        )
        
        if not psm_result.success:
            return {
                "success": False,
                "error": f"PSM generation failed: {psm_result.error_message}",
                "pim_file": str(pim_file),
                "output_dir": str(output_dir),
                "psm_generation_time": time.time() - psm_start
            }
        
        psm_time = time.time() - psm_start
        logger.info(f"PSM generated in {psm_time:.2f} seconds")
        
        # 保存 PSM 文件
        psm_file = output_dir / f"{pim_file.stem}_psm.md"
        if psm_result.psm_content:
            psm_file.write_text(psm_result.psm_content, encoding='utf-8')
        
        # 步骤 2: 生成代码
        logger.info("Step 2: Generating code...")
        code_start = time.time()
        
        code_result = self.generator.generate_code(
            psm_result.psm_content,
            output_dir / "generated",
            self.config.target_platform
        )
        
        if not code_result.success:
            return {
                "success": False,
                "error": f"Code generation failed: {code_result.error_message}",
                "pim_file": str(pim_file),
                "psm_file": str(psm_file),
                "output_dir": str(output_dir),
                "psm_generation_time": psm_time,
                "code_generation_time": time.time() - code_start
            }
        
        code_time = time.time() - code_start
        logger.info(f"Code generated in {code_time:.2f} seconds")
        
        # 统计生成的文件
        generated_files = len(code_result.code_files) if code_result.code_files else 0
        py_files = sum(1 for f in code_result.code_files if f.endswith('.py'))
        
        # 步骤 3: 运行测试（如果启用）
        test_results = None
        if self.config.auto_test and self.config.generator_type == "gemini-cli":
            logger.info("Step 3: Running tests...")
            # 这里可以调用原有的测试逻辑
            # test_results = self._run_tests(output_dir / "generated")
            logger.info("Test execution skipped for non-gemini-cli generators")
        
        # 计算总时间
        total_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "pim_file": str(pim_file),
            "psm_file": str(psm_file),
            "output_dir": str(output_dir),
            "generator_type": self.config.generator_type,
            "target_platform": self.config.target_platform,
            "psm_generation_time": psm_time,
            "code_generation_time": code_time,
            "total_compilation_time": total_time,
            "statistics": {
                "total_files": generated_files,
                "python_files": py_files,
                "psm_size": len(psm_result.psm_content) if psm_result.psm_content else 0,
                "total_code_size": sum(len(content) for content in code_result.code_files.values()) if code_result.code_files else 0
            },
            "test_results": test_results,
            "psm_logs": psm_result.logs,
            "code_logs": code_result.logs
        }
    
    def compile_batch(self, pim_files: list[Path]) -> Dict[str, Any]:
        """批量编译多个 PIM 文件
        
        Args:
            pim_files: PIM 文件列表
            
        Returns:
            Dict[str, Any]: 批量编译结果
        """
        results = []
        total_start = datetime.now()
        
        for pim_file in pim_files:
            logger.info(f"Compiling {pim_file} ({pim_files.index(pim_file) + 1}/{len(pim_files)})")
            result = self.compile(pim_file)
            results.append(result)
            
            # 如果某个文件失败且配置要求停止，则停止批处理
            if not result["success"] and self.config.fail_on_test_failure:
                logger.error(f"Compilation failed for {pim_file}, stopping batch")
                break
        
        total_time = (datetime.now() - total_start).total_seconds()
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "total_files": len(pim_files),
            "processed_files": len(results),
            "success_count": success_count,
            "failure_count": len(results) - success_count,
            "total_time": total_time,
            "generator_type": self.config.generator_type,
            "results": results
        }
    
    def get_supported_generators(self) -> Dict[str, str]:
        """获取支持的生成器列表"""
        return GeneratorFactory.list_generators()
    
    def switch_generator(self, generator_type: str):
        """切换生成器类型
        
        Args:
            generator_type: 新的生成器类型
        """
        self.config.generator_type = generator_type
        self.generator = self._create_generator()
        logger.info(f"Switched to generator: {generator_type}")