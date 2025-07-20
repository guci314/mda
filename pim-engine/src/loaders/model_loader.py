"""Main model loader that delegates to specific format loaders"""

from pathlib import Path
from typing import Optional

from core.models import ModelLoadResult, PIMModel
from loaders.yaml_loader import YAMLLoader
from loaders.markdown_loader import MarkdownLoader


class ModelLoader:
    """Main model loader that handles different file formats"""
    
    def __init__(self):
        self.yaml_loader = YAMLLoader()
        self.markdown_loader = MarkdownLoader()
    
    async def load_model(self, file_path: str) -> ModelLoadResult:
        """Load a model from file"""
        path = Path(file_path)
        
        if not path.exists():
            return ModelLoadResult(
                success=False,
                errors=[f"File not found: {file_path}"]
            )
        
        # Determine loader based on file extension
        if path.suffix.lower() in ['.yaml', '.yml']:
            return await self.yaml_loader.load(file_path)
        elif path.suffix.lower() == '.md':
            return await self.markdown_loader.load(file_path)
        else:
            return ModelLoadResult(
                success=False,
                errors=[f"Unsupported file format: {path.suffix}"]
            )
    
    async def validate_model(self, model: PIMModel) -> ModelLoadResult:
        """Validate a loaded model"""
        errors = []
        warnings = []
        
        # Check for duplicate entity names
        entity_names = [e.name for e in model.entities]
        if len(entity_names) != len(set(entity_names)):
            errors.append("Duplicate entity names found")
        
        # Check for duplicate service names
        service_names = [s.name for s in model.services]
        if len(service_names) != len(set(service_names)):
            errors.append("Duplicate service names found")
        
        # Validate entity references
        for entity in model.entities:
            for attr in entity.attributes:
                if attr.type == "reference" and attr.reference_entity:
                    if attr.reference_entity not in entity_names:
                        errors.append(
                            f"Entity '{entity.name}' references unknown entity "
                            f"'{attr.reference_entity}' in attribute '{attr.name}'"
                        )
        
        # Check for debuggable methods without flows
        for service in model.services:
            for method in service.methods:
                if method.is_debuggable and not method.flow:
                    warnings.append(
                        f"Method '{service.name}.{method.name}' marked as debuggable "
                        "but has no flow definition"
                    )
        
        return ModelLoadResult(
            success=len(errors) == 0,
            model=model if len(errors) == 0 else None,
            errors=errors,
            warnings=warnings
        )