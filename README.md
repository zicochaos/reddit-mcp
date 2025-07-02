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

## LLM Usage

This MCP server is designed to work seamlessly with Large Language Models like Claude, GPT-4, and other AI assistants that support the Model Context Protocol.

### Quick Examples

```
User: "What's trending on Reddit right now?"
User: "Show me the top posts from r/technology this week"
User: "Find discussions about climate change"
User: "What is r/python about?"
```

### Common Use Cases

1. **Content Discovery**
   - Browse trending topics across Reddit or specific subreddits
   - Find the best posts about any topic
   - Discover new communities

2. **Research & Analysis**
   - Analyze sentiment around products, events, or topics
   - Compare discussions across different communities
   - Track how conversations evolve over time

3. **Community Insights**
   - Get detailed information about subreddits
   - Understand community rules and culture
   - Find active discussions and expert opinions

### Example LLM Interaction

```
User: "I want to learn about machine learning. What are the best Reddit resources?"

LLM: "I'll help you find the best machine learning resources on Reddit. Let me search for relevant communities and posts."

[Uses get_subreddit_info for "MachineLearning"]
[Uses search_reddit for "beginner guide machine learning"]
[Uses get_subreddit_feed for top posts from relevant subreddits]

LLM: "Here are the best Reddit resources for learning machine learning:

**Communities:**
- r/MachineLearning (2.8M members) - Main hub for ML news and research
- r/learnmachinelearning (890K members) - Focused on learning and beginners
- r/MLQuestions (125K members) - Q&A for ML problems

**Top Resources:**
1. 'Complete Beginner's Guide to ML' - comprehensive guide with 5.6K upvotes
2. 'Free ML Course Collection' - curated list of courses
3. 'From Zero to ML Engineer Roadmap' - step-by-step learning path

Would you like me to get more specific posts or explore any of these communities in detail?"
```

### Best Practices for LLMs

1. **Start broad, then narrow down** - Use search or frontpage before diving into specific posts
2. **Check community info first** - Understanding subreddit culture helps interpret content
3. **Use appropriate sorting** - "top" for best content, "new" for latest, "controversial" for debates
4. **Handle errors gracefully** - Some subreddits may be private or NSFW
5. **Respect rate limits** - The server handles this automatically, but inform users of delays

For more detailed examples and integration guides, see:
- [LLM Usage Guide](docs/LLM_USAGE_GUIDE.md) - Comprehensive guide with prompts and examples
- [Response Examples](docs/RESPONSE_EXAMPLES.md) - Actual response formats from each tool

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
│   ├── LLM_USAGE_GUIDE.md  # LLM integration guide
│   ├── RESPONSE_EXAMPLES.md # Response format examples
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

- GitHub: [https://github.com/zicochaos/reddit-mcp](https://github.com/zicochaos/reddit-mcp)
- Issues: [https://github.com/zicochaos/reddit-mcp/issues](https://github.com/zicochaos/reddit-mcp/issues)
- Pull Requests: [https://github.com/zicochaos/reddit-mcp/pulls](https://github.com/zicochaos/reddit-mcp/pulls)