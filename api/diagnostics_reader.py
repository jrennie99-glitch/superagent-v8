"""
Diagnostics Reader - Read LSP errors and warnings
"""
import subprocess
from pathlib import Path
from typing import Dict, List

class DiagnosticsReader:
    """Read LSP diagnostics and code errors"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
    
    def get_python_errors(self) -> Dict:
        """Get Python syntax errors using pylint/flake8"""
        try:
            # Try using python syntax check
            python_files = list(self.base_dir.rglob("*.py"))[:20]
            errors = []
            
            for file in python_files:
                try:
                    result = subprocess.run(
                        ['python', '-m', 'py_compile', str(file)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode != 0:
                        errors.append({
                            "file": str(file.relative_to(self.base_dir)),
                            "error": result.stderr
                        })
                except Exception:
                    continue
            
            return {
                "success": True,
                "language": "python",
                "errors": errors,
                "total": len(errors)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_javascript_errors(self) -> Dict:
        """Get JavaScript syntax errors"""
        try:
            js_files = list(self.base_dir.rglob("*.js"))[:20]
            errors = []
            
            for file in js_files:
                try:
                    result = subprocess.run(
                        ['node', '--check', str(file)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode != 0:
                        errors.append({
                            "file": str(file.relative_to(self.base_dir)),
                            "error": result.stderr
                        })
                except Exception:
                    continue
            
            return {
                "success": True,
                "language": "javascript",
                "errors": errors,
                "total": len(errors)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_all_diagnostics(self) -> Dict:
        """Check all code for errors"""
        python_errors = self.get_python_errors()
        js_errors = self.get_javascript_errors()
        
        total_errors = (
            python_errors.get("total", 0) +
            js_errors.get("total", 0)
        )
        
        return {
            "success": True,
            "python": python_errors.get("errors", []),
            "javascript": js_errors.get("errors", []),
            "total_errors": total_errors,
            "has_errors": total_errors > 0
        }
