"""Dynamic API generator based on PIM models"""

from typing import Dict, Any, List, Optional, Type
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends
from pydantic import BaseModel, create_model, Field

from core.models import PIMModel, Entity, Service, AttributeType
from api.route_manager import DynamicRouteManager
from utils.logger import setup_logger


class APIGenerator:
    """Generate REST APIs dynamically from PIM models"""
    
    def __init__(self, engine):
        self.logger = setup_logger(__name__)
        self.engine = engine
        self.routers: Dict[str, APIRouter] = {}
        self.pydantic_models: Dict[str, Dict[str, Type[BaseModel]]] = {}
        self.route_manager = DynamicRouteManager(engine.app)
    
    async def register_model_routes(self, model: PIMModel):
        """Register all routes for a PIM model"""
        # Create router for this model
        router = APIRouter(
            tags=[model.domain]
        )
        
        # Generate routes for entities
        for entity in model.entities:
            await self._generate_entity_routes(router, entity, model.domain)
        
        # Generate routes for services
        for service in model.services:
            await self._generate_service_routes(router, service, model.domain)
        
        # Store router
        self.routers[model.domain] = router
        
        # Use route manager to load routes
        success = self.route_manager.load_model_routes(
            model.domain,
            router,
            prefix="/api/v1"
        )
        
        if success:
            self.logger.info(f"Registered API routes for model: {model.domain}")
        else:
            self.logger.warning(f"Failed to register routes for model: {model.domain}")
    
    async def unregister_model_routes(self, model: PIMModel):
        """Unregister routes for a model"""
        # Use route manager to unload routes
        success = self.route_manager.unload_model_routes(model.domain)
        
        if success:
            # Clean up our tracking
            if model.domain in self.routers:
                del self.routers[model.domain]
            
            if model.domain in self.pydantic_models:
                del self.pydantic_models[model.domain]
            
            self.logger.info(f"Unregistered API routes for model: {model.domain}")
        else:
            self.logger.warning(f"Failed to unregister routes for model: {model.domain}")
    
    def _check_model_loaded(self, domain: str):
        """Check if model is loaded before allowing API access"""
        if domain not in self.engine.models:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{domain}' is not loaded"
            )
    
    async def _generate_entity_routes(
        self,
        router: APIRouter,
        entity: Entity,
        domain: str
    ):
        """Generate CRUD routes for an entity"""
        # Create Pydantic models for this entity
        models = self._create_pydantic_models(entity)
        
        # Store models
        if domain not in self.pydantic_models:
            self.pydantic_models[domain] = {}
        self.pydantic_models[domain][entity.name] = models
        
        # Get model references
        CreateModel = models["create"]
        UpdateModel = models["update"]
        ResponseModel = models["response"]
        ListResponseModel = models["list_response"]
        
        entity_name_lower = entity.name.lower()
        entity_name_plural = f"{entity_name_lower}s"
        
        # CREATE endpoint
        @router.post(f"/{entity_name_plural}", response_model=ResponseModel)
        async def create_entity(
            data: CreateModel,
            entity_name: str = entity.name
        ):
            """Create a new {entity_name}"""
            try:
                result = await self.engine.data_engine.execute_operation(
                    entity_name,
                    "create",
                    data.model_dump()
                )
                return result
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # READ endpoint
        @router.get(f"/{entity_name_plural}/{{id}}", response_model=ResponseModel)
        async def read_entity(
            id: str = Path(..., description=f"The ID of the {entity.name}"),
            entity_name: str = entity.name
        ):
            """Get a {entity_name} by ID"""
            result = await self.engine.data_engine.execute_operation(
                entity_name,
                "read",
                {"id": id}
            )
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"{entity_name} not found"
                )
            return result
        
        # UPDATE endpoint
        @router.put(f"/{entity_name_plural}/{{id}}", response_model=ResponseModel)
        async def update_entity(
            id: str = Path(..., description=f"The ID of the {entity.name}"),
            data: UpdateModel = Body(...),
            entity_name: str = entity.name
        ):
            """Update a {entity_name}"""
            try:
                update_data = data.model_dump(exclude_unset=True)
                update_data["id"] = id
                
                result = await self.engine.data_engine.execute_operation(
                    entity_name,
                    "update",
                    update_data
                )
                return result
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # DELETE endpoint
        @router.delete(f"/{entity_name_plural}/{{id}}")
        async def delete_entity(
            id: str = Path(..., description=f"The ID of the {entity.name}"),
            entity_name: str = entity.name
        ):
            """Delete a {entity_name}"""
            try:
                await self.engine.data_engine.execute_operation(
                    entity_name,
                    "delete",
                    {"id": id}
                )
                return {"message": f"{entity_name} deleted successfully"}
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # LIST endpoint
        @router.get(f"/{entity_name_plural}", response_model=ListResponseModel)
        async def list_entities(
            skip: int = Query(0, ge=0, description="Number of records to skip"),
            limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
            entity_name: str = entity.name
        ):
            """List {entity_name_plural} with pagination"""
            result = await self.engine.data_engine.execute_operation(
                entity_name,
                "list",
                {
                    "skip": skip,
                    "limit": limit,
                    "filters": {}  # TODO: Add filter support
                }
            )
            return result
    
    async def _generate_service_routes(
        self,
        router: APIRouter,
        service: Service,
        domain: str
    ):
        """Generate routes for service methods"""
        service_name_lower = service.name.lower().replace("service", "")
        
        for method in service.methods:
            # Create route path
            method_path = f"/{service_name_lower}/{method.name.lower()}"
            
            # Create request model
            request_fields = {}
            for param_name, param_type in method.parameters.items():
                # Simple type mapping
                python_type = str  # Default
                if param_type.lower() in ["int", "integer"]:
                    python_type = int
                elif param_type.lower() in ["float", "number"]:
                    python_type = float
                elif param_type.lower() in ["bool", "boolean"]:
                    python_type = bool
                
                request_fields[param_name] = (python_type, Field(...))
            
            RequestModel = create_model(
                f"{service.name}{method.name}Request",
                **request_fields
            ) if request_fields else None
            
            # Create the endpoint
            @router.post(method_path)
            async def service_method(
                data: RequestModel = None if not RequestModel else Body(...),
                method_name: str = method.name,
                service_name: str = service.name,
                is_debuggable: bool = method.is_debuggable,
                flow_name: str = method.flow
            ):
                """Execute {service_name}.{method_name}"""
                try:
                    input_data = data.model_dump() if data else {}
                    
                    # If method has a flow, execute it
                    if is_debuggable and flow_name:
                        result = await self.engine.flow_engine.execute_flow(
                            flow_name,
                            input_data
                        )
                        return result
                    else:
                        # Execute method with rules
                        context = {"input": input_data}
                        
                        # Execute associated rules
                        method_obj = next(
                            (m for m in service.methods if m.name == method_name),
                            None
                        )
                        if method_obj:
                            for rule_name in method_obj.rules:
                                rule_result = await self.engine.rule_engine.execute_rule(
                                    rule_name,
                                    context
                                )
                                context[f"rule_{rule_name}_result"] = rule_result
                        
                        return {
                            "success": True,
                            "result": context
                        }
                        
                except Exception as e:
                    raise HTTPException(status_code=400, detail=str(e))
    
    def _create_pydantic_models(
        self,
        entity: Entity
    ) -> Dict[str, Type[BaseModel]]:
        """Create Pydantic models for an entity"""
        # Build field definitions
        create_fields = {}
        update_fields = {}
        response_fields = {
            "id": (str, Field(..., description="Unique identifier"))
        }
        
        for attr in entity.attributes:
            # Get Python type
            python_type = self._get_python_type(attr.type)
            
            # Create field
            if attr.required:
                field = Field(..., description=attr.description or f"{attr.name} field")
            else:
                field = Field(
                    default=attr.default,
                    description=attr.description or f"{attr.name} field"
                )
            
            # Add to create model (no ID)
            if attr.name != "id":
                create_fields[attr.name] = (python_type, field)
            
            # Add to update model (all optional)
            update_fields[attr.name] = (
                Optional[python_type],
                Field(None, description=attr.description)
            )
            
            # Add to response model
            response_fields[attr.name] = (python_type, field)
        
        # Add audit fields to response
        response_fields["created_at"] = (
            datetime,
            Field(..., description="Creation timestamp")
        )
        response_fields["updated_at"] = (
            datetime,
            Field(..., description="Last update timestamp")
        )
        
        # Create models
        CreateModel = create_model(
            f"{entity.name}Create",
            **create_fields
        )
        
        UpdateModel = create_model(
            f"{entity.name}Update",
            **update_fields
        )
        
        ResponseModel = create_model(
            f"{entity.name}Response",
            **response_fields
        )
        
        # Create list response model
        ListResponseModel = create_model(
            f"{entity.name}ListResponse",
            items=(List[ResponseModel], Field(...)),
            total=(int, Field(..., description="Total number of items")),
            skip=(int, Field(..., description="Number of items skipped")),
            limit=(int, Field(..., description="Maximum items returned"))
        )
        
        return {
            "create": CreateModel,
            "update": UpdateModel,
            "response": ResponseModel,
            "list_response": ListResponseModel
        }
    
    def _get_python_type(self, attr_type: AttributeType) -> type:
        """Convert AttributeType to Python type"""
        type_mapping = {
            AttributeType.STRING: str,
            AttributeType.INTEGER: int,
            AttributeType.FLOAT: float,
            AttributeType.BOOLEAN: bool,
            AttributeType.DATETIME: datetime,
            AttributeType.DATE: str,  # ISO date string
            AttributeType.TIME: str,  # ISO time string
            AttributeType.JSON: dict,
            AttributeType.REFERENCE: str,  # ID reference
            AttributeType.ENUM: str  # Enum as string
        }
        
        return type_mapping.get(attr_type, str)