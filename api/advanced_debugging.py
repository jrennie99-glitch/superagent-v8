"""
Advanced Debugging - Error tracing with AI-driven fix suggestions
"""
import re
import traceback
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DebugIssue:
    """Represents a detected issue"""
    severity: str  # error, warning, info
    line_number: Optional[int]
    code_snippet: str
    issue_type: str
    description: str
    fix_suggestion: str
    example_fix: Optional[str] = None


class AdvancedDebugger:
    """Advanced code debugging with AI-driven suggestions"""
    
    def __init__(self):
        self.issues: List[DebugIssue] = []
    
    def analyze_code(self, code: str, language: str) -> Dict:
        """Perform comprehensive debugging analysis"""
        
        self.issues = []
        
        # Static analysis
        if language == "python":
            self._debug_python(code)
        elif language == "javascript":
            self._debug_javascript(code)
        
        # Common issues across languages
        self._check_common_issues(code, language)
        
        return {
            "total_issues": len(self.issues),
            "errors": len([i for i in self.issues if i.severity == "error"]),
            "warnings": len([i for i in self.issues if i.severity == "warning"]),
            "issues": [
                {
                    "severity": i.severity,
                    "line": i.line_number,
                    "type": i.issue_type,
                    "description": i.description,
                    "fix": i.fix_suggestion,
                    "example": i.example_fix
                }
                for i in self.issues
            ]
        }
    
    def _debug_python(self, code: str):
        """Python-specific debugging"""
        
        lines = code.split('\n')
        
        # Check for common Python errors
        for i, line in enumerate(lines, 1):
            # Indentation issues
            if line.startswith(' ') and not line.startswith('    ') and line.strip():
                if len(line) - len(line.lstrip()) not in [0, 4, 8, 12, 16]:
                    self.issues.append(DebugIssue(
                        severity="error",
                        line_number=i,
                        code_snippet=line.strip(),
                        issue_type="indentation_error",
                        description="Inconsistent indentation (Python requires 4 spaces)",
                        fix_suggestion="Use 4 spaces for indentation",
                        example_fix="    " + line.strip()
                    ))
            
            # Missing colons
            if re.match(r'^\s*(?:if|for|while|def|class|try|except|with)\s+.*[^:]$', line):
                self.issues.append(DebugIssue(
                    severity="error",
                    line_number=i,
                    code_snippet=line.strip(),
                    issue_type="syntax_error",
                    description="Missing colon at end of statement",
                    fix_suggestion="Add ':' at end of line",
                    example_fix=line.strip() + ':'
                ))
            
            # Undefined variables (simple check)
            if '=' not in line and re.search(r'\b([a-z_]\w*)\s*\(', line):
                func_name = re.search(r'\b([a-z_]\w*)\s*\(', line).group(1)
                if func_name not in code[:code.index(line)] and func_name not in ['print', 'len', 'str', 'int', 'list', 'dict']:
                    self.issues.append(DebugIssue(
                        severity="warning",
                        line_number=i,
                        code_snippet=line.strip(),
                        issue_type="undefined_name",
                        description=f"Function '{func_name}' may not be defined",
                        fix_suggestion="Import or define function before use",
                        example_fix=f"from module import {func_name}"
                    ))
        
        # Check for exception handling
        if 'try:' in code and 'except' not in code:
            self.issues.append(DebugIssue(
                severity="error",
                line_number=None,
                code_snippet="try block",
                issue_type="incomplete_try",
                description="Try block without except clause",
                fix_suggestion="Add except clause to handle exceptions",
                example_fix="try:\n    ...\nexcept Exception as e:\n    print(f'Error: {e}')"
            ))
    
    def _debug_javascript(self, code: str):
        """JavaScript-specific debugging"""
        
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Missing semicolons (if code style uses them)
            if re.match(r'^\s*(?:const|let|var|return)\s+.*[^;{]$', line.strip()):
                if not line.strip().endswith('{'):
                    self.issues.append(DebugIssue(
                        severity="warning",
                        line_number=i,
                        code_snippet=line.strip(),
                        issue_type="missing_semicolon",
                        description="Consider adding semicolon",
                        fix_suggestion="Add semicolon at end of statement",
                        example_fix=line.strip() + ';'
                    ))
            
            # Comparing with == instead of ===
            if '==' in line and '===' not in line and '!=' in line:
                self.issues.append(DebugIssue(
                    severity="warning",
                    line_number=i,
                    code_snippet=line.strip(),
                    issue_type="loose_equality",
                    description="Using loose equality (==) instead of strict (===)",
                    fix_suggestion="Use === for strict equality",
                    example_fix=line.replace('==', '===')
                ))
            
            # Undefined variables
            if re.search(r'\b(\w+)\s*=', line) and 'var' not in line and 'let' not in line and 'const' not in line:
                if not line.strip().startswith('this.') and not line.strip().startswith('window.'):
                    self.issues.append(DebugIssue(
                        severity="error",
                        line_number=i,
                        code_snippet=line.strip(),
                        issue_type="implicit_global",
                        description="Assignment without declaration creates implicit global",
                        fix_suggestion="Declare variable with let or const",
                        example_fix="const " + line.strip()
                    ))
    
    def _check_common_issues(self, code: str, language: str):
        """Check for issues common to all languages"""
        
        # Check for TODO/FIXME comments
        todos = re.findall(r'(#|//)\s*(TODO|FIXME):?\s*(.+)', code)
        for comment_type, tag, description in todos:
            self.issues.append(DebugIssue(
                severity="info",
                line_number=None,
                code_snippet=f"{tag}: {description}",
                issue_type="incomplete_code",
                description=f"Code marked with {tag}",
                fix_suggestion="Complete the implementation",
                example_fix=description.strip()
            ))
        
        # Check for security issues
        if 'eval(' in code:
            self.issues.append(DebugIssue(
                severity="error",
                line_number=None,
                code_snippet="eval() usage",
                issue_type="security_risk",
                description="Using eval() is a security risk",
                fix_suggestion="Avoid eval() and use safer alternatives",
                example_fix="Use JSON.parse() or specific parsing functions"
            ))
    
    def suggest_fixes(self, error_message: str, code: str, language: str) -> List[Dict]:
        """Analyze error message and suggest fixes"""
        
        suggestions = []
        
        # Parse common error patterns
        if "NameError" in error_message or "not defined" in error_message:
            match = re.search(r"'(\w+)'", error_message)
            if match:
                var_name = match.group(1)
                suggestions.append({
                    "issue": f"Variable '{var_name}' is not defined",
                    "fix": f"Define '{var_name}' before using it",
                    "code": f"{var_name} = None  # or appropriate initial value"
                })
        
        elif "IndentationError" in error_message:
            suggestions.append({
                "issue": "Inconsistent indentation",
                "fix": "Use consistent 4-space indentation",
                "code": "Make sure all code blocks use 4 spaces"
            })
        
        elif "SyntaxError" in error_message:
            if "':'" in error_message:
                suggestions.append({
                    "issue": "Missing colon in control flow statement",
                    "fix": "Add ':' at the end of if/for/while/def statements",
                    "code": "if condition:  # Note the colon"
                })
        
        elif "TypeError" in error_message:
            suggestions.append({
                "issue": "Type mismatch or wrong number of arguments",
                "fix": "Check function arguments and variable types",
                "code": "Verify the data types match function expectations"
            })
        
        return suggestions
    
    def trace_error(self, error: Exception, code: str) -> Dict:
        """Trace an error through the code"""
        
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        
        return {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": tb,
            "suggestions": self.suggest_fixes(str(error), code, "python")
        }
