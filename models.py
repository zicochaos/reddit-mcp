"""Data models for Reddit MCP Server."""

from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime


def safe_int(value, default=0):
    """Safely convert value to int, handling floats and strings."""
    if value is None:
        return default if default is not None else None
    try:
        # Handle string floats like "99.0"
        if isinstance(value, str) and '.' in value:
            return int(float(value))
        return int(value)
    except (ValueError, TypeError):
        return default if default is not None else None


@dataclass
class Author:
    """Reddit author information."""
    username: str
    id: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Author":
        """Create Author from Reddit API data."""
        return cls(
            username=data.get("author", ""),
            id=data.get("author_fullname", "")
        )


@dataclass
class Subreddit:
    """Subreddit information."""
    name: str
    id: str
    subscribers: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Subreddit":
        """Create Subreddit from Reddit API data."""
        return cls(
            name=data.get("subreddit", ""),
            id=data.get("subreddit_id", ""),
            subscribers=safe_int(data.get("subreddit_subscribers"), None)
        )


@dataclass
class Stats:
    """Post or comment statistics."""
    score: int
    upvotes: int
    downvotes: int
    upvote_ratio: Optional[float] = None
    comments: Optional[int] = None
    crossposts: Optional[int] = None
    awards: Optional[int] = None
    
    @classmethod
    def from_post_dict(cls, data: Dict[str, Any]) -> "Stats":
        """Create Stats from Reddit post data."""
        return cls(
            score=safe_int(data.get("score", 0)),
            upvotes=safe_int(data.get("ups", 0)),
            downvotes=safe_int(data.get("downs", 0)),
            upvote_ratio=data.get("upvote_ratio"),
            comments=safe_int(data.get("num_comments"), None),
            crossposts=safe_int(data.get("num_crossposts"), None),
            awards=safe_int(data.get("total_awards_received"), None)
        )
    
    @classmethod
    def from_comment_dict(cls, data: Dict[str, Any]) -> "Stats":
        """Create Stats from Reddit comment data."""
        return cls(
            score=safe_int(data.get("score", 0)),
            upvotes=safe_int(data.get("ups", 0)),
            downvotes=safe_int(data.get("downs", 0)),
            awards=safe_int(data.get("total_awards_received"), None)
        )


@dataclass
class Metadata:
    """Post or comment metadata."""
    created_utc: float
    edited: bool
    is_video: Optional[bool] = None
    is_self: Optional[bool] = None
    over_18: Optional[bool] = None
    spoiler: Optional[bool] = None
    stickied: bool = False
    locked: bool = False
    archived: bool = False
    quarantine: bool = False
    hidden: Optional[bool] = None
    pinned: Optional[bool] = None
    
    @property
    def created_datetime(self) -> datetime:
        """Convert UTC timestamp to datetime."""
        return datetime.fromtimestamp(self.created_utc)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], is_post: bool = True) -> "Metadata":
        """Create Metadata from Reddit API data."""
        base_args = {
            "created_utc": data.get("created_utc", 0),
            "edited": bool(data.get("edited", False)),
            "stickied": data.get("stickied", False),
            "locked": data.get("locked", False),
            "archived": data.get("archived", False),
            "quarantine": data.get("quarantine", False),
        }
        
        if is_post:
            base_args.update({
                "is_video": data.get("is_video"),
                "is_self": data.get("is_self"),
                "over_18": data.get("over_18"),
                "spoiler": data.get("spoiler"),
                "hidden": data.get("hidden"),
                "pinned": data.get("pinned"),
            })
        
        return cls(**base_args)


