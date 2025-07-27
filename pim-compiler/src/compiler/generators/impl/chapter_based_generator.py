"""
基于章节的 PSM 生成器
使用预定义的章节结构分块生成长文档
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Any
import logging
from datetime import datetime

from openai import OpenAI
from pydantic import BaseModel, Field

from ..base_generator import BaseGenerator, GeneratorConfig, GenerationResult


class ChapterBasedGenerator(BaseGenerator):
    """基于章节的文档生成器
    
    将 PSM 分为 Domain、Service、API、App、Test 五个章节
    """
    
    # 预定义的章节结构
    PSM_CHAPTERS = [
        {
            "name": "Domain Models",
            "key": "domain",
            "sections": [
                "Entity Definitions",
                "Database Models (ORM)", 
                "Data Transfer Objects (DTOs/Schemas)",
                "Enums and Constants",
                "Domain Rules and Constraints"
            ],
            "focus": "定义所有的数据模型、实体结构、数据验证规则和领域约束"
        },
        {
            "name": "Service Layer",
            "key": "service", 
            "sections": [
                "Business Logic Services",
                "Repository Interfaces",
                "Transaction Management",
                "Business Rules Implementation",
                "Service Dependencies"
            ],
            "focus": "实现所有的业务逻辑、数据访问接口和事务管理"
        },
        {
            "name": "REST API Design",
            "key": "api",
            "sections": [
                "RESTful Endpoints",
                "Request/Response Formats",
                "API Routing",
                "Middleware and Filters",
                "API Documentation"
            ],
            "focus": "设计 RESTful API 接口、路由配置和中间件"
        },
        {
            "name": "Application Configuration", 
            "key": "app",
            "sections": [
                "Main Application Setup",
                "Dependency Injection",
                "Database Configuration",
                "Environment Variables",
                "Logging and Monitoring",
                "Deployment Configuration"
            ],
            "focus": "配置应用程序启动、依赖注入、数据库连接和部署设置"
        },
        {
            "name": "Testing Specifications",
            "key": "test",
            "sections": [
                "Unit Test Design",
                "Integration Test Design",
                "Test Data and Fixtures",
                "Mock Objects Design",
                "Testing Strategy and Coverage"
            ],
            "focus": "设计完整的测试策略，包括单元测试、集成测试和测试数据"
        }
    ]
    
    def setup(self):
        """初始化设置"""
        # 设置 LLM 配置
        api_key = self.config.api_key or os.getenv("DEEPSEEK_API_KEY")
        api_base = self.config.api_base or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        model = self.config.model or "deepseek-chat"
        
        if not api_key:
            raise ValueError("API key not provided. Set DEEPSEEK_API_KEY or provide in config")
        
        # 创建 OpenAI 兼容客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        self.model = model
        self.temperature = self.config.temperature or 0.7
        self.max_tokens_per_chapter = 4000  # 每个章节的最大 token 数
        
        self.logger.info(f"Initialized Chapter Based Generator with model: {model}")
    
    def generate_psm(
        self, 
        pim_content: str, 
        platform: str = "fastapi",
        output_dir: Optional[Path] = None
    ) -> GenerationResult:
        """从 PIM 生成 PSM - 基于章节结构"""
        start_time = time.time()
        
        if output_dir is None:
            output_dir = Path.cwd()
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 初始化 PSM 文档
            psm_document = self._initialize_psm_document(platform)
            
            # 保存章节摘要，供后续章节参考
            chapter_summaries = []
            
            # 逐章生成
            for i, chapter in enumerate(self.PSM_CHAPTERS):
                self.logger.info(f"Generating chapter {i+1}/{len(self.PSM_CHAPTERS)}: {chapter['name']}")
                
                # 生成章节内容
                chapter_content = self._generate_chapter(
                    chapter=chapter,
                    pim_content=pim_content,
                    platform=platform,
                    previous_summaries=chapter_summaries
                )
                
                # 添加到文档
                psm_document += f"\n\n# {chapter['name']}\n\n"
                psm_document += chapter_content
                
                # 生成章节摘要
                summary = self._create_chapter_summary(chapter['name'], chapter_content)
                chapter_summaries.append(summary)
                
                # 保存进度（支持断点续传）
                progress_file = output_dir / f"psm_progress_{i+1}.md"
                progress_file.write_text(psm_document, encoding='utf-8')
                
                self.logger.info(f"Chapter {chapter['name']} completed, {len(chapter_content)} chars")
            
            # 添加文档结尾
            psm_document += self._create_document_footer()
            
            # 保存最终 PSM
            psm_file = output_dir / "psm.md"
            psm_file.write_text(psm_document, encoding='utf-8')
            
            # 保存章节元数据
            metadata = {
                "platform": platform,
                "chapters": [ch['key'] for ch in self.PSM_CHAPTERS],
                "generation_time": time.time() - start_time,
                "model": self.model
            }
            metadata_file = output_dir / "psm_metadata.json"
            metadata_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
            
            return GenerationResult(
                success=True,
                output_path=output_dir,
                psm_content=psm_document,
                generation_time=time.time() - start_time,
                logs=f"PSM generated successfully with {len(self.PSM_CHAPTERS)} chapters"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate PSM: {e}")
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
    
    def _initialize_psm_document(self, platform: str) -> str:
        """初始化 PSM 文档头部"""
        return f"""# Platform Specific Model (PSM)

