"""
Deployment Manager Module - Configure deployments
"""
from pathlib import Path
from typing import Dict
import json

class DeploymentManager:
    """Manage deployment configurations"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
    
    def configure_deployment(self, 
                           deployment_type: str,
                           run_command: str,
                           build_command: str = "") -> Dict:
        """Configure deployment settings"""
        try:
            valid_types = ["autoscale", "vm", "static"]
            if deployment_type not in valid_types:
                return {
                    "success": False,
                    "error": f"Invalid deployment type. Use: {', '.join(valid_types)}"
                }
            
            config = {
                "deployment": {
                    "type": deployment_type,
                    "run": run_command
                }
            }
            
            if build_command:
                config["deployment"]["build"] = build_command
            
            config_file = self.base_dir / ".replit.deployment.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return {
                "success": True,
                "message": "Deployment configured",
                "config": config,
                "type": deployment_type
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_deployment_config(self) -> Dict:
        """Get current deployment configuration"""
        try:
            config_file = self.base_dir / ".replit.deployment.json"
            
            if not config_file.exists():
                return {
                    "success": True,
                    "configured": False,
                    "message": "No deployment configured"
                }
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            return {
                "success": True,
                "configured": True,
                "config": config
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def suggest_deployment(self, project_type: str) -> Dict:
        """Suggest deployment configuration based on project type"""
        suggestions = {
            "flask": {
                "type": "autoscale",
                "run": "gunicorn -w 4 -b 0.0.0.0:5000 app:app",
                "build": "pip install -r requirements.txt"
            },
            "fastapi": {
                "type": "autoscale",
                "run": "uvicorn main:app --host 0.0.0.0 --port 5000",
                "build": "pip install -r requirements.txt"
            },
            "node": {
                "type": "autoscale",
                "run": "node server.js",
                "build": "npm install"
            },
            "react": {
                "type": "static",
                "run": "npm run build && npx serve -s build -l 5000",
                "build": "npm install && npm run build"
            },
            "static": {
                "type": "static",
                "run": "python -m http.server 5000",
                "build": None
            }
        }
        
        project_lower = project_type.lower()
        if project_lower not in suggestions:
            return {
                "success": False,
                "error": f"Unknown project type. Available: {', '.join(suggestions.keys())}"
            }
        
        return {
            "success": True,
            "project_type": project_type,
            "suggestion": suggestions[project_lower]
        }
