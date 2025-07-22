"""Process Manager - Manages instance processes"""

import os
import sys
import signal
import psutil
import asyncio
import subprocess
from typing import Dict, Optional
from pathlib import Path
from threading import Lock

from utils.logger import setup_logger

logger = setup_logger(__name__)


class ProcessInfo:
    """Information about a running process"""
    def __init__(self, instance_id: str, pid: int, port: int, model_name: str):
        self.instance_id = instance_id
        self.pid = pid
        self.port = port
        self.model_name = model_name
        self.process: Optional[subprocess.Popen] = None
        
    def is_alive(self) -> bool:
        """Check if the process is still running"""
        try:
            if self.process:
                return self.process.poll() is None
            else:
                # Check by PID
                return psutil.pid_exists(self.pid)
        except:
            return False


class ProcessManager:
    """Manages model instance processes"""
    
    def __init__(self):
        self.processes: Dict[str, ProcessInfo] = {}
        self._lock = Lock()
        
    async def start_process(self, instance_id: str, model_name: str, port: int, 
                          config: Optional[dict] = None) -> ProcessInfo:
        """Start a new instance process"""
        with self._lock:
            if instance_id in self.processes:
                raise ValueError(f"Instance '{instance_id}' is already running")
        
        # Create instance directory
        instance_dir = Path("instances") / instance_id
        instance_dir.mkdir(parents=True, exist_ok=True)
        
        # Create instance config
        import json
        config_data = {
            "instance_id": instance_id,
            "model_name": model_name,
            "port": port,
            "database_url": f"sqlite:///instances/{instance_id}/database.db",
            "log_file": f"logs/{instance_id}.log",
            **(config or {})
        }
        
        config_file = instance_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Start the process
        cmd = [
            sys.executable,
            "-m", "worker.server",
            "--config", str(config_file)
        ]
        
        # Setup environment
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent.parent)
        
        # Start process
        logger.info(f"Starting instance '{instance_id}' on port {port}")
        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if sys.platform != 'win32' else None
            )
            
            # Wait a bit to ensure process started
            await asyncio.sleep(1)
            
            # Check if process is running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise RuntimeError(f"Process failed to start: {stderr.decode()}")
            
            # Store process info
            process_info = ProcessInfo(
                instance_id=instance_id,
                pid=process.pid,
                port=port,
                model_name=model_name
            )
            process_info.process = process
            
            with self._lock:
                self.processes[instance_id] = process_info
            
            logger.info(f"Instance '{instance_id}' started with PID {process.pid}")
            return process_info
            
        except Exception as e:
            logger.error(f"Failed to start instance '{instance_id}': {str(e)}")
            raise
    
    async def stop_process(self, instance_id: str):
        """Stop a running instance process"""
        with self._lock:
            if instance_id not in self.processes:
                raise ValueError(f"Instance '{instance_id}' not found")
            
            process_info = self.processes[instance_id]
        
        logger.info(f"Stopping instance '{instance_id}' (PID: {process_info.pid})")
        
        try:
            if process_info.process:
                # Try graceful shutdown first
                process_info.process.terminate()
                try:
                    await asyncio.wait_for(
                        asyncio.create_task(self._wait_for_process(process_info.process)),
                        timeout=10.0
                    )
                except asyncio.TimeoutError:
                    # Force kill if graceful shutdown failed
                    logger.warning(f"Graceful shutdown failed, force killing instance '{instance_id}'")
                    if sys.platform != 'win32':
                        os.killpg(os.getpgid(process_info.pid), signal.SIGKILL)
                    else:
                        process_info.process.kill()
            else:
                # Kill by PID
                try:
                    process = psutil.Process(process_info.pid)
                    process.terminate()
                    process.wait(timeout=10)
                except psutil.TimeoutExpired:
                    process.kill()
                except psutil.NoSuchProcess:
                    pass
        
        except Exception as e:
            logger.error(f"Error stopping instance '{instance_id}': {str(e)}")
        
        finally:
            with self._lock:
                del self.processes[instance_id]
            logger.info(f"Instance '{instance_id}' stopped")
    
    async def _wait_for_process(self, process: subprocess.Popen):
        """Wait for a process to terminate"""
        while process.poll() is None:
            await asyncio.sleep(0.1)
    
    def get_process(self, instance_id: str) -> Optional[ProcessInfo]:
        """Get process info for an instance"""
        return self.processes.get(instance_id)
    
    def list_processes(self) -> Dict[str, ProcessInfo]:
        """List all managed processes"""
        return self.processes.copy()
    
    async def check_health(self, instance_id: str) -> bool:
        """Check if an instance is healthy"""
        process_info = self.processes.get(instance_id)
        if not process_info:
            return False
        
        # Check if process is alive
        if not process_info.is_alive():
            return False
        
        # Try to connect to the instance
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{process_info.port}/health", timeout=5) as resp:
                    return resp.status == 200
        except:
            return False
    
    async def stop_all_processes(self):
        """Stop all running processes"""
        logger.info("Stopping all instances...")
        instance_ids = list(self.processes.keys())
        
        for instance_id in instance_ids:
            try:
                await self.stop_process(instance_id)
            except Exception as e:
                logger.error(f"Error stopping instance '{instance_id}': {str(e)}")