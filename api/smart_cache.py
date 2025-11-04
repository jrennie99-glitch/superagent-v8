"""
Smart Caching - LRU cache for API responses
"""
from functools import lru_cache
from typing import Optional
import hashlib
import json


class SmartCache:
    """In-memory LRU cache for code generation responses"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []
    
    def _generate_key(self, instruction: str, language: str) -> str:
        """Generate cache key from instruction and language"""
        content = f"{instruction}:{language}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, instruction: str, language: str) -> Optional[str]:
        """Get cached response if available"""
        key = self._generate_key(instruction, language)
        
        if key in self.cache:
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        
        return None
    
    def set(self, instruction: str, language: str, response: str):
        """Cache a response"""
        key = self._generate_key(instruction, language)
        
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = response
        
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def clear(self):
        """Clear all cached responses"""
        self.cache.clear()
        self.access_order.clear()
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "utilization": f"{(len(self.cache) / self.max_size) * 100:.1f}%"
        }


cache_instance = SmartCache(max_size=100)
