"""High-performance caching system for SuperAgent."""

import asyncio
import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
import redis.asyncio as aioredis
from diskcache import Cache
import structlog

logger = structlog.get_logger()


class CacheManager:
    """Manages both Redis and disk-based caching for optimal performance."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 cache_dir: str = ".cache", ttl: int = 3600):
        """Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL
            cache_dir: Directory for disk cache
            ttl: Time-to-live for cache entries in seconds
        """
        self.redis_url = redis_url
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.redis_client: Optional[aioredis.Redis] = None
        self.disk_cache = Cache(cache_dir)
        
    async def connect(self):
        """Connect to Redis (async)."""
        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Redis unavailable, using disk cache only: {e}")
            self.redis_client = None
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        # Try Redis first (faster)
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    logger.debug(f"Cache hit (Redis): {key[:8]}...")
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        # Fallback to disk cache
        value = self.disk_cache.get(key)
        if value:
            logger.debug(f"Cache hit (disk): {key[:8]}...")
        return value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live (uses default if not specified)
        """
        ttl = ttl or self.ttl
        
        # Store in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    key, 
                    ttl, 
                    json.dumps(value)
                )
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        # Store in disk cache
        self.disk_cache.set(key, value, expire=ttl)
        logger.debug(f"Cache set: {key[:8]}...")
    
    async def invalidate(self, pattern: str = "*"):
        """Invalidate cache entries matching pattern.
        
        Args:
            pattern: Key pattern to invalidate
        """
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis invalidate error: {e}")
        
        self.disk_cache.clear()
        logger.info(f"Cache invalidated: {pattern}")


def cached(ttl: int = 3600):
    """Decorator for caching function results.
    
    Args:
        ttl: Time-to-live for cached result
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            if not hasattr(self, 'cache'):
                return await func(self, *args, **kwargs)
            
            cache_key = f"{func.__name__}:{self.cache._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(self, *args, **kwargs)
            await self.cache.set(cache_key, result, ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator





