"""Main entry point for PIM Engine Master Controller"""

import uvicorn
from master import create_app
from core.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main function"""
    print(f"""
╔═══════════════════════════════════════════════╗
║     PIM Engine Master Controller v2.0.0       ║
║   Multi-Process Model Instance Management     ║
╚═══════════════════════════════════════════════╝
    """)
    
    # Create master app
    app = create_app()
    
    print(f"\nStarting master controller on http://{settings.host}:{settings.port}")
    print(f"API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"Health: http://{settings.host}:{settings.port}/health")
    print("\nPress CTRL+C to stop\n")
    
    # Run server
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()