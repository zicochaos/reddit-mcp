# Changelog

All notable changes to the Reddit MCP Server project will be documented in this file.

## [1.2.0] - 2025-07-02

### Added
- Frontpage support in `get_subreddit_feed` - leave subreddit parameter empty to get Reddit frontpage
- New `get_subreddit_info` tool to get detailed subreddit metadata including:
  - Description, subscriber count, active users
  - Creation date, subreddit type, over18 status
  - Banner, icon, and header images
- Enhanced `get_post_comments` to include full post details in response:
  - Complete post metadata, stats, and content
  - Author information with IDs
  - All post properties like flair, domain, thumbnail

### Changed
- Updated `get_subreddit_feed` to accept optional subreddit parameter
- Improved `get_post_comments` response structure with detailed post information

### Documentation
- Added comprehensive LLM Usage Guide with prompt templates and examples
- Created Response Examples documentation showing actual tool outputs
- Included troubleshooting section for LLM integration
- Added best practices for efficient API usage

## [1.1.0] - 2025-07-02

### Fixed
- Fixed "invalid literal for int() with base 10: '88.0'" error when Reddit API returns string floats
- Added robust string float parsing in multiple locations:
  - Model data parsing (Stats, Subreddit)
  - HTTP client retry-after header parsing
  - Rate limiter header parsing
- Fixed search endpoint to properly append .json suffix

### Added
- Comprehensive test suite with 112 tests
- String float handling tests
- Real Reddit API integration tests
- Test coverage reporting (>70% coverage)
- Improved error messages for better debugging

### Changed
- Updated all integer parsing to handle string floats from Reddit API
- Improved documentation with test coverage information
- Enhanced README with pagination and depth parameters
- Added uv package manager as recommended installation option
- Updated setup documentation with uv configuration for Claude Desktop

## [1.0.0] - 2025-07-01

### Added
- Initial enhanced implementation with:
  - LRU caching with TTL support
  - Token bucket rate limiting
  - Comprehensive error handling
  - Type-safe data models
  - Connection pooling
  - Retry logic with exponential backoff
  - Pagination support
  - Nested comment retrieval
  - Environment-based configuration
  - Full documentation suite

### Features
- Get subreddit feeds with sorting and filtering
- Get user posts and comments
- Search Reddit with advanced filters
- Retrieve post comments with nested replies
- Automatic rate limit handling
- Response caching to reduce API calls