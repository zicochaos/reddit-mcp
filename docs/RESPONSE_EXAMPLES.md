# Reddit MCP Server - Response Examples

This document provides actual response examples from each tool in the Reddit MCP Server to help developers and LLM integrators understand the data structure and format.

## Table of Contents
- [get_subreddit_feed](#get_subreddit_feed)
- [get_subreddit_info](#get_subreddit_info)
- [search_reddit](#search_reddit)
- [get_post_comments](#get_post_comments)
- [get_user_feed](#get_user_feed)
- [Error Responses](#error-responses)

## get_subreddit_feed

### Request - Frontpage
```json
{
  "sort": "hot",
  "limit": 3
}
```

### Response
```
Retrieved 3 posts from Reddit frontpage (sorted by hot)

{
  "subreddit": "frontpage",
  "sort": "hot",
  "time_filter": null,
  "post_count": 3,
  "posts": [
    {
      "id": "t3_1abc123",
      "title": "Scientists discover new species of deep-sea creature",
      "description": "",
      "link": "https://www.nature.com/articles/deep-sea-discovery",
      "author": {
        "username": "science_fan",
        "id": "t2_def456"
      },
      "subreddit": {
        "name": "science",
        "id": "t5_mouw",
        "subscribers": 28500000
      },
      "stats": {
        "score": 45623,
        "upvotes": 48234,
        "downvotes": 2611,
        "upvote_ratio": 0.95,
        "comments": 1523,
        "crossposts": 15,
        "awards": 23
      },
      "metadata": {
        "created_utc": 1719925200,
        "created_datetime": "2025-07-02T09:00:00",
        "edited": false,
        "is_video": false,
        "is_self": false,
        "over_18": false,
        "spoiler": false,
        "stickied": false,
        "locked": false,
        "archived": false,
        "quarantine": false,
        "hidden": false,
        "pinned": false
      },
      "domain": "nature.com",
      "flair_text": "Biology",
      "media_embed": null,
      "thumbnail": "https://b.thumbs.redditmedia.com/abc123.jpg",
      "preview": {
        "images": [...]
      }
    }
  ],
  "pagination": {
    "after": "t3_xyz789",
    "before": null
  }
}
```

### Request - Specific Subreddit
```json
{
  "subreddit": "python",
  "sort": "top",
  "time_filter": "week",
  "limit": 2
}
```

### Response
```
Retrieved 2 posts from r/python (sorted by top, week)

{
  "subreddit": "python",
  "sort": "top",
  "time_filter": "week",
  "post_count": 2,
  "posts": [
    {
      "id": "t3_py001",
      "title": "I made a Python script that automates my morning routine",
      "description": "Here's how I built a script that...",
      "link": "https://reddit.com/r/python/comments/py001",
      "author": {
        "username": "pythonista",
        "id": "t2_usr123"
      },
      "subreddit": {
        "name": "python",
        "id": "t5_2qh0y",
        "subscribers": 1200000
      },
      "stats": {
        "score": 2834,
        "upvotes": 2950,
        "downvotes": 116,
        "upvote_ratio": 0.96,
        "comments": 234,
        "crossposts": 5,
        "awards": 3
      },
      "metadata": {
        "created_utc": 1719838800,
        "created_datetime": "2025-07-01T09:00:00",
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
      "flair_text": "Project",
      "media_embed": null,
      "thumbnail": "self",
      "preview": null
    }
  ],
  "pagination": {
    "after": "t3_py002",
    "before": null
  }
}
```

## get_subreddit_info

### Request
```json
{
  "subreddit": "python"
}
```

### Response
```
Information for r/Python (1,234,567 subscribers, 5,432 active)

{
  "name": "t5_2qh0y",
  "display_name": "Python",
  "title": "Python",
  "description": "News about the programming language Python. If you have something to teach others post here...",
  "public_description": "The official Python community for Reddit! Stay up to date with the latest news...",
  "subscribers": 1234567,
  "active_users": 5432,
  "created_utc": 1201219200,
  "created_date": "2008-01-25T00:00:00",
  "over18": false,
  "type": "public",
  "url": "/r/Python/",
  "icons": {
    "banner": "https://styles.redditmedia.com/t5_2qh0y/banner.png",
    "icon": "https://styles.redditmedia.com/t5_2qh0y/icon.png",
    "header": null,
    "community_icon": "https://styles.redditmedia.com/t5_2qh0y/community_icon.png"
  }
}
```

## search_reddit

### Request
```json
{
  "query": "machine learning beginner",
  "subreddit": "all",
  "sort": "relevance",
  "limit": 3
}
```

### Response
```
Found 3 posts matching 'machine learning beginner' in all of Reddit

{
  "query": "machine learning beginner",
  "subreddit": "all",
  "sort": "relevance",
  "result_count": 3,
  "posts": [
    {
      "id": "t3_ml001",
      "title": "Complete beginner's guide to Machine Learning - Start here!",
      "description": "I've compiled all the resources that helped me...",
      "link": "https://reddit.com/r/learnmachinelearning/comments/ml001",
      "author": {
        "username": "ml_teacher",
        "id": "t2_teacher1"
      },
      "subreddit": {
        "name": "learnmachinelearning",
        "id": "t5_3h4tq",
        "subscribers": 890000
      },
      "stats": {
        "score": 5623,
        "upvotes": 5812,
        "downvotes": 189,
        "upvote_ratio": 0.97,
        "comments": 423,
        "crossposts": 12,
        "awards": 15
      },
      "metadata": {
        "created_utc": 1719662400,
        "created_datetime": "2025-06-29T12:00:00",
        "edited": true,
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
      },
      "domain": "self.learnmachinelearning",
      "flair_text": "Resource",
      "media_embed": null,
      "thumbnail": "self",
      "preview": null
    }
  ]
}
```

## get_post_comments

### Request
```json
{
  "post_id": "t3_abc123",
  "sort": "best",
  "limit": 50,
  "depth": 2
}
```

### Response
```
Retrieved 25 top-level comments for "What's your favorite Python library?" in r/python

{
  "post_id": "t3_abc123",
  "sort": "best",
  "comment_count": 25,
  "depth": 2,
  "post": {
    "id": "t3_abc123",
    "title": "What's your favorite Python library?",
    "description": "I'm curious what libraries everyone is using...",
    "author": {
      "username": "curious_dev",
      "id": "t2_dev123"
    },
    "subreddit": {
      "name": "python",
      "id": "t5_2qh0y"
    },
    "stats": {
      "score": 523,
      "upvotes": 567,
      "downvotes": 44,
      "upvote_ratio": 0.93,
      "comments": 234,
      "awards": 2
    },
    "metadata": {
      "created_utc": 1719921600,
      "created_datetime": "2025-07-02T08:00:00",
      "edited": false,
      "is_video": false,
      "is_self": true,
      "over_18": false,
      "spoiler": false,
      "stickied": false,
      "locked": false,
      "archived": false
    },
    "url": "https://reddit.com/r/python/comments/abc123",
    "domain": "self.python",
    "flair_text": "Discussion",
    "thumbnail": "self"
  },
  "comments": [
    {
      "id": "t1_com001",
      "body": "Definitely pandas for data manipulation. It's saved me countless hours!",
      "body_html": "<div class=\"md\"><p>Definitely pandas for data manipulation. It's saved me countless hours!</p></div>",
      "author": {
        "username": "data_wizard",
        "id": "t2_wiz456"
      },
      "post": {
        "id": "t3_abc123",
        "title": "What's your favorite Python library?",
        "link": "/r/python/comments/abc123"
      },
      "subreddit": {
        "name": "python",
        "id": "t5_2qh0y"
      },
      "stats": {
        "score": 234,
        "upvotes": 245,
        "downvotes": 11,
        "awards": 1
      },
      "metadata": {
        "created_utc": 1719925200,
        "created_datetime": "2025-07-02T09:00:00",
        "edited": false,
        "stickied": false,
        "locked": false,
        "archived": false
      },
      "parent_id": "t3_abc123",
      "replies": [
        {
          "id": "t1_rep001",
          "body": "Agreed! Pandas + NumPy is an unbeatable combo.",
          "body_html": "<div class=\"md\"><p>Agreed! Pandas + NumPy is an unbeatable combo.</p></div>",
          "author": {
            "username": "numpy_fan",
            "id": "t2_fan789"
          },
          "post": {
            "id": "t3_abc123",
            "title": "What's your favorite Python library?",
            "link": "/r/python/comments/abc123"
          },
          "subreddit": {
            "name": "python",
            "id": "t5_2qh0y"
          },
          "stats": {
            "score": 45,
            "upvotes": 47,
            "downvotes": 2,
            "awards": 0
          },
          "metadata": {
            "created_utc": 1719928800,
            "created_datetime": "2025-07-02T10:00:00",
            "edited": false,
            "stickied": false,
            "locked": false,
            "archived": false
          },
          "parent_id": "t1_com001",
          "replies": []
        }
      ]
    }
  ]
}
```

## get_user_feed

### Request
```json
{
  "username": "pythonista",
  "content_type": "posts",
  "sort": "new",
  "limit": 2
}
```

### Response
```
Retrieved 2 items from u/pythonista (posts only, sorted by new)

{
  "username": "pythonista",
  "content_type": "posts",
  "sort": "new",
  "item_count": 2,
  "items": [
    {
      "id": "t3_usr001",
      "title": "Just released my open-source Python package!",
      "description": "After months of work, I'm excited to share...",
      "link": "https://github.com/pythonista/awesome-package",
      "author": {
        "username": "pythonista",
        "id": "t2_usr123"
      },
      "subreddit": {
        "name": "python",
        "id": "t5_2qh0y",
        "subscribers": 1200000
      },
      "stats": {
        "score": 1523,
        "upvotes": 1612,
        "downvotes": 89,
        "upvote_ratio": 0.95,
        "comments": 156,
        "crossposts": 3,
        "awards": 5
      },
      "metadata": {
        "created_utc": 1719921600,
        "created_datetime": "2025-07-02T08:00:00",
        "edited": false,
        "is_video": false,
        "is_self": false,
        "over_18": false,
        "spoiler": false,
        "stickied": false,
        "locked": false,
        "archived": false,
        "quarantine": false,
        "hidden": false,
        "pinned": false
      },
      "domain": "github.com",
      "flair_text": "Project",
      "media_embed": null,
      "thumbnail": "https://b.thumbs.redditmedia.com/github123.jpg",
      "preview": null
    }
  ]
}
```

## Error Responses

### 404 - Subreddit Not Found
```
Error: Subreddit r/thissubdoesnotexist not found
```

### 403 - Private Subreddit
```
Error: Access to r/privatesubreddit is forbidden
```

### 429 - Rate Limited
```
Error: Reddit API rate limit exceeded. Please try again in 60 seconds.
```

### Invalid Input
```
Error: Invalid subreddit name. Must contain only letters, numbers, and underscores.
```

### Network Error
```
Error: Failed to retrieve subreddit feed: Connection timeout
```

## Response Structure Notes

### Common Patterns

1. **All responses include:**
   - Summary line describing what was retrieved
   - JSON data structure with results

2. **Post objects always contain:**
   - Unique ID with type prefix (t3_ for posts)
   - Author information with username and ID
   - Subreddit information
   - Statistics (score, votes, comments)
   - Metadata (timestamps, flags)
   - Content (title, description, link)

3. **Comment objects include:**
   - Unique ID with type prefix (t1_ for comments)
   - Body text in plain and HTML format
   - Parent post/comment reference
   - Nested replies array (if depth > 0)

4. **Pagination support:**
   - "after" cursor for next page
   - "before" cursor for previous page
   - null when no more pages available

5. **Numeric values:**
   - All counts are integers
   - Ratios are floats (0-1)
   - Timestamps are Unix epoch (seconds)
   - Dates are ISO 8601 strings

### Data Reliability

- **String floats:** Reddit API may return numbers as strings (e.g., "88.0")
- **Missing fields:** Some fields may be null/missing depending on post type
- **NSFW content:** Check over_18 flag before displaying
- **Deleted content:** Author may show as "[deleted]"
- **Removed content:** Body may show as "[removed]"

### Performance Considerations

- **Response size:** Large requests can return significant data
- **Caching:** Responses are cached for 5 minutes by default
- **Rate limits:** 60 requests per minute default
- **Timeouts:** 30 second request timeout

## Using Response Data

### Example: Extracting Key Information
```python
# From subreddit feed
for post in response["posts"]:
    print(f"{post['title']} - {post['stats']['score']} points")
    
# From comments
for comment in response["comments"]:
    print(f"{comment['author']['username']}: {comment['body'][:100]}...")
    for reply in comment.get("replies", []):
        print(f"  └─ {reply['author']['username']}: {reply['body'][:50]}...")

# From subreddit info
info = response
print(f"{info['display_name']} has {info['subscribers']:,} subscribers")
```

### Example: Filtering Content
```python
# Filter NSFW posts
safe_posts = [p for p in response["posts"] if not p["metadata"]["over_18"]]

# Filter by score
popular = [p for p in response["posts"] if p["stats"]["score"] > 1000]

# Filter recent content (last 24 hours)
import time
recent = [p for p in response["posts"] 
          if time.time() - p["metadata"]["created_utc"] < 86400]
```

This documentation should help developers understand the exact format and structure of responses from the Reddit MCP Server.