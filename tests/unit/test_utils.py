"""Unit tests for utility functions."""

import pytest

from utils import (
    validate_subreddit_name,
    validate_username,
    parse_reddit_listing,
    parse_posts_from_listing,
    parse_comments_from_listing,
    parse_comment_tree,
    truncate_text,
    sanitize_html,
    format_number,
    _parse_comment_listing
)
from models import Post, Comment


class TestValidation:
    """Test validation functions."""
    
    def test_validate_subreddit_name_valid(self):
        """Test validating valid subreddit names."""
        # Valid names
        assert validate_subreddit_name("python") == "python"
        assert validate_subreddit_name("test_sub") == "test_sub"
        assert validate_subreddit_name("AskReddit") == "AskReddit"
        assert validate_subreddit_name("a1") == "a1"  # 2 chars minimum
        assert validate_subreddit_name("a" * 21) == "a" * 21  # 21 chars maximum
        
        # With prefixes (should be removed)
        assert validate_subreddit_name("r/python") == "python"
        assert validate_subreddit_name("/r/python") == "python"
        assert validate_subreddit_name("  r/python  ") == "python"
    
    def test_validate_subreddit_name_invalid(self):
        """Test validating invalid subreddit names."""
        # Too short
        with pytest.raises(ValueError, match="Invalid subreddit name"):
            validate_subreddit_name("a")
        
        # Too long
        with pytest.raises(ValueError, match="Invalid subreddit name"):
            validate_subreddit_name("a" * 22)
        
        # Invalid characters
        with pytest.raises(ValueError, match="Invalid subreddit name"):
            validate_subreddit_name("test-sub")
        
        with pytest.raises(ValueError, match="Invalid subreddit name"):
            validate_subreddit_name("test sub")
        
        with pytest.raises(ValueError, match="Invalid subreddit name"):
            validate_subreddit_name("test@sub")
        
        # Empty after cleaning
        with pytest.raises(ValueError, match="Invalid subreddit name"):
            validate_subreddit_name("r/")
    
    def test_validate_username_valid(self):
        """Test validating valid usernames."""
        # Valid names
        assert validate_username("testuser") == "testuser"
        assert validate_username("test_user") == "test_user"
        assert validate_username("test-user") == "test-user"
        assert validate_username("User123") == "User123"
        assert validate_username("abc") == "abc"  # 3 chars minimum
        assert validate_username("a" * 20) == "a" * 20  # 20 chars maximum
        
        # With prefixes (should be removed)
        assert validate_username("u/testuser") == "testuser"
        assert validate_username("/u/testuser") == "testuser"
        assert validate_username("  u/testuser  ") == "testuser"
    
    def test_validate_username_invalid(self):
        """Test validating invalid usernames."""
        # Too short
        with pytest.raises(ValueError, match="Invalid username"):
            validate_username("ab")
        
        # Too long
        with pytest.raises(ValueError, match="Invalid username"):
            validate_username("a" * 21)
        
        # Invalid characters
        with pytest.raises(ValueError, match="Invalid username"):
            validate_username("test user")
        
        with pytest.raises(ValueError, match="Invalid username"):
            validate_username("test@user")
        
        with pytest.raises(ValueError, match="Invalid username"):
            validate_username("test.user")
        
        # Empty after cleaning
        with pytest.raises(ValueError, match="Invalid username"):
            validate_username("u/")


