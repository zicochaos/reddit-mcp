"""Unit tests for Reddit MCP Server models."""

import pytest
from datetime import datetime

from models import (
    Author, Subreddit, Stats, Metadata, Post, Comment,
    SortType, TimeFilter, ContentType
)


class TestAuthor:
    """Test Author model."""
    
    def test_from_dict(self):
        """Test creating Author from dictionary."""
        data = {
            "author": "testuser",
            "author_fullname": "t2_abc123"
        }
        author = Author.from_dict(data)
        
        assert author.username == "testuser"
        assert author.id == "t2_abc123"
    
    def test_from_dict_missing_fields(self):
        """Test handling missing fields."""
        author = Author.from_dict({})
        
        assert author.username == ""
        assert author.id == ""


class TestSubreddit:
    """Test Subreddit model."""
    
    def test_from_dict(self):
        """Test creating Subreddit from dictionary."""
        data = {
            "subreddit": "python",
            "subreddit_id": "t5_2qh0y",
            "subreddit_subscribers": 1234567
        }
        subreddit = Subreddit.from_dict(data)
        
        assert subreddit.name == "python"
        assert subreddit.id == "t5_2qh0y"
        assert subreddit.subscribers == 1234567
    
    def test_from_dict_no_subscribers(self):
        """Test handling missing subscribers."""
        data = {
            "subreddit": "test",
            "subreddit_id": "t5_test"
        }
        subreddit = Subreddit.from_dict(data)
        
        assert subreddit.name == "test"
        assert subreddit.id == "t5_test"
        assert subreddit.subscribers is None
    
    def test_from_dict_string_float_subscribers(self):
        """Test creating Subreddit with string float subscriber count."""
        data = {
            "subreddit": "python",
            "subreddit_id": "t5_2qh0y",
            "subreddit_subscribers": "1000000.0"
        }
        subreddit = Subreddit.from_dict(data)
        
        assert subreddit.name == "python"
        assert subreddit.id == "t5_2qh0y"
        assert subreddit.subscribers == 1000000


class TestStats:
    """Test Stats model."""
    
    def test_from_post_dict(self):
        """Test creating Stats from post dictionary."""
        data = {
            "score": 1234,
            "ups": 1300,
            "downs": 66,
            "upvote_ratio": 0.95,
            "num_comments": 456,
            "num_crossposts": 3,
            "total_awards_received": 2
        }
        stats = Stats.from_post_dict(data)
        
        assert stats.score == 1234
        assert stats.upvotes == 1300
        assert stats.downvotes == 66
        assert stats.upvote_ratio == 0.95
        assert stats.comments == 456
        assert stats.crossposts == 3
        assert stats.awards == 2
    
    def test_from_comment_dict(self):
        """Test creating Stats from comment dictionary."""
        data = {
            "score": 123,
            "ups": 130,
            "downs": 7,
            "total_awards_received": 1
        }
        stats = Stats.from_comment_dict(data)
        
        assert stats.score == 123
        assert stats.upvotes == 130
        assert stats.downvotes == 7
        assert stats.awards == 1
        assert stats.comments is None
        assert stats.crossposts is None
    
    def test_from_dict_defaults(self):
        """Test default values for missing fields."""
        stats = Stats.from_post_dict({})
        
        assert stats.score == 0
        assert stats.upvotes == 0
        assert stats.downvotes == 0
        assert stats.upvote_ratio is None
        assert stats.comments is None
        assert stats.crossposts is None
        assert stats.awards is None
    
    def test_from_dict_string_floats(self):
        """Test Stats creation with string float values."""
        data = {
            "score": "99.0",
            "ups": "123.5",
            "downs": "10.0",
            "num_comments": "45.0",
            "num_crossposts": "2.0",
            "total_awards_received": "3.0"
        }
        
        stats = Stats.from_post_dict(data)
        
        assert stats.score == 99
        assert stats.upvotes == 123
        assert stats.downvotes == 10
        assert stats.comments == 45
        assert stats.crossposts == 2
        assert stats.awards == 3


