"""Integration tests for Reddit MCP server."""

import pytest
import json
import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path

from mcp.types import TextContent

# Import from the improved server
import reddit_mcp_server_improved as server
from config import Config, CacheConfig, RateLimitConfig, RequestConfig, RedditConfig
from cache import Cache
from rate_limiter import RateLimiter
from client import RedditClient, RedditNotFoundError, RedditForbiddenError


class TestRedditMCPServer:
    """Test Reddit MCP Server integration."""
    
    @pytest.fixture
    def fixtures(self):
        """Load test fixtures."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "reddit_responses.json"
        with open(fixture_path) as f:
            return json.load(f)
    
    @pytest.fixture
    def test_config(self):
        """Create test configuration."""
        return Config(
            cache=CacheConfig(ttl=60, max_size=10, enabled=True),
            rate_limit=RateLimitConfig(calls_per_minute=60, window_seconds=60, enabled=True),
            request=RequestConfig(
                timeout=10.0,
                max_retries=2,
                retry_delay=0.1,
                max_retry_delay=1.0,
                user_agent="TestBot/1.0"
            ),
            reddit=RedditConfig(
                base_url="https://www.reddit.com",
                max_items_per_request=100,
                default_limit=25
            )
        )
    
    @pytest.fixture
    async def cleanup_cache(self):
        """Clean up cache before and after tests."""
        await server.cache.clear()
        yield
        await server.cache.clear()
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available tools."""
        tools = await server.handle_list_tools()
        
        assert len(tools) == 4
        tool_names = [tool.name for tool in tools]
        assert "get_subreddit_feed" in tool_names
        assert "get_user_feed" in tool_names
        assert "search_reddit" in tool_names
        assert "get_post_comments" in tool_names
        
        # Verify tool schemas
        for tool in tools:
            assert tool.inputSchema["type"] == "object"
            assert "properties" in tool.inputSchema
            assert "required" in tool.inputSchema
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_routing(self):
        """Test tool call routing."""
        # Mock the individual tool functions
        with patch.object(server, 'get_subreddit_feed', new_callable=AsyncMock) as mock_sub, \
             patch.object(server, 'get_user_feed', new_callable=AsyncMock) as mock_user, \
             patch.object(server, 'search_reddit', new_callable=AsyncMock) as mock_search, \
             patch.object(server, 'get_post_comments', new_callable=AsyncMock) as mock_comments:
            
            # Set return values
            mock_sub.return_value = [TextContent(type="text", text="subreddit result")]
            mock_user.return_value = [TextContent(type="text", text="user result")]
            mock_search.return_value = [TextContent(type="text", text="search result")]
            mock_comments.return_value = [TextContent(type="text", text="comments result")]
            
            # Test each tool
            result = await server.handle_call_tool("get_subreddit_feed", {"subreddit": "python"})
            assert result[0].text == "subreddit result"
            mock_sub.assert_called_once_with(subreddit="python")
            
            result = await server.handle_call_tool("get_user_feed", {"username": "spez"})
            assert result[0].text == "user result"
            mock_user.assert_called_once_with(username="spez")
            
            result = await server.handle_call_tool("search_reddit", {"query": "test"})
            assert result[0].text == "search result"
            mock_search.assert_called_once_with(query="test")
            
            result = await server.handle_call_tool("get_post_comments", {"post_id": "123"})
            assert result[0].text == "comments result"
            mock_comments.assert_called_once_with(post_id="123")
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_unknown(self):
        """Test handling unknown tool."""
        result = await server.handle_call_tool("unknown_tool", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error: Unknown tool: unknown_tool" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_exception(self):
        """Test handling exceptions in tool calls."""
        with patch.object(server, 'get_subreddit_feed', side_effect=Exception("Test error")):
            result = await server.handle_call_tool("get_subreddit_feed", {"subreddit": "test"})
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Error: Test error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_subreddit_feed_success(self, fixtures, cleanup_cache):
        """Test successful subreddit feed retrieval."""
        with patch('reddit_mcp_server_improved.RedditClient') as mock_client_class:
            # Mock the client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_subreddit.return_value = fixtures["subreddit_response"]
            
            result = await server.get_subreddit_feed(
                subreddit="python",
                sort="hot",
                limit=25
            )
            
            assert len(result) == 1
            assert result[0].type == "text"
            
            # Parse the response
            text = result[0].text
            assert "Retrieved 2 posts from r/python" in text
            
            data = json.loads(text.split("\n\n")[1])
            assert data["subreddit"] == "python"
            assert data["post_count"] == 2
            assert len(data["posts"]) == 2
            assert data["posts"][0]["title"] == "Test Python Post"
    
    @pytest.mark.asyncio
    async def test_get_subreddit_feed_not_found(self, cleanup_cache):
        """Test subreddit not found error."""
        with patch('reddit_mcp_server_improved.RedditClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_subreddit.side_effect = RedditNotFoundError("Not found")
            
            result = await server.get_subreddit_feed(subreddit="nonexistent")
            
            assert len(result) == 1
            assert "Error: Subreddit r/nonexistent not found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_subreddit_feed_forbidden(self, cleanup_cache):
        """Test private subreddit error."""
        with patch('reddit_mcp_server_improved.RedditClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_subreddit.side_effect = RedditForbiddenError("Forbidden")
            
            result = await server.get_subreddit_feed(subreddit="private")
            
            assert len(result) == 1
            assert "Error: Access to r/private is forbidden" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_subreddit_feed_invalid_name(self, cleanup_cache):
        """Test invalid subreddit name."""
        result = await server.get_subreddit_feed(subreddit="a")  # Too short
        
        assert len(result) == 1
        assert "Error: Invalid subreddit name" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_user_feed_success(self, fixtures, cleanup_cache):
        """Test successful user feed retrieval."""
        with patch('reddit_mcp_server_improved.RedditClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_user.return_value = fixtures["user_response"]
            
            result = await server.get_user_feed(
                username="spez",
                content_type="all",
                sort="new",
                limit=25
            )
            
            assert len(result) == 1
            text = result[0].text
            assert "Retrieved 1 posts and 2 comments from u/spez" in text
            
            data = json.loads(text.split("\n\n")[1])
            assert data["username"] == "spez"
            assert data["post_count"] == 1
            assert data["comment_count"] == 2
    
    @pytest.mark.asyncio
    async def test_search_reddit_success(self, fixtures, cleanup_cache):
        """Test successful Reddit search."""
        with patch('reddit_mcp_server_improved.RedditClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.search.return_value = fixtures["search_response"]
            
            result = await server.search_reddit(
                query="machine learning",
                subreddit="all",
                sort="relevance",
                limit=25
            )
            
            assert len(result) == 1
            text = result[0].text
            assert "Found 2 posts matching 'machine learning'" in text
            
            data = json.loads(text.split("\n\n")[1])
            assert data["query"] == "machine learning"
            assert data["result_count"] == 2
    
    @pytest.mark.asyncio
    async def test_search_reddit_empty_query(self, cleanup_cache):
        """Test search with empty query."""
        result = await server.search_reddit(query="", subreddit="all")
        
        assert len(result) == 1
        assert "Error: Search query cannot be empty" in result[0].text
    
    @pytest.mark.asyncio
    async def test_get_post_comments_success(self, fixtures):
        """Test successful comment retrieval."""
        with patch('reddit_mcp_server_improved.RedditClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_post_comments.return_value = fixtures["comments_response"]
            
            result = await server.get_post_comments(
                post_id="askpost",
                sort="best",
                limit=100,
                depth=2
            )
            
            assert len(result) == 1
            text = result[0].text
            assert "Retrieved 3 top-level comments" in text
            
            data = json.loads(text.split("\n\n")[1])
            assert data["post_id"] == "t3_askpost"
            assert data["comment_count"] == 3
            assert "post" in data
            assert data["post"]["title"] == "What's the best programming language?"
    
    @pytest.mark.asyncio
    async def test_get_post_comments_no_id(self):
        """Test comments with missing post ID."""
        result = await server.get_post_comments(post_id="")
        
        assert len(result) == 1
        assert "Error: Post ID is required" in result[0].text
    
    @pytest.mark.asyncio
    async def test_caching_behavior(self, fixtures, cleanup_cache):
        """Test that caching works correctly."""
        call_count = 0
        
        async def mock_get_subreddit(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return fixtures["subreddit_response"]
        
        with patch('reddit_mcp_server_improved.RedditClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_subreddit = mock_get_subreddit
            
            # First call - should hit the API
            result1 = await server.get_subreddit_feed(subreddit="python", limit=10)
            assert call_count == 1
            
            # Second call with same params - should use cache
            result2 = await server.get_subreddit_feed(subreddit="python", limit=10)
            assert call_count == 1  # No additional API call
            
            # Verify results are the same
            assert result1[0].text == result2[0].text
            
            # Different params - should hit API again
            result3 = await server.get_subreddit_feed(subreddit="python", limit=20)
            assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_rate_limiting_behavior(self, fixtures):
        """Test rate limiting integration."""
        # Test the rate limiter directly since server uses caching
        rate_limiter = RateLimiter(calls_per_minute=2, window_seconds=1)
        
        start = time.time()
        
        # First two should be immediate
        can1, wait1 = await rate_limiter.check_rate_limit("test")
        assert can1 is True
        assert wait1 == 0
        
        can2, wait2 = await rate_limiter.check_rate_limit("test")
        assert can2 is True
        assert wait2 == 0
        
        # Third should be blocked
        can3, wait3 = await rate_limiter.check_rate_limit("test")
        assert can3 is False
        assert wait3 > 0
        
        # Wait if needed
        await rate_limiter.wait_if_needed("test")
        
        elapsed = time.time() - start
        assert elapsed >= 0.8  # Should have waited
    
    @pytest.mark.asyncio
    async def test_cleanup_task(self):
        """Test that cleanup task runs."""
        # This is more of a smoke test to ensure cleanup doesn't crash
        task = asyncio.create_task(server.cleanup_task())
        
        # Let it run briefly
        await asyncio.sleep(0.1)
        
        # Cancel it
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass  # Expected
    
    @pytest.mark.asyncio
    async def test_pagination_support(self, fixtures):
        """Test pagination parameters."""
        with patch('reddit_mcp_server_improved.RedditClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_subreddit.return_value = fixtures["subreddit_response"]
            
            result = await server.get_subreddit_feed(
                subreddit="python",
                after="t3_abc123"
            )
            
            # Verify pagination token was passed
            mock_client.get_subreddit.assert_called_with(
                subreddit="python",
                sort="hot",
                time_filter=None,
                limit=25,
                after="t3_abc123"
            )
            
            # Verify response includes pagination info
            data = json.loads(result[0].text.split("\n\n")[1])
            assert "pagination" in data
            assert data["pagination"]["after"] == "t3_after123"