"""Port Manager - Manages port allocation for instances"""

import socket
from typing import Set, Optional
from threading import Lock

from utils.logger import setup_logger

logger = setup_logger(__name__)


class PortManager:
    """Manages port allocation for model instances"""
    
    def __init__(self, start_port: int = 8001, end_port: int = 8999):
        self.start_port = start_port
        self.end_port = end_port
        self.allocated_ports: Set[int] = set()
        self._lock = Lock()
    
    def allocate_port(self, preferred_port: Optional[int] = None) -> int:
        """Allocate a port for an instance"""
        with self._lock:
            # Try preferred port first
            if preferred_port:
                if self._is_port_available(preferred_port):
                    self.allocated_ports.add(preferred_port)
                    logger.info(f"Allocated preferred port: {preferred_port}")
                    return preferred_port
                else:
                    logger.warning(f"Preferred port {preferred_port} is not available")
            
            # Find next available port
            for port in range(self.start_port, self.end_port + 1):
                if port not in self.allocated_ports and self._is_port_available(port):
                    self.allocated_ports.add(port)
                    logger.info(f"Allocated port: {port}")
                    return port
            
            raise RuntimeError(f"No available ports in range {self.start_port}-{self.end_port}")
    
    def release_port(self, port: int):
        """Release a previously allocated port"""
        with self._lock:
            if port in self.allocated_ports:
                self.allocated_ports.remove(port)
                logger.info(f"Released port: {port}")
            else:
                logger.warning(f"Port {port} was not allocated")
    
    def is_port_allocated(self, port: int) -> bool:
        """Check if a port is currently allocated"""
        return port in self.allocated_ports
    
    def get_allocated_ports(self) -> Set[int]:
        """Get all currently allocated ports"""
        return self.allocated_ports.copy()
    
    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available for binding"""
        if port in self.allocated_ports:
            return False
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except OSError:
            return False