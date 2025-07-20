"""LLM-based code generator"""

from typing import List, Dict, Any, Optional
import asyncio
import logging

from .code_generator import CodeGenerator, CodePackage
from .models import CodeFile
from .psm_generator import PSMModel, PSMEntity, PSMService
from .platform_adapters import get_platform_adapter
from .llm_providers import get_llm_provider, LLMProvider
from .pim_to_prompt import PIMToPromptConverter

logger = logging.getLogger(__name__)


class LLMCodeGenerator(CodeGenerator):
    """Enhanced code generator using LLM for complex business logic"""
    
    def __init__(
        self, 
        llm_provider: Optional[LLMProvider] = None,
        use_llm_for_all: bool = False
    ):
        """
        Initialize LLM code generator
        
        Args:
            llm_provider: LLM provider instance, auto-detected if None
            use_llm_for_all: If True, use LLM for all code generation.
                           If False, use templates for simple CRUD and LLM for complex logic
        """
        super().__init__()
        self.llm = llm_provider or get_llm_provider("auto")
        self.use_llm_for_all = use_llm_for_all
        self.converter = PIMToPromptConverter()
        
    async def generate_code(
        self,
        psm_model: PSMModel,
        options: Optional[Dict[str, Any]] = None
    ) -> CodePackage:
        """Generate code package with LLM enhancement"""
        options = options or {}
        
        # Get platform adapter for basic structure
        adapter = get_platform_adapter(psm_model.platform)
        
        # Generate all code files
        files = []
        
        # Generate models (usually template-based is fine)
        model_files = await adapter.generate_models(psm_model.entities)
        files.extend(model_files)
        
        # Generate services with LLM enhancement
        if self.use_llm_for_all or self._has_complex_logic(psm_model):
            service_files = await self._generate_services_with_llm(
                psm_model.services,
                psm_model
            )
        else:
            # Use hybrid approach
            service_files = await self._generate_hybrid_services(
                psm_model.services,
                psm_model,
                adapter
            )
        files.extend(service_files)
        
        # Generate API routes (template-based)
        route_files = await adapter.generate_routes(psm_model.services)
        files.extend(route_files)
        
        # Generate main application
        main_file = await adapter.generate_main_app(psm_model)
        files.append(main_file)
        
        # Generate configuration files
        config_files = await adapter.generate_configs(psm_model, options)
        files.extend(config_files)
        
        # Generate tests with LLM if requested
        if options.get("include_tests", True):
            if options.get("llm_tests", False):
                test_files = await self._generate_tests_with_llm(psm_model)
            else:
                test_files = await adapter.generate_tests(psm_model)
            files.extend(test_files)
            
        # Generate documentation
        if options.get("include_docs", True):
            doc_files = await adapter.generate_docs(psm_model)
            files.extend(doc_files)
            
        # Generate deployment files
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
                "generated_with": "LLM" if self.use_llm_for_all else "Hybrid",
                "llm_provider": type(self.llm).__name__,
                "platform": psm_model.platform,
                "options": options
            }
        )
        
        return package
    
    async def _generate_services_with_llm(
        self, 
        services: List[PSMService],
        psm_model: PSMModel
    ) -> List[CodeFile]:
        """Generate all service code using LLM"""
        files = []
        
        # Convert model context once
        model_context = self.converter.convert_model_context(psm_model.base_model)
        
        for service in services:
            logger.info(f"Generating service {service.name} with LLM")
            
            # Generate service implementation
            service_code = await self._generate_service_with_llm(
                service,
                psm_model,
                model_context
            )
            
            file = CodeFile(
                path=f"app/services/{service.name.lower()}.py",
                content=service_code,
                description=f"LLM-generated service for {service.name}"
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
    
    async def _generate_hybrid_services(
        self,
        services: List[PSMService],
        psm_model: PSMModel,
        adapter
    ) -> List[CodeFile]:
        """Generate services using hybrid approach"""
        files = []
        model_context = self.converter.convert_model_context(psm_model.base_model)
        
        for service in services:
            # Check each method for complexity
            simple_methods = []
            complex_methods = []
            
            for method in service.methods:
                if self._is_complex_method(method, psm_model.base_model):
                    complex_methods.append(method)
                else:
                    simple_methods.append(method)
            
            if complex_methods:
                logger.info(f"Service {service.name} has {len(complex_methods)} complex methods")
                
                # Generate the entire service with LLM if it has complex methods
                service_code = await self._generate_service_with_llm(
                    service,
                    psm_model,
                    model_context
                )
            else:
                # Use template for simple CRUD services
                logger.info(f"Service {service.name} is simple CRUD, using templates")
                service_files = await adapter.generate_services([service])
                files.extend(service_files)
                continue
                
            file = CodeFile(
                path=f"app/services/{service.name.lower()}.py",
                content=service_code,
                description=f"Hybrid-generated service for {service.name}"
            )
            files.append(file)
            
        # Generate __init__.py if not already added
        if not any(f.path == "app/services/__init__.py" for f in files):
            init_content = self._generate_services_init(services)
            init_file = CodeFile(
                path="app/services/__init__.py",
                content=init_content,
                description="Services module init"
            )
            files.append(init_file)
            
        return files
    
    async def _generate_service_with_llm(
        self,
        service: PSMService,
        psm_model: PSMModel,
        model_context: str
    ) -> str:
        """Generate complete service implementation using LLM"""
        
        # Build service-specific prompt
        prompt = f"""
Generate a complete FastAPI service implementation for {service.name}.

The service should include:
1. All necessary imports
2. Service class with dependency injection for database
3. Implementation of all methods with proper business logic
4. Error handling and validation
5. Logging for important operations
6. Type hints and async/await patterns

Service Methods:
"""
        
        # Add each method description
        for method in service.methods:
            # Find original PIM method for full context
            pim_method = None
            for pim_service in psm_model.base_model.services:
                if pim_service.name == service.name:
                    for m in pim_service.methods:
                        if m.name == method["name"]:
                            pim_method = m
                            break
            
            if pim_method:
                method_prompt = self.converter.convert_method_to_prompt(
                    pim_method,
                    pim_service,
                    psm_model.base_model
                )
                prompt += f"\n{method_prompt}\n"
            else:
                # Fallback to basic method info
                prompt += f"\n- {method['name']}: {method.get('description', 'Implement this method')}\n"
        
        # Add constraints
        constraints = [
            "Use Python 3.11+ features",
            "Follow FastAPI best practices",
            "Use SQLAlchemy for database operations",
            "Include proper error handling with HTTPException",
            "Add logging with logger.info/error",
            "Use Pydantic models for validation",
            "Implement actual business logic, not TODO placeholders"
        ]
        
        # Get few-shot examples
        examples = self.converter.create_few_shot_examples(psm_model.platform)
        
        # Generate code
        code = await self.llm.generate_code(
            context=model_context,
            prompt=prompt,
            constraints=constraints,
            examples=examples
        )
        
        # Post-process to ensure quality
        return self._post_process_code(code, service.name)
    
    def _has_complex_logic(self, psm_model: PSMModel) -> bool:
        """Check if model has complex business logic requiring LLM"""
        # Has flows with decisions
        for flow in psm_model.base_model.flows.values():
            if flow.diagram and ('decision' in flow.diagram.lower() or '{' in flow.diagram):
                return True
                
        # Has business rules
        if psm_model.base_model.rules:
            return True
            
        # Has methods with complex parameters
        for service in psm_model.base_model.services:
            for method in service.methods:
                if method.flow or method.rules:
                    return True
                    
        return False
    
    def _is_complex_method(self, method: Dict[str, Any], pim_model) -> bool:
        """Check if a specific method is complex"""
        method_name = method["name"]
        
        # Check if method has associated flow or rules
        for service in pim_model.services:
            for m in service.methods:
                if m.name == method_name:
                    if m.flow or m.rules:
                        return True
                        
        # Check method name patterns
        simple_patterns = ['create', 'get', 'update', 'delete', 'list', 'find']
        method_lower = method_name.lower()
        
        # If it's not a simple CRUD operation
        if not any(pattern in method_lower for pattern in simple_patterns):
            return True
            
        return False
    
    def _post_process_code(self, code: str, service_name: str) -> str:
        """Post-process generated code to ensure quality"""
        
        # Ensure proper imports if missing
        required_imports = [
            "from typing import List, Optional, Dict, Any",
            "from datetime import datetime",
            "from sqlalchemy.orm import Session",
            "from fastapi import HTTPException",
            "import logging",
        ]
        
        lines = code.split('\n')
        import_section = []
        code_section = []
        
        in_imports = True
        for line in lines:
            if in_imports and (line.startswith('class') or line.startswith('def')):
                in_imports = False
                
            if in_imports:
                import_section.append(line)
            else:
                code_section.append(line)
                
        # Add missing imports
        for req_import in required_imports:
            if not any(req_import in line for line in import_section):
                import_section.insert(0, req_import)
                
        # Add logger if missing
        if not any('logger' in line for line in import_section):
            import_section.append("\nlogger = logging.getLogger(__name__)")
            
        # Combine sections
        processed_code = '\n'.join(import_section) + '\n\n' + '\n'.join(code_section)
        
        # Ensure class exists
        if f"class {service_name}" not in processed_code:
            logger.warning(f"LLM did not generate class {service_name}, using fallback")
            # Add a basic class structure
            class_template = f"""

class {service_name}:
    \"\"\"Service implementation for {service_name}\"\"\"
    
    def __init__(self, db: Session):
        self.db = db

{processed_code}
"""
            processed_code = '\n'.join(import_section) + class_template
            
        return processed_code
    
    def _generate_services_init(self, services: List[PSMService]) -> str:
        """Generate services __init__.py"""
        imports = []
        exports = []
        
        for service in services:
            module_name = service.name.lower()
            imports.append(f"from .{module_name} import {service.name}")
            exports.append(f'    "{service.name}",')
            
        return "\n".join(imports) + "\n\n__all__ = [\n" + "\n".join(exports) + "\n]"
    
    async def _generate_tests_with_llm(self, psm_model: PSMModel) -> List[CodeFile]:
        """Generate comprehensive tests using LLM"""
        # TODO: Implement LLM-based test generation
        # For now, return empty list
        return []