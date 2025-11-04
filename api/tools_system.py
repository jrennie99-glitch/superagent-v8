"""
SuperAgent Tool-Calling System
Enables AI to execute actions through function calling
"""

import os
import json
import subprocess
import asyncio
from typing import Any, Dict, List, Callable, Optional
from functools import wraps
import inspect
from pathlib import Path
import ast
import re

class ToolRegistry:
    """Registry for AI-callable tools"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict] = []
    
    def register(self, name: str, description: str, parameters: Dict, dangerous: bool = False):
        """Decorator to register a tool"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Log execution
                execution = {
                    "tool": name,
                    "args": args,
                    "kwargs": kwargs,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                try:
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    execution["status"] = "success"
                    execution["result"] = str(result)[:500]  # Truncate long results
                    self.execution_history.append(execution)
                    
                    return result
                except Exception as e:
                    execution["status"] = "error"
                    execution["error"] = str(e)
                    self.execution_history.append(execution)
                    raise
            
            # Register tool metadata
            self.tools[name] = {
                "function": wrapper,
                "description": description,
                "parameters": parameters,
                "dangerous": dangerous,
                "signature": inspect.signature(func)
            }
            
            return wrapper
        return decorator
    
    def get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions in OpenAI/Gemini function calling format"""
        definitions = []
        
        for name, tool in self.tools.items():
            definitions.append({
                "name": name,
                "description": tool["description"],
                "parameters": tool["parameters"]
            })
        
        return definitions
    
    async def execute_tool(self, name: str, arguments: Dict) -> Any:
        """Execute a tool by name with arguments"""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        
        tool = self.tools[name]
        
        # Safety check for dangerous operations
        if tool["dangerous"]:
            # In production, add user confirmation here
            print(f"⚠️  Executing dangerous operation: {name}")
        
        return await tool["function"](**arguments)
    
    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent tool execution history"""
        return self.execution_history[-limit:]


# Global registry instance
registry = ToolRegistry()


# ==================== FILE SYSTEM TOOLS ====================

@registry.register(
    name="read_file",
    description="Read the contents of a file from the filesystem",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read"
            }
        },
        "required": ["file_path"]
    }
)
async def read_file(file_path: str) -> str:
    """Read file contents"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@registry.register(
    name="write_file",
    description="Write content to a file (creates or overwrites)",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to write"
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file"
            }
        },
        "required": ["file_path", "content"]
    },
    dangerous=True
)
async def write_file(file_path: str, content: str) -> str:
    """Write content to file"""
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✅ Successfully wrote {len(content)} characters to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@registry.register(
    name="list_directory",
    description="List files and directories in a given path",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path to list (default: current directory)"
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to list recursively"
            }
        },
        "required": ["path"]
    }
)
async def list_directory(path: str = ".", recursive: bool = False) -> str:
    """List directory contents"""
    try:
        if recursive:
            result = []
            for root, dirs, files in os.walk(path):
                level = root.replace(path, '').count(os.sep)
                indent = ' ' * 2 * level
                result.append(f"{indent}{os.path.basename(root)}/")
                sub_indent = ' ' * 2 * (level + 1)
                for file in files:
                    result.append(f"{sub_indent}{file}")
            return '\n'.join(result)
        else:
            items = os.listdir(path)
            return '\n'.join(sorted(items))
    except Exception as e:
        return f"Error listing directory: {str(e)}"


# ==================== CODE ANALYSIS TOOLS ====================

@registry.register(
    name="analyze_code",
    description="Analyze Python code structure, imports, functions, and classes",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to Python file to analyze"
            }
        },
        "required": ["file_path"]
    }
)
async def analyze_code(file_path: str) -> str:
    """Analyze Python code structure"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        tree = ast.parse(code)
        
        analysis = {
            "imports": [],
            "functions": [],
            "classes": [],
            "global_variables": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    analysis["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    analysis["imports"].append(f"{module}.{alias.name}")
            elif isinstance(node, ast.FunctionDef):
                analysis["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "line": node.lineno
                })
            elif isinstance(node, ast.ClassDef):
                analysis["classes"].append({
                    "name": node.name,
                    "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    "line": node.lineno
                })
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        analysis["global_variables"].append(target.id)
        
        return json.dumps(analysis, indent=2)
    except Exception as e:
        return f"Error analyzing code: {str(e)}"


# ==================== SHELL EXECUTION TOOLS ====================

@registry.register(
    name="execute_command",
    description="Execute a shell command (use with caution)",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Shell command to execute"
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 30)"
            }
        },
        "required": ["command"]
    },
    dangerous=True
)
async def execute_command(command: str, timeout: int = 30) -> str:
    """Execute shell command safely"""
    try:
        # Blacklist dangerous commands
        dangerous_patterns = ['rm -rf /', 'mkfs', 'dd if=', ':(){:|:&};:']
        if any(pattern in command for pattern in dangerous_patterns):
            return "❌ Command blocked for safety reasons"
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = f"Exit code: {result.returncode}\n"
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}"
        
        return output
    except subprocess.TimeoutExpired:
        return f"❌ Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


# ==================== SEARCH TOOLS ====================

@registry.register(
    name="search_files",
    description="Search for files by name or content using grep",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Search pattern (regex supported)"
            },
            "path": {
                "type": "string",
                "description": "Directory to search in"
            },
            "search_content": {
                "type": "boolean",
                "description": "Search file contents (true) or just filenames (false)"
            }
        },
        "required": ["pattern"]
    }
)
async def search_files(pattern: str, path: str = ".", search_content: bool = False) -> str:
    """Search for files"""
    try:
        if search_content:
            # Search file contents
            result = subprocess.run(
                ['grep', '-r', '-n', '-H', pattern, path],
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            # Search filenames
            result = subprocess.run(
                ['find', path, '-name', f'*{pattern}*'],
                capture_output=True,
                text=True,
                timeout=10
            )
        
        return result.stdout if result.stdout else "No matches found"
    except Exception as e:
        return f"Error searching: {str(e)}"


# ==================== UTILITY TOOLS ====================

@registry.register(
    name="get_file_info",
    description="Get detailed information about a file (size, type, modified date)",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file"
            }
        },
        "required": ["file_path"]
    }
)
async def get_file_info(file_path: str) -> str:
    """Get file information"""
    try:
        from datetime import datetime
        
        path = Path(file_path)
        if not path.exists():
            return "File does not exist"
        
        stat = path.stat()
        
        info = {
            "path": str(path.absolute()),
            "size_bytes": stat.st_size,
            "size_human": f"{stat.st_size / 1024:.2f} KB" if stat.st_size > 1024 else f"{stat.st_size} bytes",
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "is_file": path.is_file(),
            "is_directory": path.is_dir(),
            "extension": path.suffix
        }
        
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"Error getting file info: {str(e)}"