**Target Platform**: {platform.upper()}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Generator**: Chapter Based Generator

## Table of Contents

1. [Domain Models](#domain-models)
2. [Service Layer](#service-layer)
3. [REST API Design](#rest-api-design)
4. [Application Configuration](#application-configuration)
5. [Testing Specifications](#testing-specifications)

---
"""
    
    def _generate_chapter(
        self,
        chapter: Dict,
        pim_content: str,
        platform: str,
        previous_summaries: List[str]
    ) -> str:
        """生成单个章节"""
        
        # 构建上下文
        context = ""
        if previous_summaries:
            context = "\n已生成章节的摘要：\n"
            for i, summary in enumerate(previous_summaries, 1):
                context += f"{i}. {summary}\n"
        
        # 构建系统提示
        system_prompt = f"""你是一个 {platform} 专家，负责生成高质量的技术文档。
当前正在生成 PSM（Platform Specific Model）文档的 {chapter['name']} 章节。

章节重点：{chapter['focus']}

请确保：
1. 内容详细且技术准确
2. 包含具体的代码示例
3. 遵循 {platform} 的最佳实践
4. 与已生成章节保持一致性"""

        # 构建用户提示
        user_prompt = f"""基于以下 PIM 生成 {chapter['name']} 章节的内容。

该章节应包含以下部分：
{chr(10).join(f'- {section}' for section in chapter['sections'])}

{context}

PIM 内容：
```
{pim_content}
```

请生成完整的章节内容，使用 Markdown 格式，包含必要的代码示例。
直接开始内容，不要重复章节标题。"""

        # 调用 LLM 生成
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens_per_chapter
        )
        
        return response.choices[0].message.content
    
    def _create_chapter_summary(self, chapter_name: str, content: str) -> str:
        """创建章节摘要"""
        # 提取关键信息作为摘要
        lines = content.split('\n')
        key_points = []
        
        for line in lines:
            # 提取二级标题
            if line.startswith('## '):
                key_points.append(line[3:].strip())
            # 提取关键定义
            elif 'class ' in line or 'def ' in line or 'interface ' in line:
                key_points.append(line.strip())
        
        # 限制摘要长度
        summary_points = key_points[:5] if len(key_points) > 5 else key_points
        summary = f"{chapter_name}: " + ", ".join(summary_points)
        
        # 确保摘要不超过200字符
        if len(summary) > 200:
            summary = summary[:197] + "..."
        
        return summary
    
    def _create_document_footer(self) -> str:
        """创建文档尾部"""
        return f"""

---

## Document Generation Summary

- **Total Chapters**: {len(self.PSM_CHAPTERS)}
- **Generator**: Chapter Based Generator
- **Model**: {self.model}
- **Completion Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Chapter Overview

{chr(10).join(f"{i+1}. **{ch['name']}**: {ch['focus']}" for i, ch in enumerate(self.PSM_CHAPTERS))}

---

*This PSM document was generated automatically based on the provided PIM. 
Please review and adjust as needed for your specific requirements.*
"""
    
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
        
        try:
            # 解析 PSM 章节
            chapters = self._parse_psm_chapters(psm_content)
            
            # 基于章节生成对应的代码模块
            code_files = {}
            
            # 1. 基于 Domain 章节生成模型代码
            if 'domain' in chapters:
                self.logger.info("Generating models from Domain chapter...")
                model_files = self._generate_models(chapters['domain'], platform)
                code_files.update(model_files)
            
            # 2. 基于 Service 章节生成服务代码
            if 'service' in chapters:
                self.logger.info("Generating services from Service chapter...")
                service_files = self._generate_services(chapters['service'], platform)
                code_files.update(service_files)
            
            # 3. 基于 API 章节生成路由代码
            if 'api' in chapters:
                self.logger.info("Generating API routes from API chapter...")
                api_files = self._generate_api_routes(chapters['api'], platform)
                code_files.update(api_files)
            
            # 4. 基于 App 章节生成配置代码
            if 'app' in chapters:
                self.logger.info("Generating app configuration from App chapter...")
                config_files = self._generate_app_config(chapters['app'], platform)
                code_files.update(config_files)
            
            # 5. 基于 Test 章节生成测试代码
            if 'test' in chapters:
                self.logger.info("Generating tests from Test chapter...")
                test_files = self._generate_tests(chapters['test'], platform)
                code_files.update(test_files)
            
            # 写入所有文件
            for file_path, content in code_files.items():
                full_path = output_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
            
            return GenerationResult(
                success=True,
                output_path=output_dir,
                code_files=code_files,
                generation_time=time.time() - start_time,
                logs=f"Generated {len(code_files)} files from PSM chapters"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate code: {e}")
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
    
    def _parse_psm_chapters(self, psm_content: str) -> Dict[str, str]:
        """解析 PSM 文档的章节"""
        chapters = {}
        current_chapter = None
        current_content = []
        
        for line in psm_content.split('\n'):
            # 检测一级标题（章节）
            if line.startswith('# '):
                if current_chapter:
                    chapters[current_chapter] = '\n'.join(current_content)
                
                # 匹配章节名称
                chapter_title = line[2:].strip()
                for ch in self.PSM_CHAPTERS:
                    if ch['name'] in chapter_title:
                        current_chapter = ch['key']
                        current_content = []
                        break
            elif current_chapter:
                current_content.append(line)
        
        # 保存最后一个章节
        if current_chapter:
            chapters[current_chapter] = '\n'.join(current_content)
        
        return chapters
    
    def _generate_models(self, domain_content: str, platform: str) -> Dict[str, str]:
        """基于 Domain 章节生成模型代码"""
        # 这里应该调用 LLM 生成具体代码
        # 简化示例
        return {
            "src/models/__init__.py": "",
            "src/models/base.py": "# Base model definitions",
            "src/models/entities.py": "# Entity models",
            "src/schemas/__init__.py": "",
            "src/schemas/user.py": "# User schemas"
        }
    
    def _generate_services(self, service_content: str, platform: str) -> Dict[str, str]:
        """基于 Service 章节生成服务代码"""
        return {
            "src/services/__init__.py": "",
            "src/services/user_service.py": "# User service implementation",
            "src/repositories/__init__.py": "",
            "src/repositories/user_repository.py": "# User repository"
        }
    
    def _generate_api_routes(self, api_content: str, platform: str) -> Dict[str, str]:
        """基于 API 章节生成路由代码"""
        return {
            "src/api/__init__.py": "",
            "src/api/v1/__init__.py": "",
            "src/api/v1/users.py": "# User API routes"
        }
    
    def _generate_app_config(self, app_content: str, platform: str) -> Dict[str, str]:
        """基于 App 章节生成配置代码"""
        return {
            "src/main.py": "# Main application",
            "src/config.py": "# Configuration",
            "src/database.py": "# Database setup",
            ".env.example": "# Environment variables",
            "requirements.txt": "# Dependencies"
        }
    
    def _generate_tests(self, test_content: str, platform: str) -> Dict[str, str]:
        """基于 Test 章节生成测试代码"""
        return {
            "tests/__init__.py": "",
            "tests/conftest.py": "# Test configuration",
            "tests/test_users.py": "# User tests"
        }