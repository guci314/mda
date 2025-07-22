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

logger = setup_logger(__name__)

# Import PIM compiler
COMPILER_AVAILABLE = True  # Enable compiler - will import when needed


class ModelInfo:
    """Information about a loaded model"""
    def __init__(self, name: str, model: PIMModel, source_file: str):
        self.name = name
        self.model = model
        self.source_file = source_file
        self.loaded_at = datetime.now()
        self.version = model.version
        
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
    
    def __init__(self):
        self.models: Dict[str, ModelInfo] = {}
        self.model_loader = ModelLoader()
        self.models_path = Path(settings.models_path)
        self.classpath_dir = Path("classpath")  # Directory for compiled code
        self.classpath_dir.mkdir(exist_ok=True)
        
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
        
        # Load model
        logger.info(f"Loading model from {model_file}")
        result = await self.model_loader.load_model(str(model_file))
        
        if not result.success:
            raise ValueError(f"Failed to load model: {', '.join(result.errors)}")
        
        # Store model info
        model_info = ModelInfo(
            name=model_name,
            model=result.model,
            source_file=model_file.name
        )
        
        # Compile model if compiler is available
        if COMPILER_AVAILABLE and model_file.suffix == '.md':
            try:
                await self._compile_model(model_name, model_file)
            except Exception as e:
                logger.error(f"Failed to compile model '{model_name}': {e}")
                # Continue even if compilation fails
        
        self.models[model_name] = model_info
        
        logger.info(f"Model '{model_name}' loaded successfully")
        return model_info
    
    def unload_model(self, model_name: str) -> bool:
        """Unload a model"""
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")
        
        del self.models[model_name]
        logger.info(f"Model '{model_name}' unloaded")
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
            gemini_api_key=os.getenv("GOOGLE_AI_STUDIO_KEY", ""),
            output_dir=str(output_dir),
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