class TestMetadata:
    """Test Metadata model."""
    
    def test_from_dict_post(self):
        """Test creating Metadata from post dictionary."""
        data = {
            "created_utc": 1234567890.0,
            "edited": False,
            "is_video": True,
            "is_self": False,
            "over_18": False,
            "spoiler": True,
            "stickied": False,
            "locked": False,
            "archived": False,
            "quarantine": False,
            "hidden": False,
            "pinned": True
        }
        metadata = Metadata.from_dict(data, is_post=True)
        
        assert metadata.created_utc == 1234567890.0
        assert metadata.edited is False
        assert metadata.is_video is True
        assert metadata.is_self is False
        assert metadata.over_18 is False
        assert metadata.spoiler is True
        assert metadata.stickied is False
        assert metadata.locked is False
        assert metadata.archived is False
        assert metadata.quarantine is False
        assert metadata.hidden is False
        assert metadata.pinned is True
    
    def test_from_dict_comment(self):
        """Test creating Metadata from comment dictionary."""
        data = {
            "created_utc": 1234567890.0,
            "edited": 1234567900,
            "stickied": True,
            "locked": False,
            "archived": False,
            "quarantine": False
        }
        metadata = Metadata.from_dict(data, is_post=False)
        
        assert metadata.created_utc == 1234567890.0
        assert metadata.edited is True  # Non-false value becomes True
        assert metadata.stickied is True
        assert metadata.is_video is None  # Comment-specific fields are None
        assert metadata.is_self is None
    
    def test_created_datetime(self):
        """Test datetime conversion."""
        metadata = Metadata(created_utc=1234567890.0, edited=False)
        dt = metadata.created_datetime
        
        assert isinstance(dt, datetime)
        assert dt.timestamp() == 1234567890.0


class TestPost:
    """Test Post model."""
    
    @pytest.fixture
    def post_data(self):
        """Sample post data from Reddit API."""
        return {
            "name": "t3_test123",
            "title": "Test Post Title",
            "selftext": "This is the post content",
            "url": "https://reddit.com/r/test/comments/test123/",
            "author": "testauthor",
            "author_fullname": "t2_author123",
            "subreddit": "test",
            "subreddit_id": "t5_test",
            "subreddit_subscribers": 10000,
            "score": 100,
            "ups": 110,
            "downs": 10,
            "upvote_ratio": 0.91,
            "num_comments": 25,
            "num_crossposts": 2,
            "total_awards_received": 1,
            "domain": "self.test",
            "link_flair_text": "Discussion",
            "media_embed": {},
            "thumbnail": "self",
            "preview": None,
            "created_utc": 1234567890.0,
            "edited": False,
            "is_video": False,
            "is_self": True,
            "over_18": False,
            "spoiler": False,
            "stickied": False,
            "locked": False,
            "archived": False,
            "quarantine": False,
            "hidden": False,
            "pinned": False
        }
    
    def test_from_dict(self, post_data):
        """Test creating Post from dictionary."""
        post = Post.from_dict(post_data)
        
        assert post.id == "t3_test123"
        assert post.title == "Test Post Title"
        assert post.description == "This is the post content"
        assert post.link == "https://reddit.com/r/test/comments/test123/"
        assert post.author.username == "testauthor"
        assert post.author.id == "t2_author123"
        assert post.subreddit.name == "test"
        assert post.subreddit.id == "t5_test"
        assert post.subreddit.subscribers == 10000
        assert post.stats.score == 100
        assert post.stats.upvotes == 110
        assert post.stats.downvotes == 10
        assert post.stats.upvote_ratio == 0.91
        assert post.metadata.created_utc == 1234567890.0
        assert post.domain == "self.test"
        assert post.flair_text == "Discussion"
        assert post.thumbnail is None  # "self" gets filtered out
    
    def test_from_dict_minimal(self):
        """Test creating Post with minimal data."""
        post = Post.from_dict({})
        
        assert post.id == ""
        assert post.title == ""
        assert post.description == ""
        assert post.link == ""
        assert post.author.username == ""
        assert post.stats.score == 0
    
    def test_to_dict(self, post_data):
        """Test converting Post to dictionary."""
        post = Post.from_dict(post_data)
        result = post.to_dict()
        
        assert result["id"] == "t3_test123"
        assert result["title"] == "Test Post Title"
        assert result["author"]["username"] == "testauthor"
        assert result["subreddit"]["name"] == "test"
        assert result["stats"]["score"] == 100
        assert result["metadata"]["created_utc"] == 1234567890.0
        assert isinstance(result["metadata"]["created_datetime"], str)
    
    def test_thumbnail_filtering(self):
        """Test thumbnail filtering for special values."""
        # Test that special thumbnail values are filtered
        special_thumbnails = ["self", "default", "nsfw", "spoiler"]
        
        for thumb in special_thumbnails:
            post = Post.from_dict({"thumbnail": thumb})
            assert post.thumbnail is None
        
        # Test that real thumbnails are kept
        post = Post.from_dict({"thumbnail": "https://example.com/thumb.jpg"})
        assert post.thumbnail == "https://example.com/thumb.jpg"


