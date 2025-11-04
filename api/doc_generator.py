"""
Documentation Generator - Auto-generate README and docstrings
"""
import re
from typing import Dict, List


class DocumentationGenerator:
    """Automatically generate documentation for code"""
    
    def generate_readme(self, code: str, language: str, project_name: str = "Project") -> str:
        """Generate README.md from code"""
        
        functions = self._extract_functions(code, language)
        classes = self._extract_classes(code, language)
        dependencies = self._extract_dependencies(code, language)
        
        readme = f"""# {project_name}

## Description
Auto-generated project created with SuperAgent AI.

## Features
"""
        
        if functions:
            readme += f"- {len(functions)} functions implemented\n"
        if classes:
            readme += f"- {len(classes)} classes defined\n"
        
        readme += "\n## Installation\n\n"
        
        if language == "python":
            readme += "```bash\npip install -r requirements.txt\n```\n"
        elif language == "javascript":
            readme += "```bash\nnpm install\n```\n"
        
        readme += "\n## Usage\n\n"
        
        if language == "python":
            readme += "```bash\npython main.py\n```\n"
        elif language == "javascript":
            readme += "```bash\nnode index.js\n```\n"
        
        if dependencies:
            readme += "\n## Dependencies\n\n"
            for dep in dependencies:
                readme += f"- {dep}\n"
        
        if functions:
            readme += "\n## Functions\n\n"
            for func in functions[:5]:
                readme += f"### `{func['name']}`\n"
                if func.get('params'):
                    readme += f"Parameters: `{func['params']}`\n"
                readme += "\n"
        
        if classes:
            readme += "\n## Classes\n\n"
            for cls in classes[:5]:
                readme += f"### `{cls['name']}`\n\n"
        
        readme += "\n## License\nMIT\n\n---\nGenerated with ❤️ by SuperAgent\n"
        
        return readme
    
    def add_docstrings(self, code: str, language: str) -> str:
        """Add docstrings/comments to undocumented functions"""
        
        if language == "python":
            return self._add_python_docstrings(code)
        elif language == "javascript":
            return self._add_js_docstrings(code)
        
        return code
    
    def _add_python_docstrings(self, code: str) -> str:
        """Add Python docstrings to functions"""
        lines = code.split('\n')
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            func_match = re.match(r'^(\s*)def\s+(\w+)\s*\((.*?)\):', line)
            if func_match:
                indent = func_match.group(1)
                func_name = func_match.group(2)
                params = func_match.group(3)
                
                result.append(line)
                
                if i + 1 < len(lines) and '"""' not in lines[i + 1]:
                    docstring = f'{indent}    """{func_name.replace("_", " ").title()}'
                    if params:
                        docstring += f'\n{indent}    \n{indent}    Args:\n'
                        for param in params.split(','):
                            param = param.strip().split('=')[0].strip()
                            if param and param != 'self':
                                docstring += f'{indent}        {param}: Description\n'
                    docstring += f'{indent}    """'
                    result.append(docstring)
            else:
                result.append(line)
            
            i += 1
        
        return '\n'.join(result)
    
    def _add_js_docstrings(self, code: str) -> str:
        """Add JSDoc comments to functions"""
        lines = code.split('\n')
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            func_match = re.match(r'^(\s*)(?:function|const|let|var)\s+(\w+)\s*[=\(]', line)
            if func_match and '//' not in lines[i - 1] if i > 0 else True:
                indent = func_match.group(1)
                func_name = func_match.group(2)
                
                jsdoc = f'{indent}/**\n{indent} * {func_name.replace("_", " ").title()}\n{indent} */'
                result.append(jsdoc)
            
            result.append(line)
            i += 1
        
        return '\n'.join(result)
    
    def _extract_functions(self, code: str, language: str) -> List[Dict]:
        """Extract function definitions"""
        functions = []
        
        if language == "python":
            pattern = r'def\s+(\w+)\s*\((.*?)\):'
        elif language == "javascript":
            pattern = r'(?:function|const|let|var)\s+(\w+)\s*[=\(]'
        else:
            return functions
        
        for match in re.finditer(pattern, code):
            if match:
                functions.append({
                    "name": match.group(1) if match.group(1) else "",
                    "params": match.group(2) if language == "python" and len(match.groups()) > 1 else ""
                })
        
        return functions
    
    def _extract_classes(self, code: str, language: str) -> List[Dict]:
        """Extract class definitions"""
        classes = []
        
        if language == "python":
            pattern = r'class\s+(\w+)'
        elif language == "javascript":
            pattern = r'class\s+(\w+)'
        else:
            return classes
        
        for match in re.finditer(pattern, code):
            classes.append({"name": match.group(1)})
        
        return classes
    
    def _extract_dependencies(self, code: str, language: str) -> List[str]:
        """Extract dependencies/imports"""
        deps = []
        
        if language == "python":
            imports = re.findall(r'(?:from|import)\s+([\w.]+)', code)
            deps = list(set(imports))
        elif language == "javascript":
            imports = re.findall(r'(?:import|require)\s*\(?[\'"]([^\'"]+)', code)
            deps = list(set(imports))
        
        return deps[:10]
