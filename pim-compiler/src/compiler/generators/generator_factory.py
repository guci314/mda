"""
代码生成器工厂类
用于创建和管理不同类型的代码生成器
"""

import os
from typing import Dict, Type, Optional
from pathlib import Path
import logging

from .base_generator import BaseGenerator, GeneratorConfig
from .impl import GeminiCLIGenerator, ReactAgentGenerator, AutogenGenerator, AUTOGEN_AVAILABLE, FunctionCallAgentGenerator, SimpleFunctionCallGenerator


logger = logging.getLogger(__name__)


class GeneratorFactory:
    """代码生成器工厂"""
    
    # 注册的生成器类型
    _generators: Dict[str, Type[BaseGenerator]] = {
        "gemini-cli": GeminiCLIGenerator,
        "gemini_cli": GeminiCLIGenerator,
        "react-agent": ReactAgentGenerator,
        "react_agent": ReactAgentGenerator,
        "function-call": FunctionCallAgentGenerator,
        "function_call": FunctionCallAgentGenerator,
        "simple-function-call": SimpleFunctionCallGenerator,
        "simple_function_call": SimpleFunctionCallGenerator,
    }
    
    # 只有在 Autogen 可用时才注册
    if AUTOGEN_AVAILABLE:
        _generators["autogen"] = AutogenGenerator
    
    @classmethod
    def register_generator(cls, name: str, generator_class: Type[BaseGenerator]):
        """注册新的生成器类型
        
        Args:
            name: 生成器名称
            generator_class: 生成器类
        """
        cls._generators[name.lower()] = generator_class
        logger.info(f"Registered generator: {name}")
    
    @classmethod
    def create_generator(
        cls, 
        generator_type: str,
        config: Optional[GeneratorConfig] = None
    ) -> BaseGenerator:
        """创建生成器实例
        
        Args:
            generator_type: 生成器类型
            config: 生成器配置，如果为空则使用默认配置
            
        Returns:
            BaseGenerator: 生成器实例
            
        Raises:
            ValueError: 如果生成器类型未注册
        """
        generator_type = generator_type.lower()
        
        if generator_type not in cls._generators:
            available = ", ".join(sorted(cls._generators.keys()))
            raise ValueError(
                f"Unknown generator type: {generator_type}. "
                f"Available types: {available}"
            )
        
        # 如果没有提供配置，创建默认配置
        if config is None:
            config = cls._create_default_config(generator_type)
        
        generator_class = cls._generators[generator_type]
        logger.info(f"Creating generator: {generator_type}")
        
        return generator_class(config)
    
    @classmethod
    def create_from_env(cls, generator_type: Optional[str] = None) -> BaseGenerator:
        """从环境变量创建生成器
        
        Args:
            generator_type: 生成器类型，如果为空则从环境变量读取
            
        Returns:
            BaseGenerator: 生成器实例
        """
        # 确定生成器类型
        if generator_type is None:
            generator_type = os.getenv("CODE_GENERATOR_TYPE", "gemini-cli")
        
        # 创建配置
        config = cls._create_config_from_env(generator_type)
        
        return cls.create_generator(generator_type, config)
    
    @classmethod
    def list_generators(cls) -> Dict[str, str]:
        """列出所有可用的生成器
        
        Returns:
            Dict[str, str]: 生成器名称到描述的映射
        """
        descriptions = {
            "gemini-cli": "Gemini CLI based generator (command line interface)",
            "react-agent": "LangChain React Agent based generator",
            "autogen": "Microsoft Autogen multi-agent based generator",
            "function-call": "Function Call API based generator (OpenAI compatible)",
            "simple-function-call": "Simple Function Call API based generator (JSON response)"
        }
        
        result = {}
        for name in sorted(cls._generators.keys()):
            if name.replace("-", "_") not in result:  # 避免重复
                result[name] = descriptions.get(name, "Custom generator")
        
        return result
    
    @classmethod
    def _create_default_config(cls, generator_type: str) -> GeneratorConfig:
        """创建默认配置
        
        Args:
            generator_type: 生成器类型
            
        Returns:
            GeneratorConfig: 默认配置
        """
        base_config = GeneratorConfig(
            name=generator_type,
            temperature=0.1,
            max_tokens=4000,
            timeout=300
        )
        
        # 根据生成器类型设置特定配置
        if generator_type in ["gemini-cli", "gemini_cli"]:
            base_config.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            
        elif generator_type in ["react-agent", "react_agent"]:
            base_config.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            base_config.api_key = os.getenv("DEEPSEEK_API_KEY")
            base_config.api_base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
            base_config.extra_params = {"max_iterations": 50}
            
        elif generator_type == "autogen":
            base_config.model = os.getenv("OPENAI_MODEL", "gpt-4")
            base_config.api_key = os.getenv("OPENAI_API_KEY")
            base_config.api_base = os.getenv("OPENAI_API_BASE")
            
        elif generator_type in ["function-call", "function_call"]:
            base_config.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            base_config.api_key = os.getenv("DEEPSEEK_API_KEY")
            base_config.api_base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
            
        elif generator_type in ["simple-function-call", "simple_function_call"]:
            base_config.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            base_config.api_key = os.getenv("DEEPSEEK_API_KEY")
            base_config.api_base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
            
        return base_config
    
    @classmethod
    def _create_config_from_env(cls, generator_type: str) -> GeneratorConfig:
        """从环境变量创建配置
        
        Args:
            generator_type: 生成器类型
            
        Returns:
            GeneratorConfig: 配置对象
        """
        config = cls._create_default_config(generator_type)
        
        # 通用环境变量覆盖
        if os.getenv("CODE_GENERATOR_MODEL"):
            config.model = os.getenv("CODE_GENERATOR_MODEL")
        
        if os.getenv("CODE_GENERATOR_API_KEY"):
            config.api_key = os.getenv("CODE_GENERATOR_API_KEY")
        
        if os.getenv("CODE_GENERATOR_API_BASE"):
            config.api_base = os.getenv("CODE_GENERATOR_API_BASE")
        
        if os.getenv("CODE_GENERATOR_TEMPERATURE"):
            config.temperature = float(os.getenv("CODE_GENERATOR_TEMPERATURE"))
        
        if os.getenv("CODE_GENERATOR_MAX_TOKENS"):
            config.max_tokens = int(os.getenv("CODE_GENERATOR_MAX_TOKENS"))
        
        if os.getenv("CODE_GENERATOR_TIMEOUT"):
            config.timeout = int(os.getenv("CODE_GENERATOR_TIMEOUT"))
        
        return config


# 便捷函数
def create_generator(
    generator_type: str = None,
    **kwargs
) -> BaseGenerator:
    """创建生成器的便捷函数
    
    Args:
        generator_type: 生成器类型，默认从环境变量读取
        **kwargs: 传递给 GeneratorConfig 的参数
        
    Returns:
        BaseGenerator: 生成器实例
    """
    if generator_type is None:
        generator_type = os.getenv("CODE_GENERATOR_TYPE", "gemini-cli")
    
    if kwargs:
        config = GeneratorConfig(name=generator_type, **kwargs)
        return GeneratorFactory.create_generator(generator_type, config)
    else:
        return GeneratorFactory.create_from_env(generator_type)