"""
Project Analyzer Module - Analyze project structure and dependencies
"""
import os
from pathlib import Path
from typing import Dict, List
import json

class ProjectAnalyzer:
    """Analyze project structure, dependencies, and configuration"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
    
    def detect_project_type(self) -> Dict:
        """Detect project type based on files"""
        indicators = {
            "flask": ["app.py", "application.py"],
            "fastapi": ["main.py", "api/"],
            "django": ["manage.py", "settings.py"],
            "node": ["package.json", "server.js"],
            "react": ["package.json", "src/App.js", "public/index.html"],
            "vue": ["package.json", "src/App.vue"],
            "python": ["*.py", "requirements.txt"],
            "static": ["index.html"]
        }
        
        detected = []
        
        for project_type, files in indicators.items():
            for file_pattern in files:
                if '*' in file_pattern:
                    if list(self.base_dir.glob(file_pattern)):
                        detected.append(project_type)
                        break
                else:
                    if (self.base_dir / file_pattern).exists():
                        detected.append(project_type)
                        break
        
        return {
            "success": True,
            "detected_types": detected,
            "primary_type": detected[0] if detected else "unknown"
        }
    
    def analyze_dependencies(self) -> Dict:
        """Analyze project dependencies"""
        dependencies = {
            "python": [],
            "node": [],
            "system": []
        }
        
        requirements_file = self.base_dir / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                dependencies["python"] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        package_json = self.base_dir / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
                dependencies["node"] = list(data.get("dependencies", {}).keys())
        
        return {
            "success": True,
            "dependencies": dependencies,
            "total_python": len(dependencies["python"]),
            "total_node": len(dependencies["node"])
        }
    
    def get_project_info(self) -> Dict:
        """Get comprehensive project information"""
        project_type = self.detect_project_type()
        dependencies = self.analyze_dependencies()
        
        files_count = len(list(self.base_dir.rglob("*.py")))
        js_files = len(list(self.base_dir.rglob("*.js")))
        html_files = len(list(self.base_dir.rglob("*.html")))
        
        return {
            "success": True,
            "project_type": project_type.get("primary_type"),
            "all_types": project_type.get("detected_types", []),
            "dependencies": dependencies.get("dependencies"),
            "file_counts": {
                "python": files_count,
                "javascript": js_files,
                "html": html_files
            }
        }
