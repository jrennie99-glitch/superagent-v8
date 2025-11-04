"""
File Operations Module - Complete file system management
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import subprocess
import shutil

class FileOperations:
    """Handles all file system operations"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.excluded_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.replit'}
    
    def list_files(self, directory: str = ".", recursive: bool = True, max_depth: int = 5) -> Dict:
        """List all files in directory"""
        try:
            target_dir = self.base_dir / directory
            if not target_dir.exists():
                return {"success": False, "error": "Directory not found"}
            
            files = []
            dirs = []
            
            if recursive:
                for item in target_dir.rglob("*"):
                    if any(excluded in item.parts for excluded in self.excluded_dirs):
                        continue
                    
                    relative_path = str(item.relative_to(self.base_dir))
                    if item.is_file():
                        files.append({
                            "path": relative_path,
                            "name": item.name,
                            "size": item.stat().st_size,
                            "type": item.suffix or "file"
                        })
                    elif item.is_dir():
                        dirs.append(relative_path)
            else:
                for item in target_dir.iterdir():
                    if item.name in self.excluded_dirs:
                        continue
                    
                    relative_path = str(item.relative_to(self.base_dir))
                    if item.is_file():
                        files.append({
                            "path": relative_path,
                            "name": item.name,
                            "size": item.stat().st_size,
                            "type": item.suffix or "file"
                        })
                    elif item.is_dir():
                        dirs.append(relative_path)
            
            return {
                "success": True,
                "files": files[:500],
                "directories": dirs[:100],
                "total_files": len(files),
                "total_dirs": len(dirs)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_file(self, file_path: str) -> Dict:
        """Read file content"""
        try:
            target_file = self.base_dir / file_path
            if not target_file.exists():
                return {"success": False, "error": "File not found"}
            
            if not target_file.is_file():
                return {"success": False, "error": "Path is not a file"}
            
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "path": file_path,
                "size": target_file.stat().st_size,
                "lines": len(content.split('\n'))
            }
        except UnicodeDecodeError:
            return {"success": False, "error": "Binary file - cannot read as text"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_file(self, file_path: str, content: str, create_dirs: bool = True) -> Dict:
        """Write content to file"""
        try:
            target_file = self.base_dir / file_path
            
            if create_dirs:
                target_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"File written: {file_path}",
                "path": file_path,
                "size": target_file.stat().st_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_file(self, file_path: str) -> Dict:
        """Delete a file"""
        try:
            target_file = self.base_dir / file_path
            if not target_file.exists():
                return {"success": False, "error": "File not found"}
            
            if target_file.is_file():
                target_file.unlink()
                return {"success": True, "message": f"File deleted: {file_path}"}
            else:
                return {"success": False, "error": "Path is not a file"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_in_files(self, pattern: str, file_extension: Optional[str] = None) -> Dict:
        """Search for pattern in files using grep"""
        try:
            cmd = ['grep', '-r', '-n', '-i', pattern, '.']
            
            if file_extension:
                cmd.extend(['--include', f'*.{file_extension}'])
            
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            matches = []
            for line in result.stdout.split('\n')[:100]:
                if line.strip():
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        matches.append({
                            "file": parts[0],
                            "line": parts[1],
                            "content": parts[2]
                        })
            
            return {
                "success": True,
                "pattern": pattern,
                "matches": matches,
                "total": len(matches)
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Search timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_directory(self, dir_path: str) -> Dict:
        """Create a directory"""
        try:
            target_dir = self.base_dir / dir_path
            target_dir.mkdir(parents=True, exist_ok=True)
            return {"success": True, "message": f"Directory created: {dir_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_directory(self, dir_path: str) -> Dict:
        """Delete a directory"""
        try:
            target_dir = self.base_dir / dir_path
            if not target_dir.exists():
                return {"success": False, "error": "Directory not found"}
            
            if target_dir.is_dir():
                shutil.rmtree(target_dir)
                return {"success": True, "message": f"Directory deleted: {dir_path}"}
            else:
                return {"success": False, "error": "Path is not a directory"}
        except Exception as e:
            return {"success": False, "error": str(e)}
