"""PSM to Code generator using Gemini via LangChain with caching"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
import logging
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from pydantic import SecretStr

logger = logging.getLogger(__name__)


class PSMtoCodeGeminiLangChainGenerator:
    """使用 Gemini (via LangChain) 将 PSM 转换为可执行代码，支持缓存"""
    
    def __init__(self, cache_path: str = ".langchain_gemini_code.db"):
        # 加载项目的 .env 文件
        project_root = Path(__file__).parent.parent.parent.parent
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Loaded .env from: {env_file}")
        
        # 设置 LangChain 缓存
        set_llm_cache(SQLiteCache(database_path=cache_path))
        logger.info(f"LangChain cache initialized at: {cache_path}")
        
        # 初始化 Gemini LLM
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_STUDIO_KEY')
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            api_key=SecretStr(api_key) if api_key else None,
            temperature=0,
            max_tokens=8192
        )
    
    async def generate(self, psm_file: Path, output_dir: Path) -> Dict[str, Path]:
        """从 PSM 生成完整的代码"""
        
        # 读取 PSM 内容
        with open(psm_file, 'r', encoding='utf-8') as f:
            psm_data = yaml.safe_load(f)
        
        platform = psm_data.get('platform', 'fastapi')
        
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 根据平台生成代码
        if platform == 'fastapi':
            return await self._generate_fastapi_code(psm_data, output_dir)
        elif platform == 'spring':
            raise NotImplementedError("Spring code generation is not yet implemented")
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    async def _generate_fastapi_code(self, psm_data: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
        """生成 FastAPI 代码"""
        
        generated_files = {}
        
        # 1. 生成数据库模型 (models.py)
        models_code = await self._generate_models(psm_data)
        models_path = output_dir / "models.py"
        models_path.write_text(models_code, encoding='utf-8')
        generated_files['models.py'] = models_path
        
        # 2. 生成 Pydantic 模式 (schemas.py)
        schemas_code = await self._generate_schemas(psm_data)
        schemas_path = output_dir / "schemas.py"
        schemas_path.write_text(schemas_code, encoding='utf-8')
        generated_files['schemas.py'] = schemas_path
        
        # 3. 生成数据库配置 (database.py)
        database_code = await self._generate_database_config()
        database_path = output_dir / "database.py"
        database_path.write_text(database_code, encoding='utf-8')
        generated_files['database.py'] = database_path
        
        # 4. 生成服务层 (services.py)
        services_code = await self._generate_services(psm_data)
        services_path = output_dir / "services.py"
        services_path.write_text(services_code, encoding='utf-8')
        generated_files['services.py'] = services_path
        
        # 5. 生成 API 路由 (api.py)
        api_code = await self._generate_api_routes(psm_data)
        api_path = output_dir / "api.py"
        api_path.write_text(api_code, encoding='utf-8')
        generated_files['api.py'] = api_path
        
        # 6. 生成主应用 (main.py)
        main_code = await self._generate_main_app(psm_data)
        main_path = output_dir / "main.py"
        main_path.write_text(main_code, encoding='utf-8')
        generated_files['main.py'] = main_path
        
        # 7. 生成配置文件
        await self._generate_config_files(psm_data, output_dir, generated_files)
        
        logger.info(f"Generated {len(generated_files)} files in {output_dir}")
        return generated_files
    
    async def _generate_models(self, psm_data: Dict[str, Any]) -> str:
        """生成 SQLAlchemy 模型"""
        prompt = self._build_models_prompt(psm_data)
        messages = [
            SystemMessage(content="你是一个 Python FastAPI 专家，擅长生成高质量的 SQLAlchemy 模型代码。只输出代码，不要有其他解释。"),
            HumanMessage(content=prompt)
        ]
        
        result = await self.llm.ainvoke(messages)
        return self._extract_code(str(result.content))
    
    async def _generate_schemas(self, psm_data: Dict[str, Any]) -> str:
        """生成 Pydantic 模式"""
        prompt = self._build_schemas_prompt(psm_data)
        messages = [
            SystemMessage(content="你是一个 Python FastAPI 专家，擅长生成高质量的 Pydantic 模式代码。只输出代码，不要有其他解释。"),
            HumanMessage(content=prompt)
        ]
        
        result = await self.llm.ainvoke(messages)
        return self._extract_code(str(result.content))
    
    async def _generate_services(self, psm_data: Dict[str, Any]) -> str:
        """生成服务层代码"""
        prompt = self._build_services_prompt(psm_data)
        messages = [
            SystemMessage(content="你是一个 Python FastAPI 专家，擅长生成高质量的服务层代码。只输出代码，不要有其他解释。"),
            HumanMessage(content=prompt)
        ]
        
        result = await self.llm.ainvoke(messages)
        return self._extract_code(str(result.content))
    
    async def _generate_api_routes(self, psm_data: Dict[str, Any]) -> str:
        """生成 API 路由"""
        prompt = self._build_api_routes_prompt(psm_data)
        messages = [
            SystemMessage(content="你是一个 Python FastAPI 专家，擅长生成高质量的 API 路由代码。只输出代码，不要有其他解释。"),
            HumanMessage(content=prompt)
        ]
        
        result = await self.llm.ainvoke(messages)
        return self._extract_code(str(result.content))
    
    async def _generate_main_app(self, psm_data: Dict[str, Any]) -> str:
        """生成主应用入口"""
        prompt = f"""基于以下 PSM 数据生成 FastAPI 主应用文件 (main.py)：

