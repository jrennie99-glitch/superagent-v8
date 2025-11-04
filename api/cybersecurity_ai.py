"""
Cybersecurity AI Agent - Works with Supervisor and Supreme Agent
Adds AI-powered security verification layer with Lakera Guard
"""
import os
import bleach
import re
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, ValidationError
from api.structured_logging import logger

class SecurityInput(BaseModel):
    """Validated security input"""
    code: str
    prompt: Optional[str] = None
    language: str = "python"

class CybersecurityAgent:
    """
    AI-powered cybersecurity agent that works with supervisors and supreme agent.
    
    Features:
    - AI prompt injection detection (Lakera Guard)
    - Code sanitization and XSS prevention
    - Input validation
    - Security pattern detection
    - Integration with supervisor system
    """
    
    def __init__(self):
        """Initialize cybersecurity AI agent"""
        self.enabled = True
        self.lakera_enabled = False
        
        # Try to initialize Lakera Guard
        try:
            lakera_key = os.getenv("LAKERA_API_KEY")
            if lakera_key:
                from lakera_guard import LakeraGuard
                self.lakera = LakeraGuard(api_key=lakera_key)
                self.lakera_enabled = True
                logger.info("🛡️ Lakera Guard AI enabled for advanced threat detection")
            else:
                logger.info("🛡️ Cybersecurity AI initialized (Lakera Guard disabled - set LAKERA_API_KEY to enable)")
        except ImportError:
            logger.warning("Lakera Guard not installed. Run: pip install lakera-guard")
        except Exception as e:
            logger.warning(f"Lakera Guard init failed: {e}")
        
        # Advanced security patterns
        self.threat_patterns = {
            "prompt_injection": [
                r"ignore\s+(previous|above|all)\s+instructions",
                r"you\s+are\s+now",
                r"forget\s+(everything|all|previous)",
                r"new\s+instructions?:",
                r"system\s+prompt",
                r"reveal\s+your\s+(instructions|prompt|rules)",
            ],
            "code_injection": [
                r"__import__\(['\"]os['\"]\)",
                r"exec\s*\(",
                r"eval\s*\(",
                r"compile\s*\(",
                r"subprocess\.",
                r"os\.system",
            ],
            "data_exfiltration": [
                r"requests?\.(get|post)\(",
                r"urllib\.",
                r"socket\.",
                r"ftp\.",
                r"smtp\.",
            ],
            "malicious_imports": [
                r"import\s+(os|subprocess|socket|urllib|requests|sys)",
                r"from\s+(os|subprocess|socket|urllib|requests|sys)\s+import",
            ]
        }
    
    async def guard_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        AI-powered prompt injection detection
        
        Args:
            prompt: User prompt to validate
            
        Returns:
            Security analysis with threat detection
        """
        threats = []
        
        # Pattern-based detection (fast)
        for threat_type, patterns in self.threat_patterns.items():
            if threat_type == "prompt_injection":
                for pattern in patterns:
                    if re.search(pattern, prompt, re.IGNORECASE):
                        threats.append({
                            "type": "prompt_injection",
                            "severity": "critical",
                            "pattern": pattern,
                            "description": "Possible prompt injection attack detected"
                        })
        
        # AI-powered detection (if enabled)
        lakera_result = None
        if self.lakera_enabled:
            try:
                lakera_result = await self._lakera_guard_check(prompt)
                if not lakera_result.get("safe", True):
                    threats.append({
                        "type": "ai_detected_threat",
                        "severity": "high",
                        "description": lakera_result.get("reason", "AI detected potential threat"),
                        "confidence": lakera_result.get("confidence", 0)
                    })
            except Exception as e:
                logger.warning(f"Lakera Guard check failed: {e}")
        
        # Sanitize prompt
        sanitized = bleach.clean(prompt, tags=[], attributes={}, strip=True)
        
        return {
            "safe": len(threats) == 0,
            "original_prompt": prompt,
            "sanitized_prompt": sanitized,
            "threats": threats,
            "lakera_checked": self.lakera_enabled,
            "lakera_result": lakera_result
        }
    
    async def verify_code_security(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Comprehensive security verification for code
        
        Args:
            code: Code to verify
            language: Programming language
            
        Returns:
            Security analysis with recommendations
        """
        issues = []
        risk_score = 0
        
        # Check for malicious patterns
        for threat_type, patterns in self.threat_patterns.items():
            if threat_type in ["code_injection", "data_exfiltration", "malicious_imports"]:
                for pattern in patterns:
                    matches = list(re.finditer(pattern, code, re.IGNORECASE))
                    for match in matches:
                        line_number = code[:match.start()].count('\n') + 1
                        severity = self._get_threat_severity(threat_type)
                        
                        issues.append({
                            "type": threat_type,
                            "severity": severity,
                            "line": line_number,
                            "code_snippet": match.group(),
                            "description": self._get_threat_description(threat_type),
                            "fix_suggestion": self._get_fix_suggestion(threat_type)
                        })
                        
                        # Calculate risk
                        risk_score += {"critical": 10, "high": 7, "medium": 4, "low": 2}.get(severity, 0)
        
        # Sanitize code (remove dangerous constructs if configured)
        sanitized_code = code
        
        return {
            "safe": len(issues) == 0,
            "code": code,
            "sanitized_code": sanitized_code,
            "issues": issues,
            "total_issues": len(issues),
            "risk_score": min(risk_score, 100),
            "risk_level": self._calculate_risk_level(risk_score),
            "recommendation": self._get_security_recommendation(issues)
        }
    
    async def supervisor_security_check(self, 
                                       code: str, 
                                       supervisor_results: List[Dict],
                                       description: str) -> Dict[str, Any]:
        """
        Security verification that integrates with supervisor results
        
        This runs BEFORE the Supreme Agent to add security layer
        
        Args:
            code: Code being verified
            supervisor_results: Results from 2 supervisors
            description: What the code does
            
        Returns:
            Combined security + supervisor analysis
        """
        logger.info("🛡️ Cybersecurity AI analyzing code...")
        
        # Run security scan
        security_result = await self.verify_code_security(code)
        
        # Check if supervisors passed
        supervisors_approved = sum(1 for r in supervisor_results if r.get("approved", False))
        
        # Security verdict
        security_approved = security_result["safe"] and security_result["risk_score"] < 30
        
        # Critical security issues override supervisor approval
        critical_issues = [i for i in security_result["issues"] if i["severity"] == "critical"]
        if critical_issues:
            security_approved = False
            logger.warning(f"🚨 {len(critical_issues)} CRITICAL security issues found!")
        
        return {
            "security_approved": security_approved,
            "supervisors_approved": supervisors_approved >= 2,
            "security_analysis": security_result,
            "critical_security_issues": critical_issues,
            "recommendation": (
                "APPROVED - Security scan passed" if security_approved
                else f"REJECTED - Security risks detected (score: {security_result['risk_score']})"
            ),
            "should_proceed_to_supreme": security_approved and supervisors_approved >= 2
        }
    
    async def _lakera_guard_check(self, text: str) -> Dict[str, Any]:
        """Run Lakera Guard AI check"""
        if not self.lakera_enabled:
            return {"safe": True, "reason": "Lakera Guard not enabled"}
        
        try:
            result = self.lakera.check(text)
            return {
                "safe": result.get("is_safe", True),
                "reason": result.get("reason", ""),
                "confidence": result.get("confidence", 0),
                "categories": result.get("flagged_categories", [])
            }
        except Exception as e:
            logger.error(f"Lakera Guard error: {e}")
            return {"safe": True, "error": str(e)}
    
    def _get_threat_severity(self, threat_type: str) -> str:
        """Get severity level for threat type"""
        severity_map = {
            "code_injection": "critical",
            "data_exfiltration": "high",
            "malicious_imports": "medium",
            "prompt_injection": "critical"
        }
        return severity_map.get(threat_type, "medium")
    
    def _get_threat_description(self, threat_type: str) -> str:
        """Get description for threat"""
        descriptions = {
            "code_injection": "Potential code injection vulnerability detected",
            "data_exfiltration": "Possible data exfiltration attempt",
            "malicious_imports": "Suspicious import detected",
            "prompt_injection": "Prompt injection attack detected"
        }
        return descriptions.get(threat_type, "Security issue detected")
    
    def _get_fix_suggestion(self, threat_type: str) -> str:
        """Get fix suggestion"""
        fixes = {
            "code_injection": "Avoid exec(), eval(), compile(). Use safer alternatives.",
            "data_exfiltration": "Review network calls. Ensure they're necessary and secure.",
            "malicious_imports": "Verify imports are required. Use safer alternatives if possible.",
            "prompt_injection": "Sanitize and validate all user inputs."
        }
        return fixes.get(threat_type, "Review and fix the security issue")
    
    def _calculate_risk_level(self, risk_score: int) -> str:
        """Calculate risk level from score"""
        if risk_score >= 50:
            return "CRITICAL"
        elif risk_score >= 30:
            return "HIGH"
        elif risk_score >= 15:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_security_recommendation(self, issues: List[Dict]) -> str:
        """Get overall security recommendation"""
        if not issues:
            return "✅ Code passed all security checks"
        
        critical = len([i for i in issues if i["severity"] == "critical"])
        high = len([i for i in issues if i["severity"] == "high"])
        
        if critical > 0:
            return f"🚨 BLOCK DEPLOYMENT - {critical} critical security issues found"
        elif high > 0:
            return f"⚠️ REVIEW REQUIRED - {high} high-severity security issues found"
        else:
            return "⚠️ Minor security issues detected - review recommended"

# Global instance
cybersecurity_agent = CybersecurityAgent()
