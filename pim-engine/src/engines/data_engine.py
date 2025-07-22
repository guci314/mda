"""Data engine for dynamic database operations"""

from typing import Dict, Any, List, Optional, Type
from datetime import datetime
import uuid

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean,
    DateTime, Date, Time, JSON, ForeignKey, Enum as SQLEnum,
    Index, UniqueConstraint, CheckConstraint, MetaData, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.pool import NullPool

from core.models import PIMModel, Entity, Attribute, AttributeType
from utils.logger import setup_logger


class DataEngine:
    """Handle all data operations dynamically based on PIM models"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.logger = setup_logger(__name__)
        self.database_url = database_url
        self.Base = declarative_base()
        self.metadata = MetaData()
        self.models: Dict[str, Type] = {}
        self.tables: Dict[str, Table] = {}
        
        if database_url:
            # Check if it's SQLite
            if database_url.startswith("sqlite:"):
                # SQLite specific configuration
                self.engine = create_engine(
                    database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=NullPool,
                    echo=False
                )
            else:
                # PostgreSQL and other databases
                self.engine = create_engine(
                    database_url,
                    pool_size=20,
                    max_overflow=40,
                    pool_pre_ping=True,
                    echo=False
                )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        else:
            # In-memory SQLite for testing
            self.engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=NullPool
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        
        # Create base tables
        self.Base.metadata.create_all(bind=self.engine)
    
    async def setup_model(self, pim_model: PIMModel):
        """Setup database tables for a PIM model"""
        for entity in pim_model.entities:
            await self.create_entity_model(entity)
        
        # Create all tables
        self.Base.metadata.create_all(bind=self.engine)
        
        self.logger.info(f"Database setup completed for model: {pim_model.domain}")
    
    async def create_entity_model(self, entity: Entity) -> Type:
        """Dynamically create SQLAlchemy model for an entity"""
        # Prepare attributes dict for type() creation
        attrs = {
            '__tablename__': entity.name.lower(),
            '__table_args__': self._get_table_args(entity),
            'id': Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        }
        
        # Add columns based on attributes
        for attribute in entity.attributes:
            column = self._create_column(attribute)
            if column is not None:
                attrs[attribute.name] = column
        
        # Add audit columns
        attrs['created_at'] = Column(DateTime, default=datetime.utcnow, nullable=False)
        attrs['updated_at'] = Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False
        )
        
        # Create the model class
        model_class = type(
            entity.name,
            (self.Base,),
            attrs
        )
        
        # Store the model
        self.models[entity.name] = model_class
        
        self.logger.info(f"Created model for entity: {entity.name}")
        
        return model_class
    
    def _create_column(self, attribute: Attribute) -> Optional[Column]:
        """Create SQLAlchemy column from attribute definition"""
        column_type = None
        column_args = []
        column_kwargs = {
            'nullable': not attribute.required
        }
        
        # Map attribute type to SQLAlchemy type
        if attribute.type == AttributeType.STRING:
            column_type = String(255)
        elif attribute.type == AttributeType.INTEGER:
            column_type = Integer
        elif attribute.type == AttributeType.FLOAT:
            column_type = Float
        elif attribute.type == AttributeType.BOOLEAN:
            column_type = Boolean
        elif attribute.type == AttributeType.DATETIME:
            column_type = DateTime
        elif attribute.type == AttributeType.DATE:
            column_type = Date
        elif attribute.type == AttributeType.TIME:
            column_type = Time
        elif attribute.type == AttributeType.JSON:
            column_type = JSON
        elif attribute.type == AttributeType.ENUM and attribute.enum_values:
            # Create SQLAlchemy Enum
            enum_name = f"{attribute.name}_enum"
            column_type = SQLEnum(*attribute.enum_values, name=enum_name)
        elif attribute.type == AttributeType.REFERENCE and attribute.reference_entity:
            # Foreign key reference
            column_type = String(36)
            column_args.append(
                ForeignKey(f"{attribute.reference_entity.lower()}.id")
            )
        else:
            # Default to string
            column_type = String(255)
        
        # Add unique constraint if specified
        if attribute.unique:
            column_kwargs['unique'] = True
        
        # Add default value if specified
        if attribute.default is not None:
            column_kwargs['default'] = attribute.default
        
        # Add comment if description exists
        if attribute.description:
            column_kwargs['comment'] = attribute.description
        
        return Column(column_type, *column_args, **column_kwargs)
    
    def _get_table_args(self, entity: Entity) -> tuple:
        """Get table arguments including constraints and indexes"""
        args = []
        # Allow redefining tables when reloading models
        table_kwargs = {'extend_existing': True}
        
        # Add indexes
        for index_def in entity.indexes:
            # Simple index definition parsing
            if ',' in index_def:
                # Composite index
                columns = [col.strip() for col in index_def.split(',')]
                args.append(Index(f"idx_{entity.name.lower()}_composite", *columns))
            else:
                # Single column index
                args.append(Index(f"idx_{entity.name.lower()}_{index_def}", index_def))
        
        # Add constraints
        for constraint in entity.constraints:
            # Simple constraint parsing
            if 'unique' in constraint.lower():
                # Extract column names
                # Example: "email must be unique"
                for attr in entity.attributes:
                    if attr.name in constraint:
                        args.append(UniqueConstraint(attr.name))
            elif '>' in constraint or '<' in constraint or '=' in constraint:
                # Check constraint
                args.append(CheckConstraint(constraint))
        
        # Return args with table kwargs
        if args:
            args.append(table_kwargs)
            return tuple(args)
        else:
            return (table_kwargs,)
    
    async def cleanup_model(self, pim_model: PIMModel):
        """Clean up database tables and data for a model"""
        try:
            # Drop all tables for this model
            for entity in pim_model.entities:
                table_name = entity.name.lower()
                if table_name in self.models:
                    # Get the table object
                    model_class = self.models[table_name]
                    # Drop the table if it exists
                    if hasattr(model_class, '__table__'):
                        model_class.__table__.drop(self.engine, checkfirst=True)
                        self.logger.info(f"Dropped table: {table_name}")
                    
                    # Remove from models dict
                    del self.models[table_name]
                    
                    # Remove from metadata
                    if table_name in self.Base.metadata.tables:
                        self.Base.metadata.remove(self.Base.metadata.tables[table_name])
                    
                    # Remove from tables dict if exists
                    if table_name in self.tables:
                        del self.tables[table_name]
            
            self.logger.info(f"Database cleanup completed for model: {pim_model.domain}")
        except Exception as e:
            self.logger.error(f"Error during database cleanup: {e}")
    
    async def execute_operation(
        self,
        entity_name: str,
        operation: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a data operation"""
        model_class = self.models.get(entity_name)
        if not model_class:
            raise ValueError(f"Entity '{entity_name}' not found")
        
        with self.SessionLocal() as session:
            try:
                if operation == "create":
                    return await self._create(session, model_class, data)
                elif operation == "read":
                    return await self._read(session, model_class, data.get("id"))
                elif operation == "update":
                    return await self._update(
                        session,
                        model_class,
                        data.get("id"),
                        data
                    )
                elif operation == "delete":
                    return await self._delete(session, model_class, data.get("id"))
                elif operation == "list":
                    return await self._list(
                        session,
                        model_class,
                        data.get("filters", {}),
                        data.get("skip", 0),
                        data.get("limit", 100)
                    )
                else:
                    raise ValueError(f"Unknown operation: {operation}")
            except Exception as e:
                session.rollback()
                raise e
    
    async def _create(
        self,
        session: Session,
        model_class: Type,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new record"""
        # Remove system fields if present
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None)
        
        instance = model_class(**data)
        session.add(instance)
        session.commit()
        session.refresh(instance)
        
        return self._to_dict(instance)
    
    async def _read(
        self,
        session: Session,
        model_class: Type,
        id: str
    ) -> Optional[Dict[str, Any]]:
        """Read a single record"""
        instance = session.query(model_class).filter_by(id=id).first()
        if instance:
            return self._to_dict(instance)
        return None
    
    async def _update(
        self,
        session: Session,
        model_class: Type,
        id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a record"""
        instance = session.query(model_class).filter_by(id=id).first()
        if not instance:
            raise ValueError(f"Record with id '{id}' not found")
        
        # Remove system fields
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None)
        
        # Update fields
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        session.commit()
        session.refresh(instance)
        
        return self._to_dict(instance)
    
    async def _delete(
        self,
        session: Session,
        model_class: Type,
        id: str
    ) -> bool:
        """Delete a record"""
        instance = session.query(model_class).filter_by(id=id).first()
        if not instance:
            raise ValueError(f"Record with id '{id}' not found")
        
        session.delete(instance)
        session.commit()
        
        return True
    
    async def _list(
        self,
        session: Session,
        model_class: Type,
        filters: Dict[str, Any],
        skip: int,
        limit: int
    ) -> Dict[str, Any]:
        """List records with filters and pagination"""
        query = session.query(model_class)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(model_class, key):
                query = query.filter(getattr(model_class, key) == value)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        items = query.offset(skip).limit(limit).all()
        
        return {
            "items": [self._to_dict(item) for item in items],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def _to_dict(self, instance: Any) -> Dict[str, Any]:
        """Convert SQLAlchemy instance to dictionary"""
        result = {}
        
        for column in instance.__table__.columns:
            value = getattr(instance, column.name)
            
            # Handle datetime serialization
            if isinstance(value, datetime):
                value = value.isoformat()
            
            result[column.name] = value
        
        return result