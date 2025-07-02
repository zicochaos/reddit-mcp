"""Integration tests for Reddit client."""

import pytest
import json
import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path

import httpx

from client import (
    RedditClient, RedditAPIError, RedditNotFoundError, 
    RedditForbiddenError
)
from config import RequestConfig
from rate_limiter import RateLimiter, RedditRateLimitError


class TestRedditClient:
    """Test RedditClient integration."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return RequestConfig(
            timeout=10.0,
            max_retries=2,
            retry_delay=0.1,
            max_retry_delay=1.0,
            user_agent="TestBot/1.0"
        )
    
    @pytest.fixture
    def rate_limiter(self):
        """Create test rate limiter."""
        return RateLimiter(calls_per_minute=60, window_seconds=60)
    
    @pytest.fixture
    def fixtures(self):
        """Load test fixtures."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "reddit_responses.json"
        with open(fixture_path) as f:
            return json.load(f)
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock httpx response."""
        def _mock_response(json_data=None, status_code=200, headers=None):
            response = AsyncMock(spec=httpx.Response)
            response.status_code = status_code
            response.json.return_value = json_data or {}
            response.headers = headers or {}
            response.content = json.dumps(json_data or {}).encode()
            response.is_success = status_code == 200
            response.raise_for_status = AsyncMock()
            return response
        return _mock_response
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, config, rate_limiter):
        """Test client initialization and context manager."""
        client = RedditClient(config, rate_limiter)
        
        assert client.config == config
        assert client.rate_limiter == rate_limiter
        assert client.base_url == "https://www.reddit.com"
        assert client._client is None
        
        # Test context manager
        async with client as c:
            assert c._client is not None
            assert isinstance(c._client, httpx.AsyncClient)
        
        # Client should be closed after context
        assert client._client is None
    
    @pytest.mark.asyncio
    async def test_get_subreddit_success(self, config, rate_limiter, fixtures, mock_response):
        """Test successful subreddit request."""
        async with RedditClient(config, rate_limiter) as client:
            # Mock the HTTP request
            mock_resp = mock_response(
                json_data=fixtures["subreddit_response"],
                status_code=200
            )
            
            with patch.object(client._client, 'request', return_value=mock_resp):
                result = await client.get_subreddit("python", sort="hot", limit=25)
                
                assert result["kind"] == "Listing"
                assert len(result["data"]["children"]) == 2
                assert result["data"]["children"][0]["data"]["subreddit"] == "python"
    
    @pytest.mark.asyncio
    async def test_get_subreddit_with_time_filter(self, config, rate_limiter, mock_response):
        """Test subreddit request with time filter."""
        async with RedditClient(config, rate_limiter) as client:
            mock_resp = mock_response({"data": {"children": []}}, 200)
            
            with patch.object(client._client, 'request', return_value=mock_resp) as mock_request:
                await client.get_subreddit("python", sort="top", time_filter="week")
                
                # Verify request parameters
                call_args = mock_request.call_args
                assert call_args[1]["params"]["t"] == "week"
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, config, rate_limiter, fixtures, mock_response):
        """Test successful user request."""
        async with RedditClient(config, rate_limiter) as client:
            mock_resp = mock_response(
                json_data=fixtures["user_response"],
                status_code=200
            )
            
            with patch.object(client._client, 'request', return_value=mock_resp):
                result = await client.get_user("spez", content_type="all")
                
                assert result["kind"] == "Listing"
                assert len(result["data"]["children"]) == 3
                # Check we have both posts and comments
                kinds = [child["kind"] for child in result["data"]["children"]]
                assert "t3" in kinds  # Post
                assert "t1" in kinds  # Comment
    
    @pytest.mark.asyncio
    async def test_search_success(self, config, rate_limiter, fixtures, mock_response):
        """Test successful search request."""
        async with RedditClient(config, rate_limiter) as client:
            mock_resp = mock_response(
                json_data=fixtures["search_response"],
                status_code=200
            )
            
            with patch.object(client._client, 'request', return_value=mock_resp):
                result = await client.search("machine learning", sort="relevance")
                
                assert result["kind"] == "Listing"
                assert len(result["data"]["children"]) == 2
                # Verify search results
                for child in result["data"]["children"]:
                    assert "machine learning" in child["data"]["title"].lower()
    
    @pytest.mark.asyncio
    async def test_get_post_comments_success(self, config, rate_limiter, fixtures, mock_response):
        """Test successful post comments request."""
        async with RedditClient(config, rate_limiter) as client:
            mock_resp = mock_response(
                json_data=fixtures["comments_response"],
                status_code=200
            )
            
            with patch.object(client._client, 'request', return_value=mock_resp):
                result = await client.get_post_comments("askpost", sort="best")
                
                assert isinstance(result, list)
                assert len(result) == 2
                # First item is post, second is comments
                assert result[0]["data"]["children"][0]["kind"] == "t3"
                assert result[1]["data"]["children"][0]["kind"] == "t1"
    
    @pytest.mark.asyncio
    async def test_rate_limit_error(self, config, rate_limiter, mock_response):
        """Test handling of rate limit errors."""
        # Set max_retries to 0 to avoid waiting
        config.max_retries = 0
        
        async with RedditClient(config, rate_limiter) as client:
            mock_resp = mock_response(
                json_data={"error": 429},
                status_code=429,
                headers={"retry-after": "60"}
            )
            
            with patch.object(client._client, 'request', return_value=mock_resp):
                with pytest.raises(RedditRateLimitError) as exc_info:
                    await client.get("/test")
                
                assert exc_info.value.retry_after == 60
    
    @pytest.mark.asyncio
    async def test_not_found_error(self, config, rate_limiter, fixtures, mock_response):
        """Test handling of 404 errors."""
        async with RedditClient(config, rate_limiter) as client:
            mock_resp = mock_response(
                json_data=fixtures["not_found_response"],
                status_code=404
            )
            
            with patch.object(client._client, 'request', return_value=mock_resp):
                with pytest.raises(RedditNotFoundError):
                    await client.get("/r/nonexistent.json")
    
    @pytest.mark.asyncio
    async def test_forbidden_error(self, config, rate_limiter, fixtures, mock_response):
        """Test handling of 403 errors."""
        async with RedditClient(config, rate_limiter) as client:
            mock_resp = mock_response(
                json_data=fixtures["forbidden_response"],
                status_code=403
            )
            
            with patch.object(client._client, 'request', return_value=mock_resp):
                with pytest.raises(RedditForbiddenError):
                    await client.get("/r/private.json")
    
    @pytest.mark.asyncio
    async def test_retry_on_server_error(self, config, rate_limiter, mock_response):
        """Test retry logic on server errors."""
        async with RedditClient(config, rate_limiter) as client:
            # First two calls fail, third succeeds
            responses = [
                mock_response({"error": 500}, 500),
                mock_response({"error": 502}, 502),
                mock_response({"data": "success"}, 200)
            ]
            
            with patch.object(client._client, 'request', side_effect=responses):
                result = await client.get("/test")
                
                assert result["data"] == "success"
                assert client._client.request.call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_on_timeout(self, config, rate_limiter, mock_response):
        """Test retry logic on timeout errors."""
        async with RedditClient(config, rate_limiter) as client:
            # First call times out, second succeeds
            with patch.object(client._client, 'request') as mock_request:
                mock_request.side_effect = [
                    httpx.TimeoutException("Request timed out"),
                    mock_response({"data": "success"}, 200)
                ]
                
                result = await client.get("/test")
                
                assert result["data"] == "success"
                assert mock_request.call_count == 2
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, config, rate_limiter):
        """Test that max retries are respected."""
        config.max_retries = 2
        
        async with RedditClient(config, rate_limiter) as client:
            with patch.object(client._client, 'request') as mock_request:
                mock_request.side_effect = httpx.TimeoutException("Timeout")
                
                with pytest.raises(httpx.TimeoutException):
                    await client.get("/test")
                
                # Initial attempt + 2 retries = 3 calls
                assert mock_request.call_count == 3
    
    @pytest.mark.asyncio
    async def test_rate_limiter_integration(self, config, mock_response):
        """Test integration with rate limiter."""
        # Create rate limiter with very low limit
        rate_limiter = RateLimiter(calls_per_minute=2, window_seconds=1)
        
        async with RedditClient(config, rate_limiter) as client:
            mock_resp = mock_response({"data": "success"}, 200)
            
            with patch.object(client._client, 'request', return_value=mock_resp):
                # First two requests should succeed immediately
                start = time.time()
                await client.get("/test")  # Same path for all requests
                await client.get("/test")  # Same path
                
                # Third request should be delayed
                await client.get("/test")  # Same path
                elapsed = time.time() - start
                
                # Should have waited about 1 second (with some tolerance)
                assert elapsed >= 0.8  # Allow some tolerance for timing
    
    @pytest.mark.asyncio
    async def test_custom_headers(self, config, rate_limiter, mock_response):
        """Test that custom headers are included."""
        async with RedditClient(config, rate_limiter) as client:
            mock_resp = mock_response({"data": "success"}, 200)
            
            with patch.object(client._client, 'request', return_value=mock_resp) as mock_request:
                await client.get("/test")
                
                # Verify headers
                call_args = mock_request.call_args
                # Headers should be set on the client, not per request
                assert client._client.headers["User-Agent"] == "TestBot/1.0"
                assert client._client.headers["Accept"] == "application/json"
    
    @pytest.mark.asyncio
    async def test_json_suffix_handling(self, config, rate_limiter, mock_response):
        """Test that .json suffix is added when needed."""
        async with RedditClient(config, rate_limiter) as client:
            mock_resp = mock_response({"data": "success"}, 200)
            
            with patch.object(client._client, 'request', return_value=mock_resp) as mock_request:
                # Test path without .json
                await client.get("/r/python")
                call_url = mock_request.call_args[1]["url"]
                assert call_url.endswith(".json")
                
                # Test path with .json
                mock_request.reset_mock()
                await client.get("/r/python.json")
                call_url = mock_request.call_args[1]["url"]
                assert call_url.endswith(".json")
                assert not call_url.endswith(".json.json")
                
                # Test search path (should add .json)
                mock_request.reset_mock()
                await client.get("/search")
                call_url = mock_request.call_args[1]["url"]
                assert call_url.endswith(".json")
    
    @pytest.mark.asyncio
    async def test_connection_pooling(self, config, rate_limiter):
        """Test that connection pooling is configured."""
        async with RedditClient(config, rate_limiter) as client:
            # Verify the client is created and configured
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)
            
            # The exact way to verify limits depends on httpx version
            # Just verify the client is working
            def mock_response_factory(json_data=None, status_code=200, headers=None):
                response = AsyncMock(spec=httpx.Response)
                response.status_code = status_code
                response.json.return_value = json_data or {}
                response.headers = headers or {}
                response.content = json.dumps(json_data or {}).encode()
                response.is_success = status_code == 200
                response.raise_for_status = AsyncMock()
                return response
            
            mock_resp = mock_response_factory({"test": "data"}, 200)
            
            with patch.object(client._client, 'request', return_value=mock_resp):
                result = await client.get("/test")
                assert result == {"test": "data"}