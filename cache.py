"""Caching implementation for Reddit MCP Server."""

import time
import asyncio
import hashlib
import json
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    """Single cache entry."""
    key: str
    value: Any
    expires_at: float
    created_at: float = field(default_factory=time.time)
    hit_count: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() > self.expires_at
    
    def increment_hits(self) -> None:
        """Increment hit counter."""
        self.hit_count += 1


class Cache:
    """LRU cache implementation with TTL support."""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: list[str] = []
        self._lock = asyncio.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats["misses"] += 1
                return None
            
            if entry.is_expired:
                # Remove expired entry
                self._remove_entry(key)
                self._stats["misses"] += 1
                return None
            
            # Update access order (LRU)
            self._access_order.remove(key)
            self._access_order.append(key)
            
            entry.increment_hits()
            self._stats["hits"] += 1
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        async with self._lock:
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            
            # Remove existing entry if present
            if key in self._cache:
                self._access_order.remove(key)
            
            # Add new entry
            self._cache[key] = CacheEntry(
                key=key,
                value=value,
                expires_at=expires_at
            )
            self._access_order.append(key)
            
            # Evict oldest entries if cache is full
            while len(self._cache) > self.max_size:
                self._evict_oldest()
    
    async def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        async with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    async def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            
            for key in expired_keys:
                self._remove_entry(key)
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "hit_rate": hit_rate
        }
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry from cache (internal, no lock)."""
        if key in self._cache:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
    
    def _evict_oldest(self) -> None:
        """Evict oldest entry (internal, no lock)."""
        if self._access_order:
            oldest_key = self._access_order[0]
            self._remove_entry(oldest_key)
            self._stats["evictions"] += 1


class CacheDecorator:
    """Decorator for caching function results."""
    
    def __init__(self, cache: Cache, ttl: Optional[int] = None, 
                 key_prefix: str = "", exclude_args: Optional[list] = None):
        self.cache = cache
        self.ttl = ttl
        self.key_prefix = key_prefix
        self.exclude_args = exclude_args or []
    
    def __call__(self, func):
        """Decorator implementation."""
        async def wrapper(*args, **kwargs):
            # Build cache key
            cache_args = []
            for i, arg in enumerate(args):
                if i not in self.exclude_args:
                    cache_args.append(arg)
            
            cache_kwargs = {
                k: v for k, v in kwargs.items() 
                if k not in self.exclude_args
            }
            
            cache_key = self.key_prefix + Cache.generate_key(*cache_args, **cache_kwargs)
            
            # Try to get from cache
            cached_value = await self.cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await self.cache.set(cache_key, result, ttl=self.ttl)
            
            return result
        
        return wrapper