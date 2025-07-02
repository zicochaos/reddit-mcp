"""Utility functions for Reddit MCP Server."""

import re
from typing import List, Dict, Any, Optional
from models import Post, Comment


def validate_subreddit_name(subreddit: str) -> str:
    """Validate and clean subreddit name."""
    # Remove prefixes
    subreddit = subreddit.replace("/r/", "").replace("r/", "").strip()
    
    # Validate format
    if not re.match(r"^[A-Za-z0-9_]{2,21}$", subreddit):
        raise ValueError(
            f"Invalid subreddit name '{subreddit}'. "
            "Must be 2-21 characters, alphanumeric and underscores only."
        )
    
    return subreddit


def validate_username(username: str) -> str:
    """Validate and clean username."""
    # Remove prefixes
    username = username.replace("/u/", "").replace("u/", "").strip()
    
    # Validate format
    if not re.match(r"^[A-Za-z0-9_-]{3,20}$", username):
        raise ValueError(
            f"Invalid username '{username}'. "
            "Must be 3-20 characters, alphanumeric, underscores and hyphens only."
        )
    
    return username


def parse_reddit_listing(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse Reddit listing response."""
    if not isinstance(data, dict):
        return []
    
    if "data" not in data:
        return []
    
    if "children" not in data["data"]:
        return []
    
    children = data["data"]["children"]
    if children is None:
        return []
    
    return children


def parse_posts_from_listing(listing: List[Dict[str, Any]]) -> List[Post]:
    """Parse posts from Reddit listing."""
    posts = []
    
    for item in listing:
        if item.get("kind") != "t3":
            continue
        
        try:
            post = Post.from_dict(item.get("data", {}))
            posts.append(post)
        except Exception as e:
            # Log error but continue processing
            continue
    
    return posts


def parse_comments_from_listing(listing: List[Dict[str, Any]]) -> List[Comment]:
    """Parse comments from Reddit listing."""
    comments = []
    
    for item in listing:
        if item.get("kind") != "t1":
            continue
        
        try:
            comment = Comment.from_dict(item.get("data", {}))
            comments.append(comment)
        except Exception as e:
            # Log error but continue processing
            continue
    
    return comments


def parse_comment_tree(data: List[Dict[str, Any]], depth: int = 0) -> List[Comment]:
    """Parse nested comment tree from Reddit response."""
    if not data or not isinstance(data, list):
        return []
    
    comments = []
    
    # Reddit returns [post_listing, comment_listing]
    if len(data) >= 2:
        comment_data = data[1]
    else:
        comment_data = data[0]
    
    if isinstance(comment_data, dict) and "data" in comment_data:
        return _parse_comment_listing(comment_data, depth)
    
    return comments


def _parse_comment_listing(listing_data: Dict[str, Any], depth: int = 0) -> List[Comment]:
    """Parse comment listing recursively."""
    comments = []
    
    if "data" not in listing_data or "children" not in listing_data["data"]:
        return comments
    
    for item in listing_data["data"]["children"]:
        if item.get("kind") != "t1":
            continue
        
        try:
            comment_data = item.get("data", {})
            comment = Comment.from_dict(comment_data)
            
            # Parse nested replies if depth allows
            if depth > 0 and "replies" in comment_data and comment_data["replies"]:
                replies_data = comment_data["replies"]
                if isinstance(replies_data, dict) and "data" in replies_data:
                    comment.replies = _parse_comment_listing(replies_data, depth - 1)
            
            comments.append(comment)
        except Exception:
            continue
    
    return comments


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    
    # If max_length is less than suffix length, just return suffix
    if max_length <= len(suffix):
        return suffix
    
    return text[:max_length - len(suffix)] + suffix


def sanitize_html(html: Optional[str]) -> Optional[str]:
    """Basic HTML sanitization."""
    if not html:
        return html
    
    # Remove script tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    
    # Remove style tags
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    
    # Remove event handlers
    html = re.sub(r'\son\w+\s*=\s*["\'][^"\']*["\']', '', html)
    
    return html


def format_number(num: int) -> str:
    """Format large numbers with abbreviations."""
    abs_num = abs(num)
    
    if abs_num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif abs_num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)