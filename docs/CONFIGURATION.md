# Reddit MCP Server Configuration Guide

This guide covers all configuration options for the Reddit MCP Server, including environment variables, advanced settings, and performance tuning.

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Configuration Files](#configuration-files)
3. [Cache Configuration](#cache-configuration)
4. [Rate Limiting Configuration](#rate-limiting-configuration)
5. [HTTP Client Configuration](#http-client-configuration)
6. [Reddit API Configuration](#reddit-api-configuration)
7. [Performance Tuning](#performance-tuning)
8. [Security Configuration](#security-configuration)
9. [Logging Configuration](#logging-configuration)

## Environment Variables

### Complete List of Environment Variables

```bash
# Cache Settings
REDDIT_CACHE_TTL=300              # Cache time-to-live in seconds (default: 300)
REDDIT_CACHE_SIZE=100             # Maximum number of cache entries (default: 100)
REDDIT_CACHE_ENABLED=true         # Enable/disable caching (default: true)

# Rate Limiting
REDDIT_RATE_LIMIT_CALLS=60        # API calls per minute (default: 60)
REDDIT_RATE_LIMIT_WINDOW=60       # Rate limit window in seconds (default: 60)
REDDIT_RATE_LIMIT_ENABLED=true    # Enable/disable rate limiting (default: true)

# HTTP Request Settings
REDDIT_REQUEST_TIMEOUT=30         # Request timeout in seconds (default: 30)
REDDIT_MAX_RETRIES=3              # Maximum retry attempts (default: 3)
REDDIT_RETRY_DELAY=1.0            # Initial retry delay in seconds (default: 1.0)
REDDIT_MAX_RETRY_DELAY=60.0       # Maximum retry delay in seconds (default: 60.0)
REDDIT_USER_AGENT="YourBot/1.0"   # Custom user agent string

# Reddit API Settings
REDDIT_BASE_URL=https://www.reddit.com  # Reddit base URL (default: https://www.reddit.com)
REDDIT_MAX_ITEMS=100              # Maximum items per request (default: 100)
REDDIT_DEFAULT_LIMIT=25           # Default limit for requests (default: 25)

# Logging
REDDIT_LOG_LEVEL=INFO             # Log level: DEBUG, INFO, WARNING, ERROR (default: INFO)
REDDIT_LOG_FILE=/path/to/log      # Log file path (optional)
```

### Setting Environment Variables

**Linux/macOS:**
```bash
export REDDIT_CACHE_TTL=600
export REDDIT_RATE_LIMIT_CALLS=120
```

**Windows Command Prompt:**
```cmd
set REDDIT_CACHE_TTL=600
set REDDIT_RATE_LIMIT_CALLS=120
```

**Windows PowerShell:**
```powershell
$env:REDDIT_CACHE_TTL = "600"
$env:REDDIT_RATE_LIMIT_CALLS = "120"
```

## Configuration Files

### Using .env Files

Create a `.env` file in your project root:

```env
# .env file
REDDIT_CACHE_TTL=600
REDDIT_CACHE_SIZE=200
REDDIT_RATE_LIMIT_CALLS=120
REDDIT_USER_AGENT="MyRedditBot/2.0 (by /u/myusername)"
REDDIT_LOG_LEVEL=DEBUG
```

Load in Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()

# Access variables
cache_ttl = int(os.getenv("REDDIT_CACHE_TTL", "300"))
```

### Custom Configuration Class

Create a custom configuration:

```python
# custom_config.py
from config import Config, CacheConfig, RateLimitConfig, RequestConfig, RedditConfig

custom_config = Config(
    cache=CacheConfig(
        ttl=600,  # 10 minutes
        max_size=200,
        enabled=True
    ),
    rate_limit=RateLimitConfig(
        calls_per_minute=120,
        window_seconds=60,
        enabled=True
    ),
    request=RequestConfig(
        timeout=45.0,
        max_retries=5,
        retry_delay=2.0,
        max_retry_delay=120.0,
        user_agent="CustomBot/1.0"
    ),
    reddit=RedditConfig(
        base_url="https://www.reddit.com",
        max_items_per_request=100,
        default_limit=50
    )
)
```

## Cache Configuration

### Cache TTL (Time-to-Live)

Controls how long responses are cached:

```bash
REDDIT_CACHE_TTL=300    # 5 minutes (default)
REDDIT_CACHE_TTL=600    # 10 minutes (recommended for stable data)
REDDIT_CACHE_TTL=60     # 1 minute (for frequently changing data)
REDDIT_CACHE_TTL=3600   # 1 hour (for historical data)
```

### Cache Size

Maximum number of cached responses:

```bash
REDDIT_CACHE_SIZE=100   # Default
REDDIT_CACHE_SIZE=500   # For high-traffic applications
REDDIT_CACHE_SIZE=50    # For memory-constrained environments
```

### Disable Caching

For development or debugging:

```bash
REDDIT_CACHE_ENABLED=false
```

### Cache Strategy Examples

**High-Performance Setup:**
```bash
REDDIT_CACHE_TTL=1800     # 30 minutes
REDDIT_CACHE_SIZE=1000    # Large cache
REDDIT_CACHE_ENABLED=true
```

**Real-Time Updates:**
```bash
REDDIT_CACHE_TTL=30       # 30 seconds
REDDIT_CACHE_SIZE=100
REDDIT_CACHE_ENABLED=true
```

**Development Setup:**
```bash
REDDIT_CACHE_TTL=5        # 5 seconds
REDDIT_CACHE_SIZE=10
REDDIT_CACHE_ENABLED=true
```

## Rate Limiting Configuration

### Basic Rate Limiting

```bash
REDDIT_RATE_LIMIT_CALLS=60    # 60 calls per minute (Reddit's default)
REDDIT_RATE_LIMIT_WINDOW=60   # 60-second window
```

### Aggressive Rate Limiting

For shared environments:

```bash
REDDIT_RATE_LIMIT_CALLS=30    # Conservative limit
REDDIT_RATE_LIMIT_WINDOW=60
```

### Development Rate Limiting

For testing:

```bash
REDDIT_RATE_LIMIT_CALLS=600   # 10 calls per second
REDDIT_RATE_LIMIT_WINDOW=60
REDDIT_RATE_LIMIT_ENABLED=false  # Or disable entirely
```

### Custom Rate Limit Strategies

```python
# Per-endpoint rate limiting
rate_limiters = {
    "subreddit": RateLimiter(calls_per_minute=60),
    "user": RateLimiter(calls_per_minute=30),
    "search": RateLimiter(calls_per_minute=20)
}
```

## HTTP Client Configuration

### Timeout Settings

```bash
REDDIT_REQUEST_TIMEOUT=30     # Default 30 seconds
REDDIT_REQUEST_TIMEOUT=60     # For slow connections
REDDIT_REQUEST_TIMEOUT=10     # For fast, local networks
```

### Retry Configuration

```bash
REDDIT_MAX_RETRIES=3          # Default retry attempts
REDDIT_RETRY_DELAY=1.0        # Initial delay between retries
REDDIT_MAX_RETRY_DELAY=60.0   # Maximum delay (exponential backoff)
```

**Aggressive Retry Strategy:**
```bash
REDDIT_MAX_RETRIES=5
REDDIT_RETRY_DELAY=0.5
REDDIT_MAX_RETRY_DELAY=30.0
```

**Conservative Retry Strategy:**
```bash
REDDIT_MAX_RETRIES=2
REDDIT_RETRY_DELAY=5.0
REDDIT_MAX_RETRY_DELAY=120.0
```

### User Agent Configuration

Reddit requires a descriptive user agent:

```bash
# Format: <platform>:<app ID>:<version> (by /u/<reddit username>)
REDDIT_USER_AGENT="linux:com.example.myapp:v1.0.0 (by /u/myusername)"

# Examples:
REDDIT_USER_AGENT="windows:reddit-mcp-bot:v2.0 (by /u/bot_owner)"
REDDIT_USER_AGENT="macos:data-analyzer:v1.5.3 (by /u/data_scientist)"
REDDIT_USER_AGENT="python:research-tool:v0.1 (by /u/researcher)"
```

### Connection Pool Settings

Modify in `client.py`:

```python
limits=httpx.Limits(
    max_connections=100,        # Total connections
    max_keepalive_connections=20,  # Persistent connections
    keepalive_expiry=30.0      # Keepalive timeout
)
```

## Reddit API Configuration

### Base URL

For different Reddit instances:

```bash
REDDIT_BASE_URL=https://www.reddit.com     # Default
REDDIT_BASE_URL=https://old.reddit.com     # Old Reddit
REDDIT_BASE_URL=https://oauth.reddit.com   # OAuth endpoint
```

### Request Limits

```bash
REDDIT_MAX_ITEMS=100      # Maximum items per request
REDDIT_DEFAULT_LIMIT=25   # Default when not specified
```

### API Endpoints

Configure specific endpoints:

```python
ENDPOINTS = {
    "subreddit": "/r/{subreddit}/{sort}.json",
    "user": "/user/{username}/{sort}.json",
    "search": "/search.json",
    "comments": "/comments/{post_id}.json"
}
```

## Performance Tuning

### High-Traffic Configuration

```bash
# Optimized for high throughput
REDDIT_CACHE_TTL=1800
REDDIT_CACHE_SIZE=2000
REDDIT_RATE_LIMIT_CALLS=100
REDDIT_REQUEST_TIMEOUT=20
REDDIT_MAX_RETRIES=2
```

### Low-Latency Configuration

```bash
# Optimized for speed
REDDIT_CACHE_TTL=300
REDDIT_CACHE_SIZE=500
REDDIT_REQUEST_TIMEOUT=10
REDDIT_MAX_RETRIES=1
REDDIT_RETRY_DELAY=0.5
```

### Memory-Efficient Configuration

```bash
# Optimized for low memory usage
REDDIT_CACHE_TTL=60
REDDIT_CACHE_SIZE=50
REDDIT_RATE_LIMIT_CALLS=30
```

### CPU-Efficient Configuration

```python
# Reduce JSON parsing overhead
import orjson  # Faster JSON library

# In client.py
response_json = orjson.loads(response.content)
```

## Security Configuration

### Secure Headers

Add security headers to requests:

```python
secure_headers = {
    "User-Agent": os.getenv("REDDIT_USER_AGENT"),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "DNT": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}
```

### API Key Management (Future)

Prepare for authenticated requests:

```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_REFRESH_TOKEN=your_refresh_token
```

### Request Validation

Enable strict validation:

```python
VALIDATE_SSL=True
VERIFY_CERTIFICATES=True
ALLOW_REDIRECTS=False  # Explicit redirect handling
```

## Logging Configuration

### Log Levels

```bash
REDDIT_LOG_LEVEL=DEBUG    # Verbose logging
REDDIT_LOG_LEVEL=INFO     # Standard logging (default)
REDDIT_LOG_LEVEL=WARNING  # Warnings and errors only
REDDIT_LOG_LEVEL=ERROR    # Errors only
```

### Log File Configuration

```bash
REDDIT_LOG_FILE=/var/log/reddit-mcp/app.log
REDDIT_LOG_MAX_SIZE=10485760  # 10MB
REDDIT_LOG_BACKUP_COUNT=5      # Keep 5 backup files
```

### Structured Logging

```python
import structlog

logger = structlog.get_logger()
logger.info("request_made", 
            endpoint="subreddit",
            subreddit="python",
            response_time=0.234)
```

### Log Format

```python
logging.basicConfig(
    level=os.getenv("REDDIT_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

## Advanced Configuration Examples

### Production Configuration

```bash
# Production settings
REDDIT_CACHE_TTL=900
REDDIT_CACHE_SIZE=1000
REDDIT_CACHE_ENABLED=true

REDDIT_RATE_LIMIT_CALLS=55
REDDIT_RATE_LIMIT_WINDOW=60
REDDIT_RATE_LIMIT_ENABLED=true

REDDIT_REQUEST_TIMEOUT=25
REDDIT_MAX_RETRIES=3
REDDIT_RETRY_DELAY=2.0
REDDIT_MAX_RETRY_DELAY=60.0

REDDIT_USER_AGENT="production:reddit-mcp:v1.0.0 (by /u/prod_bot)"
REDDIT_LOG_LEVEL=WARNING
REDDIT_LOG_FILE=/var/log/reddit-mcp/production.log
```

### Development Configuration

```bash
# Development settings
REDDIT_CACHE_TTL=30
REDDIT_CACHE_SIZE=50
REDDIT_CACHE_ENABLED=true

REDDIT_RATE_LIMIT_CALLS=600
REDDIT_RATE_LIMIT_WINDOW=60
REDDIT_RATE_LIMIT_ENABLED=false

REDDIT_REQUEST_TIMEOUT=60
REDDIT_MAX_RETRIES=5
REDDIT_RETRY_DELAY=0.5

REDDIT_USER_AGENT="dev:reddit-mcp:v0.1.0 (by /u/dev_user)"
REDDIT_LOG_LEVEL=DEBUG
```

### Testing Configuration

```bash
# Testing settings
REDDIT_CACHE_TTL=1
REDDIT_CACHE_SIZE=10
REDDIT_CACHE_ENABLED=false

REDDIT_RATE_LIMIT_ENABLED=false

REDDIT_REQUEST_TIMEOUT=5
REDDIT_MAX_RETRIES=0

REDDIT_USER_AGENT="test:reddit-mcp:v0.0.1 (by /u/test_user)"
REDDIT_LOG_LEVEL=DEBUG
```

## Configuration Validation

Add validation to ensure configuration is correct:

```python
def validate_config(config: Config) -> None:
    """Validate configuration settings."""
    
    # Cache validation
    assert config.cache.ttl > 0, "Cache TTL must be positive"
    assert config.cache.max_size > 0, "Cache size must be positive"
    
    # Rate limit validation
    assert config.rate_limit.calls_per_minute > 0, "Rate limit must be positive"
    assert config.rate_limit.window_seconds > 0, "Rate limit window must be positive"
    
    # Request validation
    assert config.request.timeout > 0, "Timeout must be positive"
    assert config.request.max_retries >= 0, "Retries must be non-negative"
    assert config.request.user_agent, "User agent must be provided"
    
    # Reddit validation
    assert config.reddit.base_url.startswith("http"), "Base URL must be valid"
    assert 0 < config.reddit.default_limit <= 100, "Default limit must be 1-100"
```