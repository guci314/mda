"""
长文档生成器 - 支持生成超长文档
使用分段生成和续写策略
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


class LongDocumentGenerator(BaseGenerator):
    """长文档生成器
    
    专门用于生成超长文档，使用分段和续写策略
    """
    
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
        self.max_tokens_per_request = 4000  # 每次请求的最大 token 数
        
        self.logger.info(f"Initialized Long Document Generator with model: {model}")
    
    def generate_psm(
        self, 
        pim_content: str, 
        platform: str = "fastapi",
        output_dir: Optional[Path] = None
    ) -> GenerationResult:
        """从 PIM 生成 PSM - 支持超长文档"""
        start_time = time.time()
        
        if output_dir is None:
            output_dir = Path.cwd()
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 第一步：生成文档大纲
            self.logger.info("Step 1: Generating document outline...")
            outline = self._generate_outline(pim_content, platform)
            
            # 保存大纲
            outline_file = output_dir / "psm_outline.json"
            outline_file.write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding='utf-8')
            
            # 第二步：分章节生成
            self.logger.info("Step 2: Generating sections...")
            full_content = f"# Platform Specific Model (PSM)\n\n"
            full_content += f"**Target Platform**: {platform}\n"
            full_content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            section_summaries = []
            
            for i, section in enumerate(outline['sections']):
                self.logger.info(f"Generating section {i+1}/{len(outline['sections'])}: {section['title']}")
                
                # 生成章节内容
                section_content = self._generate_section(
                    section=section,
                    pim_content=pim_content,
                    platform=platform,
                    previous_summaries=section_summaries
                )
                
                # 检查是否需要续写
                if self._seems_truncated(section_content):
                    self.logger.info(f"Section seems truncated, requesting continuation...")
                    continuation = self._continue_generation(
                        section_content=section_content,
                        section=section,
                        platform=platform
                    )
                    section_content += continuation
                
                # 添加到完整文档
                full_content += f"\n## {section['title']}\n\n"
                full_content += section_content + "\n"
                
                # 生成章节摘要供后续章节参考
                summary = self._summarize_section(section['title'], section_content)
                section_summaries.append(summary)
                
                # 保存中间结果（支持断点续传）
                temp_file = output_dir / f"psm_temp_{i+1}.md"
                temp_file.write_text(full_content, encoding='utf-8')
            
            # 保存最终 PSM
            psm_file = output_dir / "psm.md"
            psm_file.write_text(full_content, encoding='utf-8')
            
            return GenerationResult(
                success=True,
                output_path=output_dir,
                psm_content=full_content,
                generation_time=time.time() - start_time,
                logs=f"PSM generated successfully with {len(outline['sections'])} sections"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate PSM: {e}")
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
    
    def _generate_outline(self, pim_content: str, platform: str) -> Dict:
        """生成文档大纲"""
        prompt = f"""分析以下 PIM（Platform Independent Model），为 {platform} 平台生成详细的 PSM 文档大纲。

PIM 内容：
```
{pim_content}
```

请返回 JSON 格式的大纲，包含以下结构：
{{
  "title": "文档标题",
  "sections": [
    {{
      "title": "章节标题",
      "description": "章节描述",
      "subsections": ["子节1", "子节2", ...]
    }},
    ...
  ]
}}

确保大纲涵盖：
1. 数据模型定义（实体、关系、约束）
2. API 端点设计（RESTful）
3. 服务层设计（业务逻辑）
4. 数据访问层设计（Repository/DAO）
5. 验证和错误处理
6. 安全性考虑
7. 配置和部署
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的软件架构师，擅长设计详细的技术文档结构。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _generate_section(
        self, 
        section: Dict, 
        pim_content: str, 
        platform: str,
        previous_summaries: List[str]
    ) -> str:
        """生成单个章节"""
        
        # 构建上下文
        context = ""
        if previous_summaries:
            context = "已生成章节摘要：\n"
            for i, summary in enumerate(previous_summaries):
                context += f"{i+1}. {summary}\n"
        
        prompt = f"""基于以下信息生成 PSM 文档的章节内容。

章节信息：
- 标题：{section['title']}
- 描述：{section['description']}
- 包含内容：{', '.join(section.get('subsections', []))}

目标平台：{platform}

{context}

PIM 内容：
```
{pim_content}
```

要求：
1. 生成详细、完整的章节内容
2. 包含具体的代码示例（如果适用）
3. 确保与已生成章节的一致性
4. 使用 Markdown 格式
5. 对于代码，使用正确的语法高亮标记

请直接生成章节内容，不要包含章节标题（标题会自动添加）。
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"你是一个 {platform} 专家，负责生成高质量的技术文档。"},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens_per_request
        )
        
        return response.choices[0].message.content
    
    def _seems_truncated(self, content: str) -> bool:
        """检查内容是否被截断"""
        # 检查常见的截断标志
        truncation_signs = [
            "...",  # 省略号结尾
            "```",  # 代码块未关闭
            content.count("```") % 2 == 1,  # 代码块数量为奇数
            content.strip().endswith(("，", "、", "：", "；")),  # 中文标点结尾
            content.strip().endswith((",", ":", ";")),  # 英文标点结尾
            len(content.strip().split()[-1]) > 50 if content.strip() else False,  # 最后一个词过长
        ]
        
        return any(truncation_signs)
    
    def _continue_generation(
        self, 
        section_content: str, 
        section: Dict,
        platform: str,
        max_continuations: int = 3
    ) -> str:
        """续写被截断的内容"""
        continuations = []
        current_content = section_content
        
        for i in range(max_continuations):
            # 获取最后200个字符作为上下文
            last_context = current_content[-200:] if len(current_content) > 200 else current_content
            
            prompt = f"""继续生成以下未完成的内容。

