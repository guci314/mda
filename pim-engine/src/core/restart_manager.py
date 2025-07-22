"""Application restart manager for model updates"""

import os
import sys
import signal
import asyncio
import logging
from typing import Set
from pathlib import Path

logger = logging.getLogger(__name__)


class RestartManager:
    """Manages application restart when models are loaded/unloaded"""
    
    def __init__(self):
        self.pending_restart = False
        self.restart_reason = ""
        self.loaded_models: Set[str] = set()
        self._restart_file = Path("/tmp/pim_engine_restart.flag")
        
    def model_loaded(self, model_name: str):
        """Track model loading"""
        self.loaded_models.add(model_name)
        logger.info(f"Model {model_name} tracked for restart management")
        
    def model_unloaded(self, model_name: str):
        """Track model unloading and schedule restart"""
        if model_name in self.loaded_models:
            self.loaded_models.remove(model_name)
            self.schedule_restart(f"Model '{model_name}' was unloaded")
            
    def schedule_restart(self, reason: str):
        """Schedule application restart"""
        self.pending_restart = True
        self.restart_reason = reason
        logger.warning(f"Application restart scheduled: {reason}")
        
        # Create restart flag file for Docker
        self._restart_file.write_text(reason)
        
    async def check_and_restart(self):
        """Check if restart is needed and perform it"""
        if self.pending_restart:
            logger.warning(f"Restarting application: {self.restart_reason}")
            
            # Give time for response to be sent
            await asyncio.sleep(0.5)
            
            # If running in Docker, exit and let Docker restart the container
            if os.environ.get("DOCKER_CONTAINER"):
                logger.info("Running in Docker, exiting for container restart...")
                os._exit(0)
            else:
                # For local development, restart the Python process
                logger.info("Restarting Python process...")
                # Get the original command line arguments
                # In this case, we know it's "python src/main.py"
                os.execv(sys.executable, [sys.executable, 'src/main.py'])
                
    def graceful_restart(self):
        """Perform graceful restart"""
        if os.environ.get("DOCKER_CONTAINER"):
            # In Docker, just exit cleanly
            logger.info("Graceful shutdown for Docker restart...")
            sys.exit(0)
        else:
            # Send SIGTERM to self for graceful shutdown
            os.kill(os.getpid(), signal.SIGTERM)