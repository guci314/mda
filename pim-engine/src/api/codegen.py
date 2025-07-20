"""Code generation API endpoints"""

import uuid
import io
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from generators.psm_generator import PSMGenerator
from generators.code_generator import CodeGenerator
from generators.llm_code_generator import LLMCodeGenerator
from generators.llm_providers import get_llm_provider

# Router configuration
router = APIRouter(prefix="/api/v1/codegen", tags=["Code Generation"])

# In-memory storage for generated packages (in production, use Redis or database)
generated_packages: Dict[str, Any] = {}


class CodeGenerationRequest(BaseModel):
    """Request model for code generation"""
    model_name: str
    platform: str
    options: Optional[Dict[str, Any]] = None
    use_llm: bool = False  # Enable LLM-based generation
    llm_provider: Optional[str] = None  # Override default LLM provider


class CodeGenerationResponse(BaseModel):
    """Response model for code generation"""
    package_id: str
    model_name: str
    platform: str
    files: list
    metadata: Dict[str, Any]


class CodeDownloadRequest(BaseModel):
    """Request model for code download"""
    package_id: str


@router.post("/generate", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """Generate code from PIM model"""
    try:
        import traceback
        # Load the model (assuming it's already loaded in the engine)
        from core.engine import engine as global_engine
        if global_engine is None:
            from core.engine import PIMEngine
            engine = PIMEngine.get_instance()
        else:
            engine = global_engine
        
        model = None
        # Check by key first (which is the model file name)
        if request.model_name in engine.loaded_models:
            model = engine.loaded_models[request.model_name]
        else:
            # Fallback: check by domain
            for loaded_model in engine.loaded_models.values():
                if loaded_model.domain == request.model_name:
                    model = loaded_model
                    break
                
        if not model:
            raise HTTPException(
                status_code=404,
                detail=f"Model {request.model_name} not found or not loaded"
            )
        
        # Generate PSM
        psm_generator = PSMGenerator(request.platform)
        psm_model = psm_generator.generate_psm(model)
        
        # Generate code
        if request.use_llm:
            # Use LLM-based generator
            try:
                llm_provider = None
                if request.llm_provider:
                    llm_provider = get_llm_provider(request.llm_provider)
                    
                code_generator = LLMCodeGenerator(
                    llm_provider=llm_provider,
                    use_llm_for_all=request.options.get("use_llm_for_all", False) if request.options else False
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to initialize LLM provider: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"LLM provider initialization failed: {str(e)}"
                )
        else:
            # Use template-based generator
            code_generator = CodeGenerator()
            
        code_package = await code_generator.generate_code(
            psm_model,
            options=request.options or {}
        )
        
        # Store package with unique ID
        package_id = str(uuid.uuid4())
        generated_packages[package_id] = code_package
        
        # Prepare response
        response = CodeGenerationResponse(
            package_id=package_id,
            model_name=code_package.model_name,
            platform=code_package.platform,
            files=[{
                "path": file.path,
                "description": file.description
            } for file in code_package.files],
            metadata=code_package.metadata
        )
        
        return response
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Code generation failed: {str(e)}"
        )


@router.post("/preview")
async def preview_code(request: CodeGenerationRequest):
    """Preview generated code without full generation"""
    try:
        # Load the model
        from core.engine import PIMEngine
        engine = PIMEngine.get_instance()
        
        model = None
        # Check by key first (which is the model file name)
        if request.model_name in engine.loaded_models:
            model = engine.loaded_models[request.model_name]
        else:
            # Fallback: check by domain
            for loaded_model in engine.loaded_models.values():
                if loaded_model.domain == request.model_name:
                    model = loaded_model
                    break
                
        if not model:
            raise HTTPException(
                status_code=404,
                detail=f"Model {request.model_name} not found"
            )
        
        # Generate PSM
        psm_generator = PSMGenerator(request.platform)
        psm_model = psm_generator.generate_psm(model)
        
        # Preview code
        code_generator = CodeGenerator()
        preview = await code_generator.preview_code(
            psm_model,
            file_types=request.options.get("file_types") if request.options else None
        )
        
        return {"preview": preview}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Preview failed: {str(e)}"
        )


@router.post("/download")
async def download_code(request: CodeDownloadRequest):
    """Download generated code as ZIP"""
    try:
        # Get package
        package = generated_packages.get(request.package_id)
        if not package:
            raise HTTPException(
                status_code=404,
                detail="Code package not found or expired"
            )
        
        # Convert to ZIP
        zip_buffer = await package.to_zip()
        
        # Prepare response
        filename = f"{package.model_name.lower().replace(' ', '_')}_{package.platform}.zip"
        
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {str(e)}"
        )


@router.get("/platforms")
async def list_platforms():
    """List available code generation platforms"""
    return {
        "platforms": [
            {
                "id": "fastapi",
                "name": "FastAPI",
                "language": "Python",
                "description": "Modern, fast web framework for building APIs",
                "available": True
            },
            {
                "id": "spring",
                "name": "Spring Boot", 
                "language": "Java",
                "description": "Enterprise Java framework",
                "available": False
            },
            {
                "id": "express",
                "name": "Express.js",
                "language": "JavaScript/Node.js",
                "description": "Minimalist web framework for Node.js",
                "available": False
            },
            {
                "id": "django",
                "name": "Django",
                "language": "Python",
                "description": "High-level Python web framework",
                "available": False
            }
        ]
    }


@router.delete("/package/{package_id}")
async def delete_package(package_id: str):
    """Delete a generated code package"""
    if package_id in generated_packages:
        del generated_packages[package_id]
        return {"message": "Package deleted"}
    else:
        raise HTTPException(
            status_code=404,
            detail="Package not found"
        )


@router.get("/llm/providers")
async def list_llm_providers():
    """List available LLM providers and their status"""
    import os
    
    providers = []
    
    # Check Gemini
    try:
        from generators.llm_providers import GeminiCLIProvider
        gemini = GeminiCLIProvider()
        gemini_available = await gemini.is_available()
        providers.append({
            "id": "gemini",
            "name": "Gemini CLI",
            "available": gemini_available,
            "description": "Google's Gemini AI via CLI",
            "requires": "Gemini CLI installation and authentication"
        })
    except:
        providers.append({
            "id": "gemini",
            "name": "Gemini CLI",
            "available": False,
            "description": "Google's Gemini AI via CLI",
            "requires": "Gemini CLI installation and authentication"
        })
    
    # Check Anthropic
    anthropic_available = bool(os.environ.get('ANTHROPIC_API_KEY'))
    providers.append({
        "id": "anthropic",
        "name": "Claude (Anthropic)",
        "available": anthropic_available,
        "description": "Anthropic's Claude AI",
        "requires": "ANTHROPIC_API_KEY environment variable"
    })
    
    # Check Local LLM
    try:
        from generators.llm_providers import LocalLLMProvider
        local = LocalLLMProvider()
        local_available = await local.is_available()
        providers.append({
            "id": "local",
            "name": "Local LLM (Ollama)",
            "available": local_available,
            "description": "Local CodeLlama or other models via Ollama",
            "requires": "Ollama server running"
        })
    except:
        providers.append({
            "id": "local",
            "name": "Local LLM (Ollama)",
            "available": False,
            "description": "Local CodeLlama or other models via Ollama",
            "requires": "Ollama server running"
        })
    
    # Check if any provider is available
    any_available = any(p["available"] for p in providers)
    
    return {
        "providers": providers,
        "llm_enabled": any_available,
        "default_provider": os.environ.get("LLM_PROVIDER", "auto")
    }