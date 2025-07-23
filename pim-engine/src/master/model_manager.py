"""Model Manager - Manages PIM model definitions"""

import os
import sys
from pathlib import Path

# Add pim-compiler to path BEFORE any other imports
_pim_compiler_path = Path(__file__).parent.parent.parent.parent / "pim-compiler" / "src"
if str(_pim_compiler_path) not in sys.path:
    sys.path.insert(0, str(_pim_compiler_path))

from typing import Dict, List, Optional
from datetime import datetime

from core.models import PIMModel, ModelLoadResult
from loaders import ModelLoader
from core.config import settings
from utils.logger import setup_logger
from .persistence_manager import PersistenceManager
from database.models import ModelStatus

logger = setup_logger(__name__)

# Import PIM compiler
COMPILER_AVAILABLE = True  # Enable compiler - will import when needed


class ModelInfo:
    """Information about a loaded model"""
    def __init__(self, name: str, model: PIMModel, source_file: str, model_dir: Path | None = None):
        self.name = name
        self.model = model
        self.source_file = source_file
        self.loaded_at = datetime.now()
        self.version = model.version
        self.model_dir = model_dir or Path(f"classpath/{name}")
        
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "name": self.name,
            "version": self.version,
            "loaded_at": self.loaded_at.isoformat(),
            "source_file": self.source_file,
            "description": self.model.description,
            "entities": [e.name for e in self.model.entities],
            "services": [s.name for s in self.model.services]
        }


