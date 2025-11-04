"""AI-powered code review module with security and quality analysis."""

import ast
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()


class CodeReviewer:
    """
    Advanced AI-powered code reviewer.
    
    Features:
    - Security vulnerability detection
    - Code quality analysis
    - Best practices enforcement
    - Performance optimization suggestions
    - Maintainability scoring
    """
    
    def __init__(self, llm_provider):
        """Initialize code reviewer.
        
        Args:
            llm_provider: LLM provider for AI analysis
        """
        self.llm = llm_provider
        self.security_patterns = self._load_security_patterns()
        
    def _load_security_patterns(self) -> Dict[str, Any]:
        """Load common security vulnerability patterns."""
        return {
            "sql_injection": {
                "patterns": [r"execute\(.*\+.*\)", r"executemany\(.*%.*\)"],
                "severity": "critical",
                "description": "Potential SQL injection vulnerability"
            },
            "xss": {
                "patterns": [r"innerHTML\s*=", r"dangerouslySetInnerHTML"],
                "severity": "high",
                "description": "Potential XSS vulnerability"
            },
            "hardcoded_secrets": {
                "patterns": [r"password\s*=\s*['\"]", r"api_key\s*=\s*['\"]"],
                "severity": "critical",
                "description": "Hardcoded secrets detected"
            },
            "unsafe_deserialization": {
                "patterns": [r"pickle\.loads", r"yaml\.load\("],
                "severity": "high",
                "description": "Unsafe deserialization"
            },
            "command_injection": {
                "patterns": [r"os\.system\(", r"subprocess\.call\(.*shell=True"],
                "severity": "critical",
                "description": "Potential command injection"
            }
        }
    
    async def review_file(self, file_path: Path) -> Dict[str, Any]:
        """Perform comprehensive review of a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Review results
        """
        logger.info(f"Reviewing file: {file_path}")
        
        code = file_path.read_text()
        
        # Perform multiple analyses
        security_issues = await self._check_security(file_path, code)
        quality_issues = await self._check_quality(code)
        performance_issues = await self._check_performance(code)
        ai_suggestions = await self._get_ai_review(file_path, code)
        
        # Calculate scores
        scores = self._calculate_scores(
            security_issues,
            quality_issues,
            performance_issues
        )
        
        return {
            "file": str(file_path),
            "security": security_issues,
            "quality": quality_issues,
            "performance": performance_issues,
            "ai_suggestions": ai_suggestions,
            "scores": scores,
            "overall_grade": self._calculate_grade(scores)
        }
    
    async def _check_security(self, file_path: Path, code: str) -> List[Dict[str, Any]]:
        """Check for security vulnerabilities.
        
        Args:
            file_path: File path
            code: Source code
            
        Returns:
            List of security issues
        """
        issues = []
        
        # Check against known patterns
        import re
        for vuln_type, config in self.security_patterns.items():
            for pattern in config["patterns"]:
                matches = re.finditer(pattern, code)
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    issues.append({
                        "type": vuln_type,
                        "severity": config["severity"],
                        "description": config["description"],
                        "line": line_num,
                        "snippet": match.group(0)
                    })
        
        # AI-powered security analysis
        if issues or len(code) > 100:
            prompt = f"""Analyze this code for security vulnerabilities:

{code[:2000]}

Focus on:
- Injection attacks (SQL, command, XSS)
- Authentication/authorization issues
- Cryptography misuse
- Data exposure
- Input validation

Provide JSON with: [{{"type": "...", "severity": "...", "line": N, "description": "..."}}]"""
            
            try:
                ai_issues = await self.llm.generate_structured(
                    prompt,
                    schema={"issues": [{"type": "string", "severity": "string", "description": "string"}]}
                )
                issues.extend(ai_issues.get("issues", []))
            except Exception as e:
                logger.error(f"AI security analysis failed: {e}")
        
        return issues
    
    async def _check_quality(self, code: str) -> List[Dict[str, Any]]:
        """Check code quality.
        
        Args:
            code: Source code
            
        Returns:
            Quality issues
        """
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # Check for common quality issues
            for node in ast.walk(tree):
                # Long functions
                if isinstance(node, ast.FunctionDef):
                    body_lines = len(ast.unparse(node).split('\n'))
                    if body_lines > 50:
                        issues.append({
                            "type": "long_function",
                            "severity": "medium",
                            "description": f"Function '{node.name}' is too long ({body_lines} lines)",
                            "line": node.lineno,
                            "suggestion": "Consider breaking into smaller functions"
                        })
                
                # Deep nesting
                if isinstance(node, (ast.If, ast.For, ast.While)):
                    depth = self._calculate_nesting_depth(node)
                    if depth > 4:
                        issues.append({
                            "type": "deep_nesting",
                            "severity": "medium",
                            "description": f"Deep nesting detected (depth: {depth})",
                            "line": node.lineno,
                            "suggestion": "Refactor to reduce complexity"
                        })
                
                # Missing docstrings
                if isinstance(node, ast.FunctionDef):
                    if not ast.get_docstring(node) and not node.name.startswith('_'):
                        issues.append({
                            "type": "missing_docstring",
                            "severity": "low",
                            "description": f"Public function '{node.name}' missing docstring",
                            "line": node.lineno,
                            "suggestion": "Add comprehensive docstring"
                        })
        
        except Exception as e:
            logger.error(f"Quality check failed: {e}")
        
        return issues
    
    async def _check_performance(self, code: str) -> List[Dict[str, Any]]:
        """Check for performance issues.
        
        Args:
            code: Source code
            
        Returns:
            Performance issues
        """
        issues = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Inefficient loops
                if isinstance(node, ast.For):
                    # Check for appending in loop
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Attribute):
                                if child.func.attr == 'append':
                                    issues.append({
                                        "type": "inefficient_loop",
                                        "severity": "low",
                                        "description": "Consider list comprehension instead of append in loop",
                                        "line": node.lineno,
                                        "suggestion": "Use list comprehension for better performance"
                                    })
                
                # Global variable access in loops
                if isinstance(node, ast.Global):
                    issues.append({
                        "type": "global_in_function",
                        "severity": "medium",
                        "description": "Global variable usage can impact performance",
                        "line": node.lineno,
                        "suggestion": "Pass as parameter instead"
                    })
        
        except Exception as e:
            logger.error(f"Performance check failed: {e}")
        
        return issues
    
    async def _get_ai_review(self, file_path: Path, code: str) -> List[Dict[str, Any]]:
        """Get AI-powered review suggestions.
        
        Args:
            file_path: File path
            code: Source code
            
        Returns:
            AI suggestions
        """
        prompt = f"""Review this code and provide improvement suggestions:

File: {file_path.name}

{code[:3000]}

Provide specific, actionable suggestions for:
1. Code organization and structure
2. Naming conventions
3. Error handling improvements
4. Potential bugs or edge cases
5. Design patterns that could be applied

Format as JSON: [{{"category": "...", "suggestion": "...", "impact": "high/medium/low"}}]"""
        
        try:
            suggestions = await self.llm.generate_structured(
                prompt,
                schema={"suggestions": [{"category": "string", "suggestion": "string", "impact": "string"}]}
            )
            return suggestions.get("suggestions", [])
        except Exception as e:
            logger.error(f"AI review failed: {e}")
            return []
    
    def _calculate_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum nesting depth.
        
        Args:
            node: AST node
            depth: Current depth
            
        Returns:
            Maximum depth
        """
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _calculate_scores(self, security: List, quality: List, performance: List) -> Dict[str, float]:
        """Calculate quality scores.
        
        Args:
            security: Security issues
            quality: Quality issues
            performance: Performance issues
            
        Returns:
            Score dictionary
        """
        severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
        
        # Calculate deductions
        security_deduction = sum(
            severity_weights.get(issue.get("severity", "low"), 1)
            for issue in security
        )
        quality_deduction = sum(
            severity_weights.get(issue.get("severity", "low"), 1)
            for issue in quality
        )
        performance_deduction = sum(
            severity_weights.get(issue.get("severity", "low"), 1)
            for issue in performance
        )
        
        # Calculate scores (100 - deductions, min 0)
        return {
            "security": max(0, 100 - security_deduction * 2),
            "quality": max(0, 100 - quality_deduction),
            "performance": max(0, 100 - performance_deduction),
            "maintainability": max(0, 100 - (quality_deduction + performance_deduction) / 2)
        }
    
    def _calculate_grade(self, scores: Dict[str, float]) -> str:
        """Calculate overall grade.
        
        Args:
            scores: Score dictionary
            
        Returns:
            Grade (A-F)
        """
        avg_score = sum(scores.values()) / len(scores)
        
        if avg_score >= 90:
            return "A"
        elif avg_score >= 80:
            return "B"
        elif avg_score >= 70:
            return "C"
        elif avg_score >= 60:
            return "D"
        else:
            return "F"
    
    async def review_pull_request(self, files: List[Path]) -> Dict[str, Any]:
        """Review multiple files (e.g., for a pull request).
        
        Args:
            files: List of file paths
            
        Returns:
            Comprehensive review
        """
        reviews = []
        
        for file_path in files:
            if file_path.suffix in ['.py', '.js', '.ts', '.java']:
                review = await self.review_file(file_path)
                reviews.append(review)
        
        # Aggregate results
        all_security = []
        all_quality = []
        total_scores = {"security": 0, "quality": 0, "performance": 0, "maintainability": 0}
        
        for review in reviews:
            all_security.extend(review.get("security", []))
            all_quality.extend(review.get("quality", []))
            for key in total_scores:
                total_scores[key] += review["scores"][key]
        
        # Calculate averages
        if reviews:
            for key in total_scores:
                total_scores[key] /= len(reviews)
        
        return {
            "files_reviewed": len(reviews),
            "reviews": reviews,
            "summary": {
                "total_security_issues": len(all_security),
                "total_quality_issues": len(all_quality),
                "critical_issues": sum(1 for i in all_security if i.get("severity") == "critical"),
                "average_scores": total_scores,
                "overall_grade": self._calculate_grade(total_scores)
            }
        }





