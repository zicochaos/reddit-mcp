"""Rate limiting implementation for Reddit MCP Server."""

import time
import asyncio
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque


@dataclass
class RateLimitBucket:
    """Rate limit bucket for tracking requests."""
    window_seconds: int
    max_requests: int
    requests: deque = field(default_factory=deque)
    
    def can_make_request(self) -> bool:
        """Check if a request can be made."""
        now = time.time()
        # Remove old requests outside the window
        while self.requests and self.requests[0] < now - self.window_seconds:
            self.requests.popleft()
        
        return len(self.requests) < self.max_requests
    
    def add_request(self) -> None:
        """Record a new request."""
        self.requests.append(time.time())
    
    def get_retry_after(self) -> float:
        """Get seconds until next request can be made."""
        if not self.requests:
            return 0.0
        
        oldest_request = self.requests[0]
        retry_after = (oldest_request + self.window_seconds) - time.time()
        return max(0.0, retry_after)


class RateLimiter:
    """Rate limiter for Reddit API requests."""
    
    def __init__(self, calls_per_minute: int = 60, window_seconds: int = 60):
        self.buckets: Dict[str, RateLimitBucket] = {}
        self.calls_per_minute = calls_per_minute
        self.window_seconds = window_seconds
        self._lock = asyncio.Lock()
    
    async def check_rate_limit(self, key: str = "default") -> Tuple[bool, float]:
        """
        Check if request can be made.
        
        Returns:
            Tuple of (can_make_request, retry_after_seconds)
        """
        async with self._lock:
            if key not in self.buckets:
                self.buckets[key] = RateLimitBucket(
                    window_seconds=self.window_seconds,
                    max_requests=self.calls_per_minute
                )
            
            bucket = self.buckets[key]
            if bucket.can_make_request():
                bucket.add_request()
                return True, 0.0
            else:
                return False, bucket.get_retry_after()
    
    async def wait_if_needed(self, key: str = "default") -> None:
        """Wait if rate limited before allowing request."""
        can_proceed, retry_after = await self.check_rate_limit(key)
        if not can_proceed and retry_after > 0:
            await asyncio.sleep(retry_after)
            # Recursive call to check again after waiting
            await self.wait_if_needed(key)
    
    def reset(self, key: Optional[str] = None) -> None:
        """Reset rate limit tracking."""
        if key:
            self.buckets.pop(key, None)
        else:
            self.buckets.clear()


class RedditRateLimitError(Exception):
    """Raised when Reddit returns a rate limit error."""
    
    def __init__(self, retry_after: Optional[int] = None, message: str = "Rate limited"):
        self.retry_after = retry_after or 60
        super().__init__(f"{message}. Retry after {self.retry_after} seconds")


async def handle_rate_limit_response(response_headers: Dict[str, str]) -> None:
    """
    Handle Reddit rate limit headers.
    
    Raises RedditRateLimitError if rate limited.
    """
    remaining = response_headers.get("x-ratelimit-remaining")
    reset = response_headers.get("x-ratelimit-reset")
    
    if remaining:
        try:
            # Handle string floats like "88.0"
            remaining_int = int(float(remaining))
        except (ValueError, TypeError):
            return  # If we can't parse, assume we're not rate limited
            
        if remaining_int <= 0:
            retry_after = 60  # Default
            if reset:
                try:
                    reset_int = int(float(reset))
                    retry_after = max(1, reset_int - int(time.time()))
                except (ValueError, TypeError):
                    pass  # Use default retry_after
            raise RedditRateLimitError(retry_after=retry_after)