系统描述: {psm_data.get('description', '系统')}

要求：
1. 导入必要的模块
2. 创建 FastAPI 应用实例
3. 配置 CORS
4. 包含所有路由
5. 创建数据库表
6. 添加健康检查端点
7. 配置 uvicorn 启动

只输出 Python 代码。"""
        
        messages = [
            SystemMessage(content="你是一个 Python FastAPI 专家。只输出代码，不要有其他解释。"),
            HumanMessage(content=prompt)
        ]
        
        result = await self.llm.ainvoke(messages)
        return self._extract_code(str(result.content))
    
    async def _generate_database_config(self) -> str:
        """生成数据库配置"""
        prompt = """生成 FastAPI 项目的数据库配置文件 (database.py)，包含：
1. SQLAlchemy 引擎配置
2. SessionLocal 创建
3. Base 声明
4. get_db 依赖函数

使用 PostgreSQL 作为生产数据库，SQLite 作为开发数据库。
只输出 Python 代码。"""
        
        messages = [
            SystemMessage(content="你是一个 Python FastAPI 专家。只输出代码，不要有其他解释。"),
            HumanMessage(content=prompt)
        ]
        
        result = await self.llm.ainvoke(messages)
        return self._extract_code(str(result.content))
    
    async def _generate_config_files(self, psm_data: Dict[str, Any], output_dir: Path, generated_files: Dict[str, Path]):
        """生成配置文件"""
        
        # requirements.txt
        requirements = await self._generate_requirements()
        req_path = output_dir / "requirements.txt"
        req_path.write_text(requirements, encoding='utf-8')
        generated_files['requirements.txt'] = req_path
        
        # .env 示例
        env_example = await self._generate_env_example()
        env_path = output_dir / ".env.example"
        env_path.write_text(env_example, encoding='utf-8')
        generated_files['.env.example'] = env_path
        
        # Dockerfile
        dockerfile = await self._generate_dockerfile()
        docker_path = output_dir / "Dockerfile"
        docker_path.write_text(dockerfile, encoding='utf-8')
        generated_files['Dockerfile'] = docker_path
        
        # docker-compose.yml
        docker_compose = await self._generate_docker_compose(psm_data)
        compose_path = output_dir / "docker-compose.yml"
        compose_path.write_text(docker_compose, encoding='utf-8')
        generated_files['docker-compose.yml'] = compose_path
        
        # README.md
        readme = await self._generate_readme(psm_data)
        readme_path = output_dir / "README.md"
        readme_path.write_text(readme, encoding='utf-8')
        generated_files['README.md'] = readme_path
        
        # .gitignore
        gitignore = self._generate_gitignore()
        gitignore_path = output_dir / ".gitignore"
        gitignore_path.write_text(gitignore, encoding='utf-8')
        generated_files['.gitignore'] = gitignore_path
    
    def _build_models_prompt(self, psm_data: Dict[str, Any]) -> str:
        """构建生成模型的提示"""
        entities_desc = "\n\n".join([
            self._entity_to_description(entity) for entity in psm_data.get('entities', [])
        ])
        
        return f"""基于以下 PSM 实体定义生成 SQLAlchemy 模型代码：

