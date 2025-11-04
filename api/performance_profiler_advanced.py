"""
SuperAgent v8.0 - Advanced Performance Profiler
A-F Grading System with Big O Analysis and Deep Performance Metrics
"""

import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class PerformanceGrade(Enum):
    """Performance grades"""
    A = "A"  # Excellent
    B = "B"  # Good
    C = "C"  # Acceptable
    D = "D"  # Poor
    F = "F"  # Failing


@dataclass
class ComplexityAnalysis:
    """Big O complexity analysis"""
    time_complexity: str
    space_complexity: str
    explanation: str
    confidence: float


@dataclass
class PerformanceMetric:
    """A single performance metric"""
    name: str
    value: float
    unit: str
    threshold: float
    status: str


@dataclass
class PerformanceProfileResult:
    """Complete performance profile"""
    grade: PerformanceGrade
    score: float
    time_complexity: ComplexityAnalysis
    space_complexity: ComplexityAnalysis
    metrics: List[PerformanceMetric]
    issues: List[str]
    recommendations: List[str]
    benchmarks: Dict[str, float]
    comparison: Dict[str, Any]


class AdvancedPerformanceProfiler:
    """Advanced performance profiling system"""
    
    def profile_code(self, code: str, language: str = "python") -> PerformanceProfileResult:
        """Profile code for performance"""
        
        # Analyze complexity
        time_complexity = self._analyze_time_complexity(code)
        space_complexity = self._analyze_space_complexity(code)
        
        # Calculate metrics
        metrics = self._calculate_metrics(code)
        
        # Determine grade
        grade, score = self._determine_grade(metrics, time_complexity)
        
        # Identify issues
        issues = self._identify_issues(code, metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(code, metrics, issues)
        
        # Benchmark comparison
        benchmarks = self._get_benchmarks(language)
        
        # Comparison with standards
        comparison = self._compare_with_standards(metrics, benchmarks)
        
        return PerformanceProfileResult(
            grade=grade,
            score=score,
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            benchmarks=benchmarks,
            comparison=comparison,
        )
    
    def _analyze_time_complexity(self, code: str) -> ComplexityAnalysis:
        """Analyze time complexity"""
        explanation = ""
        complexity = "O(1)"
        confidence = 50.0
        
        # Count nested loops
        for_count = code.count("for")
        while_count = code.count("while")
        total_loops = for_count + while_count
        
        if total_loops == 0:
            complexity = "O(1)"
            explanation = "No loops detected - constant time"
            confidence = 95.0
        elif total_loops == 1:
            complexity = "O(n)"
            explanation = "Single loop detected - linear time"
            confidence = 85.0
        elif total_loops == 2:
            complexity = "O(n²)"
            explanation = "Two nested loops detected - quadratic time"
            confidence = 85.0
        elif total_loops >= 3:
            complexity = "O(n³)"
            explanation = f"{total_loops} nested loops detected - cubic time"
            confidence = 80.0
        
        # Check for recursion
        if "def " in code:
            func_name = code.split("def ")[1].split("(")[0] if "def " in code else ""
            if func_name and code.count(func_name) > 2:
                complexity = "O(2^n) or O(n!)"
                explanation = "Recursive function detected - exponential time"
                confidence = 70.0
        
        # Check for sorting
        if "sort(" in code or "sorted(" in code:
            complexity = "O(n log n)"
            explanation = "Sorting detected - linearithmic time"
            confidence = 90.0
        
        return ComplexityAnalysis(
            time_complexity=complexity,
            space_complexity="O(n)",
            explanation=explanation,
            confidence=confidence,
        )
    
    def _analyze_space_complexity(self, code: str) -> ComplexityAnalysis:
        """Analyze space complexity"""
        explanation = ""
        complexity = "O(1)"
        confidence = 50.0
        
        # Check for data structures
        if "[" in code and "]" in code:
            complexity = "O(n)"
            explanation = "Array/list detected - linear space"
            confidence = 85.0
        
        if "{" in code and ":" in code:
            complexity = "O(n)"
            explanation = "Dictionary/object detected - linear space"
            confidence = 85.0
        
        # Check for recursion depth
        if "def " in code and code.count("def ") > 1:
            complexity = "O(n)"
            explanation = "Recursive calls detected - linear space (call stack)"
            confidence = 80.0
        
        return ComplexityAnalysis(
            time_complexity="O(n)",
            space_complexity=complexity,
            explanation=explanation,
            confidence=confidence,
        )
    
    def _calculate_metrics(self, code: str) -> List[PerformanceMetric]:
        """Calculate performance metrics"""
        metrics = []
        
        # Code length metric
        lines = len(code.split("\n"))
        lines_metric = PerformanceMetric(
            name="Lines of Code",
            value=lines,
            unit="lines",
            threshold=500,
            status="good" if lines < 500 else "warning" if lines < 1000 else "critical"
        )
        metrics.append(lines_metric)
        
        # Cyclomatic complexity
        if_count = code.count("if")
        else_count = code.count("else")
        for_count = code.count("for")
        while_count = code.count("while")
        cyclomatic = 1 + if_count + else_count + for_count + while_count
        
        cyclomatic_metric = PerformanceMetric(
            name="Cyclomatic Complexity",
            value=cyclomatic,
            unit="paths",
            threshold=10,
            status="good" if cyclomatic < 10 else "warning" if cyclomatic < 20 else "critical"
        )
        metrics.append(cyclomatic_metric)
        
        # Function count
        func_count = code.count("def ") + code.count("function ")
        func_metric = PerformanceMetric(
            name="Function Count",
            value=func_count,
            unit="functions",
            threshold=20,
            status="good" if func_count < 20 else "warning"
        )
        metrics.append(func_metric)
        
        # Database query count
        query_count = code.count("query(") + code.count("execute(") + code.count("find(")
        query_metric = PerformanceMetric(
            name="Database Queries",
            value=query_count,
            unit="queries",
            threshold=5,
            status="good" if query_count <= 5 else "warning" if query_count <= 10 else "critical"
        )
        metrics.append(query_metric)
        
        # Loop nesting depth
        max_nesting = self._calculate_max_nesting(code)
        nesting_metric = PerformanceMetric(
            name="Max Loop Nesting",
            value=max_nesting,
            unit="levels",
            threshold=3,
            status="good" if max_nesting <= 2 else "warning" if max_nesting <= 3 else "critical"
        )
        metrics.append(nesting_metric)
        
        return metrics
    
    def _calculate_max_nesting(self, code: str) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        
        for char in code:
            if char in ["{", "("]:
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in ["}", ")"]:
                current_depth -= 1
        
        return max_depth
    
    def _determine_grade(self, metrics: List[PerformanceMetric], complexity: ComplexityAnalysis) -> Tuple[PerformanceGrade, float]:
        """Determine performance grade"""
        score = 100.0
        
        # Deduct points for bad metrics
        for metric in metrics:
            if metric.status == "critical":
                score -= 20
            elif metric.status == "warning":
                score -= 10
        
        # Deduct points for bad complexity
        if "O(n³)" in complexity.time_complexity or "O(2^n)" in complexity.time_complexity:
            score -= 30
        elif "O(n²)" in complexity.time_complexity:
            score -= 15
        
        # Determine grade
        if score >= 90:
            grade = PerformanceGrade.A
        elif score >= 80:
            grade = PerformanceGrade.B
        elif score >= 70:
            grade = PerformanceGrade.C
        elif score >= 60:
            grade = PerformanceGrade.D
        else:
            grade = PerformanceGrade.F
        
        return grade, score
    
    def _identify_issues(self, code: str, metrics: List[PerformanceMetric]) -> List[str]:
        """Identify performance issues"""
        issues = []
        
        for metric in metrics:
            if metric.status == "critical":
                issues.append(f"CRITICAL: {metric.name} is {metric.value} (threshold: {metric.threshold})")
            elif metric.status == "warning":
                issues.append(f"WARNING: {metric.name} is {metric.value} (threshold: {metric.threshold})")
        
        # Check for N+1 queries
        if code.count("for") > 0 and code.count("query(") > 0:
            issues.append("Potential N+1 query problem: queries inside loops")
        
        # Check for inefficient string operations
        if code.count("+") > 5 and ('"' in code or "'" in code):
            issues.append("Inefficient string concatenation detected")
        
        return issues
    
    def _generate_recommendations(self, code: str, metrics: List[PerformanceMetric], issues: List[str]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if "O(n²)" in code or "O(n³)" in code:
            recommendations.append("Consider using hash maps or sorting to reduce complexity")
        
        if "Potential N+1 query problem" in str(issues):
            recommendations.append("Batch queries or use joins to avoid N+1 problem")
        
        if "Inefficient string concatenation" in str(issues):
            recommendations.append("Use join() or string builders for better performance")
        
        if any(m.name == "Cyclomatic Complexity" and m.status == "critical" for m in metrics):
            recommendations.append("Refactor code to reduce cyclomatic complexity")
        
        return recommendations
    
    def _get_benchmarks(self, language: str) -> Dict[str, float]:
        """Get performance benchmarks for language"""
        benchmarks = {
            "python": {
                "max_lines": 500,
                "max_cyclomatic": 10,
                "max_functions": 20,
                "max_queries": 5,
                "max_nesting": 3,
            },
            "javascript": {
                "max_lines": 400,
                "max_cyclomatic": 10,
                "max_functions": 25,
                "max_queries": 5,
                "max_nesting": 3,
            },
        }
        return benchmarks.get(language, benchmarks["python"])
    
    def _compare_with_standards(self, metrics: List[PerformanceMetric], benchmarks: Dict[str, float]) -> Dict[str, Any]:
        """Compare metrics with industry standards"""
        comparison = {
            "meets_standards": True,
            "deviations": []
        }
        
        for metric in metrics:
            if metric.value > metric.threshold:
                comparison["meets_standards"] = False
                deviation = {
                    "metric": metric.name,
                    "value": metric.value,
                    "threshold": metric.threshold,
                    "deviation_percent": ((metric.value - metric.threshold) / metric.threshold * 100)
                }
                comparison["deviations"].append(deviation)
        
        return comparison


# API Endpoint
async def profile_code_endpoint(code: str, language: str = "python") -> Dict[str, Any]:
    """API endpoint for code profiling"""
    profiler = AdvancedPerformanceProfiler()
    result = profiler.profile_code(code, language)
    
    return {
        "grade": result.grade.value,
        "score": result.score,
        "time_complexity": {
            "complexity": result.time_complexity.time_complexity,
            "explanation": result.time_complexity.explanation,
            "confidence": result.time_complexity.confidence,
        },
        "space_complexity": {
            "complexity": result.space_complexity.space_complexity,
            "explanation": result.space_complexity.explanation,
            "confidence": result.space_complexity.confidence,
        },
        "metrics": [
            {
                "name": m.name,
                "value": m.value,
                "unit": m.unit,
                "status": m.status,
            }
            for m in result.metrics
        ],
        "issues": result.issues,
        "recommendations": result.recommendations,
        "meets_standards": result.comparison["meets_standards"],
    }
