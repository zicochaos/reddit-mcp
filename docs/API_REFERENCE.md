# Reddit MCP Server API Reference

## Overview

The Reddit MCP Server provides a Model Context Protocol interface for interacting with Reddit's API. It offers tools for retrieving posts, comments, user content, and searching Reddit with advanced filtering options.

## Authentication

The Reddit MCP Server uses Reddit's public JSON API which doesn't require authentication for read-only operations. However, rate limits apply.

## Tools

### 1. get_subreddit_feed

Retrieves posts from a specified subreddit with various sorting and filtering options.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `subreddit` | string | Yes | - | The subreddit name (without r/ prefix) |
| `sort` | string | No | "hot" | Sort order: "hot", "new", "top", "rising", "controversial" |
| `time_filter` | string | No | - | Time range for top/controversial: "hour", "day", "week", "month", "year", "all" |
| `limit` | integer | No | 25 | Number of posts to retrieve (1-100) |
| `after` | string | No | - | Pagination cursor for next page |

#### Response

```json
{
  "subreddit": "python",
  "sort": "hot",
  "time_filter": null,
  "post_count": 25,
  "posts": [
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
        "name": "python",
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
        "created_datetime": "2023-01-01T00:00:00",
        "edited": false,
        "is_video": false,
        "is_self": true,
        "over_18": false,
        "spoiler": false,
        "stickied": false,
        "locked": false,
        "archived": false,
        "quarantine": false,
        "hidden": false,
        "pinned": false
      },
      "domain": "self.python",
      "flair_text": "Discussion",
      "media_embed": {},
      "thumbnail": null,
      "preview": null
    }
  ],
  "pagination": {
    "after": "t3_xyz789",
    "before": null
  }
}
```

### 2. get_user_feed

Retrieves posts and comments from a Reddit user's profile.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `username` | string | Yes | - | The Reddit username (without u/ prefix) |
| `content_type` | string | No | "all" | Type of content: "posts", "comments", "all" |
| `sort` | string | No | "new" | Sort order: "new", "top", "controversial" |
| `time_filter` | string | No | - | Time range for top/controversial: "hour", "day", "week", "month", "year", "all" |
| `limit` | integer | No | 25 | Number of items to retrieve (1-100) |

#### Response

```json
{
  "username": "spez",
  "content_type": "all",
  "sort": "new",
  "post_count": 10,
  "comment_count": 15,
  "posts": [
    {
      "id": "t3_abc123",
      "title": "Post Title",
      "description": "Post content",
      "link": "https://reddit.com/...",
      "author": {
        "username": "spez",
        "id": "t2_user123"
      },
      "subreddit": {
        "name": "announcements",
        "id": "t5_sub123",
        "subscribers": 1000000
      },
      "stats": {
        "score": 5000,
        "upvotes": 5200,
        "downvotes": 200,
        "upvote_ratio": 0.96,
        "comments": 1500,
        "crossposts": 50,
        "awards": 25
      },
      "metadata": {
        "created_utc": 1234567890,
        "created_datetime": "2023-01-01T00:00:00",
        "edited": false,
        "is_video": false,
        "is_self": true,
        "over_18": false,
        "spoiler": false,
        "stickied": true,
        "locked": false,
        "archived": false,
        "quarantine": false,
        "hidden": false,
        "pinned": true
      }
    }
  ],
  "comments": [
    {
      "id": "t1_def456",
      "body": "Comment text",
      "body_html": "<p>Comment text</p>",
      "author": {
        "username": "spez",
        "id": "t2_user123"
      },
      "post": {
        "id": "t3_abc123",
        "title": "Original Post Title",
        "link": "/r/reddit/comments/abc123/"
      },
      "subreddit": {
        "name": "reddit",
        "id": "t5_sub456"
      },
      "stats": {
        "score": 123,
        "upvotes": 130,
        "downvotes": 7,
        "awards": 1
      },
      "metadata": {
        "created_utc": 1234567890,
        "created_datetime": "2023-01-01T00:00:00",
        "edited": false,
        "stickied": false,
        "locked": false,
        "archived": false
      },
      "parent_id": "t3_abc123"
    }
  ]
}
```

### 3. search_reddit

Search Reddit for posts matching a query with advanced filtering options.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query string |
| `subreddit` | string | No | "all" | Subreddit to search in (or "all" for global search) |
| `sort` | string | No | "relevance" | Sort order: "relevance", "hot", "top", "new", "comments" |
| `time_filter` | string | No | - | Time range for sorting: "hour", "day", "week", "month", "year", "all" |
| `limit` | integer | No | 25 | Number of results (1-100) |

#### Response

