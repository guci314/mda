"""Base platform adapter interface"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

# from ..psm_generator import PSMModel, PSMEntity, PSMService
from typing import Any
from ..models import CodeFile


class PlatformAdapter(ABC):
    """Base class for platform-specific code generation"""
    
    @abstractmethod
    async def generate_models(self, entities: List[PSMEntity]) -> List[CodeFile]:
        """Generate model/entity files"""
        pass
        
    @abstractmethod
    async def generate_services(self, services: List[PSMService]) -> List[CodeFile]:
        """Generate service/business logic files"""
        pass
        
    @abstractmethod 
    async def generate_routes(self, services: List[PSMService]) -> List[CodeFile]:
        """Generate API route files"""
        pass
        
    @abstractmethod
    async def generate_main_app(self, psm_model: PSMModel) -> CodeFile:
        """Generate main application file"""
        pass
        
    @abstractmethod
    async def generate_configs(
        self, 
        psm_model: PSMModel,
        options: Dict[str, Any]
    ) -> List[CodeFile]:
        """Generate configuration files"""
        pass
        
    @abstractmethod
    async def generate_tests(self, psm_model: PSMModel) -> List[CodeFile]:
        """Generate test files"""
        pass
        
    @abstractmethod
    async def generate_docs(self, psm_model: PSMModel) -> List[CodeFile]:
        """Generate documentation files"""
        pass
        
    @abstractmethod
    async def generate_deployment(self, psm_model: PSMModel) -> List[CodeFile]:
        """Generate deployment files"""
        pass
        
    @abstractmethod
    def get_project_structure(self) -> Dict[str, Any]:
        """Get project directory structure"""
        pass