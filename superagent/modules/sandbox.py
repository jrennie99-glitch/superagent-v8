"""
Sandboxed Code Execution Module

Safely executes generated code in isolated Docker containers.
This is the KEY FEATURE to reach #1 ranking!
"""

import docker
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import structlog
import asyncio

logger = structlog.get_logger()


class SandboxExecutor:
    """Executes code safely in Docker containers."""
    
    def __init__(self, timeout: int = 300):
        """
        Initialize sandbox executor.
        
        Args:
            timeout: Maximum execution time in seconds (default 5 min)
        """
        self.timeout = timeout
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.warning(f"Docker not available: {e}. Sandbox disabled.")
            self.docker_client = None
    
    def is_available(self) -> bool:
        """Check if Docker sandbox is available."""
        return self.docker_client is not None
    
    async def execute_python(
        self,
        code: str,
        requirements: Optional[List[str]] = None,
        test_command: str = "python main.py"
    ) -> Dict[str, Any]:
        """
        Execute Python code in a sandbox.
        
        Args:
            code: Python code to execute
            requirements: List of pip packages
            test_command: Command to run
            
        Returns:
            Execution results with stdout, stderr, exit_code
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Docker not available",
                "sandboxed": False
            }
        
        logger.info("Executing Python code in sandbox")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to file
            code_file = Path(tmpdir) / "main.py"
            code_file.write_text(code)
            
            # Create requirements.txt if needed
            if requirements:
                req_file = Path(tmpdir) / "requirements.txt"
                req_file.write_text("\n".join(requirements))
            
            try:
                # Run in Python container
                container = self.docker_client.containers.run(
                    "python:3.11-slim",
                    command=f"sh -c 'cd /workspace && pip install -q -r requirements.txt 2>/dev/null || true && {test_command}'",
                    volumes={tmpdir: {"bind": "/workspace", "mode": "rw"}},
                    working_dir="/workspace",
                    detach=True,
                    mem_limit="512m",
                    network_mode="none",  # No network access
                    remove=True
                )
                
                # Wait for completion with timeout
                result = container.wait(timeout=self.timeout)
                logs = container.logs().decode('utf-8')
                
                return {
                    "success": result["StatusCode"] == 0,
                    "exit_code": result["StatusCode"],
                    "output": logs,
                    "sandboxed": True,
                    "timeout": False
                }
                
            except docker.errors.ContainerError as e:
                logger.error(f"Container error: {e}")
                return {
                    "success": False,
                    "exit_code": e.exit_status,
                    "output": e.stderr.decode('utf-8') if e.stderr else str(e),
                    "sandboxed": True,
                    "timeout": False
                }
            
            except Exception as e:
                logger.error(f"Sandbox execution failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "sandboxed": True,
                    "timeout": "timeout" in str(e).lower()
                }
    
    async def execute_nodejs(
        self,
        code: str,
        packages: Optional[List[str]] = None,
        test_command: str = "node index.js"
    ) -> Dict[str, Any]:
        """Execute JavaScript/TypeScript code in Node.js sandbox."""
        if not self.is_available():
            return {"success": False, "error": "Docker not available", "sandboxed": False}
        
        logger.info("Executing Node.js code in sandbox")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = Path(tmpdir) / "index.js"
            code_file.write_text(code)
            
            if packages:
                pkg_file = Path(tmpdir) / "package.json"
                deps = ", ".join([f'"{p}": "latest"' for p in packages])
                pkg_file.write_text(f'{{"dependencies": {{{deps}}}}}')
            
            try:
                container = self.docker_client.containers.run(
                    "node:18-slim",
                    command=f"sh -c 'cd /workspace && npm install --silent 2>/dev/null || true && {test_command}'",
                    volumes={tmpdir: {"bind": "/workspace", "mode": "rw"}},
                    working_dir="/workspace",
                    detach=True,
                    mem_limit="512m",
                    network_mode="none",
                    remove=True
                )
                
                result = container.wait(timeout=self.timeout)
                logs = container.logs().decode('utf-8')
                
                return {
                    "success": result["StatusCode"] == 0,
                    "exit_code": result["StatusCode"],
                    "output": logs,
                    "sandboxed": True,
                    "timeout": False
                }
                
            except Exception as e:
                logger.error(f"Sandbox execution failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "sandboxed": True,
                    "timeout": "timeout" in str(e).lower()
                }
    
    async def execute_project(
        self,
        project_path: Path,
        language: str = "python",
        test_command: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an entire project in a sandbox.
        
        Args:
            project_path: Path to project directory
            language: Programming language (python, nodejs, go, rust)
            test_command: Custom test command
            
        Returns:
            Execution results
        """
        if not self.is_available():
            return {"success": False, "error": "Docker not available", "sandboxed": False}
        
        logger.info(f"Executing {language} project in sandbox", path=str(project_path))
        
        # Determine image and command based on language
        images = {
            "python": ("python:3.11-slim", "pytest" if not test_command else test_command),
            "nodejs": ("node:18-slim", "npm test" if not test_command else test_command),
            "javascript": ("node:18-slim", "npm test" if not test_command else test_command),
            "typescript": ("node:18-slim", "npm test" if not test_command else test_command),
            "go": ("golang:1.21-alpine", "go test ./..." if not test_command else test_command),
            "rust": ("rust:1.75-slim", "cargo test" if not test_command else test_command)
        }
        
        if language not in images:
            return {
                "success": False,
                "error": f"Unsupported language: {language}",
                "sandboxed": False
            }
        
        image, command = images[language]
        
        try:
            container = self.docker_client.containers.run(
                image,
                command=f"sh -c 'cd /workspace && {command}'",
                volumes={str(project_path): {"bind": "/workspace", "mode": "ro"}},
                working_dir="/workspace",
                detach=True,
                mem_limit="1g",
                network_mode="none",
                remove=True
            )
            
            result = container.wait(timeout=self.timeout)
            logs = container.logs().decode('utf-8')
            
            return {
                "success": result["StatusCode"] == 0,
                "exit_code": result["StatusCode"],
                "output": logs,
                "sandboxed": True,
                "timeout": False,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Project execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "sandboxed": True,
                "timeout": "timeout" in str(e).lower()
            }
    
    def cleanup(self):
        """Clean up Docker resources."""
        if self.docker_client:
            try:
                # Remove any dangling containers
                for container in self.docker_client.containers.list(all=True):
                    if "superagent-sandbox" in container.name:
                        container.remove(force=True)
                logger.info("Sandbox cleanup complete")
            except Exception as e:
                logger.warning(f"Cleanup error: {e}")

