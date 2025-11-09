"""
Rate Limit Failover System
Automatically switches between GROQ and Gemini when rate limits are hit
"""
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
import json

class RateLimitTracker:
    def __init__(self):
        self.rate_limits_file = "/tmp/rate_limits.json"
        self.load_state()
    
    def load_state(self):
        """Load rate limit state from file"""
        try:
            if os.path.exists(self.rate_limits_file):
                with open(self.rate_limits_file, 'r') as f:
                    data = json.load(f)
                    self.groq_reset_time = data.get('groq_reset_time')
                    self.gemini_reset_time = data.get('gemini_reset_time')
            else:
                self.groq_reset_time = None
                self.gemini_reset_time = None
        except Exception:
            self.groq_reset_time = None
            self.gemini_reset_time = None
    
    def save_state(self):
        """Save rate limit state to file"""
        try:
            with open(self.rate_limits_file, 'w') as f:
                json.dump({
                    'groq_reset_time': self.groq_reset_time,
                    'gemini_reset_time': self.gemini_reset_time
                }, f)
        except Exception:
            pass
    
    def mark_rate_limited(self, provider: str, reset_seconds: Optional[int] = None):
        """Mark a provider as rate limited"""
        if reset_seconds:
            reset_time = (datetime.now() + timedelta(seconds=reset_seconds)).timestamp()
        else:
            # Default: GROQ resets at midnight Pacific, Gemini resets daily
            reset_time = (datetime.now() + timedelta(hours=1)).timestamp()
        
        if provider == "groq":
            self.groq_reset_time = reset_time
            print(f"⚠️ GROQ rate limited. Reset at: {datetime.fromtimestamp(reset_time)}")
        elif provider == "gemini":
            self.gemini_reset_time = reset_time
            print(f"⚠️ Gemini rate limited. Reset at: {datetime.fromtimestamp(reset_time)}")
        
        self.save_state()
    
    def is_available(self, provider: str) -> bool:
        """Check if a provider is available (not rate limited)"""
        now = datetime.now().timestamp()
        
        if provider == "groq":
            if self.groq_reset_time and now < self.groq_reset_time:
                return False
            elif self.groq_reset_time and now >= self.groq_reset_time:
                # Reset time passed, clear the limit
                self.groq_reset_time = None
                self.save_state()
            return True
        
        elif provider == "gemini":
            if self.gemini_reset_time and now < self.gemini_reset_time:
                return False
            elif self.gemini_reset_time and now >= self.gemini_reset_time:
                # Reset time passed, clear the limit
                self.gemini_reset_time = None
                self.save_state()
            return True
        
        return True
    
    def get_available_provider(self) -> str:
        """Get the best available provider based on rate limits"""
        # Priority 1: GROQ (if available and key set)
        if os.getenv("USER_GROQ_API_KEY") and self.is_available("groq"):
            return "groq"
        
        # Priority 2: Gemini (if available and key set)
        if os.getenv("USER_GEMINI_API_KEY") and self.is_available("gemini"):
            return "gemini"
        
        # Priority 3: System Gemini key
        if os.getenv("GEMINI_API_KEY") and self.is_available("gemini"):
            return "gemini"
        
        # Fallback: Return GROQ even if rate limited (will fail with helpful error)
        return "groq"
    
    def get_status(self) -> Dict:
        """Get current status of all providers"""
        now = datetime.now().timestamp()
        
        groq_available = self.is_available("groq")
        gemini_available = self.is_available("gemini")
        
        status = {
            "groq": {
                "available": groq_available,
                "has_key": bool(os.getenv("USER_GROQ_API_KEY")),
                "reset_time": datetime.fromtimestamp(self.groq_reset_time).isoformat() if self.groq_reset_time else None,
                "seconds_until_reset": int(self.groq_reset_time - now) if self.groq_reset_time and self.groq_reset_time > now else 0
            },
            "gemini": {
                "available": gemini_available,
                "has_key": bool(os.getenv("USER_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")),
                "reset_time": datetime.fromtimestamp(self.gemini_reset_time).isoformat() if self.gemini_reset_time else None,
                "seconds_until_reset": int(self.gemini_reset_time - now) if self.gemini_reset_time and self.gemini_reset_time > now else 0
            },
            "recommended_provider": self.get_available_provider()
        }
        
        return status

# Global instance
rate_limit_tracker = RateLimitTracker()

def get_rate_limit_tracker():
    """Get the global rate limit tracker instance"""
    return rate_limit_tracker
