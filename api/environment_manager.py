"""
Environment Manager Module - Manage secrets and environment variables
"""
import os
from typing import Dict, List

class EnvironmentManager:
    """Manage environment variables and secrets"""
    
    def __init__(self):
        pass
    
    def list_env_vars(self, show_values: bool = False) -> Dict:
        """List environment variables"""
        try:
            env_vars = {}
            
            for key, value in os.environ.items():
                if show_values:
                    env_vars[key] = value
                else:
                    if any(secret_key in key.upper() for secret_key in ['KEY', 'SECRET', 'TOKEN', 'PASSWORD']):
                        env_vars[key] = "***HIDDEN***"
                    else:
                        env_vars[key] = value
            
            return {
                "success": True,
                "variables": env_vars,
                "total": len(env_vars)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_secret(self, secret_name: str) -> Dict:
        """Check if a secret exists"""
        exists = secret_name in os.environ
        return {
            "success": True,
            "secret": secret_name,
            "exists": exists,
            "value": "***HIDDEN***" if exists else None
        }
    
    def get_required_secrets(self, service: str) -> Dict:
        """Get required secrets for common services"""
        requirements = {
            "openai": ["OPENAI_API_KEY"],
            "stripe": ["STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY"],
            "twilio": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"],
            "sendgrid": ["SENDGRID_API_KEY"],
            "aws": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
            "google": ["GOOGLE_API_KEY"],
            "github": ["GITHUB_TOKEN"],
            "postgres": ["DATABASE_URL"]
        }
        
        service_lower = service.lower()
        if service_lower not in requirements:
            return {
                "success": False,
                "error": f"Unknown service: {service}. Available: {', '.join(requirements.keys())}"
            }
        
        required = requirements[service_lower]
        status = {}
        
        for secret in required:
            status[secret] = secret in os.environ
        
        all_present = all(status.values())
        
        return {
            "success": True,
            "service": service,
            "required_secrets": required,
            "status": status,
            "all_present": all_present,
            "missing": [k for k, v in status.items() if not v]
        }