{entities_desc}

要求：
1. 使用 SQLAlchemy 2.0 声明式风格
2. 包含所有必要的导入
3. 正确设置主键、外键、索引和约束
4. 添加 created_at 和 updated_at 时间戳字段
5. 设置合适的关系（relationship）
6. 使用类型注解

只输出 Python 代码。"""
    
    def _build_schemas_prompt(self, psm_data: Dict[str, Any]) -> str:
        """构建生成模式的提示"""
        entities_desc = "\n\n".join([
            self._entity_to_description(entity) for entity in psm_data.get('entities', [])
        ])
        
        return f"""基于以下 PSM 实体定义生成 Pydantic 模式代码：

{entities_desc}

要求：
1. 为每个实体创建 Create、Update、Response 模式
2. 使用 Pydantic v2 语法
3. 包含数据验证规则
4. 配置 from_attributes = True
5. 添加适当的示例（Config.json_schema_extra）

只输出 Python 代码。"""
    
    def _build_services_prompt(self, psm_data: Dict[str, Any]) -> str:
        """构建生成服务的提示"""
        services_desc = "\n\n".join([
            self._service_to_description(service) for service in psm_data.get('services', [])
        ])
        
        return f"""基于以下 PSM 服务定义生成服务层代码：

{services_desc}

要求：
1. 实现所有服务方法
2. 使用依赖注入（数据库会话）
3. 包含适当的错误处理
4. 实现业务逻辑和验证
5. 使用类型注解
6. 添加日志记录

只输出 Python 代码。"""
    
    def _build_api_routes_prompt(self, psm_data: Dict[str, Any]) -> str:
        """构建生成 API 路由的提示"""
        services_desc = "\n\n".join([
            self._service_to_description(service) for service in psm_data.get('services', [])
        ])
        
        return f"""基于以下 PSM 服务定义生成 FastAPI 路由代码：

{services_desc}

要求：
1. 使用 APIRouter
2. 实现所有 HTTP 端点
3. 使用适当的状态码
4. 添加 OpenAPI 文档（summary, description, response_description）
5. 实现分页（limit/offset）
6. 添加适当的依赖项

只输出 Python 代码。"""
    
    def _entity_to_description(self, entity: Dict[str, Any]) -> str:
        """将实体转换为描述"""
        attrs = "\n".join([
            f"  - {attr['name']}: {attr['type']} ({attr.get('db_type', '')}) "
            f"约束: {attr.get('constraints', {})}"
            for attr in entity.get('attributes', [])
        ])
        
        return f"""实体: {entity['name']}
表名: {entity.get('table_name', entity['name'].lower() + 's')}
描述: {entity.get('description', '')}
属性:
{attrs}"""
    
    def _service_to_description(self, service: Dict[str, Any]) -> str:
        """将服务转换为描述"""
        methods = "\n".join([
            f"  - {method['name']}: {method.get('http_method', 'POST')} "
            f"{method.get('path', '/')} - {method.get('description', '')}"
            for method in service.get('methods', [])
        ])
        
        return f"""服务: {service['name']}
