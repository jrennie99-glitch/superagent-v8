"""
Docker Sandboxed Execution Module
Provides isolated code execution environments using Docker containers
"""

import os
import json
import subprocess
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

class DockerSandbox:
    """Docker-based code execution sandbox"""
    
    def __init__(self):
        self.containers = {}
        self.execution_history = []
        self.supported_languages = {
            "python": {
                "image": "python:3.11-slim",
                "file_ext": ".py",
                "compile": None,
                "execute": "python {file}"
            },
            "javascript": {
                "image": "node:20-slim",
                "file_ext": ".js",
                "compile": None,
                "execute": "node {file}"
            },
            "typescript": {
                "image": "node:20-slim",
                "file_ext": ".ts",
                "compile": None,
                "execute": "ts-node {file}"
            },
            "go": {
                "image": "golang:1.21-alpine",
                "file_ext": ".go",
                "compile": None,
                "execute": "go run {file}"
            },
            "rust": {
                "image": "rust:1.75-slim",
                "file_ext": ".rs",
                "compile": "rustc {file} -o /workspace/program",
                "execute": "/workspace/program"
            },
            "java": {
                "image": "openjdk:21-slim",
                "file_ext": ".java",
                "compile": "javac {file}",
                "execute": "java Main"
            },
            "c": {
                "image": "gcc:13-slim",
                "file_ext": ".c",
                "compile": "gcc {file} -o /workspace/program",
                "execute": "/workspace/program"
            },
            "cpp": {
                "image": "gcc:13-slim",
                "file_ext": ".cpp",
                "compile": "g++ {file} -o /workspace/program",
                "execute": "/workspace/program"
            }
        }
        
    def is_docker_available(self) -> bool:
        """Check if Docker is available on the system"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def create_sandbox(self, language: str, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Create isolated sandbox and execute code"""
        if not self.is_docker_available():
            return {
                "success": False,
                "error": "Docker not available. Running in simulated mode.",
                "simulated": True,
                "output": self._simulate_execution(language, code)
            }
        
        lang_config = self.supported_languages.get(language.lower())
        if not lang_config:
            return {
                "success": False,
                "error": f"Language {language} not supported in sandbox"
            }
        
        # Create temporary directory for code
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = self._write_code_file(tmpdir, language, code, lang_config)
            
            try:
                # Compile if needed
                if lang_config.get("compile"):
                    compile_cmd = lang_config["compile"].format(file=os.path.basename(code_file))
                    compile_result = subprocess.run(
                        [
                            "docker", "run",
                            "--rm",
                            "--network", "none",
                            "--memory", "512m",
                            "--cpus", "1",
                            "-v", f"{tmpdir}:/workspace",
                            "-w", "/workspace",
                            lang_config["image"],
                            "sh", "-c", compile_cmd
                        ],
                        capture_output=True,
                        timeout=timeout,
                        text=True
                    )
                    
                    if compile_result.returncode != 0:
                        return {
                            "success": False,
                            "error": "Compilation failed",
                            "output": compile_result.stdout,
                            "compile_error": compile_result.stderr,
                            "sandboxed": True
                        }
                
                # Execute the code
                execute_cmd = lang_config["execute"].format(file=os.path.basename(code_file))
                result = subprocess.run(
                    [
                        "docker", "run",
                        "--rm",
                        "--network", "none",  # No network access
                        "--memory", "512m",   # Memory limit
                        "--cpus", "1",        # CPU limit
                        "-v", f"{tmpdir}:/workspace",
                        "-w", "/workspace",
                        lang_config["image"],
                        "sh", "-c", execute_cmd
                    ],
                    capture_output=True,
                    timeout=timeout,
                    text=True
                )
                
                execution_result = {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "exit_code": result.returncode,
                    "sandboxed": True,
                    "language": language,
                    "timeout": timeout
                }
                
                self._log_execution(execution_result)
                return execution_result
                
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": f"Execution timeout ({timeout}s)",
                    "sandboxed": True
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Sandbox error: {str(e)}",
                    "sandboxed": True
                }
    
    def _write_code_file(self, directory: str, language: str, code: str, lang_config: Dict[str, Any]) -> str:
        """Write code to temporary file"""
        ext = lang_config["file_ext"]
        
        # Java requires specific class name
        if language.lower() == "java":
            filename = "Main.java"
        else:
            filename = f"code{ext}"
        
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'w') as f:
            f.write(code)
        
        return filepath
    
    def _simulate_execution(self, language: str, code: str) -> str:
        """Simulate execution when Docker is not available"""
        return f"""
[SIMULATED SANDBOX EXECUTION]
Language: {language}
Code Length: {len(code)} characters
Status: Would execute in isolated Docker container
Security: Network disabled, Resource limits applied
Note: Docker not available - this is a simulation
"""
    
    def _log_execution(self, result: Dict[str, Any]) -> None:
        """Log execution to history"""
        self.execution_history.append({
            **result,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_sandbox_stats(self) -> Dict[str, Any]:
        """Get sandbox execution statistics"""
        total_executions = len(self.execution_history)
        successful = sum(1 for e in self.execution_history if e.get("success"))
        failed = total_executions - successful
        
        languages_used = {}
        for execution in self.execution_history:
            lang = execution.get("language", "unknown")
            languages_used[lang] = languages_used.get(lang, 0) + 1
        
        return {
            "total_executions": total_executions,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_executions * 100) if total_executions > 0 else 0,
            "languages_used": languages_used,
            "docker_available": self.is_docker_available(),
            "supported_languages": list(self.supported_languages.keys())
        }
    
    def cleanup_containers(self) -> Dict[str, Any]:
        """Clean up any running containers"""
        if not self.is_docker_available():
            return {"success": False, "error": "Docker not available"}
        
        try:
            # Remove all stopped containers created by sandbox
            subprocess.run(
                ["docker", "container", "prune", "-f"],
                capture_output=True,
                timeout=10
            )
            return {"success": True, "cleaned": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_available_images(self) -> List[Dict[str, Any]]:
        """List available Docker images for sandboxing"""
        return [
            {
                "language": lang,
                "image": config["image"],
                "needs_compilation": config["compile"] is not None,
                "execute_command": config["execute"]
            }
            for lang, config in self.supported_languages.items()
        ]

# Global instance
docker_sandbox = DockerSandbox()
