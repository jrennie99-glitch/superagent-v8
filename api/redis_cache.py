"""
Redis Caching Module
Optional Redis caching support alongside existing LRU cache
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class RedisCache:
    """Optional Redis caching layer"""
    
    def __init__(self):
        self.enabled = False
        self.redis_client = None
        self.fallback_cache = {}  # In-memory fallback
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        
        # Try to initialize Redis if available
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection if available"""
        try:
            import redis
            
            # Check for Redis URL in environment
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                self.enabled = True
                print("✅ Redis cache enabled")
            else:
                print("ℹ️ Redis URL not found, using fallback cache")
        except ImportError:
            print("ℹ️ Redis library not installed, using fallback cache")
        except Exception as e:
            print(f"ℹ️ Redis connection failed: {e}, using fallback cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._hash_key(key)
        
        try:
            if self.enabled and self.redis_client:
                value = self.redis_client.get(cache_key)
                if value:
                    self.stats["hits"] += 1
                    return json.loads(value)
            else:
                # Use fallback cache
                if cache_key in self.fallback_cache:
                    entry = self.fallback_cache[cache_key]
                    if not self._is_expired(entry):
                        self.stats["hits"] += 1
                        return entry["value"]
            
            self.stats["misses"] += 1
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            self.stats["misses"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (seconds)"""
        cache_key = self._hash_key(key)
        
        try:
            if self.enabled and self.redis_client:
                self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(value)
                )
            else:
                # Use fallback cache
                self.fallback_cache[cache_key] = {
                    "value": value,
                    "expires": datetime.utcnow() + timedelta(seconds=ttl)
                }
            
            self.stats["sets"] += 1
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        cache_key = self._hash_key(key)
        
        try:
            if self.enabled and self.redis_client:
                self.redis_client.delete(cache_key)
            else:
                self.fallback_cache.pop(cache_key, None)
            
            self.stats["deletes"] += 1
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            if self.enabled and self.redis_client:
                self.redis_client.flushdb()
            else:
                self.fallback_cache.clear()
            
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    def _hash_key(self, key: str) -> str:
        """Hash key for consistent storage"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if fallback cache entry is expired"""
        return datetime.utcnow() > entry["expires"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "enabled": self.enabled,
            "backend": "redis" if self.enabled else "memory",
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "deletes": self.stats["deletes"],
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests,
            "fallback_size": len(self.fallback_cache)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check cache health"""
        try:
            if self.enabled and self.redis_client:
                self.redis_client.ping()
                return {
                    "healthy": True,
                    "backend": "redis",
                    "latency_ms": self._measure_latency()
                }
            else:
                return {
                    "healthy": True,
                    "backend": "memory",
                    "latency_ms": 0
                }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    def _measure_latency(self) -> float:
        """Measure cache latency in milliseconds"""
        if not self.enabled or not self.redis_client:
            return 0.0
        
        try:
            start = datetime.utcnow()
            self.redis_client.ping()
            end = datetime.utcnow()
            return (end - start).total_seconds() * 1000
        except:
            return -1.0

# Global instance
redis_cache = RedisCache()
