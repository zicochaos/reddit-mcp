# Reddit MCP Server Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Reddit MCP Server.

## Table of Contents

1. [Common Issues](#common-issues)
2. [Installation Problems](#installation-problems)
3. [Connection Issues](#connection-issues)
4. [API Errors](#api-errors)
5. [Performance Issues](#performance-issues)
6. [Data Issues](#data-issues)
7. [Debugging Tools](#debugging-tools)
8. [FAQ](#faq)

## Common Issues

### Server Won't Start

**Symptoms:**
- Server exits immediately
- No output or error messages
- MCP client can't connect

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

2. **Verify dependencies:**
   ```bash
   pip list | grep -E "mcp|httpx"
   # Should show mcp and httpx installed
   ```

3. **Run with debug logging:**
   ```bash
   export REDDIT_LOG_LEVEL=DEBUG
   python reddit_mcp_server_improved.py
   ```

4. **Check for port conflicts:**
   ```bash
   # If using network transport
   lsof -i :8080  # or your configured port
   ```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'mcp'`

**Solution:**
```bash
# Ensure you're in the virtual environment
source venv/bin/activate  # On Unix
# or
venv\Scripts\activate  # On Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Error:** `ImportError: cannot import name 'Config' from 'config'`

**Solution:**
Ensure all required files are present:
```bash
ls *.py
# Should show: config.py, models.py, client.py, cache.py, rate_limiter.py, utils.py
```

## Installation Problems

### pip Installation Fails

**Error:** `error: Microsoft Visual C++ 14.0 is required`

**Solution (Windows):**
1. Install Visual Studio Build Tools
2. Or use pre-compiled wheels:
   ```bash
   pip install --only-binary :all: httpx
   ```

**Error:** `Permission denied`

**Solution:**
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# Or use user installation
pip install --user -r requirements.txt
```

### Dependency Conflicts

**Error:** `ERROR: pip's dependency resolver does not currently take into account all the packages that are installed`

**Solution:**
```bash
# Create fresh virtual environment
python -m venv fresh_venv
source fresh_venv/bin/activate
pip install -r requirements.txt
```

## Connection Issues

### MCP Client Can't Connect

**Error:** `Connection refused` or `Failed to connect to server`

**Solutions:**

1. **Verify server is running:**
   ```bash
   ps aux | grep reddit_mcp_server
   ```

2. **Check Claude Desktop config:**
   ```json
   {
     "mcpServers": {
       "reddit": {
         "command": "/full/path/to/python",
         "args": ["/full/path/to/reddit_mcp_server_improved.py"]
       }
     }
   }
   ```

3. **Test with stdio directly:**
   ```bash
   echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python reddit_mcp_server_improved.py
   ```

### Timeout Errors

**Error:** `TimeoutError: Request timed out`

**Solutions:**

1. **Increase timeout:**
   ```bash
   export REDDIT_REQUEST_TIMEOUT=60
   ```

2. **Check network connectivity:**
   ```bash
   curl -I https://www.reddit.com
   ping reddit.com
   ```

3. **Use a VPN if Reddit is blocked**

## API Errors

### Rate Limiting (429 Error)

**Error:** `Error: Rate limited. Retry after 60 seconds`

**Solutions:**

1. **Wait for the cooldown period**

2. **Reduce request frequency:**
   ```bash
   export REDDIT_RATE_LIMIT_CALLS=30  # More conservative
   ```

3. **Enable caching to reduce API calls:**
   ```bash
   export REDDIT_CACHE_ENABLED=true
   export REDDIT_CACHE_TTL=600  # 10 minutes
   ```

### Access Denied (403 Error)

**Error:** `Error: Access to r/subreddit is forbidden`

**Causes:**
- Private subreddit
- Quarantined subreddit
- Geo-blocked content

**Solutions:**
1. Try a different subreddit
2. Check if logged-in access is required
3. Use a VPN for geo-blocked content

### Not Found (404 Error)

**Error:** `Error: Subreddit r/example not found`

**Solutions:**

1. **Verify subreddit exists:**
   ```bash
   curl -s "https://www.reddit.com/r/example.json" | jq .
   ```

2. **Check for typos in subreddit name**

3. **Try without r/ prefix:**
   ```json
   {"subreddit": "example"}  // Not "r/example"
   ```

## Performance Issues

### Slow Response Times

**Symptoms:**
- Requests take > 30 seconds
- Frequent timeouts

**Solutions:**

1. **Enable caching:**
   ```bash
   export REDDIT_CACHE_ENABLED=true
   export REDDIT_CACHE_SIZE=500
   export REDDIT_CACHE_TTL=900  # 15 minutes
   ```

2. **Reduce request size:**
   ```json
   {"limit": 10}  // Instead of 100
   ```

3. **Check cache hit rate:**
   ```python
   # Add to server code
   print(cache.get_stats())
   ```

### High Memory Usage

**Symptoms:**
- Server uses excessive RAM
- Out of memory errors

**Solutions:**

1. **Reduce cache size:**
   ```bash
   export REDDIT_CACHE_SIZE=50  # Smaller cache
   ```

2. **Lower request limits:**
   ```bash
   export REDDIT_DEFAULT_LIMIT=10
   export REDDIT_MAX_ITEMS=50
   ```

3. **Monitor memory usage:**
   ```python
   import psutil
   process = psutil.Process()
   print(f"Memory: {process.memory_info().rss / 1024 / 1024} MB")
   ```

## Data Issues

### Missing or Incomplete Data

**Symptoms:**
- Empty responses
- Missing fields in responses

**Solutions:**

1. **Check Reddit's response:**
   ```bash
   curl -s "https://www.reddit.com/r/python.json" | jq '.data.children[0]'
   ```

2. **Enable debug logging:**
   ```python
   logger.debug(f"Raw response: {response.json()}")
   ```

3. **Handle missing fields gracefully:**
   ```python
   # In models.py
   title = data.get("title", "No title")
   score = data.get("score", 0)
   ```

### Encoding Issues

**Error:** `UnicodeDecodeError`

**Solutions:**

1. **Ensure UTF-8 encoding:**
   ```python
   response.encoding = 'utf-8'
   ```

2. **Handle special characters:**
   ```python
   text = text.encode('utf-8', errors='ignore').decode('utf-8')
   ```

### String Float Parsing Issues

**Error:** `invalid literal for int() with base 10: '88.0'`

**Cause:** Reddit API sometimes returns numeric values as string floats (e.g., "99.0", "88.0")

**Solutions:**

1. **Update to latest version** - This issue is fixed in v1.1.0

2. **Manual fix if needed:**
   ```python
   # Instead of: int(value)
   # Use: int(float(value))
   ```

3. **Affected fields:**
   - Rate limit headers (retry-after)
   - Post/comment scores
   - Subscriber counts
   - Any numeric field from Reddit API

**Prevention:** The improved server includes `safe_int()` function that handles all cases

## Debugging Tools

### Enable Debug Logging

```bash
export REDDIT_LOG_LEVEL=DEBUG
python reddit_mcp_server_improved.py 2> debug.log
```

### Test Individual Components

**Test cache:**
```python
# test_cache.py
import asyncio
from cache import Cache

async def test():
    cache = Cache()
    await cache.set("test", "value")
    result = await cache.get("test")
    print(f"Cache working: {result == 'value'}")

asyncio.run(test())
```

**Test rate limiter:**
```python
# test_rate_limit.py
import asyncio
from rate_limiter import RateLimiter

async def test():
    rl = RateLimiter(calls_per_minute=2)
    for i in range(5):
        can_proceed, wait = await rl.check_rate_limit()
        print(f"Request {i}: {can_proceed}, wait: {wait}s")
        if can_proceed:
            print("Making request...")
        else:
            print(f"Rate limited, waiting {wait}s")
            await asyncio.sleep(wait)

asyncio.run(test())
```

### Network Debugging

**Test Reddit connectivity:**
```bash
# Basic connectivity
curl -I https://www.reddit.com

# Test JSON endpoint
curl -s "https://www.reddit.com/r/python.json?limit=1" | jq '.data.children[0].data.title'

# Check headers
curl -v "https://www.reddit.com/r/python.json" 2>&1 | grep -E "< x-rate|< retry"
```

### MCP Protocol Debugging

**Test MCP communication:**
```bash
# List tools
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python reddit_mcp_server_improved.py | jq .

# Call tool
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_subreddit_feed","arguments":{"subreddit":"python","limit":1}},"id":2}' | python reddit_mcp_server_improved.py
```

## FAQ

### Q: Why am I getting "Too Many Requests" errors?

**A:** Reddit enforces rate limits. Solutions:
- Wait 1-2 minutes before retrying
- Reduce request frequency
- Enable caching to reuse responses

### Q: Can I use authentication for higher rate limits?

**A:** The current implementation uses Reddit's public API. OAuth support can be added for higher limits:
```python
# Future enhancement
headers["Authorization"] = f"Bearer {access_token}"
```

### Q: Why are some subreddits not accessible?

**A:** Several reasons:
- Private subreddits require authentication
- Quarantined subreddits need explicit opt-in
- NSFW subreddits may require account settings
- Geo-restricted content

### Q: How do I handle large result sets?

**A:** Use pagination:
```json
{
  "subreddit": "AskReddit",
  "limit": 100,
  "after": "t3_lastpostid"
}
```

### Q: Why is the cache not working?

**A:** Check:
1. Cache is enabled: `REDDIT_CACHE_ENABLED=true`
2. TTL is reasonable: `REDDIT_CACHE_TTL=300`
3. Cache size is sufficient: `REDDIT_CACHE_SIZE=100`

### Q: Can I run multiple instances?

**A:** Yes, but:
- Each instance has its own cache
- Share rate limits across instances
- Use different log files

### Q: How do I monitor server health?

**A:** Add health check endpoint:
```python
@app.route("/health")
async def health():
    return {
        "status": "healthy",
        "cache_stats": cache.get_stats(),
        "uptime": time.time() - start_time
    }
```

## Getting Help

If you're still experiencing issues:

1. **Check the logs** with `REDDIT_LOG_LEVEL=DEBUG`
2. **Search existing issues** on GitHub
3. **Create a detailed bug report** including:
   - Error messages
   - Configuration
   - Steps to reproduce
   - Expected vs actual behavior

## Common Error Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Missing dependencies | `pip install -r requirements.txt` |
| `TimeoutError` | Slow network/Reddit | Increase `REDDIT_REQUEST_TIMEOUT` |
| `429 Too Many Requests` | Rate limited | Wait and reduce request frequency |
| `403 Forbidden` | Private/quarantined content | Check subreddit accessibility |
| `404 Not Found` | Invalid subreddit/user | Verify the resource exists |
| `JSONDecodeError` | Invalid response | Check Reddit availability |
| `ConnectionError` | Network issues | Check internet connection |
| `ValueError: invalid literal for int()` | String float from API | Update to v1.1.0 or use safe_int() |