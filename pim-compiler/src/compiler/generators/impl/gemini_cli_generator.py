"""
Gemini CLI 代码生成器实现
基于命令行调用 Gemini CLI 进行代码生成
"""

import os
import subprocess
import shutil
import time
from pathlib import Path
from typing import Optional, Dict, List
import logging

from ..base_generator import BaseGenerator, GeneratorConfig, GenerationResult
from ...core.prompts import (
    PSM_GENERATION_PROMPT,
    CODE_GENERATION_PROMPT,
    TEST_FIX_PROMPT,
    STARTUP_FIX_PROMPT,
    INCREMENTAL_FIX_PROMPT,
    FILE_SPECIFIC_FIX_PROMPT
)


class GeminiCLIGenerator(BaseGenerator):
    """Gemini CLI 代码生成器
    
    使用 Gemini CLI 命令行工具进行代码生成
    """
    
    def __init__(self, config: GeneratorConfig):
        """初始化 Gemini CLI 生成器"""
        super().__init__(config)
        self.gemini_cli_path = self._find_gemini_cli()
        self.model = config.model or os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
        
    def _find_gemini_cli(self) -> str:
        """查找 Gemini CLI 路径"""
        # 尝试常见路径
        possible_paths = [
            "/home/guci/.nvm/versions/node/v22.17.0/bin/gemini",
            os.path.expanduser("~/.local/bin/gemini"),
            "/usr/local/bin/gemini",
            "/usr/bin/gemini"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Found Gemini CLI at: {path}")
                return path
        
        # 使用系统 PATH
        gemini_path = shutil.which("gemini")
        if gemini_path:
            self.logger.info(f"Found Gemini CLI in PATH: {gemini_path}")
            return gemini_path
        
        raise RuntimeError("Gemini CLI not found. Please install it from: https://github.com/GoogleCloudPlatform/gemini-cli")
    
    def generate_psm(
        self, 
        pim_content: str, 
        platform: str = "fastapi",
        output_dir: Path = None
    ) -> GenerationResult:
        """从 PIM 生成 PSM"""
        start_time = time.time()
        
        if output_dir is None:
            output_dir = Path.cwd()
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建临时 PIM 文件
        pim_file = output_dir / "temp_pim.md"
        pim_file.write_text(pim_content, encoding='utf-8')
        
        # 准备 PSM 文件路径
        psm_file = output_dir / f"{pim_file.stem}_psm.md"
        
        # 构建提示词
        prompt = PSM_GENERATION_PROMPT.format(
            pim_file=pim_file.name,
            platform=platform,
            psm_file=psm_file.name,
            framework=self._get_framework_for_platform(platform),
            orm=self._get_orm_for_platform(platform),
            validation_lib=self._get_validation_lib_for_platform(platform)
        )
        
        # 执行 Gemini CLI
        success = self._execute_gemini_cli(prompt, output_dir)
        
        if success and psm_file.exists():
            psm_content = psm_file.read_text(encoding='utf-8')
            return GenerationResult(
                success=True,
                output_path=output_dir,
                psm_content=psm_content,
                generation_time=time.time() - start_time,
                logs=f"PSM generated successfully at {psm_file}"
            )
        else:
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message="Failed to generate PSM",
                generation_time=time.time() - start_time
            )
    
    def generate_code(
        self, 
        psm_content: str, 
        output_dir: Path,
        platform: str = "fastapi"
    ) -> GenerationResult:
        """从 PSM 生成代码"""
        start_time = time.time()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建临时 PSM 文件
        psm_file = output_dir / "temp_psm.md"
        psm_file.write_text(psm_content, encoding='utf-8')
        
        # 创建 GEMINI_KNOWLEDGE.md
        self._create_knowledge_file(output_dir)
        
        # 构建提示词
        prompt = CODE_GENERATION_PROMPT.format(psm_file=psm_file.name)
        
        # 执行 Gemini CLI
        success = self._execute_gemini_cli(prompt, output_dir, timeout=600, monitor_progress=True)
        
        if success:
            # 收集生成的文件
            code_files = {}
            for file_path in output_dir.rglob("*.py"):
                if file_path.name != "temp_psm.md":
                    relative_path = file_path.relative_to(output_dir)
                    code_files[str(relative_path)] = file_path.read_text(encoding='utf-8')
            
            return GenerationResult(
                success=True,
                output_path=output_dir,
                code_files=code_files,
                generation_time=time.time() - start_time,
                logs=f"Code generated successfully in {output_dir}"
            )
        else:
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message="Failed to generate code",
                generation_time=time.time() - start_time
            )
    
    def _execute_gemini_cli(
        self, 
        prompt: str, 
        work_dir: Path, 
        timeout: int = 300,
        monitor_progress: bool = False
    ) -> bool:
        """执行 Gemini CLI 命令"""
        try:
            # 准备环境变量
            env = os.environ.copy()
            if "GOOGLE_API_KEY" in env and "GEMINI_API_KEY" in env:
                del env["GOOGLE_API_KEY"]
            
            # 保存日志
            gemini_log_path = work_dir / "gemini.log"
            
            with open(gemini_log_path, "w", encoding="utf-8") as log_file:
                log_file.write(f"=== GEMINI CLI PROMPT ===\n{prompt}\n\n=== GEMINI CLI OUTPUT ===\n")
                log_file.flush()
                
                # 执行命令
                process = subprocess.Popen(
                    [self.gemini_cli_path, "-m", self.model, "-p", prompt, "-y"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env,
                    cwd=work_dir
                )
                
                # 监控输出
                output_lines = []
                if process.stdout:
                    while True:
                        line = process.stdout.readline()
                        if not line and process.poll() is not None:
                            break
                        if line:
                            line = line.rstrip()
                            output_lines.append(line)
                            log_file.write(line + "\n")
                            log_file.flush()
                            if monitor_progress and "generated" in line.lower():
                                self.logger.info(f"Progress: {line}")
                
                # 等待进程结束
                try:
                    returncode = process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    self.logger.error(f"Gemini CLI timed out after {timeout} seconds")
                    process.kill()
                    return False
                
                return returncode == 0
                
        except Exception as e:
            self.logger.error(f"Failed to execute Gemini CLI: {e}")
            return False
    
    def _get_framework_for_platform(self, platform: str) -> str:
        """获取平台对应的框架"""
        frameworks = {
            "fastapi": "FastAPI",
            "flask": "Flask", 
            "django": "Django",
            "springboot": "Spring Boot",
            "express": "Express.js",
            "gin": "Gin"
        }
        return frameworks.get(platform, "FastAPI")
    
    def _get_orm_for_platform(self, platform: str) -> str:
        """获取平台对应的 ORM"""
        orms = {
            "fastapi": "SQLAlchemy",
            "flask": "SQLAlchemy",
            "django": "Django ORM",
            "springboot": "JPA/Hibernate",
            "express": "Sequelize",
            "gin": "GORM"
        }
        return orms.get(platform, "SQLAlchemy")
    
    def _get_validation_lib_for_platform(self, platform: str) -> str:
        """获取平台对应的验证库"""
        validators = {
            "fastapi": "Pydantic",
            "flask": "Marshmallow",
            "django": "Django Forms/Serializers",
            "springboot": "Bean Validation",
            "express": "Joi",
            "gin": "go-playground/validator"
        }
        return validators.get(platform, "Pydantic")
    
    def _create_knowledge_file(self, output_dir: Path):
        """创建 GEMINI_KNOWLEDGE.md 文件"""
        knowledge_content = """# Gemini Code Generation Knowledge Base

## FastAPI Best Practices

### Project Structure
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── domain.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── dto.py
│   └── services/
│       ├── __init__.py
│       └── business.py
├── tests/
├── requirements.txt
└── README.md
```

### Code Generation Rules
1. Always use Pydantic v2 syntax
2. Use SQLAlchemy 2.0 style 
3. Include proper error handling
4. Add type hints for all functions
5. Create __init__.py files for all packages
6. Use relative imports within the package
7. Follow RESTful API conventions
"""
        
        knowledge_file = output_dir / "GEMINI_KNOWLEDGE.md"
        knowledge_file.write_text(knowledge_content, encoding='utf-8')
        self.logger.debug(f"Created knowledge file: {knowledge_file}")