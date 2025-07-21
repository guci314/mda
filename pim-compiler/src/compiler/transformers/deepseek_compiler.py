"""DeepSeek-based PIM Compiler implementation"""

import os
import json
from typing import Optional, List, Dict, Any
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from pydantic import SecretStr

from ..core.base_compiler import BaseCompiler, CompilationResult
from ..core.compiler_config import CompilerConfig


class DeepSeekCompiler(BaseCompiler):
    """使用 DeepSeek LLM 的 PIM 编译器"""
    
    def __init__(self, config: CompilerConfig):
        super().__init__(config)
        
        # 设置 LangChain 缓存
        if config.enable_cache:
            cache_path = config.cache_dir / "deepseek_llm_cache.db"
            set_llm_cache(SQLiteCache(database_path=str(cache_path)))
            self.logger.info(f"LLM缓存已启用: {cache_path}")
        
        # 初始化 DeepSeek LLM
        self.llm = ChatOpenAI(
            temperature=config.llm_temperature,
            model=config.llm_model,
            base_url=config.deepseek_base_url,
            api_key=SecretStr(os.getenv("DEEPSEEK_API_KEY", ""))
        )
        
        # 加载提示词模板
        self._load_prompts()
    
    def _load_prompts(self):
        """加载提示词模板"""
        self.pim_to_psm_prompt = """你是一个专业的软件架构师，精通模型驱动架构(MDA)。

请将下面的 PIM（平台无关模型）转换为 {platform} 平台的 PSM（平台特定模型）。

PIM 内容：
{pim_content}

转换要求：
1. 保持 Markdown 格式
2. 添加 {platform} 平台特定的技术细节：
   - 数据类型（如 string → VARCHAR(255)）
   - 框架注解（如 @NotNull, @Entity）
   - API 路由（如 POST /api/users）
   - 数据库配置
3. 保留所有业务逻辑和约束
4. 添加必要的技术配置
5. 如果 PIM 中包含单元测试定义，转换为 {platform} 平台的测试规范：
   - 测试框架（pytest、JUnit、Jest 等）
   - 具体的测试场景和断言

请直接输出 PSM Markdown 内容，不要添加额外的解释。"""

        self.psm_to_code_prompt = """你是一个专业的 {platform} 开发者。

请根据下面的 PSM（平台特定模型）生成 {platform} 代码和对应的单元测试。

PSM 内容：
{psm_content}

生成要求：
1. 生成完整的、可运行的代码
2. 遵循 {platform} 最佳实践
3. 包含必要的导入语句
4. 添加适当的注释
5. 实现所有定义的功能
6. 为每个类和重要方法生成单元测试
7. 测试覆盖率至少80%
8. 包含正常情况和异常情况的测试

重要提示（必须遵守）：
- 使用最新版本的库语法
- Pydantic v2+: 使用 'pattern' 参数而不是 'regex'
- SQLAlchemy 2.0+: 从 sqlalchemy.orm 导入 declarative_base
- FastAPI: 确保所有导入路径正确
- 测试文件：只包含 Python 代码，不要包含命令行命令
- 使用 pytest 框架编写测试

请按以下格式输出代码：

### 文件: [文件名]
```[语言]
[代码内容]
```

### 文件: test_[文件名]
```[语言]
[测试代码]
```

生成所有必要的文件和测试文件。"""
    
    def _transform_pim_to_psm(self, pim_content: str, source_file: Path) -> Optional[str]:
        """使用 DeepSeek 将 PIM 转换为 PSM"""
        try:
            self.logger.info(f"开始 PIM 到 PSM 转换 (平台: {self.config.target_platform})")
            
            # 构建提示词
            prompt = self.pim_to_psm_prompt.format(
                platform=self.config.target_platform,
                pim_content=pim_content
            )
            
            # 调用 LLM
            messages = [
                SystemMessage(content="你是一个专业的软件架构师。"),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            psm_content = response.content
            
            self.logger.info("PIM 到 PSM 转换完成")
            return psm_content
            
        except Exception as e:
            self.logger.error(f"PIM 到 PSM 转换失败: {e}")
            return None
    
    def _generate_code_from_psm(self, psm_content: str, psm_file: Path) -> List[str]:
        """从 PSM 生成代码"""
        try:
            self.logger.info("开始代码生成")
            
            # 构建提示词
            prompt = self.psm_to_code_prompt.format(
                platform=self.config.target_platform,
                psm_content=psm_content
            )
            
            # 调用 LLM
            messages = [
                SystemMessage(content=f"你是一个专业的 {self.config.target_platform} 开发者。"),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            code_content = response.content
            
            # 解析并保存代码文件
            code_files = self._parse_and_save_code(code_content, psm_file)
            
            self.logger.info(f"代码生成完成，生成了 {len(code_files)} 个文件")
            return code_files
            
        except Exception as e:
            self.logger.error(f"代码生成失败: {e}")
            return []
    
    def _parse_and_save_code(self, code_content: str, psm_file: Path) -> List[str]:
        """解析 LLM 输出并保存代码文件"""
        code_files = []
        
        # 简单的解析逻辑，查找 ### 文件: 标记
        lines = code_content.split('\n')
        current_file = None
        current_content = []
        in_code_block = False
        
        for line in lines:
            if line.startswith("### 文件:") or line.startswith("### File:"):
                # 保存前一个文件
                if current_file and current_content:
                    file_path = self._save_code_file(current_file, '\n'.join(current_content), psm_file)
                    if file_path:
                        code_files.append(str(file_path))
                
                # 开始新文件
                current_file = line.split(":", 1)[1].strip()
                current_content = []
                in_code_block = False
            elif line.startswith("```"):
                in_code_block = not in_code_block
                if not in_code_block and current_file:
                    # 代码块结束，不添加结束标记
                    pass
                elif in_code_block and current_file:
                    # 代码块开始，不添加开始标记
                    pass
            elif in_code_block and current_file:
                current_content.append(line)
        
        # 保存最后一个文件
        if current_file and current_content:
            file_path = self._save_code_file(current_file, '\n'.join(current_content), psm_file)
            if file_path:
                code_files.append(str(file_path))
        
        return code_files
    
    def _save_code_file(self, filename: str, content: str, psm_file: Path) -> Optional[Path]:
        """保存单个代码文件"""
        try:
            # 创建代码输出目录
            code_dir = psm_file.parent / "generated" / psm_file.stem
            code_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            file_path = code_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.debug(f"代码文件已保存: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"保存代码文件失败 {filename}: {e}")
            return None