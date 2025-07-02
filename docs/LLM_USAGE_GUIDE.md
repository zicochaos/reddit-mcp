# Reddit MCP Server - LLM Usage Guide

This guide provides examples of how to use the Reddit MCP Server with Large Language Models (LLMs) like Claude, GPT-4, or other AI assistants that support the Model Context Protocol.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Tool-Specific Examples](#tool-specific-examples)
- [Common Use Cases](#common-use-cases)
- [Advanced Scenarios](#advanced-scenarios)
- [Prompt Templates](#prompt-templates)
- [Response Handling](#response-handling)
- [Best Practices](#best-practices)

## Basic Usage

When using an LLM with the Reddit MCP Server, the AI assistant will have access to five main tools for interacting with Reddit data.

### Example Conversation Starters

```
User: "What's trending on Reddit right now?"
User: "Show me the top posts from r/technology this week"
User: "What is r/python about?"
User: "Find discussions about machine learning on Reddit"
User: "What are people saying about the latest iPhone?"
```

## Tool-Specific Examples

### 1. get_subreddit_feed

#### Getting Frontpage Posts
```
User: "What's hot on Reddit's frontpage right now?"

LLM will use: get_subreddit_feed with no subreddit parameter
Response: List of trending posts from all of Reddit
```

#### Subreddit-Specific Posts
```
User: "Show me the newest posts in r/worldnews"

LLM will use: get_subreddit_feed
{
  "subreddit": "worldnews",
  "sort": "new",
  "limit": 10
}
```

#### Time-Filtered Top Posts
```
User: "What were the top posts in r/science this month?"

LLM will use: get_subreddit_feed
{
  "subreddit": "science",
  "sort": "top",
  "time_filter": "month",
  "limit": 25
}
```

### 2. get_subreddit_info

```
User: "Tell me about the r/AskReddit subreddit"

LLM will use: get_subreddit_info
{
  "subreddit": "AskReddit"
}

Response includes:
- Description and rules
- Subscriber count
- Active user count
- Creation date
- Whether it's NSFW
- Subreddit type (public/private/restricted)
```

### 3. search_reddit

#### Global Search
```
User: "Find Reddit discussions about climate change"

LLM will use: search_reddit
{
  "query": "climate change",
  "subreddit": "all",
  "sort": "relevance",
  "limit": 20
}
```

#### Subreddit-Specific Search
```
User: "Search for Python tutorials in r/learnpython"

LLM will use: search_reddit
{
  "query": "tutorial",
  "subreddit": "learnpython",
  "sort": "top",
  "time_filter": "year"
}
```

### 4. get_post_comments

```
User: "What are people saying about this post: t3_abc123"

LLM will use: get_post_comments
{
  "post_id": "t3_abc123",
  "sort": "best",
  "limit": 50,
  "depth": 2
}

Response includes:
- Full post details (title, content, author, stats)
- Nested comment threads
- Comment scores and metadata
```

### 5. get_user_feed

```
User: "What has u/spez been posting lately?"

LLM will use: get_user_feed
{
  "username": "spez",
  "content_type": "posts",
  "sort": "new",
  "limit": 10
}
```

## Common Use Cases

### 1. Trend Analysis
```
User: "What are the trending topics in r/technology today vs last week?"

The LLM will:
1. Get current hot posts from r/technology
2. Get top posts from last week
3. Compare and analyze trends
```

### 2. Sentiment Analysis
```
User: "What's the general sentiment about the new Tesla model in r/cars?"

The LLM will:
1. Search for "Tesla model" in r/cars
2. Analyze post titles and get comments for top posts
3. Summarize the overall sentiment
```

### 3. Research and Information Gathering
```
User: "I need to learn about machine learning. What are the best resources on Reddit?"

The LLM will:
1. Get info about r/MachineLearning
2. Search for "beginner guide" or "resources" in relevant subreddits
3. Get top posts of all time from r/learnmachinelearning
4. Compile a comprehensive resource list
```

### 4. Community Discovery
```
User: "Find me active Reddit communities about gardening"

The LLM will:
1. Search for "gardening" across Reddit
2. Identify subreddits from the results
3. Get info about each discovered subreddit
4. Rank by activity and subscriber count
```

## Advanced Scenarios

### Multi-Step Analysis
```
User: "Analyze the discussion quality in r/science vs r/askscience"

The LLM will:
1. Get subreddit info for both
2. Fetch recent posts from each
3. Sample comments from top posts
4. Compare moderation, comment depth, and scientific accuracy
```

### Temporal Analysis
```
User: "How has the discussion about AI changed in r/technology over the past year?"

The LLM will:
1. Search for "AI" or "artificial intelligence" with different time filters
2. Analyze posting frequency
3. Track sentiment changes
4. Identify emerging subtopics
```

### Cross-Subreddit Comparison
```
User: "Compare how r/politics and r/conservative are discussing the same news event"

The LLM will:
1. Search for the event in both subreddits
2. Get top posts and comments from each
3. Analyze differences in framing, sentiment, and focus
```

## Prompt Templates

### For Information Seeking
```
"What is [subreddit] about and how active is it?"
"Find the most helpful posts about [topic] on Reddit"
"What are the current discussions about [topic] in [subreddit]?"
```

### For Analysis
```
"Analyze the sentiment towards [topic] in [subreddit]"
"Compare discussions about [topic] across different subreddits"
"What are the trending topics in [subreddit] this [timeframe]?"
```

### For Content Discovery
```
"Show me the best [type] content from [subreddit] this [timeframe]"
"Find controversial discussions about [topic]"
"What are the most awarded posts about [topic]?"
```

## Response Handling

### Parsing Post Data
The LLM should focus on:
- Title and description for context
- Score and comment count for popularity
- Created date for recency
- Author for credibility
- Flair for categorization

### Parsing Comment Data
The LLM should analyze:
- Comment score for quality/agreement
- Reply depth for engagement
- Author consistency
- Edit status for reliability

### Handling Large Responses
When dealing with many posts or comments:
1. Summarize key themes
2. Highlight most relevant/popular items
3. Group similar content
4. Provide statistical overview

## Best Practices

### 1. Efficient Tool Usage
- Use search_reddit before get_post_comments to find relevant posts
- Get subreddit_info before analyzing a community
- Use appropriate limits to avoid overwhelming responses

### 2. Context Awareness
- Consider subreddit rules and culture when interpreting content
- Note if content is from NSFW subreddits
- Check post age for relevance

### 3. Error Handling
- Handle private/banned subreddits gracefully
- Explain rate limiting to users
- Suggest alternatives for unavailable content

### 4. Ethical Considerations
- Respect user privacy (don't deep-dive into user histories without reason)
- Note when content may be biased or from specific viewpoints
- Warn about NSFW or potentially disturbing content

## Example Full Conversation

```
User: "I'm interested in starting a small garden. Can you help me find good Reddit resources?"

LLM: "I'll help you find great gardening resources on Reddit. Let me start by checking out the main gardening communities."

[LLM uses get_subreddit_info for "gardening"]

LLM: "r/gardening is a very active community with over 4.5 million members\! It's focused on all aspects of gardening from vegetables to flowers. Let me also check some related communities."

[LLM uses search_reddit for "beginner gardening small space"]

LLM: "I found some great posts for beginners. Now let me check r/UrbanGardening since you mentioned a small garden."

[LLM uses get_subreddit_info for "UrbanGardening"]
[LLM uses get_subreddit_feed for "UrbanGardening" with sort="top" and time_filter="year"]

LLM: "Based on my research, here are the best Reddit resources for starting a small garden:

1. **r/gardening** (4.5M members) - The main hub for all things gardening
2. **r/UrbanGardening** (245K members) - Perfect for small spaces, balconies, and containers
3. **r/vegetablegardening** (890K members) - If you want to grow food
4. **r/IndoorGarden** (420K members) - Great for apartment gardening

Top beginner tips from Reddit:
- Start small with easy plants like herbs, lettuce, or tomatoes
- Container gardening is perfect for small spaces
- Check out the pinned beginner guides in r/gardening
- The community is very helpful for troubleshooting

Would you like me to find specific posts about any particular aspect of gardening?"
```

## Troubleshooting

### Common Issues

1. **Rate Limiting**
   - The server implements automatic retry with backoff
   - LLM should inform users about delays
   - Suggest reducing request frequency

2. **Private Subreddits**
   - Return clear error messages
   - Suggest alternative public communities
   - Check if subreddit was banned or made private

3. **Large Data Sets**
   - Use pagination for large result sets
   - Implement progressive loading
   - Summarize when appropriate

4. **Stale Data**
   - Cache TTL is 5 minutes by default
   - Inform users about data freshness
   - Suggest refreshing for real-time needs

## Integration Tips

### For Developers

1. **Response Parsing**
```python
# Example parsing post data
posts = response["posts"]
for post in posts:
    title = post["title"]
    score = post["stats"]["score"]
    comments = post["stats"]["comments"]
```

2. **Error Handling**
```python
try:
    result = await get_subreddit_feed(subreddit="example")
except RedditNotFoundError:
    # Handle non-existent subreddit
except RedditForbiddenError:
    # Handle private/restricted access
```

3. **Efficient Queries**
- Batch related requests when possible
- Use caching to avoid repeated calls
- Implement progressive enhancement

### For LLM Developers

1. **Tool Selection Logic**
   - Prioritize get_subreddit_info for community analysis
   - Use search before diving into specific posts
   - Chain tools for comprehensive analysis

2. **Response Formatting**
   - Present data in digestible chunks
   - Highlight key metrics (scores, comment counts)
   - Group similar content themes

3. **User Experience**
   - Acknowledge tool usage transparently
   - Explain delays or limitations
   - Offer follow-up actions

## Conclusion

The Reddit MCP Server provides powerful tools for LLMs to interact with Reddit data. By following these usage patterns and best practices, you can create rich, informative experiences that help users discover, analyze, and understand Reddit content effectively.

Remember to always respect Reddit's terms of service, user privacy, and community guidelines when using these tools.

