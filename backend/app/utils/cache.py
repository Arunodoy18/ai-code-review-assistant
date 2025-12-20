"""
Simple in-memory cache utility for API responses

This provides basic caching without requiring Redis for development.
For production, consider using Redis or Memcached.
"""

from functools import wraps
from typing import Any, Callable, Optional
from datetime import datetime, timedelta
import json
import hashlib


class SimpleCache:
    """Thread-safe in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Create a cache key from function arguments"""
        key_parts = [prefix]
        if args:
            key_parts.extend(str(arg) for arg in args)
        if kwargs:
            key_parts.append(json.dumps(kwargs, sort_keys=True))
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str, ttl: int = 300) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            timestamp = self._timestamps.get(key)
            if timestamp and datetime.utcnow() - timestamp < timedelta(seconds=ttl):
                return self._cache[key]
            else:
                # Expired, remove from cache
                self._cache.pop(key, None)
                self._timestamps.pop(key, None)
        return None
    
    def set(self, key: str, value: Any):
        """Set value in cache with current timestamp"""
        self._cache[key] = value
        self._timestamps[key] = datetime.utcnow()
    
    def delete(self, key: str):
        """Delete value from cache"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        self._timestamps.clear()
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys containing pattern"""
        keys_to_delete = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_delete:
            self.delete(key)


# Global cache instance
cache = SimpleCache()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key (default: function name)
    
    Example:
        @cached(ttl=60, key_prefix="project")
        def get_project(project_id: int):
            return db.query(Project).get(project_id)
    """
    def decorator(func: Callable) -> Callable:
        prefix = key_prefix or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = cache._make_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key, ttl=ttl)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_prefix: str = "", pattern: str = ""):
    """
    Invalidate cache entries
    
    Args:
        key_prefix: Specific key prefix to invalidate
        pattern: Pattern to match for invalidation
    """
    if pattern:
        cache.invalidate_pattern(pattern)
    elif key_prefix:
        cache.invalidate_pattern(key_prefix)
    else:
        cache.clear()
