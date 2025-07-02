"""HTTP client wrapper for Reddit API."""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

import httpx

from config import RequestConfig
from rate_limiter import RateLimiter, RedditRateLimitError, handle_rate_limit_response


logger = logging.getLogger(__name__)


class RedditAPIError(Exception):
    """Base Reddit API error."""
    pass


class RedditNotFoundError(RedditAPIError):
    """Resource not found error."""
    pass


class RedditForbiddenError(RedditAPIError):
    """Access forbidden error."""
    pass


class RedditClient:
    """HTTP client for Reddit API with retry and rate limiting."""
    
    def __init__(
        self,
        config: RequestConfig,
        rate_limiter: Optional[RateLimiter] = None,
        base_url: str = "https://www.reddit.com"
    ):
        self.config = config
        self.rate_limiter = rate_limiter
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None
        self._headers = self._build_headers()
    
    def _build_headers(self) -> Dict[str, str]:
        """Build default headers."""
        return {
            "User-Agent": self.config.user_agent,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            headers=self._headers,
            timeout=self.config.timeout,
            follow_redirects=True,
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
                keepalive_expiry=30.0
            )
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.base_url}{path}"
        if not url.endswith(".json"):
            url += ".json"
        
        attempt = 0
        delay = self.config.retry_delay
        
        while attempt <= self.config.max_retries:
            try:
                # Apply rate limiting
                if self.rate_limiter:
                    await self.rate_limiter.wait_if_needed(path)
                
                # Make request
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    **kwargs
                )
                
                # Check rate limit headers
                await handle_rate_limit_response(dict(response.headers))
                
                # Handle response status
                if response.status_code == 200:
                    return response
                elif response.status_code == 404:
                    raise RedditNotFoundError(f"Resource not found: {url}")
                elif response.status_code == 403:
                    raise RedditForbiddenError(f"Access forbidden: {url}")
                elif response.status_code == 429:
                    # Rate limited
                    retry_after_str = response.headers.get("retry-after", "60")
                    try:
                        # Handle string floats like "88.0"
                        retry_after = int(float(retry_after_str))
                    except (ValueError, TypeError):
                        retry_after = 60
                    raise RedditRateLimitError(retry_after=retry_after)
                elif response.status_code >= 500:
                    # Server error, retry
                    if attempt < self.config.max_retries:
                        logger.warning(f"Server error {response.status_code}, retrying...")
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, self.config.max_retry_delay)
                        attempt += 1
                        continue
                
                # Other error
                response.raise_for_status()
                
            except (RedditRateLimitError, httpx.TimeoutException) as e:
                if attempt < self.config.max_retries:
                    wait_time = getattr(e, "retry_after", delay) if isinstance(e, RedditRateLimitError) else delay
                    logger.warning(f"Request failed: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    delay = min(delay * 2, self.config.max_retry_delay)
                    attempt += 1
                    continue
                raise
            
            except httpx.RequestError as e:
                if attempt < self.config.max_retries:
                    logger.warning(f"Request error: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, self.config.max_retry_delay)
                    attempt += 1
                    continue
                raise
        
        raise RedditAPIError(f"Max retries exceeded for {url}")
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make GET request and return JSON."""
        response = await self._make_request("GET", path, params=params, **kwargs)
        return response.json()
    
    async def get_subreddit(
        self,
        subreddit: Optional[str],
        sort: str = "hot",
        time_filter: Optional[str] = None,
        limit: int = 25,
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get subreddit posts or frontpage if subreddit is None."""
        if subreddit:
            path = f"/r/{subreddit}/{sort}"
        else:
            # Frontpage
            path = f"/{sort}"
        
        params = {"limit": limit}
        
        if time_filter and sort in ["top", "controversial"]:
            params["t"] = time_filter
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        
        return await self.get(path, params=params)
    
    async def get_subreddit_info(self, subreddit: str) -> Dict[str, Any]:
        """Get subreddit information from about.json."""
        path = f"/r/{subreddit}/about"
        return await self.get(path)
    
    async def get_user(
        self,
        username: str,
        content_type: str = "all",
        sort: str = "new",
        time_filter: Optional[str] = None,
        limit: int = 25,
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user posts and comments."""
        path = f"/user/{username}"
        if content_type == "posts":
            path += "/submitted"
        elif content_type == "comments":
            path += "/comments"
        
        path += f"/{sort}"
        
        params = {"limit": limit}
        if time_filter and sort in ["top", "controversial"]:
            params["t"] = time_filter
        if after:
            params["after"] = after
        
        return await self.get(path, params=params)
    
    async def search(
        self,
        query: str,
        subreddit: Optional[str] = None,
        sort: str = "relevance",
        time_filter: Optional[str] = None,
        limit: int = 25,
        after: Optional[str] = None,
        type_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search Reddit."""
        if subreddit and subreddit != "all":
            path = f"/r/{subreddit}/search"
            params = {"q": query, "restrict_sr": "true"}
        else:
            path = "/search"
            params = {"q": query}
        
        params.update({
            "sort": sort,
            "limit": limit
        })
        
        if time_filter and sort in ["top", "comments"]:
            params["t"] = time_filter
        if after:
            params["after"] = after
        if type_filter:
            params["type"] = type_filter
        
        return await self.get(path, params=params)
    
    async def get_post_comments(
        self,
        post_id: str,
        subreddit: Optional[str] = None,
        sort: str = "best",
        limit: int = 100,
        depth: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get comments for a post."""
        # Extract post ID without prefix
        if post_id.startswith("t3_"):
            post_id = post_id[3:]
        
        if subreddit:
            path = f"/r/{subreddit}/comments/{post_id}"
        else:
            path = f"/comments/{post_id}"
        
        params = {"sort": sort, "limit": limit}
        if depth is not None:
            params["depth"] = depth
        
        # Reddit returns array with [post, comments]
        result = await self.get(path, params=params)
        return result if isinstance(result, list) else [result]