"""
Refactoring Engine - Code improvement suggestions
"""
import re
from typing import List, Dict, Tuple
from enum import Enum


class RefactoringPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RefactoringEngine:
    """Analyze code and suggest improvements"""
    
    def __init__(self):
        self.refactorings: List[Dict] = []
    
    def analyze(self, code: str, language: str) -> Dict:
        """Analyze code and generate refactoring suggestions"""
        
        self.refactorings = []
        
        if language == "python":
            self._analyze_python(code)
        elif language == "javascript":
            self._analyze_javascript(code)
        
        return {
            "total_suggestions": len(self.refactorings),
            "critical": len([r for r in self.refactorings if r["priority"] == RefactoringPriority.CRITICAL.value]),
            "high": len([r for r in self.refactorings if r["priority"] == RefactoringPriority.HIGH.value]),
            "suggestions": self.refactorings
        }
    
    def _analyze_python(self, code: str):
        """Python-specific refactoring analysis"""
        
        # Check for long functions
        functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):(.*?)(?=\ndef\s|\nclass\s|\Z)', code, re.DOTALL)
        for func_name, func_body in functions:
            lines = func_body.strip().split('\n')
            if len(lines) > 50:
                self.refactorings.append({
                    "type": "function_length",
                    "priority": RefactoringPriority.HIGH.value,
                    "location": f"Function '{func_name}'",
                    "issue": f"Function has {len(lines)} lines (recommended: <50)",
                    "suggestion": "Break into smaller, focused functions",
                    "example": f"Split {func_name}() into helper functions"
                })
        
        # Check for duplicate code
        if code.count('import') > 10:
            self.refactorings.append({
                "type": "imports",
                "priority": RefactoringPriority.LOW.value,
                "location": "Top of file",
                "issue": "Too many imports",
                "suggestion": "Group imports and remove unused ones",
                "example": "Use isort to organize imports"
            })
        
        # Check for magic numbers
        magic_numbers = re.findall(r'\b\d{2,}\b', code)
        if len(magic_numbers) > 5:
            self.refactorings.append({
                "type": "magic_numbers",
                "priority": RefactoringPriority.MEDIUM.value,
                "location": "Throughout code",
                "issue": f"Found {len(magic_numbers)} potential magic numbers",
                "suggestion": "Extract to named constants",
                "example": "MAX_RETRIES = 3 instead of hardcoded 3"
            })
        
        # Check for missing type hints
        if 'def ' in code and '->' not in code:
            self.refactorings.append({
                "type": "type_hints",
                "priority": RefactoringPriority.MEDIUM.value,
                "location": "Function definitions",
                "issue": "Missing type hints",
                "suggestion": "Add type hints for better code clarity",
                "example": "def process(data: List[str]) -> Dict:"
            })
        
        # Check for class design
        classes = re.findall(r'class\s+(\w+)', code)
        if len(classes) > 1:
            methods_per_class = []
            for class_name in classes:
                class_match = re.search(rf'class\s+{class_name}.*?:(.*?)(?=\nclass\s|\Z)', code, re.DOTALL)
                if class_match:
                    methods = len(re.findall(r'def\s+\w+', class_match.group(1)))
                    if methods > 15:
                        self.refactorings.append({
                            "type": "class_complexity",
                            "priority": RefactoringPriority.HIGH.value,
                            "location": f"Class '{class_name}'",
                            "issue": f"Class has {methods} methods (recommended: <15)",
                            "suggestion": "Split into smaller, focused classes",
                            "example": f"Extract responsibilities from {class_name}"
                        })
        
        # Check for nested loops
        nested_loops = len(re.findall(r'for\s+.*?:\s*\n\s+for\s+', code))
        if nested_loops > 2:
            self.refactorings.append({
                "type": "nested_loops",
                "priority": RefactoringPriority.CRITICAL.value,
                "location": "Throughout code",
                "issue": f"{nested_loops} nested loops detected",
                "suggestion": "Consider using list comprehensions or vectorization",
                "example": "Use itertools or numpy for better performance"
            })
    
    def _analyze_javascript(self, code: str):
        """JavaScript-specific refactoring analysis"""
        
        # Check for var usage
        if 'var ' in code:
            var_count = code.count('var ')
            self.refactorings.append({
                "type": "var_usage",
                "priority": RefactoringPriority.HIGH.value,
                "location": "Throughout code",
                "issue": f"Found {var_count} 'var' declarations",
                "suggestion": "Replace 'var' with 'const' or 'let'",
                "example": "const data = [] instead of var data = []"
            })
        
        # Check for callback hell
        callback_depth = code.count('function(') + code.count('=>')
        if callback_depth > 5:
            self.refactorings.append({
                "type": "callback_hell",
                "priority": RefactoringPriority.CRITICAL.value,
                "location": "Nested callbacks",
                "issue": "Deep callback nesting detected",
                "suggestion": "Refactor to use async/await",
                "example": "async function process() { await fetch(...) }"
            })
        
        # Check for long functions
        functions = re.findall(r'(?:function|const)\s+(\w+)\s*[=\(].*?{(.*?)}', code, re.DOTALL)
        for func_name, func_body in functions:
            lines = func_body.strip().split('\n')
            if len(lines) > 40:
                self.refactorings.append({
                    "type": "function_length",
                    "priority": RefactoringPriority.HIGH.value,
                    "location": f"Function '{func_name}'",
                    "issue": f"Function has {len(lines)} lines",
                    "suggestion": "Break into smaller functions",
                    "example": f"Extract logic from {func_name}()"
                })
        
        # Check for console.log
        if 'console.log' in code:
            log_count = code.count('console.log')
            self.refactorings.append({
                "type": "console_log",
                "priority": RefactoringPriority.LOW.value,
                "location": "Throughout code",
                "issue": f"Found {log_count} console.log statements",
                "suggestion": "Remove debug logs or use proper logging",
                "example": "Use a logging library like winston"
            })
    
    def apply_refactoring(self, code: str, refactoring_type: str) -> str:
        """Apply a specific refactoring to code"""
        
        if refactoring_type == "var_usage":
            code = re.sub(r'\bvar\s+', 'const ', code)
        
        elif refactoring_type == "console_log":
            code = re.sub(r'console\.log\([^)]+\);?\n?', '', code)
        
        return code
    
    def get_modernization_score(self, code: str, language: str) -> int:
        """Calculate how modern the code is (0-100)"""
        score = 100
        
        if language == "python":
            if 'def ' in code and '->' not in code:
                score -= 20  # No type hints
            if 'class ' in code and '@dataclass' not in code:
                score -= 10  # Not using modern class features
        
        elif language == "javascript":
            if 'var ' in code:
                score -= 30  # Still using var
            if 'function(' in code and '=>' not in code:
                score -= 15  # Not using arrow functions
            if 'Promise' not in code and 'async' not in code:
                score -= 15  # Not using modern async
        
        return max(score, 0)
