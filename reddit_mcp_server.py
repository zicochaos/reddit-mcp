#!/usr/bin/env python3
"""
Reddit MCP Server - Enhanced Version
A Model Context Protocol server that provides Reddit feed functionality with
caching, rate limiting, and advanced features.
"""

import json
import asyncio
import logging
from typing import Any, Sequence, Optional, List, Dict

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio

from config import config
from models import Post, Comment, SortType, TimeFilter, ContentType
from client import RedditClient, RedditAPIError, RedditNotFoundError, RedditForbiddenError
from cache import Cache, CacheDecorator
from rate_limiter import RateLimiter
from utils import (
    validate_subreddit_name,
    validate_username,
    parse_reddit_listing,
    parse_posts_from_listing,
    parse_comments_from_listing,
    parse_comment_tree,
    format_number
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reddit-server")

# Initialize server
app = Server("reddit-server-enhanced")

# Initialize components
cache = Cache(max_size=config.cache.max_size, default_ttl=config.cache.ttl)
rate_limiter = RateLimiter(
    calls_per_minute=config.rate_limit.calls_per_minute,
    window_seconds=config.rate_limit.window_seconds
)


@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_subreddit_feed",
            description="Get posts from a subreddit with advanced filtering options including sorting, time ranges, and pagination.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "The subreddit name (without r/ prefix)"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["hot", "new", "top", "rising", "controversial"],
                        "default": "hot",
                        "description": "Sort order for posts"
                    },
                    "time_filter": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "description": "Time range for top/controversial posts"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 25,
                        "description": "Number of posts to retrieve"
                    },
                    "after": {
                        "type": "string",
                        "description": "Pagination cursor for next page"
                    }
                },
                "required": ["subreddit"]
            }
        ),
        Tool(
            name="get_user_feed",
            description="Get posts and comments from a Reddit user with filtering options.",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The Reddit username (without u/ prefix)"
                    },
                    "content_type": {
                        "type": "string",
                        "enum": ["posts", "comments", "all"],
                        "default": "all",
                        "description": "Type of content to retrieve"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["new", "top", "controversial"],
                        "default": "new",
                        "description": "Sort order"
                    },
                    "time_filter": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "description": "Time range for top/controversial"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 25,
                        "description": "Number of items to retrieve"
                    }
                },
                "required": ["username"]
            }
        ),
        Tool(
            name="search_reddit",
            description="Search Reddit for posts with advanced filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "subreddit": {
                        "type": "string",
                        "default": "all",
                        "description": "Subreddit to search in (or 'all' for global search)"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["relevance", "hot", "top", "new", "comments"],
                        "default": "relevance",
                        "description": "Sort order for results"
                    },
                    "time_filter": {
                        "type": "string",
                        "enum": ["hour", "day", "week", "month", "year", "all"],
                        "description": "Time range for sorting"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 25,
                        "description": "Number of results"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_post_comments",
            description="Get comments for a specific Reddit post with nested replies.",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "string",
                        "description": "Post ID (with or without t3_ prefix)"
                    },
                    "sort": {
                        "type": "string",
                        "enum": ["best", "top", "new", "controversial", "old", "qa"],
                        "default": "best",
                        "description": "Comment sort order"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 500,
                        "default": 100,
                        "description": "Maximum comments to retrieve"
                    },
                    "depth": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "default": 2,
                        "description": "Maximum reply depth to retrieve"
                    }
                },
                "required": ["post_id"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any] | None) -> List[TextContent]:
    """Handle tool calls."""
    if not arguments:
        arguments = {}
    
    try:
        if name == "get_subreddit_feed":
            return await get_subreddit_feed(**arguments)
        elif name == "get_user_feed":
            return await get_user_feed(**arguments)
        elif name == "search_reddit":
            return await search_reddit(**arguments)
        elif name == "get_post_comments":
            return await get_post_comments(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


@CacheDecorator(cache, ttl=config.cache.ttl, key_prefix="subreddit:")
async def get_subreddit_feed(
    subreddit: str,
    sort: str = "hot",
    time_filter: Optional[str] = None,
    limit: int = 25,
    after: Optional[str] = None
) -> List[TextContent]:
    """Get posts from a subreddit with caching."""
    try:
        # Validate input
        subreddit = validate_subreddit_name(subreddit)
        
        async with RedditClient(config.request, rate_limiter, config.reddit.base_url) as client:
            # Get subreddit data
            data = await client.get_subreddit(
                subreddit=subreddit,
                sort=sort,
                time_filter=time_filter,
                limit=limit,
                after=after
            )
            
            # Parse posts
            listing = parse_reddit_listing(data)
            posts = parse_posts_from_listing(listing)
            
            # Build response
            result = {
                "subreddit": subreddit,
                "sort": sort,
                "time_filter": time_filter,
                "post_count": len(posts),
                "posts": [post.to_dict() for post in posts],
                "pagination": {
                    "after": data.get("data", {}).get("after"),
                    "before": data.get("data", {}).get("before")
                }
            }
            
            # Format response
            summary = f"Retrieved {len(posts)} posts from r/{subreddit} (sorted by {sort}"
            if time_filter:
                summary += f", {time_filter}"
            summary += ")"
            
            return [TextContent(
                type="text",
                text=f"{summary}\n\n{json.dumps(result, indent=2)}"
            )]
            
    except RedditNotFoundError:
        return [TextContent(type="text", text=f"Error: Subreddit r/{subreddit} not found")]
    except RedditForbiddenError:
        return [TextContent(type="text", text=f"Error: Access to r/{subreddit} is forbidden (private/quarantined)")]
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error getting subreddit feed: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: Failed to retrieve subreddit feed: {str(e)}")]


@CacheDecorator(cache, ttl=config.cache.ttl, key_prefix="user:")
async def get_user_feed(
    username: str,
    content_type: str = "all",
    sort: str = "new",
    time_filter: Optional[str] = None,
    limit: int = 25
) -> List[TextContent]:
    """Get user posts and comments with caching."""
    try:
        # Validate input
        username = validate_username(username)
        
        async with RedditClient(config.request, rate_limiter, config.reddit.base_url) as client:
            # Get user data
            data = await client.get_user(
                username=username,
                content_type=content_type,
                sort=sort,
                time_filter=time_filter,
                limit=limit
            )
            
            # Parse content
            listing = parse_reddit_listing(data)
            posts = parse_posts_from_listing(listing)
            comments = parse_comments_from_listing(listing)
            
            # Build response
            result = {
                "username": username,
                "content_type": content_type,
                "sort": sort,
                "post_count": len(posts),
                "comment_count": len(comments),
                "posts": [post.to_dict() for post in posts],
                "comments": [comment.to_dict(include_replies=False) for comment in comments]
            }
            
            # Format response
            summary = f"Retrieved {len(posts)} posts and {len(comments)} comments from u/{username}"
            
            return [TextContent(
                type="text",
                text=f"{summary}\n\n{json.dumps(result, indent=2)}"
            )]
            
    except RedditNotFoundError:
        return [TextContent(type="text", text=f"Error: User u/{username} not found")]
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error getting user feed: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: Failed to retrieve user feed: {str(e)}")]


async def search_reddit(
    query: str,
    subreddit: str = "all",
    sort: str = "relevance",
    time_filter: Optional[str] = None,
    limit: int = 25
) -> List[TextContent]:
    """Search Reddit for posts."""
    try:
        # Validate input
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        
        if subreddit != "all":
            subreddit = validate_subreddit_name(subreddit)
        
        # Cache key includes all search parameters
        cache_key = cache.generate_key(
            "search", query, subreddit, sort, time_filter, limit
        )
        
        # Check cache
        cached = await cache.get(cache_key)
        if cached:
            return cached
        
        async with RedditClient(config.request, rate_limiter, config.reddit.base_url) as client:
            # Search Reddit
            data = await client.search(
                query=query,
                subreddit=subreddit if subreddit != "all" else None,
                sort=sort,
                time_filter=time_filter,
                limit=limit
            )
            
            # Parse results
            listing = parse_reddit_listing(data)
            posts = parse_posts_from_listing(listing)
            
            # Build response
            result = {
                "query": query,
                "subreddit": subreddit,
                "sort": sort,
                "result_count": len(posts),
                "posts": [post.to_dict() for post in posts]
            }
            
            # Format response
            location = f"r/{subreddit}" if subreddit != "all" else "all of Reddit"
            summary = f"Found {len(posts)} posts matching '{query}' in {location}"
            
            response = [TextContent(
                type="text",
                text=f"{summary}\n\n{json.dumps(result, indent=2)}"
            )]
            
            # Cache result
            await cache.set(cache_key, response)
            
            return response
            
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error searching Reddit: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: Search failed: {str(e)}")]


async def get_post_comments(
    post_id: str,
    sort: str = "best",
    limit: int = 100,
    depth: int = 2
) -> List[TextContent]:
    """Get comments for a Reddit post."""
    try:
        # Validate input
        if not post_id:
            raise ValueError("Post ID is required")
        
        # Clean post ID
        if post_id.startswith("t3_"):
            post_id = post_id[3:]
        
        async with RedditClient(config.request, rate_limiter, config.reddit.base_url) as client:
            # Get comments
            data = await client.get_post_comments(
                post_id=post_id,
                sort=sort,
                limit=limit,
                depth=depth
            )
            
            # Parse post info (first item)
            post_info = None
            if data and len(data) > 0:
                post_listing = parse_reddit_listing(data[0])
                posts = parse_posts_from_listing(post_listing)
                if posts:
                    post_info = posts[0]
            
            # Parse comments (second item)
            comments = []
            if data and len(data) > 1:
                comments = parse_comment_tree(data, depth=depth)
            
            # Build response
            result = {
                "post_id": f"t3_{post_id}",
                "sort": sort,
                "comment_count": len(comments),
                "depth": depth
            }
            
            if post_info:
                result["post"] = {
                    "title": post_info.title,
                    "author": post_info.author.username,
                    "subreddit": post_info.subreddit.name,
                    "score": post_info.stats.score,
                    "url": post_info.link
                }
            
            result["comments"] = [
                comment.to_dict(include_replies=True) 
                for comment in comments
            ]
            
            # Format response
            post_desc = f"post {post_id}"
            if post_info:
                post_desc = f'"{post_info.title}" in r/{post_info.subreddit.name}'
            
            summary = f"Retrieved {len(comments)} top-level comments for {post_desc}"
            
            return [TextContent(
                type="text",
                text=f"{summary}\n\n{json.dumps(result, indent=2)}"
            )]
            
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Error getting post comments: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: Failed to retrieve comments: {str(e)}")]


async def cleanup_task():
    """Periodic cleanup of expired cache entries."""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            expired = await cache.cleanup_expired()
            if expired > 0:
                logger.info(f"Cleaned up {expired} expired cache entries")
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")


async def main():
    """Run the server."""
    # Start cleanup task
    cleanup = asyncio.create_task(cleanup_task())
    
    try:
        # Run the server using stdio transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Reddit MCP Server (Enhanced) starting...")
            logger.info(f"Cache: {config.cache.max_size} entries, {config.cache.ttl}s TTL")
            logger.info(f"Rate limit: {config.rate_limit.calls_per_minute} calls/minute")
            
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    finally:
        cleanup.cancel()
        try:
            await cleanup
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())