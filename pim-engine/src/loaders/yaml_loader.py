"""YAML format loader for PIM models"""

import yaml
from typing import Dict, Any, List
import time

from core.models import (
    ModelLoadResult, PIMModel, Entity, Service, Method,
    Attribute, AttributeType, Flow, Rule
)


class YAMLLoader:
    """Load PIM models from YAML format"""
    
    async def load(self, file_path: str) -> ModelLoadResult:
        """Load model from YAML file"""
        start_time = time.time()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                return ModelLoadResult(
                    success=False,
                    errors=["Empty YAML file"]
                )
            
            # Parse model
            model = await self._parse_model(data)
            
            # Validate
            errors = self._validate_yaml_structure(data)
            if errors:
                return ModelLoadResult(
                    success=False,
                    errors=errors
                )
            
            load_time_ms = (time.time() - start_time) * 1000
            
            return ModelLoadResult(
                success=True,
                model=model,
                load_time_ms=load_time_ms
            )
            
        except yaml.YAMLError as e:
            return ModelLoadResult(
                success=False,
                errors=[f"YAML parsing error: {str(e)}"]
            )
        except Exception as e:
            return ModelLoadResult(
                success=False,
                errors=[f"Failed to load YAML: {str(e)}"]
            )
    
    async def _parse_model(self, data: Dict[str, Any]) -> PIMModel:
        """Parse YAML data into PIM model"""
        # Parse entities
        entities = []
        for entity_data in data.get('entities', []):
            entities.append(self._parse_entity(entity_data))
        
        # Parse services
        services = []
        for service_data in data.get('services', []):
            services.append(self._parse_service(service_data))
        
        # Parse flows
        flows = {}
        for flow_name, flow_data in data.get('flows', {}).items():
            flows[flow_name] = self._parse_flow(flow_name, flow_data)
        
        # Parse rules
        rules = {}
        for rule_name, rule_text in data.get('rules', {}).items():
            rules[rule_name] = Rule(
                name=rule_name,
                description=rule_text,
                condition="",  # Will be parsed by rule engine
                action=""
            )
        
        # Check for debuggable methods (those with flows)
        for service in services:
            for method in service.methods:
                if method.flow and method.flow in flows:
                    method.is_debuggable = True
        
        return PIMModel(
            domain=data.get('domain', 'unknown'),
            version=data.get('version', '1.0.0'),
            description=data.get('description'),
            entities=entities,
            services=services,
            flows=flows,
            rules=rules,
            metadata=data.get('metadata', {})
        )
    
    def _parse_entity(self, data: Dict[str, Any]) -> Entity:
        """Parse entity from YAML data"""
        attributes = []
        
        for attr_name, attr_type in data.get('attributes', {}).items():
            # Parse attribute type
            if isinstance(attr_type, str):
                # Simple type
                attributes.append(Attribute(
                    name=attr_name,
                    type=self._parse_attribute_type(attr_type)
                ))
            elif isinstance(attr_type, dict):
                # Complex type with additional properties
                attributes.append(Attribute(
                    name=attr_name,
                    type=self._parse_attribute_type(attr_type.get('type', 'string')),
                    required=attr_type.get('required', True),
                    unique=attr_type.get('unique', False),
                    default=attr_type.get('default'),
                    description=attr_type.get('description'),
                    reference_entity=attr_type.get('reference'),
                    enum_values=attr_type.get('enum')
                ))
        
        return Entity(
            name=data['name'],
            description=data.get('description'),
            attributes=attributes,
            constraints=data.get('constraints', []),
            indexes=data.get('indexes', [])
        )
    
    def _parse_service(self, data: Dict[str, Any]) -> Service:
        """Parse service from YAML data"""
        methods = []
        
        for method_data in data.get('methods', []):
            methods.append(Method(
                name=method_data['name'],
                description=method_data.get('description'),
                parameters=method_data.get('parameters', {}),
                return_type=method_data.get('return_type'),
                flow=method_data.get('flow'),
                rules=method_data.get('rules', [])
            ))
        
        return Service(
            name=data['name'],
            description=data.get('description'),
            methods=methods
        )
    
    def _parse_flow(self, name: str, data: Dict[str, Any]) -> Flow:
        """Parse flow from YAML data"""
        return Flow(
            name=name,
            description=data.get('description'),
            steps=data.get('steps', []),
            diagram=data.get('diagram', '')
        )
    
    def _parse_attribute_type(self, type_str: str) -> AttributeType:
        """Parse attribute type string"""
        type_map = {
            'string': AttributeType.STRING,
            'str': AttributeType.STRING,
            'integer': AttributeType.INTEGER,
            'int': AttributeType.INTEGER,
            'float': AttributeType.FLOAT,
            'double': AttributeType.FLOAT,
            'boolean': AttributeType.BOOLEAN,
            'bool': AttributeType.BOOLEAN,
            'datetime': AttributeType.DATETIME,
            'date': AttributeType.DATE,
            'time': AttributeType.TIME,
            'json': AttributeType.JSON,
            'reference': AttributeType.REFERENCE,
            'ref': AttributeType.REFERENCE,
            'enum': AttributeType.ENUM
        }
        
        return type_map.get(type_str.lower(), AttributeType.STRING)
    
    def _validate_yaml_structure(self, data: Dict[str, Any]) -> List[str]:
        """Validate YAML structure"""
        errors = []
        
        if 'domain' not in data:
            errors.append("Missing required field: domain")
        
        if 'entities' not in data and 'services' not in data:
            errors.append("Model must define at least one entity or service")
        
        # Validate entities
        for i, entity in enumerate(data.get('entities', [])):
            if 'name' not in entity:
                errors.append(f"Entity at index {i} missing required field: name")
            if 'attributes' not in entity:
                errors.append(f"Entity '{entity.get('name', 'unknown')}' has no attributes")
        
        # Validate services
        for i, service in enumerate(data.get('services', [])):
            if 'name' not in service:
                errors.append(f"Service at index {i} missing required field: name")
        
        return errors