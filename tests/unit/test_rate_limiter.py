"""Unit tests for rate limiter implementation."""

import pytest
import asyncio
import time
from unittest.mock import patch

from rate_limiter import (
    RateLimitBucket, RateLimiter, RedditRateLimitError,
    handle_rate_limit_response
)


class TestRateLimitBucket:
    """Test RateLimitBucket class."""
    
    def test_bucket_creation(self):
        """Test creating a rate limit bucket."""
        bucket = RateLimitBucket(window_seconds=60, max_requests=10)
        
        assert bucket.window_seconds == 60
        assert bucket.max_requests == 10
        assert len(bucket.requests) == 0
    
    def test_can_make_request_empty(self):
        """Test checking if request can be made with empty bucket."""
        bucket = RateLimitBucket(window_seconds=60, max_requests=10)
        
        assert bucket.can_make_request() is True
    
    def test_can_make_request_full(self):
        """Test checking if request can be made with full bucket."""
        bucket = RateLimitBucket(window_seconds=60, max_requests=2)
        
        # Fill the bucket
        bucket.add_request()
        bucket.add_request()
        
        assert bucket.can_make_request() is False
    
    def test_can_make_request_with_old_requests(self):
        """Test that old requests are removed from bucket."""
        bucket = RateLimitBucket(window_seconds=2, max_requests=2)
        
        # Add requests
        with patch('time.time', return_value=100):
            bucket.add_request()
            bucket.add_request()
        
        # Immediately after, bucket is full
        with patch('time.time', return_value=100):
            assert bucket.can_make_request() is False
        
        # After window expires, bucket should allow requests
        with patch('time.time', return_value=103):  # 3 seconds later
            assert bucket.can_make_request() is True
    
    def test_add_request(self):
        """Test adding requests to bucket."""
        bucket = RateLimitBucket(window_seconds=60, max_requests=10)
        
        assert len(bucket.requests) == 0
        
        bucket.add_request()
        assert len(bucket.requests) == 1
        
        bucket.add_request()
        assert len(bucket.requests) == 2
    
    def test_get_retry_after(self):
        """Test calculating retry after time."""
        bucket = RateLimitBucket(window_seconds=60, max_requests=1)
        
        # Empty bucket
        assert bucket.get_retry_after() == 0.0
        
        # Add request at specific time
        with patch('time.time', return_value=100):
            bucket.add_request()
        
        # Check retry after at different times
        with patch('time.time', return_value=100):
            retry_after = bucket.get_retry_after()
            assert retry_after == 60.0  # Full window
        
        with patch('time.time', return_value=130):
            retry_after = bucket.get_retry_after()
            assert retry_after == 30.0  # 30 seconds left
        
        with patch('time.time', return_value=200):
            retry_after = bucket.get_retry_after()
            assert retry_after == 0.0  # Window expired


