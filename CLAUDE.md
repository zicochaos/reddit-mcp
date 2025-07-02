# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Setup and Installation
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### Running the Server
```bash
# Run enhanced server (recommended - includes caching, rate limiting, all features)
python reddit_mcp_server_improved.py

# Run basic server (minimal implementation)
python reddit_mcp_server.py
```

### Development Commands
```bash
# Code formatting
black .

# Linting
ruff .

# Type checking
mypy .

# Run all tests
pytest

# Run specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m "not slow"        # Skip slow tests

# Run specific test file or function
pytest tests/unit/test_models.py
pytest tests/unit/test_models.py::TestPost::test_from_dict

# Run with coverage
pytest --cov=. --cov-report=html

# Using the test runner script
./run_tests.py              # Run all tests
./run_tests.py --unit       # Unit tests only
./run_tests.py --coverage   # With coverage report
./run_tests.py -k "cache"   # Tests matching "cache"
./run_tests.py -x           # Stop on first failure
```

## Architecture Overview

The codebase implements a Model Context Protocol (MCP) server for Reddit API access with two implementations:

1. **reddit_mcp_server.py** - Basic implementation with core functionality
2. **reddit_mcp_server_improved.py** - Production-ready server with caching, rate limiting, and advanced features

### Core Component Interactions

```
User Request → MCP Server → RedditClient → Reddit API
                   ↓              ↓
                Cache ←──── RateLimiter
                   ↓
              Response
```

### Key Components

**reddit_mcp_server_improved.py**
- Entry point for the enhanced server
- Implements MCP tool handlers decorated with `@app.list_tools()` and `@app.call_tool()`
- Uses `CacheDecorator` for automatic response caching
- All tool functions are async and return `List[TextContent]`

**models.py**
- Dataclasses for type-safe data representation
- Factory methods (`from_dict`) parse Reddit's JSON responses
- Nested object structure: Post → Author, Subreddit, Stats, Metadata
- `to_dict()` methods for serialization

**client.py**
- `RedditClient` wraps httpx with retry logic and rate limit handling
- Implements exponential backoff for failed requests
- Connection pooling for performance
- Automatic 429 (rate limit) detection and handling

**cache.py**
- LRU cache with TTL (time-to-live) support
- `CacheDecorator` for transparent function result caching
- Thread-safe with asyncio locks
- Cache key generation from function arguments

**rate_limiter.py**
- Token bucket algorithm implementation
- Per-endpoint rate limiting capability
- Calculates retry-after times for rate-limited requests
- Integrates with Reddit's rate limit headers

**config.py**
- Environment-based configuration using dataclasses
- `Config.from_env()` loads all settings from environment variables
- Hierarchical config structure: Config → CacheConfig, RateLimitConfig, RequestConfig, RedditConfig

## Critical Implementation Details

### MCP Tool Pattern
All tools follow this pattern:
```python
@app.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> List[TextContent]:
    # Tool routing logic
    return await specific_tool_function(**arguments)

@CacheDecorator(cache, ttl=config.cache.ttl, key_prefix="tool:")
async def specific_tool_function(...) -> List[TextContent]:
    # Implementation
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
```

### Error Handling Hierarchy
- `RedditAPIError` - Base exception
- `RedditNotFoundError` - 404 responses
- `RedditForbiddenError` - 403 responses  
- `RedditRateLimitError` - 429 responses with retry_after

### Reddit API Constraints
- Public API endpoints only (no OAuth)
- Rate limit: ~60 requests/minute
- JSON endpoints require `.json` suffix
- User agent must be descriptive

### Data Flow
1. MCP client sends tool request
2. Server validates and routes to tool handler
3. Cache checked for existing response
4. If miss, RedditClient makes API request with rate limiting
5. Response parsed into model objects
6. Models serialized to JSON
7. Response cached and returned

## Environment Configuration

Essential environment variables:
```bash
REDDIT_CACHE_TTL=300          # Cache duration in seconds
REDDIT_CACHE_SIZE=100         # Max cached responses
REDDIT_RATE_LIMIT_CALLS=60    # Calls per minute
REDDIT_REQUEST_TIMEOUT=30     # Request timeout
REDDIT_USER_AGENT="YourApp/1.0 (by /u/username)"  # Required by Reddit
```

## Testing Approach

When adding features:
1. Add type hints to all new functions
2. Create model tests in `tests/unit/test_models.py`
3. Mock Reddit API responses using `tests/fixtures/reddit_responses.json`
4. Test error conditions (rate limits, timeouts, malformed data)
5. Verify cache behavior with different TTL values