"""AI-powered code refactoring engine."""

import ast
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()


class RefactoringEngine:
    """
    Intelligent code refactoring with AI assistance.
    
    Features:
    - Extract method/class refactoring
    - Rename with scope awareness
    - Dead code elimination
    - Design pattern application
    - Code modernization (e.g., Python 2→3, ES5→ES6)
    """
    
    def __init__(self, llm_provider):
        """Initialize refactoring engine.
        
        Args:
            llm_provider: LLM provider
        """
        self.llm = llm_provider
        
    async def suggest_refactorings(self, file_path: Path) -> List[Dict[str, Any]]:
        """Suggest refactorings for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of refactoring suggestions
        """
        code = file_path.read_text()
        
        suggestions = []
        
        # Analyze with AST
        try:
            tree = ast.parse(code)
            
            # Check for long methods
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if self._should_extract_method(node):
                        suggestions.append({
                            "type": "extract_method",
                            "location": node.lineno,
                            "function": node.name,
                            "description": f"Function '{node.name}' could be broken into smaller methods"
                        })
            
            # Check for duplicate code
            duplicates = self._find_duplicate_code(tree)
            for dup in duplicates:
                suggestions.append({
                    "type": "extract_common",
                    "description": "Duplicate code detected",
                    "locations": dup
                })
        
        except Exception as e:
            logger.error(f"AST analysis failed: {e}")
        
        # AI-powered suggestions
        ai_suggestions = await self._get_ai_refactorings(code)
        suggestions.extend(ai_suggestions)
        
        return suggestions
    
    async def apply_refactoring(self, file_path: Path, refactoring: Dict[str, Any]) -> str:
        """Apply a specific refactoring.
        
        Args:
            file_path: Path to file
            refactoring: Refactoring specification
            
        Returns:
            Refactored code
        """
        code = file_path.read_text()
        refactoring_type = refactoring.get("type")
        
        if refactoring_type == "extract_method":
            return await self._extract_method(code, refactoring)
        elif refactoring_type == "rename":
            return await self._rename_symbol(code, refactoring)
        elif refactoring_type == "modernize":
            return await self._modernize_code(code, refactoring)
        else:
            # Use AI for complex refactorings
            return await self._ai_refactor(code, refactoring)
    
    async def _extract_method(self, code: str, spec: Dict[str, Any]) -> str:
        """Extract method refactoring using AI.
        
        Args:
            code: Original code
            spec: Refactoring specification
            
        Returns:
            Refactored code
        """
        prompt = f"""Refactor this code by extracting a method:

{code}

Extract method from function: {spec.get('function')}
New method should handle: {spec.get('description')}

Provide the refactored code with:
1. New extracted method with descriptive name
2. Updated original function calling the new method
3. Proper parameters and return values"""
        
        return await self.llm.generate(prompt)
    
    async def _rename_symbol(self, code: str, spec: Dict[str, Any]) -> str:
        """Rename symbol with scope awareness.
        
        Args:
            code: Original code
            spec: Renaming specification
            
        Returns:
            Refactored code
        """
        old_name = spec.get("old_name")
        new_name = spec.get("new_name")
        
        # Use AST for intelligent renaming
        try:
            tree = ast.parse(code)
            # Implementation would use NodeTransformer
            # For now, use AI
        except:
            pass
        
        prompt = f"""Rename '{old_name}' to '{new_name}' in this code, ensuring:
1. All references are updated
2. Scope is respected (don't rename unrelated variables with same name)
3. Comments and docstrings are updated

{code}"""
        
        return await self.llm.generate(prompt)
    
    async def _modernize_code(self, code: str, spec: Dict[str, Any]) -> str:
        """Modernize code to use newer language features.
        
        Args:
            code: Original code
            spec: Modernization specification
            
        Returns:
            Modernized code
        """
        prompt = f"""Modernize this code using latest best practices:

{code}

Apply:
- Type hints (Python 3.10+)
- F-strings instead of .format()
- Dataclasses instead of __init__ boilerplate
- Async/await where beneficial
- List comprehensions instead of loops
- Context managers (with statements)

Provide modernized code:"""
        
        return await self.llm.generate(prompt)
    
    async def _ai_refactor(self, code: str, spec: Dict[str, Any]) -> str:
        """Generic AI-powered refactoring.
        
        Args:
            code: Original code
            spec: Refactoring specification
            
        Returns:
            Refactored code
        """
        prompt = f"""Refactor this code:

{code}

Refactoring: {spec.get('description')}
Type: {spec.get('type')}

Provide refactored code following best practices.
"""
        
        return await self.llm.generate(prompt)
    
    def _should_extract_method(self, node: ast.FunctionDef) -> bool:
        """Check if method should be extracted.
        
        Args:
            node: Function node
            
        Returns:
            True if should extract
        """
        # Check function length
        body_lines = len(ast.unparse(node).split('\n'))
        if body_lines > 50:
            return True
        
        # Check complexity (number of branches)
        branches = sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While)))
        if branches > 10:
            return True
        
        return False
    
    def _find_duplicate_code(self, tree: ast.AST) -> List[List[int]]:
        """Find duplicate code blocks.
        
        Args:
            tree: AST tree
            
        Returns:
            List of duplicate locations
        """
        # Simplified duplicate detection
        # Real implementation would use more sophisticated algorithms
        return []
    
    async def _get_ai_refactorings(self, code: str) -> List[Dict[str, Any]]:
        """Get AI-powered refactoring suggestions.
        
        Args:
            code: Source code
            
        Returns:
            Refactoring suggestions
        """
        prompt = f"""Analyze this code and suggest refactorings:

{code[:2000]}

Suggest improvements for:
1. Code structure and organization
2. Design patterns that could be applied
3. Performance optimizations
4. Readability improvements

Format as JSON: [{{"type": "...", "description": "...", "benefit": "..."}}]"""
        
        try:
            result = await self.llm.generate_structured(
                prompt,
                schema={"refactorings": [{"type": "string", "description": "string", "benefit": "string"}]}
            )
            return result.get("refactorings", [])
        except:
            return []