class ModelManager:
    """Manages loaded PIM models"""
    
    def __init__(self, persistence_manager: Optional[PersistenceManager] = None):
        self.models: Dict[str, ModelInfo] = {}
        self.model_loader = ModelLoader()
        self.models_path = Path(settings.models_path)
        self.classpath_dir = Path("classpath")  # Directory for compiled code
        self.classpath_dir.mkdir(exist_ok=True)
        self.persistence_manager = persistence_manager
        
    async def load_model(self, model_name: str) -> ModelInfo:
        """Load a model from file"""
        # Check if already loaded
        if model_name in self.models:
            raise ValueError(f"Model '{model_name}' is already loaded")
        
        # Find model file
        model_file = None
        for ext in ['.yaml', '.yml', '.md']:
            path = self.models_path / f"{model_name}{ext}"
            if path.exists():
                model_file = path
                break
        
        if not model_file:
            raise FileNotFoundError(f"Model file not found for '{model_name}'")
        
        # Update persistence status - loading
        if self.persistence_manager:
            self.persistence_manager.update_model_status(model_name, ModelStatus.LOADING)
        
        # Load model
        logger.info(f"Loading model from {model_file}")
        result = await self.model_loader.load_model(str(model_file))
        
        if not result.success:
            if self.persistence_manager:
                self.persistence_manager.update_model_status(
                    model_name, ModelStatus.ERROR, 
                    ', '.join(result.errors)
                )
            raise ValueError(f"Failed to load model: {', '.join(result.errors)}")
        
        # Store model info
        if result.model is None:
            if self.persistence_manager:
                self.persistence_manager.update_model_status(
                    model_name, ModelStatus.ERROR,
                    "Model loading returned None"
                )
            raise ValueError(f"Model loading returned None for '{model_name}'")
        
        model_info = ModelInfo(
            name=model_name,
            model=result.model,
            source_file=model_file.name,
            model_dir=Path(f"classpath/{model_name}")
        )
        
        # Save to persistence before compilation
        if self.persistence_manager:
            try:
                # Read file content
                content = model_file.read_text()
                self.persistence_manager.save_model(
                    name=model_name,
                    model=result.model,
                    source_file=str(model_file),
                    content=content,
                    format=model_file.suffix[1:]  # Remove the dot
                )
            except Exception as e:
                logger.error(f"Failed to persist model '{model_name}': {e}")
        
        # Compile model if compiler is available
        if COMPILER_AVAILABLE and model_file.suffix == '.md':
            try:
                if self.persistence_manager:
                    self.persistence_manager.update_model_status(model_name, ModelStatus.COMPILING)
                await self._compile_model(model_name, model_file)
                if self.persistence_manager:
                    self.persistence_manager.update_model_status(model_name, ModelStatus.COMPILED)
            except Exception as e:
                logger.error(f"Failed to compile model '{model_name}': {e}")
                if self.persistence_manager:
                    self.persistence_manager.update_model_status(
                        model_name, ModelStatus.LOADED,
                        f"Compilation failed: {str(e)}"
                    )
                # Continue even if compilation fails
        
        self.models[model_name] = model_info
        
        logger.info(f"Model '{model_name}' loaded successfully")
        return model_info
    
    def unload_model(self, model_name: str, hard: bool = False) -> bool:
        """Unload a model
        
        Args:
            model_name: Name of the model to unload
            hard: If True, delete all model files and directories
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")
        
        model_info = self.models[model_name]
        
        # Update persistence status
        if self.persistence_manager:
            self.persistence_manager.update_model_status(model_name, ModelStatus.UNLOADING)
        
        # Remove from memory
        del self.models[model_name]
        
        if hard:
            # Delete model directory (contains generated code, PSM, etc.)
            if model_info.model_dir.exists():
                logger.info(f"Deleting model directory: {model_info.model_dir}")
                import shutil
                try:
                    shutil.rmtree(model_info.model_dir)
                    logger.info(f"Model directory deleted: {model_info.model_dir}")
                except Exception as e:
                    logger.error(f"Failed to delete model directory: {e}")
            
            # Delete from persistence
            if self.persistence_manager:
                self.persistence_manager.delete_model(model_name)
        else:
            # Just update status for soft unload
            if self.persistence_manager:
                self.persistence_manager.update_model_status(model_name, ModelStatus.LOADED)
        
        logger.info(f"Model '{model_name}' {'hard' if hard else ''} unloaded")
        return True
    
    def get_model(self, model_name: str) -> Optional[ModelInfo]:
        """Get a loaded model"""
        return self.models.get(model_name)
    
    def list_models(self) -> List[ModelInfo]:
        """List all loaded models"""
        return list(self.models.values())
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a model is loaded"""
        return model_name in self.models
    
    async def _compile_model(self, model_name: str, model_file: Path):
        """Compile a PIM model to FastAPI code"""
        logger.info(f"Compiling model '{model_name}' from {model_file}")
        
        # Import compiler here to avoid import conflicts
        try:
            from compiler import PureGeminiCompiler, CompilerConfig
        except ImportError as e:
            logger.error(f"Failed to import compiler: {e}")
            raise Exception(f"Compiler not available: {e}")
        
        # Create output directory for this model
        output_dir = self.classpath_dir / model_name
        output_dir.mkdir(exist_ok=True)
        
        # Configure compiler
        config = CompilerConfig(
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            output_dir=output_dir,  # CompilerConfig expects Path object
            target_platform="fastapi",
            enable_cache=False,  # 禁用缓存确保重新生成完整代码
            verbose=True,
            auto_test=False,  # 暂时禁用自动测试
            generate_tests=True,
            generate_docs=True
        )
        
        # Create compiler instance
        compiler = PureGeminiCompiler(config)
        
        # Compile the model (PureGeminiCompiler.compile is synchronous)
        result = compiler.compile(model_file)
        
        if result.success:
            logger.info(f"Model '{model_name}' compiled successfully to {output_dir}")
            # Add the compiled code directory to Python path
            if str(output_dir) not in sys.path:
                sys.path.insert(0, str(output_dir))
        else:
            raise Exception(f"Compilation failed for model '{model_name}': {result.error}")
    
    async def restore_from_database(self):
        """Restore models from database on startup"""
        if not self.persistence_manager:
            logger.info("No persistence manager, skipping model restoration")
            return
        
        logger.info("Restoring models from database...")
        try:
            # Get all models from database - this should return detached objects
            db_models = self.persistence_manager.get_all_models()
            
            for model_data in db_models:
                try:
                    # model_data is already a dict from get_all_models()
                    model_name = model_data.get('name')
                    
                    # Skip if no name or model already loaded in memory
                    if not model_name:
                        logger.warning("Model without name found in database, skipping")
                        continue
                        
                    if model_name in self.models:
                        continue
                    
                    # Only restore models that were successfully loaded/compiled
                    status = model_data.get('status')
                    if status not in ['LOADED', 'COMPILED', ModelStatus.LOADED.value, ModelStatus.COMPILED.value]:
                        logger.info(f"Skipping model '{model_name}' with status {status}")
                        continue
                    
                    # Get compiled model data
                    compiled_model = model_data.get('compiled_model')
                    
                    # Recreate PIMModel from stored data
                    if compiled_model and isinstance(compiled_model, dict):
                        from core.models import PIMModel
                        model = PIMModel(**compiled_model)
                        
                        # Get source file with default
                        source_file = model_data.get('source_file', f"{model_name}.yaml")
                        
                        # Create ModelInfo
                        model_info = ModelInfo(
                            name=model_name,
                            model=model,
                            source_file=source_file,
                            model_dir=Path(f"classpath/{model_name}")
                        )
                        
                        # Store in memory
                        self.models[model_name] = model_info
                        logger.info(f"Restored model '{model_name}' from database")
                    else:
                        logger.warning(f"Model '{model_name}' has no compiled data, skipping")
                        
                except Exception as e:
                    logger.error(f"Failed to restore model: {e}")
                    
            logger.info(f"Restored {len(self.models)} models from database")
            
        except Exception as e:
            logger.error(f"Failed to restore models from database: {e}")