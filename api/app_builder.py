"""
SuperAgent App Builder - Actually builds working applications
Creates files, installs dependencies, sets up workflows like Replit Agent
"""
import os
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import json
import re

class AppBuilder:
    def __init__(self):
        # Use current directory as workspace
        self.workspace_root = Path.cwd()
        self.active_processes = {}  # Track running servers
    
    async def start_server(self, app_name: str, app_dir: Path, run_command: str, port: int) -> bool:
        """Start a server process for the built app"""
        try:
            # Kill any existing server on this port
            await self.stop_server(app_name)
            await self._kill_port(port)  # Ensure port is free
            
            # Parse command
            parts = run_command.split()
            
            # Start the server process in the app directory
            process = await asyncio.create_subprocess_exec(
                *parts,
                cwd=str(app_dir),  # CRITICAL: Run in app directory
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Store the process
            self.active_processes[app_name] = {
                "process": process,
                "port": port,
                "command": run_command,
                "dir": str(app_dir)
            }
            
            # Give it time to start and verify
            await asyncio.sleep(3)
            
            # Check if port is listening (basic health check)
            is_running = await self._check_port(port)
            
            return is_running
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    async def _check_port(self, port: int) -> bool:
        """Check if a port is listening"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
    
    async def _kill_port(self, port: int):
        """Kill any process using this port"""
        try:
            process = await asyncio.create_subprocess_exec(
                "lsof", "-t", f"-i:{port}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            if stdout:
                pid = stdout.decode().strip()
                if pid:
                    await asyncio.create_subprocess_exec("kill", "-9", pid)
                    await asyncio.sleep(0.5)
        except:
            pass
    
    async def stop_server(self, app_name: str) -> bool:
        """Stop a running server"""
        try:
            if app_name in self.active_processes:
                process_info = self.active_processes[app_name]
                process = process_info["process"]
                process.terminate()
                await process.wait()
                del self.active_processes[app_name]
            return True
        except Exception as e:
            print(f"Error stopping server: {e}")
            return False
        
    async def build_app(self, instruction: str, generated_code: str, language: str) -> Dict:
        """
        Actually builds the complete application:
        1. Creates all necessary files
        2. Installs dependencies
        3. Sets up workflows
        4. Returns build status
        """
        try:
            # CRITICAL FIX: If generated code is HTML, force static_web type
            code_stripped = generated_code.strip()
            if code_stripped.startswith('<!DOCTYPE') or code_stripped.startswith('<html'):
                app_type = "static_web"
            else:
                # Determine app type and structure
                app_type = self._detect_app_type(instruction, language)
            
            # Create app directory
            app_name = self._generate_app_name(instruction)
            app_dir = self.workspace_root / app_name
            app_dir.mkdir(parents=True, exist_ok=True)
            
            # Build based on app type
            if app_type == "flask_app":
                result = await self._build_flask_app(app_dir, generated_code, instruction)
            elif app_type == "fastapi_app":
                result = await self._build_fastapi_app(app_dir, generated_code, instruction)
            elif app_type == "node_express":
                result = await self._build_node_express_app(app_dir, generated_code, instruction)
            elif app_type == "react_app":
                result = await self._build_react_app(app_dir, generated_code, instruction)
            elif app_type == "static_web":
                result = await self._build_static_website(app_dir, generated_code, instruction)
            elif app_type == "python_script":
                result = await self._build_python_script(app_dir, generated_code, instruction)
            else:
                result = await self._build_static_website(app_dir, generated_code, instruction)
            
            # Start server if it's a server-based app
            server_port = result.get("server_port")
            server_started = False
            if server_port and result.get("workflow"):
                server_started = await self.start_server(
                    app_name,
                    app_dir,  # Pass app directory
                    result.get("run_command", ""),
                    server_port
                )
            
            return {
                "success": True,
                "app_name": app_name,
                "app_dir": str(app_dir),
                "files_created": result.get("files", []),
                "packages_installed": result.get("packages", []),
                "workflow_created": result.get("workflow", False),
                "run_command": result.get("run_command", ""),
                "server_port": server_port,
                "server_started": server_started,
                "message": f"✅ Built complete working app: {app_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Build failed: {str(e)}"
            }
    
    def _detect_app_type(self, instruction: str, language: str) -> str:
        """Detect what type of app to build based on instruction and language"""
        instruction_lower = instruction.lower()
        
        # Force static web for HTML language
        if language == "html":
            return "static_web"
        
        # Detect React/frontend frameworks
        if any(word in instruction_lower for word in ["react", "vue", "next", "frontend", "vite"]):
            return "react_app"
        
        # Detect Node.js/Express
        if any(word in instruction_lower for word in ["express", "node", "api"]) and language != "python":
            return "node_express"
        
        # Detect Flask/FastAPI
        if "flask" in instruction_lower or ("api" in instruction_lower and language == "python"):
            return "flask_app"
        
        if "fastapi" in instruction_lower:
            return "fastapi_app"
        
        # Detect static websites - expanded keywords
        if any(word in instruction_lower for word in ["website", "landing", "portfolio", "blog", "page", "web", "site", "html"]):
            return "static_web"
        
        # Default based on language
        if language == "python":
            return "python_script"
        elif language == "javascript":
            return "static_web"
        
        # Default to static web for test/demo apps
        return "static_web"
    
    def _generate_app_name(self, instruction: str) -> str:
        """Generate clean app name from instruction"""
        # Extract key words and create clean name
        words = instruction.lower().split()
        name_words = [w for w in words[:3] if w.isalnum() and len(w) > 2]
        return "_".join(name_words[:2]) if name_words else "superagent_app"
    
    async def _build_static_website(self, app_dir: Path, code: str, instruction: str) -> Dict:
        """Build a static HTML website that can be previewed immediately"""
        files_created = []
        
        # Extract HTML from generated code or create complete HTML
        html_content = code
        if not html_content.strip().startswith('<!DOCTYPE') and not html_content.strip().startswith('<html'):
            # Wrap code in proper HTML structure
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SuperAgent App</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{ color: #667eea; margin-bottom: 20px; }}
        p {{ margin-bottom: 15px; }}
        .content {{ margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Generated by SuperAgent</h1>
        <div class="content">
            {html_content}
        </div>
    </div>
</body>
</html>"""
        
        # Create index.html
        index_file = app_dir / "index.html"
        index_file.write_text(html_content)
        files_created.append("index.html")
        
        return {
            "files": files_created,
            "packages": [],
            "workflow": False,
            "run_command": f"Open index.html in browser"
        }
    
    async def _build_flask_app(self, app_dir: Path, code: str, instruction: str) -> Dict:
        """Build a complete Flask web application with real package installation"""
        files_created = []
        packages_installed = []
        
        # Ensure code has proper Flask structure
        if "from flask import" not in code and "import flask" not in code:
            code = f"""from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '''
{code}
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
"""
        elif "if __name__ ==" not in code:
            code += "\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5001, debug=True)\n"
        
        # Create app.py
        app_file = app_dir / "app.py"
        app_file.write_text(code)
        files_created.append("app.py")
        
        # Create requirements.txt
        requirements = app_dir / "requirements.txt"
        requirements.write_text("flask>=3.0.0\n")
        files_created.append("requirements.txt")
        
        # Install Flask
        try:
            result = await asyncio.create_subprocess_exec(
                "pip", "install", "-q", "flask",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            packages_installed.append("flask")
        except Exception as e:
            print(f"Package install error: {e}")
        
        return {
            "files": files_created,
            "packages": packages_installed,
            "workflow": True,
            "run_command": "python app.py",  # Run from app dir
            "server_port": 5001
        }
    
    async def _build_fastapi_app(self, app_dir: Path, code: str, instruction: str) -> Dict:
        """Build FastAPI application"""
        files_created = []
        packages_installed = []
        
        # Ensure proper FastAPI structure
        if "from fastapi import" not in code:
            code = f"""from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {{"message": "SuperAgent FastAPI App"}}

{code}
"""
        
        # Create main.py
        main_file = app_dir / "main.py"
        main_file.write_text(code)
        files_created.append("main.py")
        
        # Create requirements.txt
        requirements = app_dir / "requirements.txt"
        requirements.write_text("fastapi>=0.104.0\nuvicorn>=0.24.0\n")
        files_created.append("requirements.txt")
        
        # Install packages
        try:
            result = await asyncio.create_subprocess_exec(
                "pip", "install", "-q", "fastapi", "uvicorn",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            packages_installed.extend(["fastapi", "uvicorn"])
        except Exception as e:
            print(f"Package install error: {e}")
        
        return {
            "files": files_created,
            "packages": packages_installed,
            "workflow": True,
            "run_command": "uvicorn main:app --host 0.0.0.0 --port 5002",  # Run from app dir
            "server_port": 5002
        }
    
    async def _build_node_express_app(self, app_dir: Path, code: str, instruction: str) -> Dict:
        """Build Node.js Express application"""
        files_created = []
        packages_installed = []
        
        # Ensure proper Express structure
        if "express" not in code:
            code = f"""const express = require('express');
const app = express();
const port = 5003;

app.get('/', (req, res) => {{
  res.send(`{code}`);
}});

app.listen(port, '0.0.0.0', () => {{
  console.log(`Server running on port ${{port}}`);
}});
"""
        
        # Create server.js
        server_file = app_dir / "server.js"
        server_file.write_text(code)
        files_created.append("server.js")
        
        # Create package.json
        package_json = {
            "name": app_dir.name,
            "version": "1.0.0",
            "main": "server.js",
            "dependencies": {
                "express": "^4.18.2"
            },
            "scripts": {
                "start": "node server.js"
            }
        }
        package_file = app_dir / "package.json"
        package_file.write_text(json.dumps(package_json, indent=2))
        files_created.append("package.json")
        
        # Install npm packages
        try:
            result = await asyncio.create_subprocess_exec(
                "npm", "install",
                cwd=str(app_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            packages_installed.append("express")
        except Exception as e:
            print(f"Package install error: {e}")
        
        return {
            "files": files_created,
            "packages": packages_installed,
            "workflow": True,
            "run_command": "node server.js",  # Run from app dir
            "server_port": 5003
        }
    
    async def _build_python_script(self, app_dir: Path, code: str, instruction: str) -> Dict:
        """Build a Python script application"""
        files_created = []
        
        # Create main.py
        main_file = app_dir / "main.py"
        main_file.write_text(code)
        files_created.append("main.py")
        
        # Create README.md
        readme = app_dir / "README.md"
        readme.write_text(f"""# {app_dir.name}

{instruction}

## Usage
```bash
python main.py
```
""")
        files_created.append("README.md")
        
        return {
            "files": files_created,
            "packages": [],
            "workflow": True,
            "run_command": f"cd {app_dir.name} && python main.py"
        }
    
    async def _build_react_app(self, app_dir: Path, code: str, instruction: str) -> Dict:
        """Build a React application"""
        files_created = []
        
        # Create index.html with React
        index_file = app_dir / "index.html"
        index_file.write_text(code)
        files_created.append("index.html")
        
        return {
            "files": files_created,
            "packages": [],
            "workflow": True,
            "run_command": f"Open {app_dir.name}/index.html in browser"
        }
    
    async def _build_generic_app(self, app_dir: Path, code: str, language: str, instruction: str) -> Dict:
        """Build a generic application"""
        files_created = []
        
        # Determine file extension
        ext_map = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "html": "html",
            "css": "css"
        }
        ext = ext_map.get(language, "txt")
        
        # Create main file
        main_file = app_dir / f"main.{ext}"
        main_file.write_text(code)
        files_created.append(f"main.{ext}")
        
        return {
            "files": files_created,
            "packages": [],
            "workflow": False,
            "run_command": f"Open {app_dir.name}/main.{ext}"
        }

# Global instance
app_builder = AppBuilder()