class TestRateLimiter:
    """Test RateLimiter class."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create a rate limiter for testing."""
        return RateLimiter(calls_per_minute=60, window_seconds=60)
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_allowed(self, rate_limiter):
        """Test checking rate limit when requests are allowed."""
        can_proceed, retry_after = await rate_limiter.check_rate_limit()
        
        assert can_proceed is True
        assert retry_after == 0.0
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_blocked(self):
        """Test checking rate limit when requests are blocked."""
        # Create limiter with very low limit
        rate_limiter = RateLimiter(calls_per_minute=2, window_seconds=60)
        
        # Make allowed requests
        can1, retry1 = await rate_limiter.check_rate_limit()
        can2, retry2 = await rate_limiter.check_rate_limit()
        
        assert can1 is True
        assert can2 is True
        
        # Next request should be blocked
        can3, retry3 = await rate_limiter.check_rate_limit()
        
        assert can3 is False
        assert retry3 > 0  # Should have retry time
    
    @pytest.mark.asyncio
    async def test_multiple_keys(self, rate_limiter):
        """Test rate limiting with multiple keys."""
        # Different keys should have separate buckets
        can1, _ = await rate_limiter.check_rate_limit("key1")
        can2, _ = await rate_limiter.check_rate_limit("key2")
        
        assert can1 is True
        assert can2 is True
        
        # Keys should be independent
        limiter = RateLimiter(calls_per_minute=1, window_seconds=60)
        
        await limiter.check_rate_limit("key1")
        can_key1, _ = await limiter.check_rate_limit("key1")
        can_key2, _ = await limiter.check_rate_limit("key2")
        
        assert can_key1 is False  # key1 is rate limited
        assert can_key2 is True   # key2 is not
    
    @pytest.mark.asyncio
    async def test_wait_if_needed(self):
        """Test waiting when rate limited."""
        # Create limiter with very short window for testing
        rate_limiter = RateLimiter(calls_per_minute=1, window_seconds=1)
        
        # First request should proceed immediately
        start = time.time()
        await rate_limiter.wait_if_needed()
        elapsed = time.time() - start
        assert elapsed < 0.1  # Should be instant
        
        # Second request should wait
        start = time.time()
        await rate_limiter.wait_if_needed()
        elapsed = time.time() - start
        assert elapsed >= 0.9  # Should wait about 1 second
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self, rate_limiter):
        """Test concurrent access to rate limiter."""
        async def make_request(key):
            return await rate_limiter.check_rate_limit(key)
        
        # Make many concurrent requests
        tasks = [make_request("test") for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should complete without error
        assert len(results) == 10
        
        # Count allowed requests
        allowed = sum(1 for can_proceed, _ in results if can_proceed)
        assert allowed <= rate_limiter.calls_per_minute
    
    def test_reset(self, rate_limiter):
        """Test resetting rate limiter."""
        # Add some buckets
        rate_limiter.buckets["key1"] = RateLimitBucket(60, 10)
        rate_limiter.buckets["key2"] = RateLimitBucket(60, 10)
        
        # Reset specific key
        rate_limiter.reset("key1")
        assert "key1" not in rate_limiter.buckets
        assert "key2" in rate_limiter.buckets
        
        # Reset all
        rate_limiter.reset()
        assert len(rate_limiter.buckets) == 0


class TestRedditRateLimitError:
    """Test RedditRateLimitError exception."""
    
    def test_error_creation(self):
        """Test creating rate limit error."""
        error = RedditRateLimitError(retry_after=60)
        
        assert error.retry_after == 60
        assert "Retry after 60 seconds" in str(error)
    
    def test_error_default_retry(self):
        """Test default retry time."""
        error = RedditRateLimitError()
        
        assert error.retry_after == 60
        assert "Retry after 60 seconds" in str(error)
    
    def test_error_custom_message(self):
        """Test custom error message."""
        error = RedditRateLimitError(retry_after=120, message="Custom message")
        
        assert error.retry_after == 120
        assert "Custom message" in str(error)
        assert "Retry after 120 seconds" in str(error)


class TestHandleRateLimitResponse:
    """Test handle_rate_limit_response function."""
    
    @pytest.mark.asyncio
    async def test_no_rate_limit_headers(self):
        """Test handling response without rate limit headers."""
        headers = {"content-type": "application/json"}
        
        # Should not raise
        await handle_rate_limit_response(headers)
    
    @pytest.mark.asyncio
    async def test_rate_limit_not_exceeded(self):
        """Test handling response with remaining requests."""
        headers = {
            "x-ratelimit-remaining": "10",
            "x-ratelimit-reset": "1234567890"
        }
        
        # Should not raise
        await handle_rate_limit_response(headers)
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """Test handling response when rate limit exceeded."""
        with patch('time.time', return_value=1234567800):  # 90 seconds before reset
            headers = {
                "x-ratelimit-remaining": "0",
                "x-ratelimit-reset": "1234567890"
            }
            
            with pytest.raises(RedditRateLimitError) as exc_info:
                await handle_rate_limit_response(headers)
            
            assert exc_info.value.retry_after == 90
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded_no_reset(self):
        """Test handling rate limit without reset header."""
        headers = {
            "x-ratelimit-remaining": "0"
        }
        
        with pytest.raises(RedditRateLimitError) as exc_info:
            await handle_rate_limit_response(headers)
        
        assert exc_info.value.retry_after == 60  # Default
    
    @pytest.mark.asyncio
    async def test_rate_limit_past_reset_time(self):
        """Test handling when reset time is in the past."""
        with patch('time.time', return_value=1234567900):  # After reset time
            headers = {
                "x-ratelimit-remaining": "0",
                "x-ratelimit-reset": "1234567890"
            }
            
            with pytest.raises(RedditRateLimitError) as exc_info:
                await handle_rate_limit_response(headers)
            
            assert exc_info.value.retry_after == 1  # Minimum 1 second