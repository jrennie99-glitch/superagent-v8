"""
Real-Time Code Execution Module
Executes code in sandboxed environment and provides live preview
"""

import os
import asyncio
import json
import subprocess
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path
import docker
from docker.types import Mount


class RealtimeCodeExecutor:
    """Executes code in real-time with sandboxing"""
    
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
            self.docker_available = True
        except Exception:
            self.docker_available = False
            print("⚠️ Docker not available - using subprocess execution")
    
    async def execute_code(
        self,
        code: str,
        language: str = "python",
        timeout: int = 30,
        environment: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute code in sandboxed environment
        
        Args:
            code: Code to execute
            language: Programming language (python, javascript, etc.)
            timeout: Execution timeout in seconds
            environment: Environment variables
        
        Returns:
            Execution result with output, errors, and metrics
        """
        
        try:
            print(f"🚀 Executing {language} code...")
            
            if self.docker_available:
                result = await self._execute_in_docker(code, language, timeout, environment)
            else:
                result = await self._execute_locally(code, language, timeout, environment)
            
            print(f"✅ Execution complete: {result.get('status')}")
            return result
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "output": "",
                "stderr": "",
                "execution_time": 0,
            }
    
    async def _execute_in_docker(
        self,
        code: str,
        language: str,
        timeout: int,
        environment: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Execute code in Docker container"""
        
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(language), delete=False) as f:
            f.write(code)
            code_file = f.name
        
        try:
            # Select appropriate Docker image
            image = self._get_docker_image(language)
            
            # Prepare environment
            env_vars = environment or {}
            env_vars["TIMEOUT"] = str(timeout)
            
            # Run container
            container = self.docker_client.containers.run(
                image,
                f"timeout {timeout} {self._get_run_command(language, code_file)}",
                volumes={code_file: {"bind": "/code", "mode": "ro"}},
                mem_limit="512m",
                memswap_limit="512m",
                cpus="1",
                environment=env_vars,
                detach=True,
                remove=False,
            )
            
            # Wait for completion
            exit_code = container.wait(timeout=timeout + 5)
            
            # Get output
            output = container.logs(stdout=True, stderr=False).decode('utf-8')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8')
            
            # Clean up
            container.remove()
            
            return {
                "status": "success" if exit_code == 0 else "error",
                "output": output,
                "stderr": stderr,
                "exit_code": exit_code,
                "execution_time": timeout,
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(code_file):
                os.remove(code_file)
    
    async def _execute_locally(
        self,
        code: str,
        language: str,
        timeout: int,
        environment: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Execute code locally (fallback)"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(language), delete=False) as f:
            f.write(code)
            code_file = f.name
        
        try:
            # Prepare command
            command = self._get_run_command(language, code_file)
            
            # Prepare environment
            env = os.environ.copy()
            if environment:
                env.update(environment)
            
            # Execute
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "status": "timeout",
                    "output": "",
                    "stderr": f"Execution timeout after {timeout} seconds",
                    "execution_time": timeout,
                }
            
            return {
                "status": "success" if process.returncode == 0 else "error",
                "output": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8'),
                "exit_code": process.returncode,
                "execution_time": timeout,
            }
        
        finally:
            if os.path.exists(code_file):
                os.remove(code_file)
    
    async def execute_and_preview(
        self,
        frontend_code: str,
        backend_code: Optional[str] = None,
        database_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute frontend and backend code, return preview URL
        
        Args:
            frontend_code: React/Vue/Svelte code
            backend_code: FastAPI/Express code
            database_config: Database configuration
        
        Returns:
            Preview URL and execution details
        """
        
        try:
            print("🌐 Starting live preview...")
            
            # Create temporary directory for project
            project_dir = tempfile.mkdtemp()
            
            # Write frontend code
            frontend_path = Path(project_dir) / "frontend"
            frontend_path.mkdir()
            (frontend_path / "App.tsx").write_text(frontend_code)
            
            # Write backend code if provided
            if backend_code:
                backend_path = Path(project_dir) / "backend"
                backend_path.mkdir()
                (backend_path / "main.py").write_text(backend_code)
            
            # Create Docker Compose file
            compose_content = self._generate_docker_compose(project_dir, backend_code is not None)
            (Path(project_dir) / "docker-compose.yml").write_text(compose_content)
            
            # Start services
            result = await self._start_preview_services(project_dir)
            
            return {
                "status": "success",
                "preview_url": "http://localhost:3000",
                "api_url": "http://localhost:8001" if backend_code else None,
                "project_dir": project_dir,
                "services": result.get("services", []),
                "logs": result.get("logs", ""),
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def stop_preview(self, project_dir: str) -> Dict[str, Any]:
        """Stop preview services"""
        
        try:
            # Stop Docker Compose services
            result = subprocess.run(
                ["docker-compose", "down"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "status": "success",
                "message": "Preview stopped",
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def _get_docker_image(self, language: str) -> str:
        """Get appropriate Docker image for language"""
        
        images = {
            "python": "python:3.11-slim",
            "javascript": "node:18-alpine",
            "typescript": "node:18-alpine",
            "go": "golang:1.21-alpine",
            "rust": "rust:latest",
        }
        
        return images.get(language, "python:3.11-slim")
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "go": ".go",
            "rust": ".rs",
        }
        
        return extensions.get(language, ".txt")
    
    def _get_run_command(self, language: str, file_path: str) -> str:
        """Get command to run code"""
        
        commands = {
            "python": f"python {file_path}",
            "javascript": f"node {file_path}",
            "typescript": f"npx ts-node {file_path}",
            "go": f"go run {file_path}",
            "rust": f"rustc {file_path} && ./{Path(file_path).stem}",
        }
        
        return commands.get(language, f"python {file_path}")
    
    def _generate_docker_compose(self, project_dir: str, with_backend: bool = False) -> str:
        """Generate Docker Compose configuration"""
        
        if with_backend:
            return """version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8001
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/app
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
"""
        else:
            return """version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
"""
    
    async def _start_preview_services(self, project_dir: str) -> Dict[str, Any]:
        """Start preview services with Docker Compose"""
        
        try:
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "status": "success",
                "services": ["frontend", "backend", "database"],
                "logs": result.stdout,
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }


# Global instance
realtime_executor = RealtimeCodeExecutor()
