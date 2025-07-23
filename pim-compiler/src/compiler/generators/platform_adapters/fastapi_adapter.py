"""FastAPI platform adapter"""

from typing import List, Dict, Any
import textwrap

from .base import PlatformAdapter
from ..psm_generator import PSMModel, PSMEntity, PSMService, PSMAttribute
from ..models import CodeFile


class FastAPIAdapter(PlatformAdapter):
    """Generate FastAPI code from PSM"""
    
    async def generate_models(self, entities: List[PSMEntity]) -> List[CodeFile]:
        """Generate SQLAlchemy models and Pydantic schemas"""
        # Database models
        db_models_content = self._generate_db_models(entities)
        db_file = CodeFile(
            path="app/models/database.py",
            content=db_models_content,
            description="SQLAlchemy database models"
        )
        
        # Pydantic schemas
        schemas_content = self._generate_schemas(entities)
        schema_file = CodeFile(
            path="app/schemas/__init__.py",
            content=schemas_content,
            description="Pydantic schemas for API validation"
        )
        
        return [db_file, schema_file]
        
    def _generate_db_models(self, entities: List[PSMEntity]) -> str:
        """Generate SQLAlchemy models"""
        imports = [
            "from datetime import datetime",
            "from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float",
            "from sqlalchemy.ext.declarative import declarative_base",
            "",
            "Base = declarative_base()"
        ]
        
        models = []
        for entity in entities:
            model_code = f"\n\nclass {entity.name}(Base):\n"
            model_code += f'    """Database model for {entity.name}"""\n'
            model_code += f'    __tablename__ = "{entity.table_name}"\n\n'
            
            for attr in entity.attributes:
                col_def = self._generate_column_definition(attr)
                model_code += f"    {attr.name} = {col_def}\n"
                
            # Add string representation
            model_code += f"\n    def __repr__(self):\n"
            model_code += f'        return f"<{entity.name}(id={{self.id}})>"'
            
            models.append(model_code)
            
        return "\n".join(imports) + "\n".join(models)
        
    def _generate_column_definition(self, attr: PSMAttribute) -> str:
        """Generate SQLAlchemy column definition"""
        col_type = attr.db_type
        constraints = []
        
        if attr.constraints.get("primary_key"):
            constraints.append("primary_key=True")
        if attr.constraints.get("unique"):
            constraints.append("unique=True")
        if attr.constraints.get("nullable") is False:
            constraints.append("nullable=False")
        if attr.constraints.get("index"):
            constraints.append("index=True")
        if attr.constraints.get("default"):
            default = attr.constraints["default"]
            if callable(default) or "." in str(default):
                constraints.append(f"default={default}")
            else:
                constraints.append(f"default={repr(default)}")
                
        constraint_str = ", " + ", ".join(constraints) if constraints else ""
        return f"Column({col_type}{constraint_str})"
        
    def _generate_schemas(self, entities: List[PSMEntity]) -> str:
        """Generate Pydantic schemas"""
        imports = [
            "from datetime import datetime",
            "from typing import Optional, List",
            "from pydantic import BaseModel, EmailStr, HttpUrl, UUID4",
            ""
        ]
        
        schemas = []
        for entity in entities:
            # Base schema
            base_schema = f"\n\nclass {entity.name}Base(BaseModel):\n"
            base_schema += f'    """Base schema for {entity.name}"""\n'
            
            for attr in entity.attributes:
                if attr.name not in ["id", "created_at", "updated_at"]:
                    field_def = self._generate_pydantic_field(attr)
                    base_schema += f"    {attr.name}: {field_def}\n"
                    
            schemas.append(base_schema)
            
            # Create schema
            create_schema = f"\n\nclass {entity.name}Create({entity.name}Base):\n"
            create_schema += f'    """Schema for creating {entity.name}"""\n'
            create_schema += "    pass"
            schemas.append(create_schema)
            
            # Update schema  
            update_schema = f"\n\nclass {entity.name}Update(BaseModel):\n"
            update_schema += f'    """Schema for updating {entity.name}"""\n'
            
            for attr in entity.attributes:
                if attr.name not in ["id", "created_at", "updated_at"]:
                    field_def = self._generate_pydantic_field(attr, optional=True)
                    update_schema += f"    {attr.name}: Optional[{field_def}] = None\n"
                    
            schemas.append(update_schema)
            
            # Response schema
            response_schema = f"\n\nclass {entity.name}Response({entity.name}Base):\n"
            response_schema += f'    """Schema for {entity.name} response"""\n'
            response_schema += "    id: int\n"
            response_schema += "    created_at: datetime\n" 
            response_schema += "    updated_at: datetime\n\n"
            response_schema += "    class Config:\n"
            response_schema += "        orm_mode = True"
            schemas.append(response_schema)
            
        return "\n".join(imports) + "\n".join(schemas)
        
    def _generate_pydantic_field(self, attr: PSMAttribute, optional: bool = False) -> str:
        """Generate Pydantic field type"""
        type_map = {
            "str": "str",
            "int": "int", 
            "float": "float",
            "bool": "bool",
            "datetime": "datetime",
            "date": "date",
            "EmailStr": "EmailStr",
            "HttpUrl": "HttpUrl",
            "UUID": "UUID4"
        }
        
        field_type = type_map.get(attr.platform_type, "str")
        
        if optional or not attr.constraints.get("nullable", True):
            return field_type
        else:
            return f"Optional[{field_type}]"
            
    async def generate_services(self, services: List[PSMService]) -> List[CodeFile]:
        """Generate service layer files"""
        files = []
        
        for service in services:
            service_content = self._generate_service_class(service)
            file = CodeFile(
                path=f"app/services/{service.name.lower()}.py",
                content=service_content,
                description=f"Service layer for {service.name}"
            )
            files.append(file)
            
        # Generate __init__.py
        init_content = self._generate_services_init(services)
        init_file = CodeFile(
            path="app/services/__init__.py",
            content=init_content,
            description="Services module init"
        )
        files.append(init_file)
        
        return files
        
    def _generate_service_class(self, service: PSMService) -> str:
        """Generate service class implementation"""
        imports = [
            "from typing import List, Optional",
            "from sqlalchemy.orm import Session",
            "from fastapi import HTTPException",
            "",
            "from ..models.database import *",
            "from ..schemas import *"
        ]
        
        class_def = f"\n\nclass {service.name}:\n"
        class_def += f'    """Service layer for {service.name}"""\n\n'
        class_def += "    def __init__(self, db: Session):\n"
        class_def += "        self.db = db\n"
        
        # Generate methods
        for method in service.methods:
            method_impl = self._generate_service_method(method)
            class_def += method_impl
            
        return "\n".join(imports) + class_def
        
    def _generate_service_method(self, method: Dict[str, Any]) -> str:
        """Generate service method implementation"""
        method_name = method["name"]
        params = method.get("parameters", [])
        
        # Simple CRUD implementations
        if "create" in method_name.lower():
            return self._generate_create_method(method)
        elif "get" in method_name.lower() or "find" in method_name.lower():
            return self._generate_get_method(method)
        elif "update" in method_name.lower():
            return self._generate_update_method(method)
        elif "delete" in method_name.lower():
            return self._generate_delete_method(method)
        else:
            return self._generate_generic_method(method)
            
    def _generate_create_method(self, method: Dict[str, Any]) -> str:
        """Generate create method"""
        entity_name = self._infer_entity_name(method["name"])
        
        return f"""
    async def {method["name"]}(self, data: {entity_name}Create) -> {entity_name}:
        \"\"\"{method.get('description', 'Create a new ' + entity_name)}\"\"\"
        db_obj = {entity_name}(**data.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
"""
        
    def _generate_get_method(self, method: Dict[str, Any]) -> str:
        """Generate get/find method"""
        entity_name = self._infer_entity_name(method["name"])
        
        if "all" in method["name"].lower() or "list" in method["name"].lower():
            return f"""
    async def {method["name"]}(self, skip: int = 0, limit: int = 100) -> List[{entity_name}]:
        \"\"\"{method.get('description', 'Get all ' + entity_name + 's')}\"\"\"
        return self.db.query({entity_name}).offset(skip).limit(limit).all()
"""
        else:
            return f"""
    async def {method["name"]}(self, id: int) -> {entity_name}:
        \"\"\"{method.get('description', 'Get ' + entity_name + ' by ID')}\"\"\"
        obj = self.db.query({entity_name}).filter({entity_name}.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="{entity_name} not found")
        return obj
"""
            
    def _generate_update_method(self, method: Dict[str, Any]) -> str:
        """Generate update method"""
        entity_name = self._infer_entity_name(method["name"])
        
        return f"""
    async def {method["name"]}(self, id: int, data: {entity_name}Update) -> {entity_name}:
        \"\"\"{method.get('description', 'Update ' + entity_name)}\"\"\"
        obj = await self.get_{entity_name.lower()}_by_id(id)
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj
"""
        
    def _generate_delete_method(self, method: Dict[str, Any]) -> str:
        """Generate delete method"""
        entity_name = self._infer_entity_name(method["name"]) 
        
        return f"""
    async def {method["name"]}(self, id: int) -> bool:
        \"\"\"{method.get('description', 'Delete ' + entity_name)}\"\"\"
        obj = await self.get_{entity_name.lower()}_by_id(id)
        self.db.delete(obj)
        self.db.commit()
        return True
"""
        
    def _generate_generic_method(self, method: Dict[str, Any]) -> str:
        """Generate generic method stub"""
        parameters = method.get("parameters", {})
        if isinstance(parameters, dict):
            params = ", ".join(f"{name}: {type_}" for name, type_ in parameters.items())
        else:
            params = ""
        
        return f"""
    async def {method["name"]}(self{', ' + params if params else ''}) -> Any:
        \"\"\"{method.get('description', method['name'])}\"\"\"
        # TODO: Implement business logic
        raise NotImplementedError("{method['name']} not implemented")
"""
        
    def _infer_entity_name(self, method_name: str) -> str:
        """Infer entity name from method name"""
        # Simple heuristic - improve as needed
        parts = method_name.split("_")
        for part in parts:
            if part[0].isupper():
                return part
        # Fallback
        return "Entity"
        
    def _generate_services_init(self, services: List[PSMService]) -> str:
        """Generate services __init__.py"""
        imports = []
        exports = []
        
        for service in services:
            module_name = service.name.lower()
            imports.append(f"from .{module_name} import {service.name}")
            exports.append(f'    "{service.name}",')
            
        return "\n".join(imports) + "\n\n__all__ = [\n" + "\n".join(exports) + "\n]"
        
    async def generate_routes(self, services: List[PSMService]) -> List[CodeFile]:
        """Generate API route files"""
        files = []
        
        for service in services:
            route_content = self._generate_route_file(service)
            file = CodeFile(
                path=f"app/api/routes/{service.name.lower()}.py",
                content=route_content,
                description=f"API routes for {service.name}"
            )
            files.append(file)
            
        # Generate API router
        router_content = self._generate_api_router(services)
        router_file = CodeFile(
            path="app/api/__init__.py",
            content=router_content,
            description="Main API router"
        )
        files.append(router_file)
        
        return files
        
    def _generate_route_file(self, service: PSMService) -> str:
        """Generate route file for a service"""
        imports = [
            "from typing import List",
            "from fastapi import APIRouter, Depends, HTTPException",
            "from sqlalchemy.orm import Session",
            "",
            "from ...core.database import get_db",
            f"from ...services import {service.name}",
            "from ...schemas import *"
        ]
        
        router_def = f"\n\nrouter = APIRouter(\n"
        router_def += f'    prefix="{service.base_path}",\n'
        router_def += f'    tags=["{service.name}"]\n'
        router_def += ")\n"
        
        routes = []
        for method in service.methods:
            route = self._generate_route_method(method, service.name)
            routes.append(route)
            
        return "\n".join(imports) + router_def + "\n".join(routes)
        
    def _generate_route_method(self, method: Dict[str, Any], service_name: str) -> str:
        """Generate route method"""
        http_method = method["http_method"].lower()
        path = method["path"]
        method_name = method["name"]
        
        # Infer response model
        entity_name = self._infer_entity_name(method_name)
        
        if "list" in method_name.lower() or "all" in method_name.lower():
            response_model = f"List[{entity_name}Response]"
        else:
            response_model = f"{entity_name}Response"
            
        route = f'\n\n@router.{http_method}("{path}", response_model={response_model})\n'
        route += f'async def {method_name}(\n'
        
        # Add parameters
        if "{id}" in path:
            route += "    id: int,\n"
            
        if http_method in ["post", "put"]:
            route += f"    data: {entity_name}{'Create' if http_method == 'post' else 'Update'},\n"
            
        route += "    db: Session = Depends(get_db)\n"
        route += "):\n"
        route += f'    """{method.get("description", method_name)}"""\n'
        route += f"    service = {service_name}(db)\n"
        
        # Call service method
        if http_method in ["post", "put"]:
            route += f"    return await service.{method_name}("
            if "{id}" in path:
                route += "id, data"
            else:
                route += "data"
            route += ")\n"
        elif "{id}" in path:
            route += f"    return await service.{method_name}(id)\n"
        else:
            route += f"    return await service.{method_name}()\n"
            
        return route
        
    def _generate_api_router(self, services: List[PSMService]) -> str:
        """Generate main API router"""
        imports = ["from fastapi import APIRouter", ""]
        
        for service in services:
            imports.append(f"from .routes.{service.name.lower()} import router as {service.name.lower()}_router")
            
        router_code = "\n\napi_router = APIRouter()\n\n"
        
        for service in services:
            router_code += f"api_router.include_router({service.name.lower()}_router)\n"
            
        return "\n".join(imports) + router_code
        
    async def generate_main_app(self, psm_model: PSMModel) -> CodeFile:
        """Generate main FastAPI application"""
        content = f'''"""
{psm_model.base_model.description}
Generated FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .core.config import settings
from .core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="{psm_model.base_model.domain}",
    description="{psm_model.base_model.description}",
    version="{psm_model.base_model.version}",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {{
        "message": "Welcome to {psm_model.base_model.domain}",
        "version": "{psm_model.base_model.version}"
    }}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{"status": "healthy"}}
'''
        
        return CodeFile(
            path="app/main.py",
            content=content,
            description="Main FastAPI application"
        )
        
    async def generate_configs(
        self,
        psm_model: PSMModel,
        options: Dict[str, Any]
    ) -> List[CodeFile]:
        """Generate configuration files"""
        files = []
        
        # Settings file
        settings_content = self._generate_settings()
        files.append(CodeFile(
            path="app/core/config.py",
            content=settings_content,
            description="Application configuration"
        ))
        
        # Database config
        db_content = self._generate_database_config()
        files.append(CodeFile(
            path="app/core/database.py",
            content=db_content,
            description="Database configuration"
        ))
        
        # Requirements file
        requirements = self._generate_requirements()
        files.append(CodeFile(
            path="requirements.txt",
            content=requirements,
            description="Python dependencies"
        ))
        
        # Environment template
        env_template = self._generate_env_template()
        files.append(CodeFile(
            path=".env.example",
            content=env_template,
            description="Environment variables template"
        ))
        
        return files
        
    def _generate_settings(self) -> str:
        """Generate settings configuration"""
        return '''"""Application settings"""

from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API
    API_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "PIM Generated API"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
'''
        
    def _generate_database_config(self) -> str:
        """Generate database configuration"""
        return '''"""Database configuration"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        
    def _generate_requirements(self) -> str:
        """Generate requirements.txt"""
        return """fastapi>=0.100.0
uvicorn[standard]>=0.23.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pydantic>=2.0.0
python-dotenv>=1.0.0
alembic>=1.12.0
pytest>=7.4.0
httpx>=0.24.0
"""
        
    def _generate_env_template(self) -> str:
        """Generate .env template"""
        return """# API Configuration
API_PREFIX=/api/v1
PROJECT_NAME="PIM Generated API"
VERSION=1.0.0

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your-secret-key-here-please-change
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["*"]
"""
        
    async def generate_tests(self, psm_model: PSMModel) -> List[CodeFile]:
        """Generate test files"""
        files = []
        
        # Test configuration
        conftest = self._generate_conftest()
        files.append(CodeFile(
            path="tests/conftest.py",
            content=conftest,
            description="Pytest configuration"
        ))
        
        # API tests
        for service in psm_model.services:
            test_content = self._generate_service_tests(service)
            files.append(CodeFile(
                path=f"tests/test_{service.name.lower()}.py",
                content=test_content,
                description=f"Tests for {service.name}"
            ))
            
        return files
        
    def _generate_conftest(self) -> str:
        """Generate pytest configuration"""
        return '''"""Test configuration"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client():
    """Test client fixture"""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
        
    Base.metadata.drop_all(bind=engine)
'''
        
    def _generate_service_tests(self, service: PSMService) -> str:
        """Generate tests for a service"""
        entity_name = self._infer_entity_name(service.methods[0]["name"] if service.methods else "Entity")
        
        return f'''"""Tests for {service.name}"""

import pytest
from fastapi.testclient import TestClient


def test_create_{entity_name.lower()}(client: TestClient):
    """Test creating a {entity_name}"""
    response = client.post(
        "{service.base_path}",
        json={{"name": "Test {entity_name}", "email": "test@example.com"}}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test {entity_name}"
    assert "id" in data


def test_get_{entity_name.lower()}(client: TestClient):
    """Test getting a {entity_name}"""
    # First create
    create_response = client.post(
        "{service.base_path}",
        json={{"name": "Test {entity_name}", "email": "test@example.com"}}
    )
    created_id = create_response.json()["id"]
    
    # Then get
    response = client.get(f"{service.base_path}/{{created_id}}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_id


def test_list_{entity_name.lower()}s(client: TestClient):
    """Test listing {entity_name}s"""
    response = client.get("{service.base_path}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
'''
        
    async def generate_docs(self, psm_model: PSMModel) -> List[CodeFile]:
        """Generate documentation files"""
        files = []
        
        # README
        readme = self._generate_readme(psm_model)
        files.append(CodeFile(
            path="README.md",
            content=readme,
            description="Project documentation"
        ))
        
        # API documentation
        api_docs = self._generate_api_docs(psm_model)
        files.append(CodeFile(
            path="docs/API.md",
            content=api_docs,
            description="API documentation"
        ))
        
        return files
        
    def _generate_readme(self, psm_model: PSMModel) -> str:
        """Generate README.md"""
        return f"""# {psm_model.base_model.domain}

