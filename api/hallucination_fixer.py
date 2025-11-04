"""
Hallucination Fixer - 4-layer verification system
Detects and fixes AI-generated code errors
"""
import re
from typing import Dict, List, Tuple
import ast


class HallucinationFixer:
    """4-layer verification system for AI-generated code"""
    
    def __init__(self):
        self.verification_layers = [
            self._syntax_check,
            self._logic_check,
            self._consistency_check,
            self._grounding_check
        ]
    
    def verify_code(self, code: str, language: str, context: str = "") -> Dict:
        """
        Run 4-layer verification on generated code
        Returns: {verified: bool, issues: List[str], score: int}
        """
        issues = []
        layer_scores = []
        
        for layer_func in self.verification_layers:
            passed, layer_issues, score = layer_func(code, language, context)
            layer_scores.append(score)
            if not passed:
                issues.extend(layer_issues)
        
        avg_score = sum(layer_scores) // len(layer_scores)
        
        return {
            "verified": len(issues) == 0,
            "issues": issues,
            "score": avg_score,
            "layer_scores": {
                "syntax": layer_scores[0],
                "logic": layer_scores[1],
                "consistency": layer_scores[2],
                "grounding": layer_scores[3]
            }
        }
    
    def _syntax_check(self, code: str, language: str, context: str) -> Tuple[bool, List[str], int]:
        """Layer 1: Syntax validation"""
        issues = []
        
        if language == "python":
            try:
                ast.parse(code)
                return True, [], 100
            except SyntaxError as e:
                issues.append(f"Syntax error: {str(e)}")
                return False, issues, 0
        
        elif language == "javascript":
            if "var " in code and "const " in code:
                issues.append("Mixed var/const - inconsistent variable declarations")
            if code.count("{") != code.count("}"):
                issues.append("Mismatched braces")
                return False, issues, 30
        
        return True, issues, 90 if issues else 100
    
    def _logic_check(self, code: str, language: str, context: str) -> Tuple[bool, List[str], int]:
        """Layer 2: Logic validation"""
        issues = []
        score = 100
        
        if "function" in code or "def " in code:
            if code.count("return") == 0 and "void" not in code:
                issues.append("Function may be missing return statement")
                score = 70
        
        if re.search(r'\b(undefined|None|null)\s*==\s*', code):
            issues.append("Loose equality check on null/undefined")
            score = min(score, 80)
        
        if re.search(r'while\s*\(\s*true\s*\)|while\s+True\s*:', code, re.IGNORECASE):
            if "break" not in code:
                issues.append("Infinite loop detected without break")
                score = 50
        
        return len(issues) == 0, issues, score
    
    def _consistency_check(self, code: str, language: str, context: str) -> Tuple[bool, List[str], int]:
        """Layer 3: Self-consistency validation"""
        issues = []
        score = 100
        
        functions = re.findall(r'(?:function|def)\s+(\w+)', code)
        if len(functions) != len(set(functions)):
            issues.append("Duplicate function names detected")
            score = 60
        
        variables = re.findall(r'(?:let|const|var)\s+(\w+)', code)
        if len(variables) != len(set(variables)):
            issues.append("Variable redeclaration detected")
            score = min(score, 80)
        
        return len(issues) == 0, issues, score
    
    def _grounding_check(self, code: str, language: str, context: str) -> Tuple[bool, List[str], int]:
        """Layer 4: Context-based grounding validation"""
        issues = []
        score = 100
        
        if context:
            context_lower = context.lower()
            code_lower = code.lower()
            
            if "database" in context_lower and "sql" not in code_lower and "db" not in code_lower:
                issues.append("Database mentioned in context but not implemented")
                score = 70
            
            if "api" in context_lower and "fetch" not in code_lower and "request" not in code_lower:
                issues.append("API mentioned in context but no HTTP calls found")
                score = 70
        
        placeholder_patterns = [
            r'# TODO', r'// TODO', r'placeholder', r'FIXME',
            r'YOUR_.*_HERE', r'REPLACE_THIS'
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(f"Placeholder code detected: {pattern}")
                score = min(score, 60)
        
        return len(issues) == 0, issues, score
    
    def fix_common_issues(self, code: str, language: str) -> str:
        """Auto-fix common hallucination issues"""
        fixed_code = code
        
        if language == "python":
            fixed_code = re.sub(r'from\s+\.\s+import', 'from . import', fixed_code)
            fixed_code = re.sub(r'\t', '    ', fixed_code)
        
        elif language == "javascript":
            fixed_code = re.sub(r'var\s+', 'const ', fixed_code)
        
        return fixed_code
