#!/usr/bin/env python3
"""
Reddit MCP Server
A Model Context Protocol server that provides Reddit feed functionality.
"""

import re
import json
import asyncio
import logging
from typing import Any, Sequence
from urllib.parse import urljoin

import httpx
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reddit-server")

# Default user agent - more realistic browser agent
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

app = Server("reddit-server")


def parse_reddit_page(data: dict) -> list:
    """Parse Reddit JSON response and extract children."""
    output = []
    if "data" not in data:
        return output
    if "children" not in data["data"]:
        return output
    for item in data["data"]["children"]:
        output.append(item)
    return output


def parse_posts(data: list) -> list:
    """Parse Reddit data and extract post information."""
    posts = []
    for item in data:
        if item["kind"] != "t3":
            continue
        item_data = item["data"]
        posts.append({
            "id": item_data["name"],
            "title": item_data["title"],
            "description": item_data["selftext"],
            "link": item_data["url"],
            "author_username": item_data["author"],
            "author_id": item_data["author_fullname"],
            "subreddit_name": item_data["subreddit"],
            "subreddit_id": item_data["subreddit_id"],
            "subreddit_subscribers": item_data["subreddit_subscribers"],
            "score": item_data["score"],
            "upvotes": item_data["ups"],
            "downvotes": item_data["downs"],
            "upvote_ratio": item_data["upvote_ratio"],
            "total_comments": item_data["num_comments"],
            "total_crossposts": item_data["num_crossposts"],
            "total_awards": item_data["total_awards_received"],
            "domain": item_data["domain"],
            "flair_text": item_data["link_flair_text"],
            "media_embed": item_data["media_embed"],
            "is_pinned": item_data["pinned"],
            "is_self": item_data["is_self"],
            "is_video": item_data["is_video"],
            "is_media_only": item_data["media_only"],
            "is_over_18": item_data["over_18"],
            "is_edited": item_data["edited"],
            "is_hidden": item_data["hidden"],
            "is_archived": item_data["archived"],
            "is_locked": item_data["locked"],
            "is_quarantined": item_data["quarantine"],
            "is_spoiler": item_data["spoiler"],
            "is_stickied": item_data["stickied"],
            "is_send_replies": item_data["send_replies"],
            "published_at": item_data["created_utc"],
        })
    return posts


def parse_comments(data: list) -> list:
    """Parse Reddit data and extract comment information."""
    comments = []
    for item in data:
        if item["kind"] != "t1":
            continue
        item_data = item["data"]
        comments.append({
            "id": item_data["name"],
            "body": item_data["body"],
            "link": item_data["permalink"],
            "post_id": item_data["link_id"],
            "post_title": item_data["link_title"],
            "post_link": item_data["link_permalink"],
            "author_username": item_data["author"],
            "author_id": item_data["author_fullname"],
            "subreddit_name": item_data["subreddit"],
            "subreddit_id": item_data["subreddit_id"],
            "score": item_data["score"],
            "upvotes": item_data["ups"],
            "downvotes": item_data["downs"],
            "total_comments": item_data["num_comments"],
            "total_awards": item_data["total_awards_received"],
            "is_edited": item_data["edited"],
            "is_archived": item_data["archived"],
            "is_locked": item_data["locked"],
            "is_quarantined": item_data["quarantine"],
            "is_stickied": item_data["stickied"],
            "is_send_replies": item_data["send_replies"],
            "published_at": item_data["created_utc"],
        })
    return comments


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_subreddit_feed",
            description="Get the latest posts from a subreddit. Returns an array of JSON objects with post details including id, title, description, link, author info, scores, and metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "The subreddit name (without r/ prefix)"
                    }
                },
                "required": ["subreddit"]
            }
        ),
        Tool(
            name="get_user_feed", 
            description="Get the latest posts and comments from a Reddit user. Returns a JSON object with separate arrays for posts and comments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The Reddit username (without u/ prefix)"
                    }
                },
                "required": ["username"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool calls."""
    if not arguments:
        arguments = {}
    
    try:
        if name == "get_subreddit_feed":
            return await get_subreddit_feed(arguments.get("subreddit", ""))
        elif name == "get_user_feed":
            return await get_user_feed(arguments.get("username", ""))
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_subreddit_feed(subreddit: str) -> list[TextContent]:
    """Get the latest posts from a subreddit."""
    if not subreddit:
        return [TextContent(type="text", text="Error: No subreddit provided")]
    
    # Clean subreddit name
    subreddit = subreddit.replace("/r/", "").replace("r/", "")
    
    # Validate subreddit name
    if not re.match(r"^[A-Za-z0-9_]{2,21}$", subreddit):
        return [TextContent(type="text", text=f"Error: Invalid subreddit name '{subreddit}' (must be 2-21 characters, alphanumeric and underscores only)")]
    
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"https://www.reddit.com/r/{subreddit}.json",
                headers=headers,
                timeout=30.0
            )
            
            if not response.is_success:
                return [TextContent(type="text", text=f"Error: Failed to retrieve r/{subreddit} feed: HTTP {response.status_code}")]
            
            data = response.json()
            parsed_data = parse_reddit_page(data)
            posts = parse_posts(parsed_data)
            
            result = {
                "subreddit": subreddit,
                "post_count": len(posts),
                "posts": posts
            }
            
            return [TextContent(
                type="text", 
                text=f"Retrieved {len(posts)} posts from r/{subreddit}:\n\n{json.dumps(result, indent=2)}"
            )]
            
    except httpx.TimeoutException:
        return [TextContent(type="text", text=f"Error: Request to r/{subreddit} timed out")]
    except httpx.RequestError as e:
        return [TextContent(type="text", text=f"Error: Network error when accessing r/{subreddit}: {str(e)}")]
    except json.JSONDecodeError:
        return [TextContent(type="text", text=f"Error: Invalid JSON response from r/{subreddit}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def get_user_feed(username: str) -> list[TextContent]:
    """Get the latest posts and comments from a Reddit user."""
    if not username:
        return [TextContent(type="text", text="Error: No username provided")]
    
    # Clean username
    username = username.replace("/u/", "").replace("u/", "")
    
    # Validate username
    if not re.match(r"^[A-Za-z0-9_]{3,20}$", username):
        return [TextContent(type="text", text=f"Error: Invalid username '{username}' (must be 3-20 characters, alphanumeric and underscores only)")]
    
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate", 
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"https://www.reddit.com/u/{username}.json",
                headers=headers,
                timeout=30.0
            )
            
            if not response.is_success:
                return [TextContent(type="text", text=f"Error: Failed to retrieve u/{username} feed: HTTP {response.status_code}")]
            
            data = response.json()
            parsed_data = parse_reddit_page(data)
            posts = parse_posts(parsed_data)
            comments = parse_comments(parsed_data)
            
            result = {
                "username": username,
                "post_count": len(posts),
                "comment_count": len(comments),
                "posts": posts,
                "comments": comments
            }
            
            return [TextContent(
                type="text",
                text=f"Retrieved {len(posts)} posts and {len(comments)} comments from u/{username}:\n\n{json.dumps(result, indent=2)}"
            )]
            
    except httpx.TimeoutException:
        return [TextContent(type="text", text=f"Error: Request to u/{username} timed out")]
    except httpx.RequestError as e:
        return [TextContent(type="text", text=f"Error: Network error when accessing u/{username}: {str(e)}")]
    except json.JSONDecodeError:
        return [TextContent(type="text", text=f"Error: Invalid JSON response from u/{username}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the server."""
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())