{psm_model.base_model.description}

## Generated with PIM Engine

This project was automatically generated from a PIM (Platform Independent Model) using the PIM Execution Engine.

## Features

- RESTful API built with FastAPI
- PostgreSQL database with SQLAlchemy ORM
- Pydantic for data validation
- JWT authentication ready
- Docker support
- Comprehensive test suite

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Docker (optional)

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd {psm_model.base_model.domain.lower().replace(' ', '-')}
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations
```bash
alembic upgrade head
```

6. Start the application
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with pytest:
```bash
pytest
```

## Docker

Build and run with Docker:
```bash
docker build -t {psm_model.base_model.domain.lower().replace(' ', '-')} .
docker run -p 8000:8000 {psm_model.base_model.domain.lower().replace(' ', '-')}
```

## Project Structure

```
.
├── app/
│   ├── api/          # API routes
│   ├── core/         # Core configuration
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── main.py       # Application entry point
├── tests/            # Test suite
├── docs/             # Documentation
├── requirements.txt  # Python dependencies
├── Dockerfile        # Docker configuration
└── README.md         # This file
```

## License

This project is generated code and is provided as-is.
"""
        
    def _generate_api_docs(self, psm_model: PSMModel) -> str:
        """Generate API documentation"""
        docs = f"# {psm_model.base_model.domain} API Documentation\n\n"
        
        for service in psm_model.services:
            docs += f"## {service.name}\n\n"
            docs += f"Base URL: `{service.base_path}`\n\n"
            
            for method in service.methods:
                docs += f"### {method['name']}\n\n"
                docs += f"- **Method**: `{method['http_method']}`\n"
                docs += f"- **Path**: `{method['path']}`\n"
                docs += f"- **Description**: {method.get('description', 'No description')}\n\n"
                
        return docs
        
    async def generate_deployment(self, psm_model: PSMModel) -> List[CodeFile]:
        """Generate deployment files"""
        files = []
        
        # Dockerfile
        dockerfile = self._generate_dockerfile()
        files.append(CodeFile(
            path="Dockerfile",
            content=dockerfile,
            description="Docker configuration"
        ))
        
        # Docker Compose
        docker_compose = self._generate_docker_compose(psm_model)
        files.append(CodeFile(
            path="docker-compose.yml",
            content=docker_compose,
            description="Docker Compose configuration"
        ))
        
        # GitHub Actions
        github_actions = self._generate_github_actions()
        files.append(CodeFile(
            path=".github/workflows/ci.yml",
            content=github_actions,
            description="CI/CD pipeline"
        ))
        
        return files
        
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile"""
        return """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
    def _generate_docker_compose(self, psm_model: PSMModel) -> str:
        """Generate docker-compose.yml"""
        return f"""version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/{psm_model.base_model.domain.lower().replace(' ', '_')}
    depends_on:
      - db
    volumes:
      - ./app:/app

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB={psm_model.base_model.domain.lower().replace(' ', '_')}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
"""
        
    def _generate_github_actions(self) -> str:
        """Generate GitHub Actions workflow"""
        return """name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      run: |
        pytest
        
    - name: Run linting
      run: |
        pip install flake8
        flake8 app --max-line-length=88
"""
        
    def get_project_structure(self) -> Dict[str, Any]:
        """Get FastAPI project structure"""
        return {
            "app": {
                "api": {
                    "routes": {},
                    "__init__.py": "API router"
                },
                "core": {
                    "config.py": "Settings",
                    "database.py": "Database config"
                },
                "models": {
                    "database.py": "SQLAlchemy models"
                },
                "schemas": {
                    "__init__.py": "Pydantic schemas"
                },
                "services": {},
                "main.py": "Application entry"
            },
            "tests": {
                "conftest.py": "Test config",
                "test_*.py": "Test files"
            },
            "docs": {
                "API.md": "API documentation"
            },
            ".env.example": "Environment template",
            ".gitignore": "Git ignore",
            "requirements.txt": "Dependencies",
            "Dockerfile": "Docker config",
            "docker-compose.yml": "Docker Compose",
            "README.md": "Documentation"
        }