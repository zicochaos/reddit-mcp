# Reddit MCP Server

A Model Context Protocol (MCP) server that provides Reddit feed functionality with enhanced features including caching, rate limiting, comprehensive error handling, and robust data parsing.

## Quick Start with Claude Desktop

1. Install [uv](https://github.com/astral-sh/uv):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Add to Claude Desktop config:
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
         ]
       }
     }
   }
   ```

3. Restart Claude Desktop and start using Reddit tools!

## Features

- **Subreddit Feed Retrieval**: Get the latest posts from any subreddit
- **User Feed Retrieval**: Get posts and comments from Reddit users
- **Advanced Filtering**: Sort by hot, new, top, controversial with time ranges
- **Search Functionality**: Search within subreddits and across Reddit
- **Comment Retrieval**: Get comments for specific posts with nested replies
- **Caching**: Built-in LRU caching with TTL to reduce API calls
- **Rate Limiting**: Token bucket rate limiting with automatic retry
- **Type Safety**: Full type hints and data validation
- **Error Handling**: Comprehensive error handling with detailed messages
- **Robust Parsing**: Handles Reddit API quirks including string float values
- **Connection Pooling**: Efficient HTTP connection management
- **Pagination Support**: Navigate through large result sets

## Installation

### Option 1: Traditional Installation

```bash
# Clone the repository
git clone <repository-url>
cd reddit-mcp

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using uv (no virtual environment needed)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd reddit-mcp

# Run directly with uv (see Configuration section for Claude Desktop setup)
uv run --no-project --with mcp>=0.1.0 --with httpx>=0.25.0 --with typing-extensions>=4.8.0 reddit_mcp_server.py
```

## Configuration

The server can be configured through environment variables:

```bash
# Cache settings
REDDIT_CACHE_TTL=300  # Cache TTL in seconds (default: 300)
REDDIT_CACHE_SIZE=100  # Maximum cache entries (default: 100)

# Rate limiting
REDDIT_RATE_LIMIT_CALLS=60  # Calls per minute (default: 60)
REDDIT_RATE_LIMIT_WINDOW=60  # Window in seconds (default: 60)

# Request settings
REDDIT_REQUEST_TIMEOUT=30  # Request timeout in seconds (default: 30)
REDDIT_MAX_RETRIES=3  # Maximum retry attempts (default: 3)

# Reddit API settings
REDDIT_USER_AGENT="YourApp/1.0"  # Custom user agent (optional)
```

## Usage

### Starting the Server

```bash
# Option 1: With Python (requires virtual environment)
python reddit_mcp_server.py

# Option 2: With uv (no virtual environment needed)
uv run --no-project --with mcp>=0.1.0 --with httpx>=0.25.0 --with typing-extensions>=4.8.0 reddit_mcp_server.py
```

For Claude Desktop integration, see the [Setup Guide](docs/SETUP_GUIDE.md) for configuration examples.

For LLM usage examples and best practices, see:
- [LLM Usage Guide](docs/LLM_USAGE_GUIDE.md) - Prompts, examples, and integration tips
- [Response Examples](docs/RESPONSE_EXAMPLES.md) - Actual response formats from each tool

### Available Tools

#### 1. get_subreddit_feed
Get posts from a subreddit or Reddit frontpage with optional filtering.

```json
{
  "subreddit": "python",  // Optional: leave empty for frontpage
  "sort": "hot",
  "time_filter": "week",
  "limit": 25,
  "after": "t3_abc123"  // Optional: for pagination
}
```

#### 2. get_user_feed
Get posts and comments from a Reddit user.

```json
{
  "username": "spez",
  "content_type": "all",
  "sort": "new",
  "limit": 25
}
```

#### 3. search_reddit
Search Reddit for posts.

```json
{
  "query": "machine learning",
  "subreddit": "all",
  "sort": "relevance",
  "time_filter": "month",
  "limit": 25
}
```

#### 4. get_post_comments
Get detailed post content and comments for a specific post.

```json
{
  "post_id": "t3_abc123",
  "sort": "best",
  "limit": 100,
  "depth": 2  // Optional: depth of nested replies to retrieve
}
```

#### 5. get_subreddit_info
Get detailed information about a subreddit.

```json
{
  "subreddit": "python"
}
```

## Data Models

### Post Object
```python
{
  "id": "t3_abc123",
  "title": "Post Title",
  "description": "Post content",
  "link": "https://reddit.com/...",
  "author": {
    "username": "author_name",
    "id": "t2_user123"
  },
  "subreddit": {
    "name": "subreddit_name",
    "id": "t5_sub123",
    "subscribers": 1000000
  },
  "stats": {
    "score": 1234,
    "upvotes": 1300,
    "downvotes": 66,
    "upvote_ratio": 0.95,
    "comments": 456,
    "crossposts": 3,
    "awards": 2
  },
  "metadata": {
    "created_utc": 1234567890,
    "edited": false,
    "is_video": false,
    "is_self": true,
    "over_18": false,
    "spoiler": false,
    "stickied": false,
    "locked": false,
    "archived": false
  }
}
```

### Comment Object
```python
{
  "id": "t1_def456",
  "body": "Comment text",
  "author": {
    "username": "commenter",
    "id": "t2_user456"
  },
  "post": {
    "id": "t3_abc123",
    "title": "Post Title"
  },
  "stats": {
    "score": 123,
    "upvotes": 130,
    "downvotes": 7
  },
  "metadata": {
    "created_utc": 1234567890,
    "edited": false,
    "stickied": false
  },
  "replies": []  # Nested replies if depth > 0
}
```

## Error Handling

The server provides detailed error messages for common scenarios:

- **Invalid Input**: Validation errors with specific field information
- **Rate Limiting**: Automatic retry with exponential backoff
- **Network Errors**: Timeout and connection error handling
- **API Errors**: Reddit API error responses with status codes
- **Data Errors**: Graceful handling of missing or malformed data
- **String Float Parsing**: Handles Reddit API returning floats as strings (e.g., "88.0")
- **404 Errors**: Graceful handling of non-existent subreddits or users
- **403 Errors**: Clear messages for private/quarantined subreddits

## Development

### Project Structure
```
reddit-mcp/
├── reddit_mcp_server.py    # Main MCP server implementation
├── models.py               # Data models with safe int parsing
├── client.py               # HTTP client with retry logic
├── cache.py                # LRU caching with TTL support
├── rate_limiter.py         # Token bucket rate limiting
├── config.py               # Configuration management
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── docs/                   # Documentation
│   ├── API_REFERENCE.md    # Complete API documentation
│   ├── CONFIGURATION.md    # Configuration guide
│   ├── SETUP_GUIDE.md      # Installation guide
│   ├── TROUBLESHOOTING.md  # Common issues and solutions
│   ├── USAGE_EXAMPLES.md   # Code examples
│   └── CONTRIBUTING.md     # Contribution guidelines
├── CHANGELOG.md            # Version history
├── LICENSE                 # MIT License
└── README.md              # This file
```

### Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed contribution guidelines.

## License

MIT License - see LICENSE file for details

## Repository

- GitHub: [https://github.com/YOUR_USERNAME/reddit-mcp](https://github.com/YOUR_USERNAME/reddit-mcp)
- Issues: [https://github.com/YOUR_USERNAME/reddit-mcp/issues](https://github.com/YOUR_USERNAME/reddit-mcp/issues)
- Pull Requests: [https://github.com/YOUR_USERNAME/reddit-mcp/pulls](https://github.com/YOUR_USERNAME/reddit-mcp/pulls)