基础路径: {service.get('base_path', '/api')}
描述: {service.get('description', '')}
方法:
{methods}"""
    
    async def _generate_requirements(self) -> str:
        """生成 requirements.txt"""
        return """fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
alembic>=1.12.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
"""
    
    async def _generate_env_example(self) -> str:
        """生成 .env.example"""
        return """# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your-secret-key-here

# API Settings
API_PREFIX=/api
DEBUG=True
"""
    
    async def _generate_dockerfile(self) -> str:
        """生成 Dockerfile"""
        return """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    async def _generate_docker_compose(self, psm_data: Dict[str, Any]) -> str:
        """生成 docker-compose.yml"""
        app_name = psm_data.get('description', 'app').lower().replace(' ', '_')
        return f"""version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: {app_name}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres/{app_name}
    depends_on:
      - postgres
    volumes:
      - .:/app

volumes:
  postgres_data:
"""
    
    async def _generate_readme(self, psm_data: Dict[str, Any]) -> str:
        """生成 README.md"""
        return f"""# {psm_data.get('description', '应用')}

## 描述
{psm_data.get('description', '这是一个基于 FastAPI 的应用程序。')}

## 快速开始

### 使用 Docker
```bash
docker-compose up
```

### 本地开发
1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 设置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件
```

4. 运行应用
```bash
uvicorn main:app --reload
```

## API 文档
启动应用后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构
- `models.py` - 数据库模型
- `schemas.py` - Pydantic 模式
- `services.py` - 业务逻辑
- `api.py` - API 路由
- `main.py` - 应用入口
"""
    
    def _generate_gitignore(self) -> str:
        """生成 .gitignore"""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.*
!.env.example

# Database
*.db
*.sqlite3

# Logs
*.log

# OS
.DS_Store
Thumbs.db
"""
    
    def _extract_code(self, response: str) -> str:
        """从响应中提取代码"""
        # 查找代码块
        import re
        
        # 尝试找到 ```python 代码块
        code_match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # 尝试找到 ``` 代码块
        code_match = re.search(r'```\n(.*?)\n```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # 如果没有代码块，假设整个响应都是代码
        # 但要去除可能的解释性文字
        lines = response.strip().split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            # 检测代码开始的标志
            if line.strip().startswith(('import ', 'from ', 'def ', 'class ', '#')):
                in_code = True
            
            if in_code:
                code_lines.append(line)
        
        if code_lines:
            return '\n'.join(code_lines)
        
        # 如果还是没有找到代码，返回整个响应
        return response.strip()
    
    def generate_sync(self, psm_file: Path, output_dir: Path) -> Dict[str, Path]:
        """同步版本的代码生成"""
        import asyncio
        return asyncio.run(self.generate(psm_file, output_dir))


async def generate_code_from_psm(psm_file: Path, output_dir: Path, cache_path: str = ".langchain_gemini_code.db") -> Dict[str, Path]:
    """便捷函数：从 PSM 生成代码"""
    generator = PSMtoCodeGeminiLangChainGenerator(cache_path=cache_path)
    return await generator.generate(psm_file, output_dir)


def generate_code_from_psm_sync(psm_file: Path, output_dir: Path, cache_path: str = ".langchain_gemini_code.db") -> Dict[str, Path]:
    """同步版本的便捷函数"""
    generator = PSMtoCodeGeminiLangChainGenerator(cache_path=cache_path)
    return generator.generate_sync(psm_file, output_dir)


if __name__ == "__main__":
    # 测试代码生成
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python psm_to_code_gemini_langchain.py <psm_file> <output_dir>")
        sys.exit(1)
    
    psm_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    async def main():
        try:
            files = await generate_code_from_psm(psm_file, output_dir)
            print(f"✅ Generated {len(files)} files:")
            for filename in sorted(files.keys()):
                print(f"  - {filename}")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    asyncio.run(main())