# Reddit MCP Server Usage Examples

This guide provides practical examples of using the Reddit MCP Server for common tasks.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Fetching Subreddit Posts](#fetching-subreddit-posts)
3. [Getting User Content](#getting-user-content)
4. [Searching Reddit](#searching-reddit)
5. [Retrieving Comments](#retrieving-comments)
6. [Advanced Patterns](#advanced-patterns)
7. [Integration Examples](#integration-examples)

## Basic Usage

### Simple Subreddit Feed

Get the latest hot posts from r/python:

```python
# Using the MCP tool
{
  "tool": "get_subreddit_feed",
  "arguments": {
    "subreddit": "python"
  }
}
```

### With Sorting and Limit

Get top 10 posts from r/science this week:

```python
{
  "tool": "get_subreddit_feed",
  "arguments": {
    "subreddit": "science",
    "sort": "top",
    "time_filter": "week",
    "limit": 10
  }
}
```

## Fetching Subreddit Posts

### Example 1: Hot Posts

Get trending posts from r/technology:

```python
{
  "tool": "get_subreddit_feed",
  "arguments": {
    "subreddit": "technology",
    "sort": "hot",
    "limit": 25
  }
}
```

### Example 2: New Posts

Get the newest posts from r/worldnews:

```python
{
  "tool": "get_subreddit_feed",
  "arguments": {
    "subreddit": "worldnews",
    "sort": "new",
    "limit": 30
  }
}
```

### Example 3: Top Posts of All Time

Get the best posts ever from r/AskReddit:

```python
{
  "tool": "get_subreddit_feed",
  "arguments": {
    "subreddit": "AskReddit",
    "sort": "top",
    "time_filter": "all",
    "limit": 50
  }
}
```

### Example 4: Controversial Posts

Get controversial posts from r/politics today:

```python
{
  "tool": "get_subreddit_feed",
  "arguments": {
    "subreddit": "politics",
    "sort": "controversial",
    "time_filter": "day",
    "limit": 20
  }
}
```

### Example 5: Pagination

Get the next page of results:

```python
# First request
{
  "tool": "get_subreddit_feed",
  "arguments": {
    "subreddit": "gaming",
    "sort": "hot",
    "limit": 25
  }
}

# Use the 'after' token from the response for the next page
{
  "tool": "get_subreddit_feed",
  "arguments": {
    "subreddit": "gaming",
    "sort": "hot",
    "limit": 25,
    "after": "t3_abc123"  # From previous response
  }
}
```

## Getting User Content

### Example 1: All User Activity

Get recent activity from u/spez:

```python
{
  "tool": "get_user_feed",
  "arguments": {
    "username": "spez",
    "content_type": "all"
  }
}
```

### Example 2: User Posts Only

Get only posts from a user:

```python
{
  "tool": "get_user_feed",
  "arguments": {
    "username": "GovSchwarzenegger",
    "content_type": "posts",
    "sort": "top",
    "time_filter": "year"
  }
}
```

### Example 3: User Comments Only

Get recent comments from a user:

```python
{
  "tool": "get_user_feed",
  "arguments": {
    "username": "poem_for_your_sprog",
    "content_type": "comments",
    "sort": "new",
    "limit": 50
  }
}
```

### Example 4: Top User Content

Get a user's most popular content:

```python
{
  "tool": "get_user_feed",
  "arguments": {
    "username": "Shitty_Watercolour",
    "content_type": "all",
    "sort": "top",
    "time_filter": "all",
    "limit": 10
  }
}
```

## Searching Reddit

### Example 1: Basic Search

Search for "machine learning" across all of Reddit:

```python
{
  "tool": "search_reddit",
  "arguments": {
    "query": "machine learning"
  }
}
```

### Example 2: Subreddit-Specific Search

Search within a specific subreddit:

```python
{
  "tool": "search_reddit",
  "arguments": {
    "query": "beginner projects",
    "subreddit": "learnpython",
    "sort": "relevance"
  }
}
```

### Example 3: Time-Filtered Search

Search for recent posts about a topic:

```python
{
  "tool": "search_reddit",
  "arguments": {
    "query": "ChatGPT",
    "sort": "new",
    "time_filter": "week",
    "limit": 50
  }
}
```

### Example 4: Popular Discussions

Find the most commented posts about a topic:

```python
{
  "tool": "search_reddit",
  "arguments": {
    "query": "climate change",
    "sort": "comments",
    "time_filter": "month",
    "limit": 25
  }
}
```

### Example 5: Complex Queries

Use Reddit search operators:

```python
{
  "tool": "search_reddit",
  "arguments": {
    "query": "title:announcement author:spez",
    "subreddit": "reddit",
    "sort": "new"
  }
}
```

## Retrieving Comments

### Example 1: Basic Comment Retrieval

Get comments for a post:

```python
{
  "tool": "get_post_comments",
  "arguments": {
    "post_id": "t3_15pz4m8"
  }
}
```

### Example 2: Sorted Comments

Get top comments:

```python
{
  "tool": "get_post_comments",
  "arguments": {
    "post_id": "15pz4m8",  // Works with or without t3_ prefix
    "sort": "top",
    "limit": 200
  }
}
```

### Example 3: Q&A Style

Get comments in Q&A format:

```python
{
  "tool": "get_post_comments",
  "arguments": {
    "post_id": "t3_abc123",
    "sort": "qa",
    "limit": 100
  }
}
```

### Example 4: Deep Comment Threads

Get nested replies:

```python
{
  "tool": "get_post_comments",
  "arguments": {
    "post_id": "t3_xyz789",
    "sort": "best",
    "limit": 100,
    "depth": 5  // Get up to 5 levels of nested replies
  }
}
```

### Example 5: Controversial Discussions

Get controversial comments:

```python
{
  "tool": "get_post_comments",
  "arguments": {
    "post_id": "t3_def456",
    "sort": "controversial",
    "limit": 50
  }
}
```

## Advanced Patterns

### Pattern 1: Monitor New Posts

Check for new posts periodically:

```python
async def monitor_subreddit(subreddit, interval=300):
    seen_posts = set()
    
    while True:
        result = await get_subreddit_feed(
            subreddit=subreddit,
            sort="new",
            limit=10
        )
        
        posts = json.loads(result[0].text)["posts"]
        
        for post in posts:
            if post["id"] not in seen_posts:
                print(f"New post: {post['title']}")
                seen_posts.add(post["id"])
        
        await asyncio.sleep(interval)
```

### Pattern 2: Aggregate User Stats

Analyze a user's posting patterns:

```python
async def analyze_user(username):
    result = await get_user_feed(
        username=username,
        content_type="all",
        limit=100
    )
    
    data = json.loads(result[0].text)
    posts = data["posts"]
    comments = data["comments"]
    
    # Calculate statistics
    total_post_karma = sum(p["stats"]["score"] for p in posts)
    total_comment_karma = sum(c["stats"]["score"] for c in comments)
    
    subreddits = {}
    for post in posts:
        sub = post["subreddit"]["name"]
        subreddits[sub] = subreddits.get(sub, 0) + 1
    
    return {
        "total_posts": len(posts),
        "total_comments": len(comments),
        "post_karma": total_post_karma,
        "comment_karma": total_comment_karma,
        "top_subreddits": sorted(subreddits.items(), 
                                key=lambda x: x[1], 
                                reverse=True)[:5]
    }
```

### Pattern 3: Content Analysis

Analyze trending topics:

```python
async def analyze_trending(subreddit):
    result = await get_subreddit_feed(
        subreddit=subreddit,
        sort="hot",
        limit=100
    )
    
    posts = json.loads(result[0].text)["posts"]
    
    # Extract common words from titles
    word_freq = {}
    for post in posts:
        words = post["title"].lower().split()
        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
    
    # Find trending topics
    trending = sorted(word_freq.items(), 
                     key=lambda x: x[1], 
                     reverse=True)[:20]
    
    return trending
```

### Pattern 4: Cross-Subreddit Search

Search multiple subreddits:

```python
async def multi_search(query, subreddits):
    results = []
    
    for subreddit in subreddits:
        result = await search_reddit(
            query=query,
            subreddit=subreddit,
            limit=10
        )
        
        data = json.loads(result[0].text)
        results.extend(data["posts"])
    
    # Sort by score
    results.sort(key=lambda x: x["stats"]["score"], reverse=True)
    
    return results[:25]  # Top 25 across all subreddits
```

## Integration Examples

### Example 1: Discord Bot Integration

```python
import discord
from reddit_mcp_server import get_subreddit_feed

client = discord.Client()

@client.event
async def on_message(message):
    if message.content.startswith('!reddit'):
        parts = message.content.split()
        if len(parts) >= 2:
            subreddit = parts[1]
            
            result = await get_subreddit_feed(
                subreddit=subreddit,
                limit=5
            )
            
            posts = json.loads(result[0].text)["posts"]
            
            for post in posts:
                embed = discord.Embed(
                    title=post["title"],
                    url=post["link"],
                    description=post["description"][:200]
                )
                embed.add_field(name="Score", value=post["stats"]["score"])
                embed.add_field(name="Comments", value=post["stats"]["comments"])
                
                await message.channel.send(embed=embed)
```

### Example 2: Web API Integration

```python
from fastapi import FastAPI
from reddit_mcp_server import get_subreddit_feed, search_reddit

app = FastAPI()

@app.get("/subreddit/{name}")
async def subreddit_endpoint(name: str, sort: str = "hot", limit: int = 25):
    result = await get_subreddit_feed(
        subreddit=name,
        sort=sort,
        limit=limit
    )
    
    return json.loads(result[0].text)

@app.get("/search")
async def search_endpoint(q: str, subreddit: str = "all"):
    result = await search_reddit(
        query=q,
        subreddit=subreddit
    )
    
    return json.loads(result[0].text)
```

### Example 3: Data Pipeline

```python
import pandas as pd
from datetime import datetime

async def create_dataset(subreddit, days=7):
    posts_data = []
    
    for time_filter in ["day", "week"]:
        result = await get_subreddit_feed(
            subreddit=subreddit,
            sort="top",
            time_filter=time_filter,
            limit=100
        )
        
        posts = json.loads(result[0].text)["posts"]
        
        for post in posts:
            posts_data.append({
                "title": post["title"],
                "score": post["stats"]["score"],
                "comments": post["stats"]["comments"],
                "upvote_ratio": post["stats"]["upvote_ratio"],
                "created": datetime.fromtimestamp(post["metadata"]["created_utc"]),
                "author": post["author"]["username"],
                "is_video": post["metadata"]["is_video"],
                "is_self": post["metadata"]["is_self"]
            })
    
    df = pd.DataFrame(posts_data)
    df.to_csv(f"{subreddit}_dataset.csv", index=False)
    
    return df
```

## Best Practices

1. **Rate Limiting**: Always respect rate limits. The server handles this automatically.

2. **Caching**: Use caching for frequently accessed data to improve performance.

3. **Error Handling**: Always handle potential errors:
   ```python
   try:
       result = await get_subreddit_feed(subreddit="example")
   except Exception as e:
       print(f"Error: {e}")
   ```

4. **Pagination**: For large datasets, use pagination:
   ```python
   all_posts = []
   after = None
   
   for _ in range(4):  # Get 4 pages
       result = await get_subreddit_feed(
           subreddit="python",
           after=after,
           limit=100
       )
       data = json.loads(result[0].text)
       all_posts.extend(data["posts"])
       after = data["pagination"]["after"]
       
       if not after:
           break
   ```

5. **Efficient Queries**: Request only the data you need by using appropriate limits and filters.