"""
Performance Profiler - Code performance analysis
"""
import re
from typing import Dict, List


class PerformanceProfiler:
    """Analyze code for performance issues"""
    
    def analyze(self, code: str, language: str) -> Dict:
        """
        Analyze code performance
        Returns: {score: int, issues: List, suggestions: List}
        """
        
        issues = []
        suggestions = []
        score = 100
        
        if language == "python":
            score, issues, suggestions = self._analyze_python(code)
        elif language == "javascript":
            score, issues, suggestions = self._analyze_javascript(code)
        
        return {
            "score": score,
            "issues": issues,
            "suggestions": suggestions,
            "grade": self._get_grade(score)
        }
    
    def _analyze_python(self, code: str) -> tuple:
        """Analyze Python code performance"""
        issues = []
        suggestions = []
        score = 100
        
        if re.search(r'for\s+\w+\s+in\s+range\(len\(', code):
            issues.append("Using range(len()) instead of enumerate()")
            suggestions.append("Use enumerate() for better performance")
            score -= 10
        
        nested_loops = len(re.findall(r'for\s+.*?:\s*\n\s+for\s+', code))
        if nested_loops > 0:
            issues.append(f"Found {nested_loops} nested loop(s) - O(n²) complexity")
            suggestions.append("Consider using list comprehensions or vectorization")
            score -= nested_loops * 15
        
        if '+=' in code and 'str' in code.lower():
            issues.append("String concatenation with += in loop (slow)")
            suggestions.append("Use ''.join() or f-strings for better performance")
            score -= 15
        
        if re.search(r'global\s+\w+', code):
            issues.append("Global variables used (slower access)")
            suggestions.append("Use function parameters instead of globals")
            score -= 5
        
        if 'import *' in code:
            issues.append("Wildcard imports slow down module loading")
            suggestions.append("Import only what you need")
            score -= 5
        
        return max(score, 0), issues, suggestions
    
    def _analyze_javascript(self, code: str) -> tuple:
        """Analyze JavaScript code performance"""
        issues = []
        suggestions = []
        score = 100
        
        if 'document.getElementById' in code and code.count('document.getElementById') > 3:
            issues.append("Multiple DOM queries (expensive)")
            suggestions.append("Cache DOM references in variables")
            score -= 10
        
        nested_loops = len(re.findall(r'for\s*\(.*?\)\s*{\s*for\s*\(', code))
        if nested_loops > 0:
            issues.append(f"Found {nested_loops} nested loop(s)")
            suggestions.append("Consider using map/filter/reduce")
            score -= nested_loops * 15
        
        if 'var ' in code:
            issues.append("Using 'var' instead of 'const'/'let'")
            suggestions.append("Use const/let for better scoping")
            score -= 5
        
        if '== ' in code or '!= ' in code:
            issues.append("Using loose equality (==)")
            suggestions.append("Use strict equality (===) for better performance")
            score -= 5
        
        return max(score, 0), issues, suggestions
    
    def _get_grade(self, score: int) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def get_complexity_estimate(self, code: str) -> Dict:
        """Estimate time complexity"""
        
        nested_loops = len(re.findall(r'for\s+.*?:\s*\n\s+for\s+', code))
        single_loops = len(re.findall(r'\bfor\s+', code)) - (nested_loops * 2)
        
        if nested_loops >= 3:
            complexity = "O(n³) or worse"
        elif nested_loops >= 2:
            complexity = "O(n²)"
        elif nested_loops == 1:
            complexity = "O(n²)"
        elif single_loops > 0:
            complexity = "O(n)"
        else:
            complexity = "O(1)"
        
        return {
            "estimated_complexity": complexity,
            "nested_loops": nested_loops,
            "single_loops": single_loops
        }
