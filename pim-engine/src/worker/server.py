"""Worker Server - Standalone model instance server"""

import asyncio
import sys
import argparse
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from worker.config import WorkerConfig
from worker.app import create_app
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def main():
    """Main entry point for worker server"""
    parser = argparse.ArgumentParser(description="PIM Engine Worker Server")
    parser.add_argument("--config", type=str, required=True, help="Path to config file")
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = WorkerConfig.from_file(args.config)
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        sys.exit(1)
    
    # Setup logging to file
    import logging
    file_handler = logging.FileHandler(config.log_file)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logging.getLogger().addHandler(file_handler)
    
    logger.info(f"Starting worker server for instance '{config.instance_id}'")
    
    # Create app
    app = await create_app(config)
    
    # Run server
    uvicorn_config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=config.port,
        log_level="info" if config.debug else "warning",
        access_log=config.debug
    )
    
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())