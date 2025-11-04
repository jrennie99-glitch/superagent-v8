"""
Codebase Search Module - Search and analyze code
"""
import os
from pathlib import Path
import subprocess
from typing import Dict, List
import re

class CodebaseSearch:
    """Search and analyze codebase"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.excluded_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
    
    def search_pattern(self, pattern: str, file_types: List[str] = None) -> Dict:
        """Search for pattern in codebase"""
        try:
            cmd = ['grep', '-r', '-n', pattern, '.']
            
            if file_types:
                for ft in file_types:
                    cmd.extend(['--include', f'*.{ft}'])
            
            for excluded in self.excluded_dirs:
                cmd.extend(['--exclude-dir', excluded])
            
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            matches = []
            for line in result.stdout.split('\n')[:200]:
                if line.strip():
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        matches.append({
                            "file": parts[0],
                            "line": int(parts[1]) if parts[1].isdigit() else 0,
                            "content": parts[2].strip()
                        })
            
            return {
                "success": True,
                "pattern": pattern,
                "matches": matches,
                "total": len(matches)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_function(self, function_name: str) -> Dict:
        """Find function definitions"""
        patterns = [
            f'def {function_name}',
            f'function {function_name}',
            f'const {function_name} =',
            f'let {function_name} =',
            f'async def {function_name}',
        ]
        
        all_matches = []
        for pattern in patterns:
            result = self.search_pattern(pattern)
            if result.get('success'):
                all_matches.extend(result.get('matches', []))
        
        return {
            "success": True,
            "function": function_name,
            "definitions": all_matches,
            "total": len(all_matches)
        }
    
    def find_class(self, class_name: str) -> Dict:
        """Find class definitions"""
        pattern = f'class {class_name}'
        return self.search_pattern(pattern)
    
    def get_imports(self, file_path: str) -> Dict:
        """Extract imports from a file"""
        try:
            target_file = self.base_dir / file_path
            if not target_file.exists():
                return {"success": False, "error": "File not found"}
            
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            imports = []
            
            python_imports = re.findall(r'^(?:from|import)\s+[\w.]+', content, re.MULTILINE)
            imports.extend(python_imports)
            
            js_imports = re.findall(r'(?:import|require)\s*\([\'"]([^\'"]+)[\'"]\)', content)
            imports.extend(js_imports)
            
            return {
                "success": True,
                "file": file_path,
                "imports": list(set(imports)),
                "total": len(set(imports))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_structure(self) -> Dict:
        """Analyze project structure"""
        try:
            structure = {
                "python_files": [],
                "javascript_files": [],
                "html_files": [],
                "css_files": [],
                "other_files": []
            }
            
            for item in self.base_dir.rglob("*"):
                if any(excluded in item.parts for excluded in self.excluded_dirs):
                    continue
                
                if item.is_file():
                    relative_path = str(item.relative_to(self.base_dir))
                    
                    if item.suffix == '.py':
                        structure["python_files"].append(relative_path)
                    elif item.suffix in ['.js', '.jsx', '.ts', '.tsx']:
                        structure["javascript_files"].append(relative_path)
                    elif item.suffix == '.html':
                        structure["html_files"].append(relative_path)
                    elif item.suffix == '.css':
                        structure["css_files"].append(relative_path)
                    else:
                        structure["other_files"].append(relative_path)
            
            return {
                "success": True,
                "structure": structure,
                "total_files": sum(len(files) for files in structure.values())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
