"""Unit tests for cache implementation."""

import pytest
import asyncio
import time
import json
from unittest.mock import AsyncMock, MagicMock

from cache import Cache, CacheEntry, CacheDecorator


class TestCacheEntry:
    """Test CacheEntry class."""
    
    def test_cache_entry_creation(self):
        """Test creating a cache entry."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            expires_at=time.time() + 300
        )
        
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.hit_count == 0
        assert not entry.is_expired
    
    def test_cache_entry_expiration(self):
        """Test cache entry expiration."""
        # Create an already expired entry
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            expires_at=time.time() - 1  # Expired 1 second ago
        )
        
        assert entry.is_expired
    
    def test_increment_hits(self):
        """Test hit counter increment."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            expires_at=time.time() + 300
        )
        
        assert entry.hit_count == 0
        entry.increment_hits()
        assert entry.hit_count == 1
        entry.increment_hits()
        assert entry.hit_count == 2


class TestCache:
    """Test Cache class."""
    
    @pytest.fixture
    def cache(self):
        """Create a cache instance for testing."""
        return Cache(max_size=3, default_ttl=60)
    
    def test_generate_key(self):
        """Test cache key generation."""
        # Test with various arguments
        key1 = Cache.generate_key("func", 1, 2, 3)
        key2 = Cache.generate_key("func", 1, 2, 3)
        key3 = Cache.generate_key("func", 3, 2, 1)
        
        assert key1 == key2  # Same args should produce same key
        assert key1 != key3  # Different args should produce different key
        
        # Test with kwargs
        key4 = Cache.generate_key("func", a=1, b=2)
        key5 = Cache.generate_key("func", b=2, a=1)
        
        assert key4 == key5  # Kwargs order shouldn't matter
    
    @pytest.mark.asyncio
    async def test_get_set(self, cache):
        """Test basic get and set operations."""
        # Set a value
        await cache.set("key1", "value1")
        
        # Get the value
        result = await cache.get("key1")
        assert result == "value1"
        
        # Get non-existent key
        result = await cache.get("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache):
        """Test TTL expiration."""
        # Set with short TTL
        await cache.set("key1", "value1", ttl=1)
        
        # Should exist immediately
        assert await cache.get("key1") == "value1"
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be expired
        assert await cache.get("key1") is None
    
    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache):
        """Test LRU eviction when cache is full."""
        # Fill cache to capacity
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")
        
        # Access key1 to make it recently used
        await cache.get("key1")
        
        # Add new item, should evict key2 (least recently used)
        await cache.set("key4", "value4")
        
        assert await cache.get("key1") == "value1"  # Still exists
        assert await cache.get("key2") is None      # Evicted
        assert await cache.get("key3") == "value3"  # Still exists
        assert await cache.get("key4") == "value4"  # New item
    
    @pytest.mark.asyncio
    async def test_delete(self, cache):
        """Test deleting cache entries."""
        await cache.set("key1", "value1")
        
        # Delete existing key
        assert await cache.delete("key1") is True
        assert await cache.get("key1") is None
        
        # Delete non-existent key
        assert await cache.delete("nonexistent") is False
    
    @pytest.mark.asyncio
    async def test_clear(self, cache):
        """Test clearing all cache entries."""
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        
        await cache.clear()
        
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
    
    @pytest.mark.asyncio
    async def test_cleanup_expired(self, cache):
        """Test cleanup of expired entries."""
        # Set entries with different TTLs
        await cache.set("key1", "value1", ttl=1)
        await cache.set("key2", "value2", ttl=1000)
        await cache.set("key3", "value3", ttl=1)
        
        # Wait for some to expire
        await asyncio.sleep(1.1)
        
        # Cleanup expired
        expired_count = await cache.cleanup_expired()
        
        assert expired_count == 2
        assert await cache.get("key1") is None
        assert await cache.get("key2") == "value2"
        assert await cache.get("key3") is None
    
    @pytest.mark.asyncio
    async def test_stats(self, cache):
        """Test cache statistics."""
        # Initial stats
        stats = cache.get_stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["evictions"] == 0
        
        # Add items and access them
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        
        # Hits
        await cache.get("key1")
        await cache.get("key1")
        
        # Misses
        await cache.get("nonexistent")
        
        stats = cache.get_stats()
        assert stats["size"] == 2
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 2/3
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self, cache):
        """Test concurrent cache access."""
        async def writer(key, value):
            await cache.set(key, value)
        
        async def reader(key):
            return await cache.get(key)
        
        # Run concurrent operations
        tasks = []
        for i in range(10):
            tasks.append(writer(f"key{i}", f"value{i}"))
            tasks.append(reader(f"key{i}"))
        
        await asyncio.gather(*tasks)
        
        # Verify some entries exist (cache size is 3, so only last 3 should remain)
        remaining = 0
        for i in range(10):
            if await cache.get(f"key{i}") is not None:
                remaining += 1
        
        assert remaining <= 3  # At most 3 due to cache size