class TestParsing:
    """Test parsing functions."""
    
    def test_parse_reddit_listing(self):
        """Test parsing Reddit listing response."""
        # Valid listing
        data = {
            "data": {
                "children": [
                    {"kind": "t3", "data": {"title": "Post 1"}},
                    {"kind": "t1", "data": {"body": "Comment 1"}}
                ]
            }
        }
        result = parse_reddit_listing(data)
        assert len(result) == 2
        assert result[0]["kind"] == "t3"
        assert result[1]["kind"] == "t1"
        
        # Invalid structure
        assert parse_reddit_listing({}) == []
        assert parse_reddit_listing({"data": {}}) == []
        # When children is None, it's not in data["data"] so returns []
        assert parse_reddit_listing({"data": {"children": None}}) == []
        assert parse_reddit_listing("not a dict") == []
    
    def test_parse_posts_from_listing(self):
        """Test parsing posts from listing."""
        listing = [
            {
                "kind": "t3",
                "data": {
                    "name": "t3_test1",
                    "title": "Test Post 1",
                    "selftext": "Content 1",
                    "url": "https://reddit.com/1",
                    "author": "user1",
                    "author_fullname": "t2_user1",
                    "subreddit": "test",
                    "subreddit_id": "t5_test",
                    "score": 100,
                    "ups": 110,
                    "downs": 10,
                    "created_utc": 1234567890
                }
            },
            {
                "kind": "t1",  # Comment, should be skipped
                "data": {"body": "Comment"}
            },
            {
                "kind": "t3",
                "data": {
                    "name": "t3_test2",
                    "title": "Test Post 2",
                    "selftext": "Content 2",
                    "url": "https://reddit.com/2",
                    "author": "user2",
                    "author_fullname": "t2_user2",
                    "subreddit": "test",
                    "subreddit_id": "t5_test",
                    "score": 200,
                    "ups": 210,
                    "downs": 10,
                    "created_utc": 1234567890
                }
            }
        ]
        
        posts = parse_posts_from_listing(listing)
        assert len(posts) == 2
        assert all(isinstance(post, Post) for post in posts)
        assert posts[0].title == "Test Post 1"
        assert posts[1].title == "Test Post 2"
        
        # Test with invalid post data
        # Note: Post.from_dict creates posts with empty/default values rather than failing
        listing_with_invalid = [
            {"kind": "t3", "data": {}},  # Missing required fields - creates empty post
            {"kind": "t3"}  # Missing data - also creates empty post
        ]
        posts = parse_posts_from_listing(listing_with_invalid)
        assert len(posts) == 2  # Both create posts with default values
        assert all(post.title == "" for post in posts)  # But with empty titles
    
    def test_parse_comments_from_listing(self):
        """Test parsing comments from listing."""
        listing = [
            {
                "kind": "t1",
                "data": {
                    "name": "t1_test1",
                    "body": "Comment 1",
                    "author": "user1",
                    "author_fullname": "t2_user1",
                    "link_id": "t3_post1",
                    "link_title": "Post Title",
                    "link_permalink": "/r/test/comments/1/",
                    "subreddit": "test",
                    "subreddit_id": "t5_test",
                    "score": 50,
                    "ups": 55,
                    "downs": 5,
                    "created_utc": 1234567890
                }
            },
            {
                "kind": "t3",  # Post, should be skipped
                "data": {"title": "Post"}
            },
            {
                "kind": "t1",
                "data": {
                    "name": "t1_test2",
                    "body": "Comment 2",
                    "author": "user2",
                    "author_fullname": "t2_user2",
                    "link_id": "t3_post1",
                    "link_title": "Post Title",
                    "link_permalink": "/r/test/comments/1/",
                    "subreddit": "test",
                    "subreddit_id": "t5_test",
                    "score": 25,
                    "ups": 30,
                    "downs": 5,
                    "created_utc": 1234567890
                }
            }
        ]
        
        comments = parse_comments_from_listing(listing)
        assert len(comments) == 2
        assert all(isinstance(comment, Comment) for comment in comments)
        assert comments[0].body == "Comment 1"
        assert comments[1].body == "Comment 2"
    
    def test_parse_comment_tree(self):
        """Test parsing nested comment tree."""
        # Reddit response format: [post_listing, comment_listing]
        data = [
            {
                "data": {
                    "children": [
                        {"kind": "t3", "data": {"title": "Post"}}
                    ]
                }
            },
            {
                "data": {
                    "children": [
                        {
                            "kind": "t1",
                            "data": {
                                "name": "t1_comment1",
                                "body": "Top level comment",
                                "author": "user1",
                                "author_fullname": "t2_user1",
                                "link_id": "t3_post1",
                                "link_title": "Post",
                                "link_permalink": "/r/test/1/",
                                "subreddit": "test",
                                "subreddit_id": "t5_test",
                                "score": 10,
                                "ups": 10,
                                "downs": 0,
                                "created_utc": 1234567890,
                                "replies": {
                                    "data": {
                                        "children": [
                                            {
                                                "kind": "t1",
                                                "data": {
                                                    "name": "t1_reply1",
                                                    "body": "Reply",
                                                    "author": "user2",
                                                    "author_fullname": "t2_user2",
                                                    "link_id": "t3_post1",
                                                    "link_title": "Post",
                                                    "link_permalink": "/r/test/1/",
                                                    "subreddit": "test",
                                                    "subreddit_id": "t5_test",
                                                    "score": 5,
                                                    "ups": 5,
                                                    "downs": 0,
                                                    "created_utc": 1234567890
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        ]
        
        # Parse with depth
        comments = parse_comment_tree(data, depth=2)
        assert len(comments) == 1
        assert comments[0].body == "Top level comment"
        assert len(comments[0].replies) == 1
        assert comments[0].replies[0].body == "Reply"
        
        # Parse without depth
        comments = parse_comment_tree(data, depth=0)
        assert len(comments) == 1
        assert len(comments[0].replies) == 0  # Replies not parsed
    
    def test_parse_comment_tree_edge_cases(self):
        """Test parse_comment_tree with edge cases."""
        # Empty data
        assert parse_comment_tree([]) == []
        assert parse_comment_tree(None) == []
        
        # Single listing (not the expected format)
        single_listing = {
            "data": {
                "children": [
                    {
                        "kind": "t1",
                        "data": {
                            "name": "t1_test",
                            "body": "Comment",
                            "author": "user",
                            "author_fullname": "t2_user",
                            "link_id": "t3_post",
                            "link_title": "Post",
                            "link_permalink": "/r/test/1/",
                            "subreddit": "test",
                            "subreddit_id": "t5_test",
                            "score": 1,
                            "ups": 1,
                            "downs": 0,
                            "created_utc": 1234567890
                        }
                    }
                ]
            }
        }
        comments = parse_comment_tree([single_listing])
        assert len(comments) == 1


class TestTextUtilities:
    """Test text manipulation utilities."""
    
    def test_truncate_text(self):
        """Test text truncation."""
        # Text shorter than limit
        text = "Short text"
        assert truncate_text(text, max_length=20) == "Short text"
        
        # Text exactly at limit
        text = "a" * 10
        assert truncate_text(text, max_length=10) == "a" * 10
        
        # Text longer than limit
        text = "This is a very long text that needs truncation"
        result = truncate_text(text, max_length=20)
        assert result == "This is a very lo..."
        assert len(result) == 20
        
        # Custom suffix
        result = truncate_text(text, max_length=20, suffix="[...]")
        assert result == "This is a very [...]"
        assert len(result) == 20
        
        # Edge case: max_length less than suffix
        result = truncate_text("Hello", max_length=2, suffix="...")
        assert result == "..."  # Just the suffix
    
    def test_sanitize_html(self):
        """Test HTML sanitization."""
        # None input
        assert sanitize_html(None) is None
        assert sanitize_html("") == ""
        
        # Remove script tags
        html = 'Hello <script>alert("xss")</script> World'
        assert sanitize_html(html) == "Hello  World"
        
        # Remove script tags with attributes
        html = 'Hello <script type="text/javascript">alert("xss")</script> World'
        assert sanitize_html(html) == "Hello  World"
        
        # Remove style tags
        html = 'Hello <style>body { color: red; }</style> World'
        assert sanitize_html(html) == "Hello  World"
        
        # Remove event handlers
        html = '<div onclick="alert(1)">Click me</div>'
        assert sanitize_html(html) == '<div>Click me</div>'
        
        html = '<img src="test.jpg" onload="alert(1)" onerror="alert(2)">'
        assert sanitize_html(html) == '<img src="test.jpg">'
        
        # Preserve normal HTML
        html = '<p>Hello <strong>World</strong></p>'
        assert sanitize_html(html) == '<p>Hello <strong>World</strong></p>'
        
        # Multiple malicious elements
        html = '''
        <p>Normal text</p>
        <script>bad();</script>
        <div onclick="hack()">Click</div>
        <style>* { display: none; }</style>
        <p>More text</p>
        '''
        result = sanitize_html(html)
        assert "<script>" not in result
        assert "<style>" not in result
        assert "onclick=" not in result
        assert "<p>Normal text</p>" in result
        assert "<p>More text</p>" in result
    
    def test_format_number(self):
        """Test number formatting."""
        # Small numbers (no abbreviation)
        assert format_number(0) == "0"
        assert format_number(999) == "999"
        assert format_number(-500) == "-500"
        
        # Thousands
        assert format_number(1_000) == "1.0K"
        assert format_number(1_500) == "1.5K"
        assert format_number(999_999) == "1000.0K"  # Just under 1M
        assert format_number(-2_500) == "-2.5K"
        
        # Millions
        assert format_number(1_000_000) == "1.0M"
        assert format_number(2_500_000) == "2.5M"
        assert format_number(999_999_999) == "1000.0M"
        assert format_number(-1_500_000) == "-1.5M"
        
        # Edge cases
        assert format_number(1_234) == "1.2K"
        assert format_number(12_345) == "12.3K"
        assert format_number(123_456) == "123.5K"
        assert format_number(1_234_567) == "1.2M"