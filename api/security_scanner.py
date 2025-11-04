"""
Code Security Scanner
Detect vulnerabilities and security issues
"""
import re
from typing import Dict, List

class SecurityScanner:
    """Scan code for security vulnerabilities"""
    
    def __init__(self):
        # Common vulnerability patterns
        self.patterns = {
            "sql_injection": [
                r'execute\(["\'].*%s.*["\']',
                r'execute\(["\'].*\+.*["\']',
                r'raw\s*\(.*\+.*\)',
            ],
            "xss": [
                r'innerHTML\s*=',
                r'document\.write\(',
                r'eval\(',
            ],
            "hardcoded_secrets": [
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'password\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ],
            "path_traversal": [
                r'open\(.*\+.*\)',
                r'\.\./',
            ],
            "command_injection": [
                r'os\.system\(',
                r'subprocess\.call\(.*shell=True',
                r'exec\(',
            ],
            "insecure_random": [
                r'random\.random\(',
                r'Math\.random\(',
            ],
        }
    
    def scan(self, code: str, language: str) -> Dict:
        """Scan code for security vulnerabilities"""
        vulnerabilities = []
        
        for vuln_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code, re.IGNORECASE)
                for match in matches:
                    line_number = code[:match.start()].count('\n') + 1
                    vulnerabilities.append({
                        "type": vuln_type,
                        "line": line_number,
                        "code": match.group(),
                        "severity": self._get_severity(vuln_type),
                        "description": self._get_description(vuln_type)
                    })
        
        severity_counts = {
            "critical": len([v for v in vulnerabilities if v["severity"] == "critical"]),
            "high": len([v for v in vulnerabilities if v["severity"] == "high"]),
            "medium": len([v for v in vulnerabilities if v["severity"] == "medium"]),
            "low": len([v for v in vulnerabilities if v["severity"] == "low"]),
        }
        
        return {
            "success": True,
            "vulnerabilities": vulnerabilities,
            "total_issues": len(vulnerabilities),
            "severity_counts": severity_counts,
            "is_safe": len(vulnerabilities) == 0,
            "risk_score": self._calculate_risk_score(severity_counts)
        }
    
    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type"""
        severity_map = {
            "sql_injection": "critical",
            "command_injection": "critical",
            "xss": "high",
            "hardcoded_secrets": "high",
            "path_traversal": "high",
            "insecure_random": "medium",
        }
        return severity_map.get(vuln_type, "low")
    
    def _get_description(self, vuln_type: str) -> str:
        """Get description for vulnerability type"""
        descriptions = {
            "sql_injection": "Potential SQL injection vulnerability. Use parameterized queries.",
            "xss": "Cross-site scripting vulnerability. Sanitize user input.",
            "hardcoded_secrets": "Hardcoded secrets detected. Use environment variables.",
            "path_traversal": "Path traversal vulnerability. Validate file paths.",
            "command_injection": "Command injection vulnerability. Avoid shell=True.",
            "insecure_random": "Using insecure random. Use secrets module for crypto.",
        }
        return descriptions.get(vuln_type, "Security issue detected")
    
    def _calculate_risk_score(self, severity_counts: Dict) -> int:
        """Calculate overall risk score (0-100)"""
        score = (
            severity_counts["critical"] * 25 +
            severity_counts["high"] * 15 +
            severity_counts["medium"] * 8 +
            severity_counts["low"] * 3
        )
        return min(score, 100)