@dataclass
class Post:
    """Reddit post model."""
    id: str
    title: str
    description: str
    link: str
    author: Author
    subreddit: Subreddit
    stats: Stats
    metadata: Metadata
    domain: Optional[str] = None
    flair_text: Optional[str] = None
    media_embed: Optional[Dict[str, Any]] = None
    thumbnail: Optional[str] = None
    preview: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Post":
        """Create Post from Reddit API data."""
        return cls(
            id=data.get("name", ""),
            title=data.get("title", ""),
            description=data.get("selftext", ""),
            link=data.get("url", ""),
            author=Author.from_dict(data),
            subreddit=Subreddit.from_dict(data),
            stats=Stats.from_post_dict(data),
            metadata=Metadata.from_dict(data, is_post=True),
            domain=data.get("domain"),
            flair_text=data.get("link_flair_text"),
            media_embed=data.get("media_embed"),
            thumbnail=data.get("thumbnail") if data.get("thumbnail") not in ["self", "default", "nsfw", "spoiler"] else None,
            preview=data.get("preview")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Post to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "link": self.link,
            "author": {
                "username": self.author.username,
                "id": self.author.id
            },
            "subreddit": {
                "name": self.subreddit.name,
                "id": self.subreddit.id,
                "subscribers": self.subreddit.subscribers
            },
            "stats": {
                "score": self.stats.score,
                "upvotes": self.stats.upvotes,
                "downvotes": self.stats.downvotes,
                "upvote_ratio": self.stats.upvote_ratio,
                "comments": self.stats.comments,
                "crossposts": self.stats.crossposts,
                "awards": self.stats.awards
            },
            "metadata": {
                "created_utc": self.metadata.created_utc,
                "created_datetime": self.metadata.created_datetime.isoformat(),
                "edited": self.metadata.edited,
                "is_video": self.metadata.is_video,
                "is_self": self.metadata.is_self,
                "over_18": self.metadata.over_18,
                "spoiler": self.metadata.spoiler,
                "stickied": self.metadata.stickied,
                "locked": self.metadata.locked,
                "archived": self.metadata.archived,
                "quarantine": self.metadata.quarantine,
                "hidden": self.metadata.hidden,
                "pinned": self.metadata.pinned
            },
            "domain": self.domain,
            "flair_text": self.flair_text,
            "media_embed": self.media_embed,
            "thumbnail": self.thumbnail,
            "preview": self.preview
        }


@dataclass
class Comment:
    """Reddit comment model."""
    id: str
    body: str
    body_html: Optional[str]
    author: Author
    post_id: str
    post_title: str
    post_link: str
    subreddit: Subreddit
    stats: Stats
    metadata: Metadata
    parent_id: Optional[str] = None
    replies: List["Comment"] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Comment":
        """Create Comment from Reddit API data."""
        return cls(
            id=data.get("name", ""),
            body=data.get("body", ""),
            body_html=data.get("body_html"),
            author=Author.from_dict(data),
            post_id=data.get("link_id", ""),
            post_title=data.get("link_title", ""),
            post_link=data.get("link_permalink", ""),
            subreddit=Subreddit.from_dict(data),
            stats=Stats.from_comment_dict(data),
            metadata=Metadata.from_dict(data, is_post=False),
            parent_id=data.get("parent_id"),
            replies=[]
        )
    
    def to_dict(self, include_replies: bool = True) -> Dict[str, Any]:
        """Convert Comment to dictionary."""
        result = {
            "id": self.id,
            "body": self.body,
            "body_html": self.body_html,
            "author": {
                "username": self.author.username,
                "id": self.author.id
            },
            "post": {
                "id": self.post_id,
                "title": self.post_title,
                "link": self.post_link
            },
            "subreddit": {
                "name": self.subreddit.name,
                "id": self.subreddit.id
            },
            "stats": {
                "score": self.stats.score,
                "upvotes": self.stats.upvotes,
                "downvotes": self.stats.downvotes,
                "awards": self.stats.awards
            },
            "metadata": {
                "created_utc": self.metadata.created_utc,
                "created_datetime": self.metadata.created_datetime.isoformat(),
                "edited": self.metadata.edited,
                "stickied": self.metadata.stickied,
                "locked": self.metadata.locked,
                "archived": self.metadata.archived
            },
            "parent_id": self.parent_id
        }
        
        if include_replies and self.replies:
            result["replies"] = [reply.to_dict(include_replies=True) for reply in self.replies]
        
        return result


# Type definitions for sorting and filtering
SortType = Literal["hot", "new", "top", "rising", "controversial", "best", "relevance"]
TimeFilter = Literal["hour", "day", "week", "month", "year", "all"]
ContentType = Literal["posts", "comments", "all"]