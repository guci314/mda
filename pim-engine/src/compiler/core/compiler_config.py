"""Compiler configuration"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CompilerConfig:
    """编译器配置"""
    
    # 基础路径配置
    pim_home: Path = field(default_factory=lambda: Path(os.getenv("PIM_HOME", "/opt/pim-engine")))
    classpath_dirs: List[Path] = field(default_factory=list)
    output_dir: Optional[Path] = None
    
    # LLM配置
    llm_provider: str = "deepseek"  # deepseek, gemini, openai
    llm_model: str = "deepseek-chat"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 8192
    
    # API配置
    deepseek_api_key: Optional[str] = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY"))
    deepseek_base_url: str = "https://api.deepseek.com"
    gemini_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    
    # 编译选项
    target_platform: str = "fastapi"  # fastapi, spring, django
    enable_cache: bool = True
    cache_dir: Path = field(default_factory=lambda: Path(".pim_cache"))
    enable_validation: bool = True
    enable_optimization: bool = True
    generate_code: bool = False  # 是否生成代码（除了PSM）
    
    # 代码质量选项
    enable_lint: bool = True  # 是否进行 lint 检查
    auto_fix_lint: bool = True  # 是否自动修复 lint 错误
    enable_unit_tests: bool = True  # 是否生成单元测试
    run_tests: bool = True  # 是否运行生成的测试
    auto_fix_tests: bool = True  # 是否自动修复失败的测试
    min_test_coverage: float = 80.0  # 最低测试覆盖率要求
    
    # 调试选项
    debug: bool = False
    verbose: bool = False
    save_intermediate: bool = False  # 保存中间表示
    
    # 提示模板配置
    prompt_templates_dir: Optional[Path] = None
    use_few_shot: bool = True
    few_shot_examples: int = 3
    
    # 并发配置
    max_concurrent_compilations: int = 4
    compilation_timeout: int = 300  # 秒
    
    def __post_init__(self):
        """初始化后处理"""
        # 设置默认classpath
        if not self.classpath_dirs:
            self.classpath_dirs = [
                self.pim_home / "classpath" / "models",
                self.pim_home / "classpath" / "lib"
            ]
        
        # 设置默认输出目录
        if not self.output_dir:
            self.output_dir = self.pim_home / "classpath" / "models"
        
        # 创建必要的目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置提示模板目录
        if not self.prompt_templates_dir:
            self.prompt_templates_dir = Path(__file__).parent.parent / "templates"
    
    def validate(self) -> List[str]:
        """验证配置的有效性"""
        errors = []
        
        # 检查LLM配置
        if self.llm_provider == "deepseek" and not self.deepseek_api_key:
            errors.append("使用DeepSeek时必须设置DEEPSEEK_API_KEY")
        elif self.llm_provider == "gemini" and not self.gemini_api_key:
            errors.append("使用Gemini时必须设置GEMINI_API_KEY")
        elif self.llm_provider == "openai" and not self.openai_api_key:
            errors.append("使用OpenAI时必须设置OPENAI_API_KEY")
        
        # 检查目标平台
        supported_platforms = ["fastapi", "spring", "django", "flask", "express"]
        if self.target_platform not in supported_platforms:
            errors.append(f"不支持的目标平台: {self.target_platform}")
        
        # 检查路径
        for classpath in self.classpath_dirs:
            if not classpath.exists():
                errors.append(f"Classpath目录不存在: {classpath}")
        
        return errors
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'CompilerConfig':
        """从字典创建配置"""
        # 转换路径字符串为Path对象
        if "pim_home" in config_dict:
            config_dict["pim_home"] = Path(config_dict["pim_home"])
        if "classpath_dirs" in config_dict:
            config_dict["classpath_dirs"] = [Path(p) for p in config_dict["classpath_dirs"]]
        if "output_dir" in config_dict:
            config_dict["output_dir"] = Path(config_dict["output_dir"])
        if "cache_dir" in config_dict:
            config_dict["cache_dir"] = Path(config_dict["cache_dir"])
        if "prompt_templates_dir" in config_dict:
            config_dict["prompt_templates_dir"] = Path(config_dict["prompt_templates_dir"])
        
        return cls(**config_dict)
    
    @classmethod
    def from_env(cls) -> 'CompilerConfig':
        """从环境变量创建配置"""
        config = cls()
        
        # 从环境变量覆盖配置
        if os.getenv("PIM_CLASSPATH"):
            config.classpath_dirs = [Path(p) for p in os.getenv("PIM_CLASSPATH").split(":")]
        if os.getenv("PIM_OUTPUT"):
            config.output_dir = Path(os.getenv("PIM_OUTPUT"))
        if os.getenv("PIM_PLATFORM"):
            config.target_platform = os.getenv("PIM_PLATFORM")
        if os.getenv("PIM_LLM_PROVIDER"):
            config.llm_provider = os.getenv("PIM_LLM_PROVIDER")
        if os.getenv("PIM_DEBUG"):
            config.debug = os.getenv("PIM_DEBUG").lower() in ["true", "1", "yes"]
        if os.getenv("PIM_VERBOSE"):
            config.verbose = os.getenv("PIM_VERBOSE").lower() in ["true", "1", "yes"]
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "pim_home": str(self.pim_home),
            "classpath_dirs": [str(p) for p in self.classpath_dirs],
            "output_dir": str(self.output_dir) if self.output_dir else None,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "llm_max_tokens": self.llm_max_tokens,
            "target_platform": self.target_platform,
            "enable_cache": self.enable_cache,
            "cache_dir": str(self.cache_dir),
            "enable_validation": self.enable_validation,
            "enable_optimization": self.enable_optimization,
            "generate_code": self.generate_code,
            "debug": self.debug,
            "verbose": self.verbose,
            "save_intermediate": self.save_intermediate,
            "use_few_shot": self.use_few_shot,
            "few_shot_examples": self.few_shot_examples,
            "max_concurrent_compilations": self.max_concurrent_compilations,
            "compilation_timeout": self.compilation_timeout
        }