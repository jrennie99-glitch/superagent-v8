"""
Dedicated Code Review System
Comprehensive code review with security scanning and best practices
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime

class CodeReviewSystem:
    """Comprehensive code review and quality analysis"""
    
    def __init__(self):
        self.review_history = []
        self.severity_levels = ["critical", "high", "medium", "low", "info"]
        
    def review_code(self, code: str, language: str, context: str = "") -> Dict[str, Any]:
        """Comprehensive code review"""
        issues = []
        
        # Security checks
        issues.extend(self._security_scan(code, language))
        
        # Code quality checks
        issues.extend(self._quality_checks(code, language))
        
        # Best practices
        issues.extend(self._best_practices(code, language))
        
        # Performance analysis
        issues.extend(self._performance_analysis(code, language))
        
        # Documentation check
        issues.extend(self._documentation_check(code, language))
        
        # Calculate score
        score = self._calculate_score(issues)
        
        review_result = {
            "language": language,
            "total_issues": len(issues),
            "issues_by_severity": self._group_by_severity(issues),
            "issues": issues,
            "score": score,
            "grade": self._score_to_grade(score),
            "recommendations": self._generate_recommendations(issues),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.review_history.append(review_result)
        return review_result
    
    def _security_scan(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Scan for security vulnerabilities"""
        issues = []
        
        # SQL Injection patterns
        sql_patterns = [
            r"execute\s*\(.+\+.+\)",
            r"cursor\.execute\(.+%.*\)",
            r"query\s*=.+\+",
        ]
        for pattern in sql_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "type": "security",
                    "severity": "critical",
                    "message": "Potential SQL injection vulnerability",
                    "pattern": pattern,
                    "fix": "Use parameterized queries instead of string concatenation"
                })
        
        # Hardcoded secrets
        secret_patterns = [
            r"password\s*=\s*['\"][\w!@#$%^&*]+['\"]",
            r"api_key\s*=\s*['\"][\w-]+['\"]",
            r"secret\s*=\s*['\"][\w-]+['\"]",
            r"token\s*=\s*['\"][\w-]+['\"]",
        ]
        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "type": "security",
                    "severity": "high",
                    "message": "Hardcoded secret detected",
                    "pattern": pattern,
                    "fix": "Use environment variables for sensitive data"
                })
        
        # Command injection
        if language.lower() == "python":
            if re.search(r"os\.system\(|subprocess\.(call|run|Popen)\(.+shell\s*=\s*True", code):
                issues.append({
                    "type": "security",
                    "severity": "high",
                    "message": "Potential command injection vulnerability",
                    "fix": "Avoid shell=True, use list arguments instead"
                })
        
        # XSS vulnerabilities
        if language.lower() in ["javascript", "typescript"]:
            if re.search(r"innerHTML\s*=|document\.write\(", code):
                issues.append({
                    "type": "security",
                    "severity": "medium",
                    "message": "Potential XSS vulnerability",
                    "fix": "Use textContent or sanitize HTML input"
                })
        
        return issues
    
    def _quality_checks(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Code quality checks"""
        issues = []
        
        # Long functions (>50 lines)
        lines = code.split('\n')
        if len(lines) > 50:
            issues.append({
                "type": "quality",
                "severity": "medium",
                "message": f"Function is too long ({len(lines)} lines)",
                "fix": "Consider breaking into smaller functions"
            })
        
        # Deep nesting (>4 levels)
        max_indent = 0
        for line in lines:
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent // 4)
        
        if max_indent > 4:
            issues.append({
                "type": "quality",
                "severity": "medium",
                "message": f"Deep nesting detected ({max_indent} levels)",
                "fix": "Refactor to reduce complexity"
            })
        
        # Magic numbers
        if language.lower() in ["python", "javascript", "typescript"]:
            magic_numbers = re.findall(r'\b\d{2,}\b', code)
            if len(magic_numbers) > 3:
                issues.append({
                    "type": "quality",
                    "severity": "low",
                    "message": "Magic numbers detected",
                    "fix": "Define constants for numeric literals"
                })
        
        return issues
    
    def _best_practices(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Best practices checks"""
        issues = []
        
        if language.lower() == "python":
            # Missing type hints
            if "def " in code and "->" not in code and ":" not in code:
                issues.append({
                    "type": "best_practice",
                    "severity": "low",
                    "message": "Missing type hints",
                    "fix": "Add type hints for better code clarity"
                })
            
            # Using mutable default arguments
            if re.search(r"def\s+\w+\([^)]*=\s*\[\]", code):
                issues.append({
                    "type": "best_practice",
                    "severity": "medium",
                    "message": "Mutable default argument",
                    "fix": "Use None as default and initialize inside function"
                })
        
        if language.lower() in ["javascript", "typescript"]:
            # Using var instead of let/const
            if re.search(r"\bvar\s+", code):
                issues.append({
                    "type": "best_practice",
                    "severity": "low",
                    "message": "Using 'var' keyword",
                    "fix": "Use 'let' or 'const' instead"
                })
        
        return issues
    
    def _performance_analysis(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Performance analysis"""
        issues = []
        
        # Nested loops
        if language.lower() in ["python", "javascript", "typescript"]:
            nested_loops = len(re.findall(r"for\s+.+:\s+.*for\s+", code))
            if nested_loops > 0:
                issues.append({
                    "type": "performance",
                    "severity": "medium",
                    "message": f"Nested loops detected ({nested_loops})",
                    "fix": "Consider optimizing with better data structures"
                })
        
        # String concatenation in loops
        if language.lower() == "python":
            if re.search(r"for\s+.+:\s+.*\+=.*['\"]", code):
                issues.append({
                    "type": "performance",
                    "severity": "low",
                    "message": "String concatenation in loop",
                    "fix": "Use list.append() and ''.join() instead"
                })
        
        return issues
    
    def _documentation_check(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Documentation quality check"""
        issues = []
        
        lines = code.split('\n')
        comment_ratio = sum(1 for line in lines if line.strip().startswith('#') or line.strip().startswith('//')) / max(len(lines), 1)
        
        if comment_ratio < 0.1:
            issues.append({
                "type": "documentation",
                "severity": "low",
                "message": "Low comment ratio",
                "fix": "Add more comments to explain complex logic"
            })
        
        # Check for docstrings in Python
        if language.lower() == "python":
            if "def " in code and '"""' not in code and "'''" not in code:
                issues.append({
                    "type": "documentation",
                    "severity": "medium",
                    "message": "Missing docstrings",
                    "fix": "Add docstrings to functions and classes"
                })
        
        return issues
    
    def _calculate_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate overall code score (0-100)"""
        base_score = 100
        
        severity_penalties = {
            "critical": 20,
            "high": 15,
            "medium": 10,
            "low": 5,
            "info": 2
        }
        
        for issue in issues:
            penalty = severity_penalties.get(issue["severity"], 5)
            base_score -= penalty
        
        return max(0, min(100, base_score))
    
    def _score_to_grade(self, score: float) -> str:
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
    
    def _group_by_severity(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group issues by severity"""
        grouped = {severity: 0 for severity in self.severity_levels}
        for issue in issues:
            grouped[issue["severity"]] += 1
        return grouped
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Prioritize critical issues
        critical_issues = [i for i in issues if i["severity"] == "critical"]
        if critical_issues:
            recommendations.append("🚨 Fix critical security vulnerabilities immediately")
        
        # Group by type
        issue_types = {}
        for issue in issues:
            issue_type = issue["type"]
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
            recommendations.append(f"Address {count} {issue_type} issue(s)")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def get_review_stats(self) -> Dict[str, Any]:
        """Get review statistics"""
        total_reviews = len(self.review_history)
        if total_reviews == 0:
            return {"total_reviews": 0, "message": "No reviews yet"}
        
        avg_score = sum(r["score"] for r in self.review_history) / total_reviews
        avg_issues = sum(r["total_issues"] for r in self.review_history) / total_reviews
        
        return {
            "total_reviews": total_reviews,
            "average_score": round(avg_score, 2),
            "average_issues": round(avg_issues, 2),
            "average_grade": self._score_to_grade(avg_score)
        }

# Global instance
code_review_system = CodeReviewSystem()