class TestComment:
    """Test Comment model."""
    
    @pytest.fixture
    def comment_data(self):
        """Sample comment data from Reddit API."""
        return {
            "name": "t1_comment123",
            "body": "This is a comment",
            "body_html": "<p>This is a comment</p>",
            "author": "commenter",
            "author_fullname": "t2_commenter123",
            "link_id": "t3_post123",
            "link_title": "Original Post Title",
            "link_permalink": "/r/test/comments/post123/",
            "subreddit": "test",
            "subreddit_id": "t5_test",
            "score": 50,
            "ups": 55,
            "downs": 5,
            "total_awards_received": 0,
            "created_utc": 1234567900.0,
            "edited": False,
            "stickied": False,
            "locked": False,
            "archived": False,
            "quarantine": False,
            "parent_id": "t3_post123"
        }
    
    def test_from_dict(self, comment_data):
        """Test creating Comment from dictionary."""
        comment = Comment.from_dict(comment_data)
        
        assert comment.id == "t1_comment123"
        assert comment.body == "This is a comment"
        assert comment.body_html == "<p>This is a comment</p>"
        assert comment.author.username == "commenter"
        assert comment.author.id == "t2_commenter123"
        assert comment.post_id == "t3_post123"
        assert comment.post_title == "Original Post Title"
        assert comment.post_link == "/r/test/comments/post123/"
        assert comment.subreddit.name == "test"
        assert comment.stats.score == 50
        assert comment.metadata.created_utc == 1234567900.0
        assert comment.parent_id == "t3_post123"
        assert comment.replies == []
    
    def test_from_dict_minimal(self):
        """Test creating Comment with minimal data."""
        comment = Comment.from_dict({})
        
        assert comment.id == ""
        assert comment.body == ""
        assert comment.body_html is None
        assert comment.author.username == ""
        assert comment.stats.score == 0
        assert comment.replies == []
    
    def test_to_dict(self, comment_data):
        """Test converting Comment to dictionary."""
        comment = Comment.from_dict(comment_data)
        result = comment.to_dict()
        
        assert result["id"] == "t1_comment123"
        assert result["body"] == "This is a comment"
        assert result["author"]["username"] == "commenter"
        assert result["post"]["id"] == "t3_post123"
        assert result["stats"]["score"] == 50
        assert "replies" not in result  # No replies by default
    
    def test_to_dict_with_replies(self, comment_data):
        """Test converting Comment with replies to dictionary."""
        parent = Comment.from_dict(comment_data)
        
        # Add a reply
        reply_data = comment_data.copy()
        reply_data["name"] = "t1_reply123"
        reply_data["body"] = "This is a reply"
        reply_data["parent_id"] = "t1_comment123"
        
        reply = Comment.from_dict(reply_data)
        parent.replies.append(reply)
        
        result = parent.to_dict(include_replies=True)
        
        assert "replies" in result
        assert len(result["replies"]) == 1
        assert result["replies"][0]["id"] == "t1_reply123"
        assert result["replies"][0]["body"] == "This is a reply"
    
    def test_to_dict_without_replies(self, comment_data):
        """Test excluding replies from dictionary."""
        parent = Comment.from_dict(comment_data)
        reply = Comment.from_dict(comment_data)
        parent.replies.append(reply)
        
        result = parent.to_dict(include_replies=False)
        
        assert "replies" not in result


class TestTypeDefinitions:
    """Test type definitions."""
    
    def test_sort_type_values(self):
        """Test SortType literal values."""
        # This is mainly for documentation, actual validation happens at runtime
        valid_sorts = ["hot", "new", "top", "rising", "controversial", "best", "relevance"]
        # Just verify the type exists
        assert SortType is not None
    
    def test_time_filter_values(self):
        """Test TimeFilter literal values."""
        valid_filters = ["hour", "day", "week", "month", "year", "all"]
        # Just verify the type exists
        assert TimeFilter is not None
    
    def test_content_type_values(self):
        """Test ContentType literal values."""
        valid_types = ["posts", "comments", "all"]
        # Just verify the type exists
        assert ContentType is not None