```json
{
  "query": "machine learning",
  "subreddit": "all",
  "sort": "relevance",
  "result_count": 25,
  "posts": [
    {
      "id": "t3_abc123",
      "title": "Introduction to Machine Learning",
      "description": "A beginner's guide to ML concepts",
      "link": "https://reddit.com/r/learnmachinelearning/...",
      "author": {
        "username": "ml_expert",
        "id": "t2_user123"
      },
      "subreddit": {
        "name": "learnmachinelearning",
        "id": "t5_sub123",
        "subscribers": 500000
      },
      "stats": {
        "score": 2500,
        "upvotes": 2600,
        "downvotes": 100,
        "upvote_ratio": 0.96,
        "comments": 150,
        "crossposts": 5,
        "awards": 3
      },
      "metadata": {
        "created_utc": 1234567890,
        "created_datetime": "2023-01-01T00:00:00",
        "edited": false,
        "is_video": false,
        "is_self": true,
        "over_18": false,
        "spoiler": false,
        "stickied": false,
        "locked": false,
        "archived": false,
        "quarantine": false,
        "hidden": false,
        "pinned": false
      }
    }
  ]
}
```

### 4. get_post_comments

Retrieves comments for a specific Reddit post with nested replies.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `post_id` | string | Yes | - | Post ID (with or without t3_ prefix) |
| `sort` | string | No | "best" | Comment sort: "best", "top", "new", "controversial", "old", "qa" |
| `limit` | integer | No | 100 | Maximum comments to retrieve (1-500) |
| `depth` | integer | No | 2 | Maximum reply depth to retrieve (0-10) |

#### Response

```json
{
  "post_id": "t3_abc123",
  "sort": "best",
  "comment_count": 50,
  "depth": 2,
  "post": {
    "title": "Post Title",
    "author": "original_poster",
    "subreddit": "AskReddit",
    "score": 5000,
    "url": "https://reddit.com/r/AskReddit/comments/abc123/"
  },
  "comments": [
    {
      "id": "t1_comment1",
      "body": "Top level comment",
      "body_html": "<p>Top level comment</p>",
      "author": {
        "username": "commenter1",
        "id": "t2_user456"
      },
      "post": {
        "id": "t3_abc123",
        "title": "Post Title",
        "link": "/r/AskReddit/comments/abc123/"
      },
      "subreddit": {
        "name": "AskReddit",
        "id": "t5_sub789"
      },
      "stats": {
        "score": 1500,
        "upvotes": 1550,
        "downvotes": 50,
        "awards": 2
      },
      "metadata": {
        "created_utc": 1234567890,
        "created_datetime": "2023-01-01T00:00:00",
        "edited": false,
        "stickied": false,
        "locked": false,
        "archived": false
      },
      "parent_id": "t3_abc123",
      "replies": [
        {
          "id": "t1_reply1",
          "body": "Reply to top comment",
          "author": {
            "username": "replier1",
            "id": "t2_user789"
          },
          "stats": {
            "score": 500,
            "upvotes": 520,
            "downvotes": 20,
            "awards": 0
          },
          "parent_id": "t1_comment1",
          "replies": []
        }
      ]
    }
  ]
}
```

## Error Responses

All tools return error messages in a consistent format:

```json
{
  "error": "Error message describing what went wrong"
}
```

### Common Error Types

1. **Invalid Input**
   - Invalid subreddit name format
   - Invalid username format
   - Empty search query
   - Invalid parameter values

2. **Not Found**
   - Subreddit doesn't exist
   - User doesn't exist
   - Post doesn't exist

3. **Access Denied**
   - Private subreddit
   - Quarantined content
   - Deleted content

4. **Rate Limiting**
   - Too many requests
   - Temporary ban

5. **Network Errors**
   - Timeout
   - Connection failed
   - Invalid response

## Rate Limiting

The server implements automatic rate limiting:

- Default: 60 requests per minute
- Automatic retry with exponential backoff
- Respects Reddit's rate limit headers
- Configurable via environment variables

## Caching

Responses are cached to improve performance:

- Default TTL: 5 minutes
- LRU eviction policy
- Configurable cache size
- Automatic cleanup of expired entries

## Data Types

### Post Object
Contains comprehensive post information including author, subreddit, statistics, and metadata.

### Comment Object
Contains comment text, author information, parent relationships, and nested replies.

### Author Object
Contains username and Reddit user ID.

### Subreddit Object
Contains subreddit name, ID, and subscriber count.

### Stats Object
Contains voting statistics, comment counts, and award information.

### Metadata Object
Contains timestamps, flags (locked, archived, etc.), and content properties.

## Data Handling Notes

### Numeric Value Parsing
The Reddit API sometimes returns numeric values as strings with decimal points (e.g., "88.0", "99.0"). The server automatically handles these cases by:

- Converting string floats to integers where appropriate
- Handling edge cases like invalid numeric formats
- Preserving None values for optional fields

This ensures consistent integer types for fields like:
- Post/comment scores
- Upvote/downvote counts
- Subscriber counts
- Comment counts
- Award counts
- Rate limit values in headers