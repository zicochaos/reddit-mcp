"""Configuration management for Reddit MCP Server."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class CacheConfig:
    """Cache configuration settings."""
    ttl: int = 300  # 5 minutes
    max_size: int = 100
    enabled: bool = True


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    calls_per_minute: int = 60
    window_seconds: int = 60
    enabled: bool = True


@dataclass
class RequestConfig:
    """HTTP request configuration."""
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@dataclass
class RedditConfig:
    """Reddit API configuration."""
    base_url: str = "https://www.reddit.com"
    max_items_per_request: int = 100
    default_limit: int = 25


@dataclass
class Config:
    """Main configuration class."""
    cache: CacheConfig
    rate_limit: RateLimitConfig
    request: RequestConfig
    reddit: RedditConfig
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            cache=CacheConfig(
                ttl=int(os.getenv("REDDIT_CACHE_TTL", "300")),
                max_size=int(os.getenv("REDDIT_CACHE_SIZE", "100")),
                enabled=os.getenv("REDDIT_CACHE_ENABLED", "true").lower() == "true"
            ),
            rate_limit=RateLimitConfig(
                calls_per_minute=int(os.getenv("REDDIT_RATE_LIMIT_CALLS", "60")),
                window_seconds=int(os.getenv("REDDIT_RATE_LIMIT_WINDOW", "60")),
                enabled=os.getenv("REDDIT_RATE_LIMIT_ENABLED", "true").lower() == "true"
            ),
            request=RequestConfig(
                timeout=float(os.getenv("REDDIT_REQUEST_TIMEOUT", "30")),
                max_retries=int(os.getenv("REDDIT_MAX_RETRIES", "3")),
                retry_delay=float(os.getenv("REDDIT_RETRY_DELAY", "1.0")),
                max_retry_delay=float(os.getenv("REDDIT_MAX_RETRY_DELAY", "60.0")),
                user_agent=os.getenv("REDDIT_USER_AGENT", RequestConfig.user_agent)
            ),
            reddit=RedditConfig(
                base_url=os.getenv("REDDIT_BASE_URL", "https://www.reddit.com"),
                max_items_per_request=int(os.getenv("REDDIT_MAX_ITEMS", "100")),
                default_limit=int(os.getenv("REDDIT_DEFAULT_LIMIT", "25"))
            )
        )


# Global config instance
config = Config.from_env()