class TestCacheDecorator:
    """Test CacheDecorator functionality."""
    
    @pytest.fixture
    def cache(self):
        """Create a cache instance for testing."""
        return Cache(max_size=10, default_ttl=60)
    
    @pytest.mark.asyncio
    async def test_decorator_basic(self, cache):
        """Test basic decorator functionality."""
        call_count = 0
        
        @CacheDecorator(cache, ttl=60)
        async def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate expensive operation
            return x + y
        
        # First call - should execute function
        result1 = await expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call with same args - should use cache
        result2 = await expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Function not called again
        
        # Call with different args - should execute function
        result3 = await expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_decorator_with_kwargs(self, cache):
        """Test decorator with keyword arguments."""
        @CacheDecorator(cache)
        async def function_with_kwargs(a, b=10, c=20):
            return a + b + c
        
        # Test various combinations
        result1 = await function_with_kwargs(1)
        assert result1 == 31
        
        result2 = await function_with_kwargs(1, b=10)  # Same as default
        assert result2 == 31
        
        result3 = await function_with_kwargs(1, b=5)
        assert result3 == 26
    
    @pytest.mark.asyncio
    async def test_decorator_exclude_args(self, cache):
        """Test excluding certain arguments from cache key."""
        call_count = 0
        
        @CacheDecorator(cache, exclude_args=[1])  # Exclude second positional arg
        async def function_with_timestamp(value, timestamp):
            nonlocal call_count
            call_count += 1
            return f"{value}_{timestamp}"
        
        # Calls with different timestamps but same value should use cache
        result1 = await function_with_timestamp("test", 12345)
        result2 = await function_with_timestamp("test", 67890)
        
        assert call_count == 1  # Only called once
        assert result1 == result2  # Same cached result
    
    @pytest.mark.asyncio
    async def test_decorator_key_prefix(self, cache):
        """Test cache key prefix."""
        @CacheDecorator(cache, key_prefix="prefix:")
        async def prefixed_function(x):
            return x * 2
        
        # Call function
        result = await prefixed_function(5)
        assert result == 10
        
        # Verify key in cache has prefix
        # This is implementation-specific test
        cache_keys = list(cache._cache.keys())
        assert any(key.startswith("prefix:") for key in cache_keys)
    
    @pytest.mark.asyncio
    async def test_decorator_with_exception(self, cache):
        """Test that exceptions are not cached."""
        call_count = 0
        
        @CacheDecorator(cache)
        async def failing_function(should_fail):
            nonlocal call_count
            call_count += 1
            if should_fail:
                raise ValueError("Test error")
            return "success"
        
        # First call fails
        with pytest.raises(ValueError):
            await failing_function(True)
        assert call_count == 1
        
        # Second call with same args should try again (not cached)
        with pytest.raises(ValueError):
            await failing_function(True)
        assert call_count == 2
        
        # Successful call should be cached
        result1 = await failing_function(False)
        assert result1 == "success"
        assert call_count == 3
        
        result2 = await failing_function(False)
        assert result2 == "success"
        assert call_count == 3  # Used cache