章节：{section['title']}
平台：{platform}

已生成内容的结尾部分：
...{last_context}

请直接从断点处继续写，不要重复已有内容。保持相同的格式和风格。
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "继续生成技术文档，保持一致性。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens_per_request
            )
            
            continuation = response.choices[0].message.content
            continuations.append(continuation)
            current_content += continuation
            
            # 如果新内容不再被截断，停止续写
            if not self._seems_truncated(continuation):
                break
                
            self.logger.info(f"Continuation {i+1} completed, checking if more needed...")
        
        return "\n".join(continuations)
    
    def _summarize_section(self, title: str, content: str) -> str:
        """生成章节摘要"""
        # 简单的摘要：标题 + 前100个字符
        preview = content[:100].replace('\n', ' ') + "..." if len(content) > 100 else content
        return f"{title}: {preview}"
    
    def generate_code(
        self, 
        psm_content: str, 
        output_dir: Path,
        platform: str = "fastapi"
    ) -> GenerationResult:
        """从 PSM 生成代码 - 支持大型项目"""
        start_time = time.time()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 分析 PSM 确定需要生成的模块
            self.logger.info("Analyzing PSM to determine modules...")
            modules = self._analyze_psm_modules(psm_content, platform)
            
            # 逐模块生成代码
            code_files = {}
            for i, module in enumerate(modules):
                self.logger.info(f"Generating module {i+1}/{len(modules)}: {module['name']}")
                
                module_files = self._generate_module(
                    module=module,
                    psm_content=psm_content,
                    platform=platform,
                    existing_modules=[m['name'] for m in modules[:i]]
                )
                
                # 写入文件
                for file_path, content in module_files.items():
                    full_path = output_dir / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(content, encoding='utf-8')
                    code_files[file_path] = content
            
            # 生成项目配置文件
            self.logger.info("Generating project configuration files...")
            config_files = self._generate_project_config(platform, modules)
            for file_path, content in config_files.items():
                full_path = output_dir / file_path
                full_path.write_text(content, encoding='utf-8')
                code_files[file_path] = content
            
            return GenerationResult(
                success=True,
                output_path=output_dir,
                code_files=code_files,
                generation_time=time.time() - start_time,
                logs=f"Generated {len(code_files)} files in {len(modules)} modules"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate code: {e}")
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
    
    def _analyze_psm_modules(self, psm_content: str, platform: str) -> List[Dict]:
        """分析 PSM 确定需要生成的模块"""
        prompt = f"""分析以下 PSM，确定需要为 {platform} 生成的代码模块。

PSM 内容：
```
{psm_content[:2000]}...  # 只传入前2000字符
```

返回 JSON 格式的模块列表：
{{
  "modules": [
    {{
      "name": "模块名称",
      "type": "模块类型(model/schema/service/api/repository/config)",
      "files": ["文件1", "文件2"],
      "dependencies": ["依赖模块1", "依赖模块2"]
    }}
  ]
}}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('modules', [])
    
    def _generate_module(
        self, 
        module: Dict, 
        psm_content: str,
        platform: str,
        existing_modules: List[str]
    ) -> Dict[str, str]:
        """生成单个模块的代码"""
        context = ""
        if existing_modules:
            context = f"已生成的模块：{', '.join(existing_modules)}"
        
        prompt = f"""基于 PSM 生成 {module['name']} 模块的代码。

模块信息：
- 名称：{module['name']}
- 类型：{module['type']}
- 包含文件：{', '.join(module['files'])}
- 依赖：{', '.join(module.get('dependencies', []))}

平台：{platform}
{context}

PSM 相关部分：
```
{self._extract_relevant_psm(psm_content, module)}
```

生成完整的模块代码，返回 JSON 格式：
{{
  "files": {{
    "path/to/file.py": "文件内容",
    ...
  }}
}}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens_per_request,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('files', {})
    
    def _extract_relevant_psm(self, psm_content: str, module: Dict) -> str:
        """提取与模块相关的 PSM 内容"""
        # 简单实现：根据模块类型提取相关部分
        keywords = {
            'model': ['Model', '模型', 'Entity', '实体'],
            'schema': ['Schema', 'Pydantic', 'Validation', '验证'],
            'service': ['Service', '服务', 'Business', '业务'],
            'api': ['API', 'Endpoint', '端点', 'Route'],
            'repository': ['Repository', 'DAO', '数据访问'],
        }
        
        module_keywords = keywords.get(module['type'], [])
        relevant_lines = []
        
        for line in psm_content.split('\n'):
            if any(keyword.lower() in line.lower() for keyword in module_keywords):
                relevant_lines.append(line)
        
        # 返回相关内容，最多2000字符
        relevant_content = '\n'.join(relevant_lines)
        return relevant_content[:2000] + "..." if len(relevant_content) > 2000 else relevant_content
    
    def _generate_project_config(self, platform: str, modules: List[Dict]) -> Dict[str, str]:
        """生成项目配置文件"""
        config_files = {}
        
        if platform == "fastapi":
            # requirements.txt
            config_files["requirements.txt"] = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-dotenv==1.0.0
alembic==1.12.1
pytest==7.4.3
httpx==0.25.2
"""
            
            # .env.example
            config_files[".env.example"] = """DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
DEBUG=True
"""
            
            # README.md
            module_list = '\n'.join([f"- {m['name']}: {m['type']}" for m in modules])
            config_files["README.md"] = f"""# {platform.title()} Application

Generated application with the following modules:
{module_list}

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```
"""
        
        return config_files