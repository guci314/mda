"""PIM to PSM transformation"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

# from core.models import PIMModel, Entity, Service, Attribute
# 暂时注释掉，因为这个文件当前没有被使用


@dataclass
class PSMAttribute:
    """Platform-specific attribute"""
    name: str
    pim_type: str
    platform_type: str
    db_type: str
    constraints: Dict[str, Any]
    
    
@dataclass 
class PSMEntity:
    """Platform-specific entity"""
    name: str
    table_name: str
    attributes: List[PSMAttribute]
    platform_annotations: Dict[str, Any]
    

@dataclass
class PSMService:
    """Platform-specific service"""  
    name: str
    base_path: str
    methods: List[Dict[str, Any]]
    platform_config: Dict[str, Any]


# @dataclass
# class PSMModel:
#     """Platform-specific model"""
#     platform: str
#     base_model: PIMModel
#     entities: List[PSMEntity]
#     services: List[PSMService]
#     platform_config: Dict[str, Any]
#     generated_at: datetime


class PSMGenerator:
    """Generate Platform Specific Model from PIM"""
    
    # Type mappings for different platforms
    TYPE_MAPPINGS = {
        "fastapi": {
            "string": ("str", "String"),
            "integer": ("int", "Integer"), 
            "float": ("float", "Float"),
            "boolean": ("bool", "Boolean"),
            "date": ("date", "Date"),
            "datetime": ("datetime", "DateTime"),
            "text": ("str", "Text"),
            "email": ("EmailStr", "String"),
            "url": ("HttpUrl", "String"),
            "uuid": ("UUID", "String(36)"),
            "json": ("Dict[str, Any]", "JSON")
        },
        "spring": {
            "string": ("String", "VARCHAR(255)"),
            "integer": ("Integer", "INTEGER"),
            "float": ("Double", "DOUBLE"),
            "boolean": ("Boolean", "BOOLEAN"),
            "date": ("LocalDate", "DATE"),
            "datetime": ("LocalDateTime", "TIMESTAMP"),
            "text": ("String", "TEXT"),
            "email": ("String", "VARCHAR(255)"),
            "url": ("String", "VARCHAR(500)"),
            "uuid": ("UUID", "UUID"),
            "json": ("Map<String, Object>", "JSON")
        }
    }
    
    def __init__(self, target_platform: str):
        self.platform = target_platform
        if target_platform not in self.TYPE_MAPPINGS:
            raise ValueError(f"Unsupported platform: {target_platform}")
            
    def generate_psm(self, pim_model: PIMModel) -> PSMModel:
        """Generate PSM from PIM model"""
        psm = PSMModel(
            platform=self.platform,
            base_model=pim_model,
            entities=[],
            services=[],
            platform_config=self._get_platform_config(),
            generated_at=datetime.now()
        )
        
        # Transform entities
        for entity in pim_model.entities:
            psm_entity = self._transform_entity(entity)
            psm.entities.append(psm_entity)
            
        # Transform services  
        for service in pim_model.services:
            psm_service = self._transform_service(service)
            psm.services.append(psm_service)
            
        return psm
        
    def _transform_entity(self, entity: Entity) -> PSMEntity:
        """Transform PIM entity to PSM entity"""
        table_name = entity.name.lower() + "s"  # Simple pluralization
        
        attributes = []
        for attr in entity.attributes:
            psm_attr = self._transform_attribute(attr)
            attributes.append(psm_attr)
            
        # Add platform-specific attributes
        if self.platform == "fastapi":
            # Add ID if not present
            if not any(a.name == "id" for a in attributes):
                attributes.insert(0, PSMAttribute(
                    name="id",
                    pim_type="integer",
                    platform_type="int",
                    db_type="Integer",
                    constraints={"primary_key": True, "index": True}
                ))
            
            # Add timestamps
            attributes.extend([
                PSMAttribute(
                    name="created_at",
                    pim_type="datetime",
                    platform_type="datetime",
                    db_type="DateTime",
                    constraints={"default": "datetime.utcnow"}
                ),
                PSMAttribute(
                    name="updated_at", 
                    pim_type="datetime",
                    platform_type="datetime",
                    db_type="DateTime",
                    constraints={"default": "datetime.utcnow", "onupdate": "datetime.utcnow"}
                )
            ])
            
        return PSMEntity(
            name=entity.name,
            table_name=table_name,
            attributes=attributes,
            platform_annotations=self._get_entity_annotations(entity)
        )
        
    def _transform_attribute(self, attr: Attribute) -> PSMAttribute:
        """Transform PIM attribute to PSM attribute"""
        type_mapping = self.TYPE_MAPPINGS[self.platform].get(
            attr.type, 
            ("str", "String")  # Default
        )
        
        constraints = {}
        if attr.required:
            constraints["nullable"] = False
        if attr.unique:
            constraints["unique"] = True
        if hasattr(attr, "max_length"):
            constraints["max_length"] = attr.max_length
            
        return PSMAttribute(
            name=attr.name,
            pim_type=attr.type,
            platform_type=type_mapping[0],
            db_type=type_mapping[1],
            constraints=constraints
        )
        
    def _transform_service(self, service: Service) -> PSMService:
        """Transform PIM service to PSM service"""
        base_path = f"/{service.name.lower().replace('service', '')}"
        
        methods = []
        for method in service.methods:
            psm_method = {
                "name": method.name,
                "http_method": self._infer_http_method(method.name),
                "path": self._generate_method_path(method.name),
                "parameters": method.parameters,
                "return_type": method.return_type,
                "description": method.description
            }
            methods.append(psm_method)
            
        return PSMService(
            name=service.name,
            base_path=base_path,
            methods=methods,
            platform_config=self._get_service_config(service)
        )
        
    def _infer_http_method(self, method_name: str) -> str:
        """Infer HTTP method from method name"""
        name_lower = method_name.lower()
        if any(prefix in name_lower for prefix in ["get", "list", "find", "search"]):
            return "GET"
        elif any(prefix in name_lower for prefix in ["create", "add", "register"]):
            return "POST"
        elif any(prefix in name_lower for prefix in ["update", "modify", "edit"]):
            return "PUT"
        elif any(prefix in name_lower for prefix in ["delete", "remove"]):
            return "DELETE"
        else:
            return "POST"  # Default
            
    def _generate_method_path(self, method_name: str) -> str:
        """Generate URL path for method"""
        # Simple conversion: camelCase to kebab-case
        import re
        path = re.sub('([a-z0-9])([A-Z])', r'\1-\2', method_name).lower()
        
        # Handle common patterns
        if "byid" in path:
            path = path.replace("byid", "/{id}")
        elif any(x in path for x in ["update", "delete", "get"]) and "/{id}" not in path:
            # These usually need an ID
            path = "/{id}"
            
        return path
        
    def _get_platform_config(self) -> Dict[str, Any]:
        """Get platform-specific configuration"""
        configs = {
            "fastapi": {
                "framework_version": "0.100+",
                "python_version": "3.11+",
                "orm": "sqlalchemy",
                "database": "postgresql",
                "authentication": "jwt"
            },
            "spring": {
                "framework_version": "3.0+", 
                "java_version": "17+",
                "orm": "jpa",
                "database": "postgresql",
                "authentication": "jwt"
            }
        }
        return configs.get(self.platform, {})
        
    def _get_entity_annotations(self, entity: Entity) -> Dict[str, Any]:
        """Get platform-specific entity annotations"""
        if self.platform == "fastapi":
            return {
                "orm_mode": True,
                "schema_extra": {
                    "example": self._generate_example(entity)
                }
            }
        elif self.platform == "spring":
            return {
                "entity": True,
                "table": entity.name.lower() + "s"
            }
        return {}
        
    def _get_service_config(self, service: Service) -> Dict[str, Any]:
        """Get platform-specific service configuration"""
        if self.platform == "fastapi":
            return {
                "tags": [service.name],
                "dependencies": ["Depends(get_db)"]
            }
        elif self.platform == "spring":
            return {
                "rest_controller": True,
                "request_mapping": f"/api/{service.name.lower()}"
            }
        return {}
        
    def _generate_example(self, entity: Entity) -> Dict[str, Any]:
        """Generate example data for entity"""
        example = {}
        for attr in entity.attributes:
            if attr.type == "string":
                example[attr.name] = f"example_{attr.name}"
            elif attr.type == "integer":
                example[attr.name] = 123
            elif attr.type == "boolean":
                example[attr.name] = True
            elif attr.type == "email":
                example[attr.name] = "user@example.com"
            # Add more types as needed
        return example