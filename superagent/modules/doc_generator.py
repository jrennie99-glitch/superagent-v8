"""Automatic documentation generator."""

import ast
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()


class DocumentationGenerator:
    """
    Automated documentation generation with AI.
    
    Features:
    - API documentation from code
    - README generation
    - Docstring generation
    - Architecture diagrams
    - Tutorial creation
    - OpenAPI/Swagger specs
    """
    
    def __init__(self, llm_provider):
        """Initialize documentation generator.
        
        Args:
            llm_provider: LLM provider
        """
        self.llm = llm_provider
    
    async def generate_readme(self, project_path: Path) -> str:
        """Generate comprehensive README for project.
        
        Args:
            project_path: Path to project
            
        Returns:
            README content
        """
        # Analyze project structure
        structure = self._analyze_project_structure(project_path)
        
        # Extract main functionality
        main_features = await self._extract_features(project_path)
        
        # Generate README with AI
        prompt = f"""Generate a comprehensive README.md for this project:

Project Structure:
{structure}

Main Features:
{main_features}

Include:
1. Project title and description
2. Installation instructions
3. Quick start guide
4. API documentation
5. Usage examples
6. Configuration
7. Contributing guidelines
8. License information

Make it professional and user-friendly."""
        
        readme = await self.llm.generate(prompt)
        
        return readme
    
    async def generate_api_docs(self, project_path: Path) -> Dict[str, Any]:
        """Generate API documentation.
        
        Args:
            project_path: Path to project
            
        Returns:
            API documentation structure
        """
        docs = {
            "endpoints": [],
            "classes": [],
            "functions": [],
            "modules": []
        }
        
        # Find all Python files
        py_files = list(project_path.rglob("*.py"))
        
        for file_path in py_files:
            try:
                code = file_path.read_text()
                tree = ast.parse(code)
                
                # Extract classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_doc = {
                            "name": node.name,
                            "docstring": ast.get_docstring(node) or "No description",
                            "methods": [],
                            "file": str(file_path.relative_to(project_path))
                        }
                        
                        # Extract methods
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                class_doc["methods"].append({
                                    "name": item.name,
                                    "docstring": ast.get_docstring(item) or "No description",
                                    "parameters": [arg.arg for arg in item.args.args]
                                })
                        
                        docs["classes"].append(class_doc)
                    
                    elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                        # Top-level function
                        docs["functions"].append({
                            "name": node.name,
                            "docstring": ast.get_docstring(node) or "No description",
                            "parameters": [arg.arg for arg in node.args.args],
                            "file": str(file_path.relative_to(project_path))
                        })
            
            except Exception as e:
                logger.error(f"Failed to parse {file_path}: {e}")
        
        return docs
    
    async def generate_docstrings(self, file_path: Path) -> str:
        """Generate missing docstrings for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Code with added docstrings
        """
        code = file_path.read_text()
        
        prompt = f"""Add comprehensive docstrings to this code:

{code}

For each function/class, add:
- Brief description
- Args with types
- Returns with type
- Raises (if applicable)
- Examples (for complex functions)

Use Google-style docstrings. Return the complete code with docstrings:"""
        
        documented_code = await self.llm.generate(prompt)
        
        return documented_code
    
    async def generate_tutorial(self, project_path: Path) -> str:
        """Generate tutorial for using the project.
        
        Args:
            project_path: Path to project
            
        Returns:
            Tutorial content
        """
        # Analyze project
        features = await self._extract_features(project_path)
        examples = self._find_example_files(project_path)
        
        prompt = f"""Create a beginner-friendly tutorial for this project:

Features:
{features}

Example files found:
{examples}

Structure the tutorial as:
1. Introduction - What the project does
2. Prerequisites - What users need
3. Installation - Step-by-step setup
4. Basic Usage - Simple examples
5. Advanced Usage - Complex scenarios
6. Best Practices - Tips and recommendations
7. Troubleshooting - Common issues
8. Next Steps - Further learning

Make it engaging and easy to follow:"""
        
        tutorial = await self.llm.generate(prompt)
        
        return tutorial
    
    async def generate_openapi_spec(self, project_path: Path) -> Dict[str, Any]:
        """Generate OpenAPI/Swagger specification.
        
        Args:
            project_path: Path to project
            
        Returns:
            OpenAPI spec
        """
        # Find API routes (Flask, FastAPI, etc.)
        routes = await self._extract_api_routes(project_path)
        
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": project_path.name,
                "version": "1.0.0",
                "description": "Auto-generated API documentation"
            },
            "paths": {}
        }
        
        for route in routes:
            spec["paths"][route["path"]] = {
                route["method"].lower(): {
                    "summary": route.get("description", ""),
                    "responses": {
                        "200": {"description": "Success"}
                    }
                }
            }
        
        return spec
    
    def _analyze_project_structure(self, project_path: Path) -> str:
        """Analyze project structure.
        
        Args:
            project_path: Path to project
            
        Returns:
            Structure description
        """
        structure_lines = []
        
        for item in sorted(project_path.rglob("*")):
            if item.is_file() and not any(p in str(item) for p in [".git", "__pycache__", ".pyc"]):
                rel_path = item.relative_to(project_path)
                indent = "  " * (len(rel_path.parts) - 1)
                structure_lines.append(f"{indent}- {item.name}")
                
                if len(structure_lines) > 50:  # Limit output
                    structure_lines.append("  ... (more files)")
                    break
        
        return "\n".join(structure_lines)
    
    async def _extract_features(self, project_path: Path) -> str:
        """Extract main features from code.
        
        Args:
            project_path: Path to project
            
        Returns:
            Features description
        """
        # Find main entry points
        main_files = []
        for pattern in ["main.py", "app.py", "__main__.py", "cli.py"]:
            found = list(project_path.rglob(pattern))
            main_files.extend(found)
        
        features = []
        for file_path in main_files[:3]:  # Analyze first 3
            try:
                code = file_path.read_text()
                tree = ast.parse(code)
                
                # Extract class and function names
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        doc = ast.get_docstring(node)
                        features.append(f"- {node.name}: {doc[:100] if doc else 'No description'}")
                    elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                        doc = ast.get_docstring(node)
                        if not node.name.startswith('_'):
                            features.append(f"- {node.name}(): {doc[:100] if doc else 'No description'}")
            except:
                pass
        
        return "\n".join(features[:10]) if features else "No features detected"
    
    def _find_example_files(self, project_path: Path) -> List[str]:
        """Find example files in project.
        
        Args:
            project_path: Path to project
            
        Returns:
            List of example file paths
        """
        examples = []
        for pattern in ["example*.py", "*_example.py", "demo*.py"]:
            examples.extend([str(f.relative_to(project_path)) for f in project_path.rglob(pattern)])
        
        return examples
    
    async def _extract_api_routes(self, project_path: Path) -> List[Dict[str, Any]]:
        """Extract API routes from code.
        
        Args:
            project_path: Path to project
            
        Returns:
            List of routes
        """
        routes = []
        
        # Search for Flask/FastAPI decorators
        py_files = list(project_path.rglob("*.py"))
        
        for file_path in py_files:
            try:
                code = file_path.read_text()
                
                # Simple pattern matching for Flask routes
                import re
                route_pattern = r'@app\.(get|post|put|delete|patch)\(["\'](.+?)["\']\)'
                matches = re.finditer(route_pattern, code)
                
                for match in matches:
                    routes.append({
                        "method": match.group(1).upper(),
                        "path": match.group(2),
                        "file": str(file_path.relative_to(project_path))
                    })
            except:
                pass
        
        return routes





