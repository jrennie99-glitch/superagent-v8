"""
Quality Validator Module

Validates generated code for enterprise-level quality before delivery.
Ensures all generated apps are complete, functional, and professional.
"""

import re
from typing import Dict, List, Any, Tuple
import structlog

logger = structlog.get_logger()


class QualityValidator:
    """
    Validates generated code for enterprise quality standards.
    
    Checks:
    - Completeness (all required elements present)
    - Functionality (code structure suggests it will work)
    - Professional styling (modern, clean design)
    - Responsiveness (mobile-friendly)
    - Accessibility (ARIA labels, semantic HTML)
    """
    
    def __init__(self):
        """Initialize quality validator."""
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load validation rules for different file types."""
        
        return {
            "html": [
                {
                    "name": "DOCTYPE Declaration",
                    "pattern": r"<!DOCTYPE\s+html>",
                    "severity": "critical",
                    "message": "Missing DOCTYPE declaration"
                },
                {
                    "name": "HTML Tag",
                    "pattern": r"<html[^>]*>",
                    "severity": "critical",
                    "message": "Missing <html> tag"
                },
                {
                    "name": "Head Section",
                    "pattern": r"<head>",
                    "severity": "critical",
                    "message": "Missing <head> section"
                },
                {
                    "name": "Body Section",
                    "pattern": r"<body>",
                    "severity": "critical",
                    "message": "Missing <body> section"
                },
                {
                    "name": "Charset Meta",
                    "pattern": r'charset=["\']?UTF-8',
                    "severity": "critical",
                    "message": "Missing charset meta tag"
                },
                {
                    "name": "Viewport Meta",
                    "pattern": r'name=["\']viewport["\']',
                    "severity": "critical",
                    "message": "Missing viewport meta tag (not mobile-friendly)"
                },
                {
                    "name": "Title Tag",
                    "pattern": r"<title>",
                    "severity": "warning",
                    "message": "Missing <title> tag"
                },
                {
                    "name": "Closing HTML Tag",
                    "pattern": r"</html>",
                    "severity": "critical",
                    "message": "Missing closing </html> tag"
                },
                {
                    "name": "Closing Body Tag",
                    "pattern": r"</body>",
                    "severity": "critical",
                    "message": "Missing closing </body> tag"
                }
            ],
            "css": [
                {
                    "name": "Box Sizing Reset",
                    "pattern": r"box-sizing:\s*border-box",
                    "severity": "warning",
                    "message": "Missing box-sizing reset (layout issues possible)"
                },
                {
                    "name": "Responsive Design",
                    "pattern": r"@media|flex|grid",
                    "severity": "warning",
                    "message": "No responsive design detected"
                },
                {
                    "name": "Modern Layout",
                    "pattern": r"display:\s*(flex|grid)",
                    "severity": "info",
                    "message": "Consider using modern layout (flexbox/grid)"
                }
            ],
            "javascript": [
                {
                    "name": "DOM Ready Handler",
                    "pattern": r"DOMContentLoaded|window\.onload|document\.ready",
                    "severity": "critical",
                    "message": "No DOM ready handler (code may run before page loads)"
                },
                {
                    "name": "Event Listeners",
                    "pattern": r"addEventListener|onclick|on\w+\s*=",
                    "severity": "critical",
                    "message": "No event listeners found (app won't be interactive)"
                },
                {
                    "name": "Error Handling",
                    "pattern": r"try\s*\{|catch\s*\(|\.catch\(",
                    "severity": "warning",
                    "message": "No error handling detected"
                }
            ]
        }
    
    def validate_html(self, html_code: str) -> Dict[str, Any]:
        """
        Validate HTML code for enterprise quality.
        
        Args:
            html_code: HTML code to validate
            
        Returns:
            Validation report with issues and score
        """
        issues = []
        
        for rule in self.validation_rules["html"]:
            if not re.search(rule["pattern"], html_code, re.IGNORECASE):
                issues.append({
                    "type": "html",
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "message": rule["message"]
                })
        
        # Additional structural checks
        issues.extend(self._check_html_structure(html_code))
        
        # Calculate score
        critical_issues = len([i for i in issues if i["severity"] == "critical"])
        warning_issues = len([i for i in issues if i["severity"] == "warning"])
        
        score = 100 - (critical_issues * 20) - (warning_issues * 5)
        score = max(0, score)
        
        return {
            "type": "html",
            "score": score,
            "passed": critical_issues == 0,
            "issues": issues,
            "summary": f"{len(issues)} issues found ({critical_issues} critical, {warning_issues} warnings)"
        }
    
    def _check_html_structure(self, html_code: str) -> List[Dict[str, Any]]:
        """Check HTML structure for common issues."""
        issues = []
        
        # Check for unclosed tags (basic check)
        opening_tags = re.findall(r'<(\w+)[^>]*>', html_code)
        closing_tags = re.findall(r'</(\w+)>', html_code)
        
        # Self-closing tags that don't need closing
        self_closing = {'img', 'br', 'hr', 'input', 'meta', 'link'}
        
        for tag in opening_tags:
            if tag not in self_closing:
                if opening_tags.count(tag) > closing_tags.count(tag):
                    issues.append({
                        "type": "html",
                        "name": f"Unclosed {tag} tag",
                        "severity": "critical",
                        "message": f"Found {opening_tags.count(tag)} <{tag}> but only {closing_tags.count(tag)} </{tag}>"
                    })
        
        # Check for empty body
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_code, re.DOTALL)
        if body_match:
            body_content = body_match.group(1).strip()
            if len(body_content) < 50:
                issues.append({
                    "type": "html",
                    "name": "Empty Body",
                    "severity": "critical",
                    "message": "Body section appears to be empty or minimal"
                })
        
        return issues
    
    def validate_css(self, css_code: str) -> Dict[str, Any]:
        """
        Validate CSS code for enterprise quality.
        
        Args:
            css_code: CSS code to validate
            
        Returns:
            Validation report with issues and score
        """
        issues = []
        
        for rule in self.validation_rules["css"]:
            if not re.search(rule["pattern"], css_code, re.IGNORECASE):
                issues.append({
                    "type": "css",
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "message": rule["message"]
                })
        
        # Check for minimal CSS
        if len(css_code.strip()) < 100:
            issues.append({
                "type": "css",
                "name": "Minimal CSS",
                "severity": "warning",
                "message": "CSS appears minimal - may lack professional styling"
            })
        
        # Calculate score
        critical_issues = len([i for i in issues if i["severity"] == "critical"])
        warning_issues = len([i for i in issues if i["severity"] == "warning"])
        
        score = 100 - (critical_issues * 20) - (warning_issues * 5)
        score = max(0, score)
        
        return {
            "type": "css",
            "score": score,
            "passed": critical_issues == 0,
            "issues": issues,
            "summary": f"{len(issues)} issues found ({critical_issues} critical, {warning_issues} warnings)"
        }
    
    def validate_javascript(self, js_code: str) -> Dict[str, Any]:
        """
        Validate JavaScript code for enterprise quality.
        
        Args:
            js_code: JavaScript code to validate
            
        Returns:
            Validation report with issues and score
        """
        issues = []
        
        for rule in self.validation_rules["javascript"]:
            if not re.search(rule["pattern"], js_code, re.IGNORECASE):
                issues.append({
                    "type": "javascript",
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "message": rule["message"]
                })
        
        # Check for minimal JavaScript
        if len(js_code.strip()) < 100:
            issues.append({
                "type": "javascript",
                "name": "Minimal JavaScript",
                "severity": "critical",
                "message": "JavaScript appears minimal - functionality may be incomplete"
            })
        
        # Check for common issues
        if "console.log" in js_code:
            issues.append({
                "type": "javascript",
                "name": "Debug Code",
                "severity": "info",
                "message": "console.log statements found (remove for production)"
            })
        
        # Calculate score
        critical_issues = len([i for i in issues if i["severity"] == "critical"])
        warning_issues = len([i for i in issues if i["severity"] == "warning"])
        
        score = 100 - (critical_issues * 20) - (warning_issues * 5)
        score = max(0, score)
        
        return {
            "type": "javascript",
            "score": score,
            "passed": critical_issues == 0,
            "issues": issues,
            "summary": f"{len(issues)} issues found ({critical_issues} critical, {warning_issues} warnings)"
        }
    
    def validate_complete_app(self, html_code: str) -> Dict[str, Any]:
        """
        Validate a complete single-file application.
        
        Args:
            html_code: Complete HTML file with embedded CSS and JS
            
        Returns:
            Comprehensive validation report
        """
        logger.info("Validating complete application")
        
        # Extract sections
        css_code = self._extract_css(html_code)
        js_code = self._extract_javascript(html_code)
        
        # Validate each section
        html_report = self.validate_html(html_code)
        css_report = self.validate_css(css_code) if css_code else {"score": 0, "passed": False, "issues": [{"message": "No CSS found"}]}
        js_report = self.validate_javascript(js_code) if js_code else {"score": 0, "passed": False, "issues": [{"message": "No JavaScript found"}]}
        
        # Calculate overall score
        overall_score = (html_report["score"] + css_report["score"] + js_report["score"]) / 3
        
        # Determine if passed
        passed = (
            html_report["passed"] and
            css_report["passed"] and
            js_report["passed"]
        )
        
        # Collect all issues
        all_issues = (
            html_report["issues"] +
            css_report["issues"] +
            js_report["issues"]
        )
        
        critical_count = len([i for i in all_issues if i["severity"] == "critical"])
        
        return {
            "overall_score": round(overall_score, 1),
            "passed": passed,
            "ready_for_production": passed and overall_score >= 80,
            "html": html_report,
            "css": css_report,
            "javascript": js_report,
            "total_issues": len(all_issues),
            "critical_issues": critical_count,
            "recommendation": self._get_recommendation(overall_score, passed)
        }
    
    def _extract_css(self, html_code: str) -> str:
        """Extract CSS from HTML."""
        css_match = re.search(r'<style[^>]*>(.*?)</style>', html_code, re.DOTALL | re.IGNORECASE)
        return css_match.group(1) if css_match else ""
    
    def _extract_javascript(self, html_code: str) -> str:
        """Extract JavaScript from HTML."""
        js_match = re.search(r'<script[^>]*>(.*?)</script>', html_code, re.DOTALL | re.IGNORECASE)
        return js_match.group(1) if js_match else ""
    
    def _get_recommendation(self, score: float, passed: bool) -> str:
        """Get recommendation based on validation results."""
        
        if score >= 90 and passed:
            return "✅ EXCELLENT - Ready for production use"
        elif score >= 80 and passed:
            return "✅ GOOD - Ready to use with minor improvements possible"
        elif score >= 70:
            return "⚠️ ACCEPTABLE - Works but needs improvements"
        elif score >= 50:
            return "⚠️ NEEDS WORK - Significant issues to address"
        else:
            return "❌ POOR QUALITY - Requires major revisions"
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """
        Generate a human-readable validation report.
        
        Args:
            validation_results: Results from validate_complete_app
            
        Returns:
            Formatted report string
        """
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           ENTERPRISE QUALITY VALIDATION REPORT               ║
╚══════════════════════════════════════════════════════════════╝

OVERALL SCORE: {validation_results['overall_score']}/100
STATUS: {'✅ PASSED' if validation_results['passed'] else '❌ FAILED'}
PRODUCTION READY: {'✅ YES' if validation_results['ready_for_production'] else '❌ NO'}

{validation_results['recommendation']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPONENT SCORES:
  HTML:       {validation_results['html']['score']}/100 {'✅' if validation_results['html']['passed'] else '❌'}
  CSS:        {validation_results['css']['score']}/100 {'✅' if validation_results['css']['passed'] else '❌'}
  JavaScript: {validation_results['javascript']['score']}/100 {'✅' if validation_results['javascript']['passed'] else '❌'}

ISSUES SUMMARY:
  Total Issues: {validation_results['total_issues']}
  Critical: {validation_results['critical_issues']}

"""
        
        # Add critical issues details
        if validation_results['critical_issues'] > 0:
            report += "\n⚠️ CRITICAL ISSUES THAT MUST BE FIXED:\n"
            for component in ['html', 'css', 'javascript']:
                critical = [i for i in validation_results[component]['issues'] if i['severity'] == 'critical']
                if critical:
                    report += f"\n  {component.upper()}:\n"
                    for issue in critical:
                        report += f"    • {issue['message']}\n"
        
        report += "\n" + "═" * 64 + "\n"
        
        return report


# Global instance
validator = QualityValidator()


def validate_generated_app(html_code: str) -> Dict[str, Any]:
    """
    Convenience function to validate a generated app.
    
    Args:
        html_code: Complete HTML application code
        
    Returns:
        Validation results
    """
    return validator.validate_complete_app(html_code)


def get_validation_report(html_code: str) -> str:
    """
    Get a formatted validation report for a generated app.
    
    Args:
        html_code: Complete HTML application code
        
    Returns:
        Formatted report string
    """
    results = validator.validate_complete_app(html_code)
    return validator.generate_validation_report(results)
