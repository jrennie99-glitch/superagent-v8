"""
Codebase Intelligence Engine
Advanced code analysis and understanding
"""

import os
import ast
import json
from typing import List, Dict, Any, Set
from pathlib import Path
from collections import defaultdict
import re

class CodebaseAnalyzer:
    """Analyzes entire codebase structure and dependencies"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = root_path
        self.file_cache: Dict[str, Any] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
    
    def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive Python file analysis"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"error": f"Syntax error: {str(e)}"}
        
        analysis = {
            "file_path": file_path,
            "imports": self._extract_imports(tree),
            "functions": self._extract_functions(tree),
            "classes": self._extract_classes(tree),
            "global_variables": self._extract_globals(tree),
            "complexity": self._calculate_complexity(tree),
            "lines_of_code": len(code.split('\n')),
            "docstrings": self._extract_docstrings(tree)
        }
        
        return analysis
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict]:
        """Extract all imports"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "module": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append({
                        "type": "from_import",
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno
                    })
        
        return imports
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict]:
        """Extract function definitions"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip methods (functions inside classes)
                parent = getattr(node, 'parent', None)
                if parent and isinstance(parent, ast.ClassDef):
                    continue
                
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "defaults": len(node.args.defaults),
                    "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
                    "line_start": node.lineno,
                    "line_end": node.end_lineno,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "docstring": ast.get_docstring(node)
                })
        
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict]:
        """Extract class definitions"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            "name": item.name,
                            "args": [arg.arg for arg in item.args.args],
                            "is_async": isinstance(item, ast.AsyncFunctionDef),
                            "decorators": [self._get_decorator_name(d) for d in item.decorator_list]
                        })
                
                classes.append({
                    "name": node.name,
                    "bases": [self._get_base_name(b) for b in node.bases],
                    "methods": methods,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno,
                    "docstring": ast.get_docstring(node)
                })
        
        return classes
    
    def _extract_globals(self, tree: ast.AST) -> List[str]:
        """Extract global variables"""
        globals_vars = []
        
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        globals_vars.append(target.id)
        
        return globals_vars
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Decision points increase complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _extract_docstrings(self, tree: ast.AST) -> Dict[str, str]:
        """Extract all docstrings"""
        docstrings = {}
        
        # Module docstring
        module_doc = ast.get_docstring(tree)
        if module_doc:
            docstrings["module"] = module_doc
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                doc = ast.get_docstring(node)
                if doc:
                    docstrings[node.name] = doc
        
        return docstrings
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        return str(decorator)
    
    def _get_base_name(self, base: ast.AST) -> str:
        """Get base class name"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{base.value.id}.{base.attr}"
        return str(base)
    
    def scan_codebase(self, extensions: List[str] = ['.py']) -> Dict[str, Any]:
        """Scan entire codebase"""
        all_files = []
        total_lines = 0
        total_functions = 0
        total_classes = 0
        
        for ext in extensions:
            for file_path in Path(self.root_path).rglob(f'*{ext}'):
                if '.git' in str(file_path) or 'node_modules' in str(file_path):
                    continue
                
                if ext == '.py':
                    analysis = self.analyze_python_file(str(file_path))
                    all_files.append(analysis)
                    
                    total_lines += analysis.get('lines_of_code', 0)
                    total_functions += len(analysis.get('functions', []))
                    total_classes += len(analysis.get('classes', []))
        
        return {
            "total_files": len(all_files),
            "total_lines": total_lines,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "files": all_files
        }
    
    def find_unused_imports(self, file_path: str) -> List[str]:
        """Find unused imports in a file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        tree = ast.parse(code)
        
        # Get all imports
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name.split('.')[0]
                    imports.add(name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports.add(name)
        
        # Find which imports are actually used
        used_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id in imports:
                    used_imports.add(node.id)
        
        # Return unused
        return list(imports - used_imports)
    
    def suggest_refactoring(self, file_path: str) -> List[str]:
        """Suggest code refactoring opportunities"""
        analysis = self.analyze_python_file(file_path)
        suggestions = []
        
        # Check complexity
        if analysis.get('complexity', 0) > 10:
            suggestions.append("⚠️  High cyclomatic complexity. Consider breaking down complex functions.")
        
        # Check file length
        if analysis.get('lines_of_code', 0) > 500:
            suggestions.append("⚠️  Large file. Consider splitting into multiple modules.")
        
        # Check for missing docstrings
        functions = analysis.get('functions', [])
        functions_without_docs = [f for f in functions if not f.get('docstring')]
        if len(functions_without_docs) > len(functions) / 2:
            suggestions.append("📝 Many functions lack docstrings. Add documentation.")
        
        # Check unused imports
        unused = self.find_unused_imports(file_path)
        if unused:
            suggestions.append(f"🧹 Unused imports: {', '.join(unused)}")
        
        return suggestions if suggestions else ["✅ No refactoring suggestions. Code looks good!"]
