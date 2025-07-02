"""Test string float handling in various parts of the code."""

import pytest
from unittest.mock import AsyncMock, patch

from client import RedditClient, RedditRateLimitError
from rate_limiter import handle_rate_limit_response, RedditRateLimitError as RateLimiterError
from config import RequestConfig


class TestStringFloatHandling:
    """Test handling of string floats like '88.0' from Reddit API."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return RequestConfig(
            timeout=10.0,
            max_retries=0,  # No retries for these tests
            retry_delay=0.1,
            max_retry_delay=1.0,
            user_agent="TestBot/1.0"
        )
    
    @pytest.mark.asyncio
    async def test_retry_after_string_float(self, config):
        """Test handling retry-after header with string float value."""
        async with RedditClient(config) as client:
            # Mock response with string float in retry-after header
            mock_response = AsyncMock()
            mock_response.status_code = 429
            mock_response.headers = {"retry-after": "88.0"}  # String float
            mock_response.json.return_value = {"error": 429}
            
            with patch.object(client._client, 'request', return_value=mock_response):
                with pytest.raises(RedditRateLimitError) as exc_info:
                    await client.get("/test")
                
                # Should parse "88.0" as 88
                assert exc_info.value.retry_after == 88
    
    @pytest.mark.asyncio
    async def test_retry_after_string_float_with_decimals(self, config):
        """Test handling retry-after header with decimal string float."""
        async with RedditClient(config) as client:
            mock_response = AsyncMock()
            mock_response.status_code = 429
            mock_response.headers = {"retry-after": "123.456"}  # String float with decimals
            mock_response.json.return_value = {"error": 429}
            
            with patch.object(client._client, 'request', return_value=mock_response):
                with pytest.raises(RedditRateLimitError) as exc_info:
                    await client.get("/test")
                
                # Should parse "123.456" as 123
                assert exc_info.value.retry_after == 123
    
    @pytest.mark.asyncio
    async def test_retry_after_invalid_value(self, config):
        """Test handling retry-after header with invalid value."""
        async with RedditClient(config) as client:
            mock_response = AsyncMock()
            mock_response.status_code = 429
            mock_response.headers = {"retry-after": "invalid"}  # Invalid value
            mock_response.json.return_value = {"error": 429}
            
            with patch.object(client._client, 'request', return_value=mock_response):
                with pytest.raises(RedditRateLimitError) as exc_info:
                    await client.get("/test")
                
                # Should default to 60
                assert exc_info.value.retry_after == 60
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers_string_floats(self):
        """Test handle_rate_limit_response with string float headers."""
        # Test with string float remaining
        headers = {
            "x-ratelimit-remaining": "0.0",
            "x-ratelimit-reset": "1234567890.0"
        }
        
        with pytest.raises(RateLimiterError) as exc_info:
            await handle_rate_limit_response(headers)
        
        # Should raise error when remaining is 0
        assert "Rate limited" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers_remaining_positive_float(self):
        """Test rate limit headers with positive float remaining."""
        headers = {
            "x-ratelimit-remaining": "5.0",  # Positive, should not rate limit
            "x-ratelimit-reset": "1234567890.0"
        }
        
        # Should not raise
        await handle_rate_limit_response(headers)
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers_invalid_values(self):
        """Test rate limit headers with invalid values."""
        headers = {
            "x-ratelimit-remaining": "invalid",
            "x-ratelimit-reset": "also-invalid"
        }
        
        # Should not raise (assumes not rate limited if can't parse)
        await handle_rate_limit_response(headers)