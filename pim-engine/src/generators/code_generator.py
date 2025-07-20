"""Code generation from PSM"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from .psm_generator import PSMModel, PSMEntity, PSMService
from .platform_adapters import get_platform_adapter
from .models import CodeFile, CodePackage


class CodeGenerator:
    """Generate code from PSM models"""
    
    def __init__(self):
        self.adapters = {}
        
    async def generate_code(
        self,
        psm_model: PSMModel,
        options: Optional[Dict[str, Any]] = None
    ) -> CodePackage:
        """Generate complete code package from PSM"""
        options = options or {}
        
        # Get platform adapter
        adapter = get_platform_adapter(psm_model.platform)
        
        # Generate all code files
        files = []
        
        # Generate models
        model_files = await adapter.generate_models(psm_model.entities)
        files.extend(model_files)
        
        # Generate services
        service_files = await adapter.generate_services(psm_model.services)
        files.extend(service_files)
        
        # Generate API routes
        route_files = await adapter.generate_routes(psm_model.services)
        files.extend(route_files)
        
        # Generate main application
        main_file = await adapter.generate_main_app(psm_model)
        files.append(main_file)
        
        # Generate configuration files
        config_files = await adapter.generate_configs(psm_model, options)
        files.extend(config_files)
        
        # Generate tests if requested
        if options.get("include_tests", True):
            test_files = await adapter.generate_tests(psm_model)
            files.extend(test_files)
            
        # Generate documentation if requested
        if options.get("include_docs", True):
            doc_files = await adapter.generate_docs(psm_model)
            files.extend(doc_files)
            
        # Generate deployment files if requested
        if options.get("include_deployment", True):
            deployment_files = await adapter.generate_deployment(psm_model)
            files.extend(deployment_files)
            
        # Get project structure
        structure = adapter.get_project_structure()
        
        # Create package
        package = CodePackage(
            platform=psm_model.platform,
            model_name=psm_model.base_model.domain,
            files=files,
            structure=structure,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "platform": psm_model.platform,
                "platform_config": psm_model.platform_config,
                "options": options
            }
        )
        
        return package
        
    async def preview_code(
        self,
        psm_model: PSMModel,
        file_types: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Preview generated code without full generation"""
        file_types = file_types or ["models", "routes", "services", "main"]
        
        adapter = get_platform_adapter(psm_model.platform)
        preview = {}
        
        if "models" in file_types:
            model_files = await adapter.generate_models(psm_model.entities)
            for file in model_files:
                preview[file.path] = file.content
                
        if "routes" in file_types:
            route_files = await adapter.generate_routes(psm_model.services)
            for file in route_files:
                preview[file.path] = file.content
                
        if "services" in file_types:
            service_files = await adapter.generate_services(psm_model.services)
            for file in service_files:
                preview[file.path] = file.content
                
        if "main" in file_types:
            main_file = await adapter.generate_main_app(psm_model)
            preview[main_file.path] = main_file.content
            
        return preview