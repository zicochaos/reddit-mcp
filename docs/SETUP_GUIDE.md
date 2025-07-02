# Reddit MCP Server Setup Guide

## Prerequisites

Before installing the Reddit MCP Server, ensure you have:

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)
- A terminal/command prompt
- Basic knowledge of Python and command line

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/zicochaos/reddit-mcp.git
cd reddit-mcp
```

### 2. Create a Virtual Environment (Recommended)

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import mcp, httpx; print('Dependencies installed successfully!')"
```

## Quick Start

### Running the Server

To run the Reddit MCP server:

```bash
python reddit_mcp_server.py
```

Or with uv (no virtual environment needed):

```bash
uv run --no-project --with mcp>=0.1.0 --with httpx>=0.25.0 --with typing-extensions>=4.8.0 reddit_mcp_server.py
```

## Configuration

### Environment Variables

Create a `.env` file in the project root or export these variables:

```bash
# Cache Configuration
export REDDIT_CACHE_TTL=300           # Cache time-to-live in seconds
export REDDIT_CACHE_SIZE=100          # Maximum cache entries
export REDDIT_CACHE_ENABLED=true      # Enable/disable caching

# Rate Limiting
export REDDIT_RATE_LIMIT_CALLS=60     # Calls per minute
export REDDIT_RATE_LIMIT_WINDOW=60    # Rate limit window in seconds
export REDDIT_RATE_LIMIT_ENABLED=true # Enable/disable rate limiting

# Request Configuration
export REDDIT_REQUEST_TIMEOUT=30      # Request timeout in seconds
export REDDIT_MAX_RETRIES=3          # Maximum retry attempts
export REDDIT_RETRY_DELAY=1.0        # Initial retry delay
export REDDIT_MAX_RETRY_DELAY=60.0   # Maximum retry delay

# Reddit API Configuration
export REDDIT_BASE_URL=https://www.reddit.com
export REDDIT_MAX_ITEMS=100          # Max items per request
export REDDIT_DEFAULT_LIMIT=25       # Default items limit

# Custom User Agent (optional)
export REDDIT_USER_AGENT="YourApp/1.0"
```

### Using a .env File

Install python-dotenv for easier environment management:

```bash
pip install python-dotenv
```

Create `.env` file:
```
REDDIT_CACHE_TTL=300
REDDIT_RATE_LIMIT_CALLS=60
REDDIT_REQUEST_TIMEOUT=30
```

Add to your Python script:
```python
from dotenv import load_dotenv
load_dotenv()
```

## MCP Integration

### Claude Desktop Configuration

Add the Reddit MCP server to your Claude Desktop configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

#### Option 1: Using Python directly

```json
{
  "mcpServers": {
    "reddit": {
      "command": "python",
      "args": ["/path/to/reddit-mcp/reddit_mcp_server.py"],
      "env": {
        "REDDIT_CACHE_TTL": "300",
        "REDDIT_RATE_LIMIT_CALLS": "60"
      }
    }
  }
}
```

#### Option 2: Using uv (recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that can run scripts with dependencies without requiring a virtual environment:

```json
{
  "mcpServers": {
    "reddit": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "--no-project",
        "--with",
        "mcp>=0.1.0",
        "--with",
        "httpx>=0.25.0",
        "--with",
        "typing-extensions>=4.8.0",
        "/path/to/reddit-mcp/reddit_mcp_server.py"
      ],
      "env": {
        "REDDIT_CACHE_TTL": "300",
        "REDDIT_RATE_LIMIT_CALLS": "60"
      }
    }
  }
}
```

Benefits of using uv:
- No need to manually create and manage virtual environments
- Automatically installs dependencies
- Faster startup time
- Isolated execution environment

### Using with Other MCP Clients

For other MCP clients, start the server and connect via stdio:

```python
import subprocess
import json

# Start the server
process = subprocess.Popen(
    ["python", "reddit_mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send MCP messages
message = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "get_subreddit_feed",
        "arguments": {"subreddit": "python"}
    },
    "id": 1
}

process.stdin.write(json.dumps(message) + "\n")
process.stdin.flush()
```

## Project Structure

```
reddit-mcp/
├── reddit_mcp_server.py         # Main MCP server implementation
├── models.py                    # Data models and types
├── config.py                    # Configuration management
├── client.py                    # HTTP client wrapper
├── cache.py                     # Caching implementation
├── rate_limiter.py             # Rate limiting logic
├── utils.py                     # Utility functions
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables (create this)
├── README.md                   # Project documentation
└── docs/                       # Additional documentation
    ├── API_REFERENCE.md
    ├── SETUP_GUIDE.md
    ├── USAGE_EXAMPLES.md
    ├── CONFIGURATION.md
    ├── TROUBLESHOOTING.md
    ├── LLM_USAGE_GUIDE.md
    ├── RESPONSE_EXAMPLES.md
    └── CONTRIBUTING.md
```

## Testing the Installation

### 1. Test Basic Functionality

```python
# test_reddit_mcp.py
import asyncio
from reddit_mcp_server import get_subreddit_feed

async def test():
    result = await get_subreddit_feed("python", limit=5)
    print(result[0].text)

asyncio.run(test())
```

### 2. Run Unit Tests (if available)

```bash
pytest tests/
```

### 3. Verify MCP Communication

Use the MCP test client to verify the server is responding correctly:

```bash
# Install mcp-cli if not already installed
pip install mcp-cli

# Test the server
mcp-cli test reddit_mcp_server.py
```

## Performance Optimization

### 1. Enable Caching

Caching significantly improves performance for repeated requests:

```bash
export REDDIT_CACHE_ENABLED=true
export REDDIT_CACHE_TTL=600  # 10 minutes
export REDDIT_CACHE_SIZE=200  # Store up to 200 responses
```

### 2. Adjust Rate Limits

For development, you might want more relaxed limits:

```bash
export REDDIT_RATE_LIMIT_CALLS=120  # 120 calls per minute
export REDDIT_RATE_LIMIT_WINDOW=60
```

### 3. Connection Pooling

The enhanced server automatically uses connection pooling. Adjust limits if needed:

```python
# In client.py, modify the httpx.Limits
limits=httpx.Limits(
    max_connections=100,
    max_keepalive_connections=20,
    keepalive_expiry=30.0
)
```

## Security Considerations

1. **Never share your configuration** if it contains sensitive data
2. **Use environment variables** instead of hardcoding values
3. **Respect Reddit's terms of service** and rate limits
4. **Monitor your usage** to avoid being banned
5. **Use HTTPS** for all Reddit API calls (default)

## Next Steps

- Read the [Usage Examples](USAGE_EXAMPLES.md) for practical examples
- Check the [Configuration Guide](CONFIGURATION.md) for advanced settings
- See [Troubleshooting](TROUBLESHOOTING.md) if you encounter issues
- Contribute to the project following our [Contributing Guidelines](CONTRIBUTING.md)