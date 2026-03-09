"""
Data caching mechanism for performance optimization.

This module provides a simple in-memory cache with TTL (time-to-live) support
for caching expensive data operations like price generation and weather data.
"""

from typing import Any, Optional, Callable
from datetime import datetime, timedelta
import hashlib
import json
from functools import wraps


class CacheEntry:
    """Represents a single cache entry with expiration."""
    
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return datetime.now() > self.expires_at
    
    def get_age_seconds(self) -> float:
        """Get the age of this cache entry in seconds."""
        return (datetime.now() - self.created_at).total_seconds()


class DataCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize the cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self._cache = {}
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        # Create a stable string representation
        key_data = {
            "args": [str(arg) for arg in args],
            "kwargs": {k: str(v) for k, v in sorted(kwargs.items())}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        # Hash for consistent key length
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value if found and not expired, None otherwise
        """
        if key in self._cache:
            entry = self._cache[key]
            if not entry.is_expired():
                self._hits += 1
                return entry.value
            else:
                # Remove expired entry
                del self._cache[key]
        
        self._misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        ttl = ttl if ttl is not None else self.default_ttl
        self._cache[key] = CacheEntry(value, ttl)
    
    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def cleanup_expired(self):
        """Remove all expired entries from the cache."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "entries": len(self._cache),
            "default_ttl": self.default_ttl,
        }


# Global cache instances for different data types
price_cache = DataCache(default_ttl=300)  # 5 minutes for price data
weather_cache = DataCache(default_ttl=1800)  # 30 minutes for weather data
calendar_cache = DataCache(default_ttl=86400)  # 24 hours for crop calendar (static data)


def cached(cache: DataCache, ttl: Optional[int] = None):
    """
    Decorator to cache function results.
    
    Args:
        cache: DataCache instance to use
        ttl: Optional TTL override in seconds
    
    Example:
        @cached(price_cache, ttl=600)
        def expensive_function(arg1, arg2):
            # ... expensive computation
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{cache._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Compute and cache the result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def get_all_cache_stats() -> dict:
    """Get statistics for all cache instances."""
    return {
        "price_cache": price_cache.get_stats(),
        "weather_cache": weather_cache.get_stats(),
        "calendar_cache": calendar_cache.get_stats(),
    }


def clear_all_caches():
    """Clear all cache instances."""
    price_cache.clear()
    weather_cache.clear()
    calendar_cache.clear()


def cleanup_all_caches():
    """Remove expired entries from all caches."""
    price_cache.cleanup_expired()
    weather_cache.cleanup_expired()
    calendar_cache.cleanup_expired()
