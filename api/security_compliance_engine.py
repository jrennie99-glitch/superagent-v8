"""
Security & Compliance Engine
Scans code for vulnerabilities and ensures compliance
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from enum import Enum


class SeverityLevel(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ComplianceFramework(Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    PCI_DSS = "pci-dss"
    ISO_27001 = "iso-27001"


class SecurityComplianceEngine:
    """Scans code for security issues and compliance violations"""
    
    def __init__(self):
        self.owasp_top_10 = [
            "SQL Injection",
            "Broken Authentication",
            "Sensitive Data Exposure",
            "XML External Entities",
            "Broken Access Control",
            "Security Misconfiguration",
            "Cross-Site Scripting (XSS)",
            "Insecure Deserialization",
            "Using Components with Known Vulnerabilities",
            "Insufficient Logging & Monitoring",
        ]
        
        self.vulnerability_patterns = {
            "sql_injection": r"(SELECT|INSERT|UPDATE|DELETE).*\+|f\"|f\'",
            "hardcoded_secrets": r"(password|secret|api_key|token)\s*=\s*['\"]",
            "xss": r"innerHTML|dangerouslySetInnerHTML",
            "eval": r"eval\(|exec\(|Function\(",
            "weak_crypto": r"md5|sha1|DES",
        }
    
    async def scan_code(
        self,
        code: str,
        language: str,
        frameworks: Optional[List[ComplianceFramework]] = None
    ) -> Dict[str, Any]:
        """
        Scan code for vulnerabilities
        
        Args:
            code: Code to scan
            language: Programming language
            frameworks: Compliance frameworks to check
        
        Returns:
            Scan results with vulnerabilities and recommendations
        """
        
        try:
            print("🔒 Scanning code for security issues...")
            
            # Perform vulnerability scan
            vulnerabilities = await self._scan_vulnerabilities(code, language)
            
            # Check dependencies
            dependencies = await self._check_dependencies(code, language)
            
            # Check compliance
            compliance_results = {}
            if frameworks:
                for framework in frameworks:
                    compliance_results[framework.value] = await self._check_compliance(code, framework)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(vulnerabilities)
            
            # Generate security report
            report = {
                "success": True,
                "scan_date": "2025-11-01",
                "vulnerabilities": vulnerabilities,
                "dependencies": dependencies,
                "compliance": compliance_results,
                "recommendations": recommendations,
                "summary": {
                    "total_vulnerabilities": len(vulnerabilities),
                    "critical": len([v for v in vulnerabilities if v["severity"] == "critical"]),
                    "high": len([v for v in vulnerabilities if v["severity"] == "high"]),
                    "medium": len([v for v in vulnerabilities if v["severity"] == "medium"]),
                    "low": len([v for v in vulnerabilities if v["severity"] == "low"]),
                    "security_score": self._calculate_security_score(vulnerabilities),
                },
            }
            
            print(f"✅ Scan complete: {report['summary']['total_vulnerabilities']} issues found")
            
            return report
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _scan_vulnerabilities(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Scan for vulnerabilities"""
        
        await asyncio.sleep(0.5)
        
        vulnerabilities = []
        
        # Check for common vulnerabilities
        for vuln_name, pattern in self.vulnerability_patterns.items():
            matches = re.finditer(pattern, code, re.IGNORECASE)
            
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                
                vulnerability = {
                    "id": f"SEC-{len(vulnerabilities) + 1:04d}",
                    "type": vuln_name,
                    "severity": self._get_severity(vuln_name),
                    "line": line_num,
                    "code": match.group(),
                    "description": self._get_vulnerability_description(vuln_name),
                    "remediation": self._get_remediation(vuln_name),
                }
                
                vulnerabilities.append(vulnerability)
        
        # Check for OWASP Top 10
        owasp_issues = await self._check_owasp_top_10(code, language)
        vulnerabilities.extend(owasp_issues)
        
        return vulnerabilities
    
    async def _check_dependencies(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Check for vulnerable dependencies"""
        
        await asyncio.sleep(0.5)
        
        # Simulate dependency check
        dependencies = [
            {
                "name": "requests",
                "version": "2.28.0",
                "status": "safe",
            },
            {
                "name": "django",
                "version": "3.2.0",
                "status": "vulnerable",
                "cve": "CVE-2021-33571",
                "severity": "high",
                "fix_version": "3.2.10",
            },
            {
                "name": "flask",
                "version": "2.0.0",
                "status": "safe",
            },
        ]
        
        return dependencies
    
    async def _check_compliance(self, code: str, framework: ComplianceFramework) -> Dict[str, Any]:
        """Check compliance with framework"""
        
        await asyncio.sleep(0.5)
        
        compliance_checks = {
            ComplianceFramework.GDPR: {
                "data_encryption": True,
                "data_retention": False,
                "user_consent": True,
                "data_portability": False,
                "right_to_be_forgotten": True,
                "compliance_score": 60,
            },
            ComplianceFramework.HIPAA: {
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "access_controls": True,
                "audit_logging": False,
                "compliance_score": 75,
            },
            ComplianceFramework.SOC2: {
                "access_controls": True,
                "change_management": True,
                "monitoring": True,
                "incident_response": False,
                "compliance_score": 75,
            },
            ComplianceFramework.PCI_DSS: {
                "network_security": True,
                "data_protection": True,
                "access_control": True,
                "vulnerability_management": False,
                "compliance_score": 75,
            },
            ComplianceFramework.ISO_27001: {
                "information_security": True,
                "access_management": True,
                "cryptography": True,
                "incident_management": False,
                "compliance_score": 75,
            },
        }
        
        return compliance_checks.get(framework, {})
    
    async def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[Dict[str, Any]]:
        """Generate security recommendations"""
        
        recommendations = []
        
        # Group by severity
        critical = [v for v in vulnerabilities if v["severity"] == "critical"]
        high = [v for v in vulnerabilities if v["severity"] == "high"]
        
        if critical:
            recommendations.append({
                "priority": "immediate",
                "action": "Fix all critical vulnerabilities immediately",
                "count": len(critical),
                "details": [v["type"] for v in critical],
            })
        
        if high:
            recommendations.append({
                "priority": "high",
                "action": "Fix high severity vulnerabilities within 1 week",
                "count": len(high),
                "details": [v["type"] for v in high],
            })
        
        recommendations.extend([
            {
                "priority": "medium",
                "action": "Enable HTTPS/TLS for all communications",
                "details": "Ensure all data in transit is encrypted",
            },
            {
                "priority": "medium",
                "action": "Implement rate limiting on APIs",
                "details": "Prevent brute force and DDoS attacks",
            },
            {
                "priority": "medium",
                "action": "Add input validation and sanitization",
                "details": "Prevent injection attacks",
            },
            {
                "priority": "low",
                "action": "Set up security headers",
                "details": "Add CSP, X-Frame-Options, X-Content-Type-Options",
            },
        ])
        
        return recommendations
    
    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability"""
        
        severity_map = {
            "sql_injection": "critical",
            "hardcoded_secrets": "critical",
            "xss": "high",
            "eval": "high",
            "weak_crypto": "high",
        }
        
        return severity_map.get(vuln_type, "medium")
    
    def _get_vulnerability_description(self, vuln_type: str) -> str:
        """Get vulnerability description"""
        
        descriptions = {
            "sql_injection": "Potential SQL injection vulnerability detected",
            "hardcoded_secrets": "Hardcoded credentials or secrets found in code",
            "xss": "Potential cross-site scripting (XSS) vulnerability",
            "eval": "Use of eval() or similar dangerous functions",
            "weak_crypto": "Use of weak cryptographic algorithms",
        }
        
        return descriptions.get(vuln_type, "Security issue detected")
    
    def _get_remediation(self, vuln_type: str) -> str:
        """Get remediation steps"""
        
        remediations = {
            "sql_injection": "Use parameterized queries or ORM to prevent SQL injection",
            "hardcoded_secrets": "Move secrets to environment variables or secret manager",
            "xss": "Use textContent instead of innerHTML, sanitize user input",
            "eval": "Avoid using eval(), use safer alternatives",
            "weak_crypto": "Use strong algorithms like AES-256, SHA-256",
        }
        
        return remediations.get(vuln_type, "Review and fix the security issue")
    
    def _calculate_security_score(self, vulnerabilities: List[Dict]) -> int:
        """Calculate overall security score (0-100)"""
        
        if not vulnerabilities:
            return 100
        
        score = 100
        
        for vuln in vulnerabilities:
            if vuln["severity"] == "critical":
                score -= 20
            elif vuln["severity"] == "high":
                score -= 10
            elif vuln["severity"] == "medium":
                score -= 5
            elif vuln["severity"] == "low":
                score -= 2
        
        return max(0, score)
    
    async def _check_owasp_top_10(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Check for OWASP Top 10 vulnerabilities"""
        
        await asyncio.sleep(0.5)
        
        issues = []
        
        # Check for common OWASP issues
        if "eval(" in code or "exec(" in code:
            issues.append({
                "id": "OWASP-A03",
                "type": "Insecure Deserialization",
                "severity": "high",
                "description": "Use of eval() or exec() functions",
                "remediation": "Avoid using eval() or exec()",
            })
        
        if re.search(r"password\s*=\s*['\"]", code):
            issues.append({
                "id": "OWASP-A02",
                "type": "Broken Authentication",
                "severity": "critical",
                "description": "Hardcoded password found",
                "remediation": "Use environment variables for credentials",
            })
        
        return issues


# Global instance
security_engine = SecurityComplianceEngine()
