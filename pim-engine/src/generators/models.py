"""Models for code generation"""

import io
import zipfile
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CodeFile:
    """Generated code file"""
    path: str
    content: str
    description: Optional[str] = None


@dataclass 
class CodePackage:
    """Complete code package"""
    platform: str
    model_name: str
    files: List[CodeFile]
    structure: Dict[str, Any]
    metadata: Dict[str, Any]
    
    async def to_zip(self) -> io.BytesIO:
        """Convert to ZIP file"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all code files
            for file in self.files:
                zip_file.writestr(file.path, file.content)
                
            # Add metadata
            metadata_content = f"""# {self.model_name} - {self.platform}
Generated at: {datetime.now().isoformat()}
Platform: {self.platform}

## Project Structure
{self._format_structure(self.structure)}

## Files
{self._format_files_list()}
"""
            zip_file.writestr("README.md", metadata_content)
            
        zip_buffer.seek(0)
        return zip_buffer
        
    def _format_structure(self, structure: Dict[str, Any], indent: int = 0) -> str:
        """Format project structure for display"""
        lines = []
        for key, value in structure.items():
            if isinstance(value, dict):
                lines.append(f"{'  ' * indent}{key}/")
                lines.append(self._format_structure(value, indent + 1))
            else:
                lines.append(f"{'  ' * indent}{key}")
        return '\n'.join(lines)
        
    def _format_files_list(self) -> str:
        """Format files list"""
        return '\n'.join(f"- {file.path}: {file.description or 'Generated file'}" 
                        for file in self.files)