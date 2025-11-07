"""
Health Check Module
Provides system health and configuration status
"""
import os
from typing import Dict, List

class HealthCheck:
    """Check system health and configuration"""
    
    def check_api_keys(self) -> Dict[str, bool]:
        """Check which API keys are configured"""
        return {
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "groq": bool(os.getenv("GROQ_API_KEY")),
        }
    
    def check_optional_services(self) -> Dict[str, bool]:
        """Check optional service configuration"""
        return {
            "redis": bool(os.getenv("REDIS_HOST")),
            "database": bool(os.getenv("DATABASE_URL")),
            "github": bool(os.getenv("GITHUB_TOKEN")),
            "lakera": bool(os.getenv("LAKERA_API_KEY")),
        }
    
    def get_missing_requirements(self) -> List[str]:
        """Get list of missing required configurations"""
        missing = []
        api_keys = self.check_api_keys()
        
        # At least one AI provider is required
        if not any([api_keys["gemini"], api_keys["anthropic"], api_keys["openai"], api_keys["groq"]]):
            missing.append("At least one AI API key required (GEMINI_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY)")
        
        return missing
    
    def get_setup_instructions(self) -> Dict[str, str]:
        """Get setup instructions for missing configurations"""
        instructions = {}
        api_keys = self.check_api_keys()
        
        if not api_keys["gemini"]:
            instructions["gemini"] = {
                "name": "Google Gemini API Key",
                "env_var": "GEMINI_API_KEY",
                "url": "https://makersuite.google.com/app/apikey",
                "description": "Required for app generation. Free tier available.",
                "priority": "HIGH"
            }
        
        if not api_keys["anthropic"]:
            instructions["anthropic"] = {
                "name": "Anthropic Claude API Key",
                "env_var": "ANTHROPIC_API_KEY",
                "url": "https://console.anthropic.com/",
                "description": "Alternative AI provider. Requires paid account.",
                "priority": "MEDIUM"
            }
        
        if not api_keys["openai"]:
            instructions["openai"] = {
                "name": "OpenAI API Key",
                "env_var": "OPENAI_API_KEY",
                "url": "https://platform.openai.com/api-keys",
                "description": "Alternative AI provider. Works with gpt-4.1-mini model.",
                "priority": "MEDIUM"
            }
        
        if not api_keys["groq"]:
            instructions["groq"] = {
                "name": "Groq API Key",
                "env_var": "GROQ_API_KEY",
                "url": "https://console.groq.com/keys",
                "description": "Fast AI provider with free tier. Uses Llama models.",
                "priority": "MEDIUM"
            }
        
        return instructions
    
    def get_health_status(self) -> Dict:
        """Get complete health status"""
        api_keys = self.check_api_keys()
        optional = self.check_optional_services()
        missing = self.get_missing_requirements()
        
        # Determine overall status
        if missing:
            status = "unhealthy"
            message = "Missing required configuration"
        else:
            status = "healthy"
            message = "All required services configured"
        
        return {
            "status": status,
            "message": message,
            "api_keys": api_keys,
            "optional_services": optional,
            "missing_requirements": missing,
            "setup_instructions": self.get_setup_instructions() if missing else {},
            "ready_to_build": not missing
        }

health_check = HealthCheck()
