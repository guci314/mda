"""Main entry point for PIM Engine"""

import asyncio
from pathlib import Path

from core.engine import PIMEngine
from core.config import settings


async def load_initial_models(engine: PIMEngine):
    """Load models from the models directory on startup"""
    models_path = Path(settings.models_path)
    
    if not models_path.exists():
        print(f"Models directory not found: {models_path}")
        return
    
    # Load all YAML models
    for model_file in models_path.glob("*.yaml"):
        print(f"Loading model: {model_file.name}")
        result = await engine.load_model(model_file.stem)
        if result.success:
            print(f"✓ Loaded {model_file.stem}")
        else:
            print(f"✗ Failed to load {model_file.stem}: {result.errors}")
    
    # Load all Markdown models
    for model_file in models_path.glob("*.md"):
        # Skip non-PIM files
        if "_pim" not in model_file.name:
            continue
            
        print(f"Loading model: {model_file.name}")
        result = await engine.load_model(model_file.stem)
        if result.success:
            print(f"✓ Loaded {model_file.stem}")
        else:
            print(f"✗ Failed to load {model_file.stem}: {result.errors}")


def main():
    """Main function"""
    print(f"""
╔═══════════════════════════════════════╗
║       PIM Execution Engine v{settings.app_version}      ║
║   Platform Independent Model Runtime  ║
╚═══════════════════════════════════════╝
    """)
    
    # Get engine instance
    engine = PIMEngine.get_instance()
    
    # Load initial models
    asyncio.run(load_initial_models(engine))
    
    print(f"\nStarting server on http://{settings.host}:{settings.port}")
    print(f"API Docs: http://{settings.host}:{settings.port}{settings.docs_url}")
    print(f"Health: http://{settings.host}:{settings.port}/health")
    print("\nPress CTRL+C to stop\n")
    
    # Run engine
    engine.run()


if __name__ == "__main__":
    main()