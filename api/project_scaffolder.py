"""
Project Scaffolder - Create new projects from templates
"""
from typing import Dict, List
import os
from pathlib import Path

class ProjectScaffolder:
    """Create new projects from templates"""
    
    def __init__(self):
        self.templates = {
            "flask": {
                "name": "Flask App",
                "description": "Python Flask web application",
                "files": {
                    "app.py": "from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'Hello Flask!'\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000)",
                    "requirements.txt": "flask==3.0.0",
                    "README.md": "# Flask App\n\nA simple Flask application."
                }
            },
            "fastapi": {
                "name": "FastAPI App",
                "description": "Python FastAPI REST API",
                "files": {
                    "main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'message': 'Hello FastAPI!'}",
                    "requirements.txt": "fastapi==0.104.0\nuvicorn==0.24.0",
                    "README.md": "# FastAPI App\n\nA modern REST API built with FastAPI."
                }
            },
            "react": {
                "name": "React App",
                "description": "React frontend application",
                "files": {
                    "package.json": '{\n  "name": "react-app",\n  "version": "1.0.0",\n  "dependencies": {\n    "react": "^18.2.0",\n    "react-dom": "^18.2.0"\n  }\n}',
                    "README.md": "# React App\n\nA React application."
                }
            },
            "express": {
                "name": "Express API",
                "description": "Node.js Express REST API",
                "files": {
                    "index.js": "const express = require('express');\nconst app = express();\n\napp.get('/', (req, res) => {\n  res.json({ message: 'Hello Express!' });\n});\n\napp.listen(3000, () => console.log('Server running on port 3000'));",
                    "package.json": '{\n  "name": "express-api",\n  "version": "1.0.0",\n  "dependencies": {\n    "express": "^4.18.2"\n  }\n}',
                    "README.md": "# Express API\n\nA REST API built with Express.js."
                }
            }
        }
    
    def list_templates(self) -> Dict:
        """List all available templates"""
        return {
            "success": True,
            "templates": [
                {"id": k, **v}
                for k, v in self.templates.items()
            ],
            "total": len(self.templates)
        }
    
    def create_project(self, template_id: str, project_name: str, target_dir: str = ".") -> Dict:
        """Create a new project from template"""
        if template_id not in self.templates:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        template = self.templates[template_id]
        project_path = Path(target_dir) / project_name
        
        # Create project directory
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            
            created_files = []
            for filename, content in template["files"].items():
                file_path = project_path / filename
                file_path.write_text(content)
                created_files.append(str(file_path))
            
            return {
                "success": True,
                "message": f"Project created: {project_name}",
                "template": template_id,
                "path": str(project_path),
                "files_created": created_files,
                "total_files": len(created_files)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create project: {str(e)}"
            }
    
    def get_template_info(self, template_id: str) -> Dict:
        """Get detailed information about a template"""
        if template_id not in self.templates:
            return {
                "success": False,
                "error": f"Template not found: {template_id}"
            }
        
        template = self.templates[template_id]
        
        return {
            "success": True,
            "template": {
                "id": template_id,
                **template,
                "file_list": list(template["files"].keys())
            }
        }
