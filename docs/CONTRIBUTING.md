# Contributing to Reddit MCP Server

Thank you for your interest in contributing to the Reddit MCP Server! This guide will help you get started.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [How to Contribute](#how-to-contribute)
5. [Pull Request Process](#pull-request-process)
6. [Code Style Guidelines](#code-style-guidelines)
7. [Testing Guidelines](#testing-guidelines)
8. [Documentation](#documentation)
9. [Community](#community)

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors include:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Basic understanding of Reddit's API
- Familiarity with async Python programming

### First Steps

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/reddit-mcp.git
   cd reddit-mcp
   ```
3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/reddit-mcp.git
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Development Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools
```

### 3. Install Pre-commit Hooks

```bash
pre-commit install
```

### 4. Run Tests

```bash
pytest
```

### 5. Set Up Your Editor

We recommend:
- **VS Code** with Python extension
- **PyCharm** Professional or Community
- **Vim/Neovim** with Python LSP

Editor settings:
- Line length: 88 characters (Black default)
- Use spaces, not tabs
- 4 spaces per indentation level

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

1. **Clear title and description**
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **System information:**
   ```python
   import sys
   import platform
   print(f"Python: {sys.version}")
   print(f"Platform: {platform.platform()}")
   ```
6. **Configuration used**
7. **Full error messages and stack traces**

**Bug Report Template:**
```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Configure server with...
2. Call tool with...
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version:
- OS:
- Reddit MCP version:

## Additional Context
Any other relevant information
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

1. **Use case:** Why is this needed?
2. **Proposed solution:** How should it work?
3. **Alternatives considered:** What other approaches did you think about?
4. **Additional context:** Any examples or mockups

### Contributing Code

1. **Find an issue** labeled `good first issue` or `help wanted`
2. **Comment on the issue** to claim it
3. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes**
5. **Write/update tests**
6. **Update documentation**
7. **Submit a pull request**

## Pull Request Process

### Before Submitting

1. **Update your fork:**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Rebase your feature branch:**
   ```bash
   git checkout feature/your-feature
   git rebase main
   ```

3. **Run tests:**
   ```bash
   pytest
   mypy .
   black --check .
   ruff .
   ```

4. **Update documentation** if needed

### PR Requirements

Your PR should:
- Have a clear title and description
- Reference any related issues
- Pass all CI checks
- Include tests for new functionality
- Update documentation as needed
- Follow code style guidelines

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No new warnings
```

## Code Style Guidelines

### Python Style

We use [Black](https://black.readthedocs.io/) for code formatting and [Ruff](https://github.com/astral-sh/ruff) for linting.

**Key conventions:**
```python
# Imports grouped and sorted
import asyncio
import json
from typing import Dict, List, Optional

import httpx
from mcp.server import Server

from config import config
from models import Post, Comment


# Type hints for all functions
async def get_posts(subreddit: str, limit: int = 25) -> List[Post]:
    """Get posts from a subreddit.
    
    Args:
        subreddit: The subreddit name
        limit: Maximum number of posts
        
    Returns:
        List of Post objects
        
    Raises:
        RedditAPIError: If the API request fails
    """
    pass


# Descriptive variable names
user_posts = await get_user_content(username)
# Not: posts = await get_content(u)


# Error handling
try:
    result = await client.get(url)
except httpx.TimeoutException:
    logger.error(f"Request timed out: {url}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise RedditAPIError(f"Failed to fetch {url}") from e
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(cache): add TTL support for cache entries

- Implement time-based expiration
- Add cleanup task for expired entries
- Update tests for TTL functionality

Closes #45
```

```
fix(client): handle rate limit headers correctly

Previously, the client would crash when Reddit returned
non-standard rate limit headers. This fix adds proper
validation and fallback values.
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/              # Unit tests
│   ├── test_models.py
│   ├── test_cache.py
│   └── test_utils.py
├── integration/       # Integration tests
│   ├── test_client.py
│   └── test_server.py
└── fixtures/         # Test data
    └── reddit_responses.json
```

### Writing Tests

```python
import pytest
from models import Post

class TestPost:
    """Test Post model."""
    
    @pytest.fixture
    def post_data(self):
        """Sample post data."""
        return {
            "name": "t3_test123",
            "title": "Test Post",
            "author": "testuser",
            # ... more fields
        }
    
    def test_from_dict(self, post_data):
        """Test creating Post from dictionary."""
        post = Post.from_dict(post_data)
        assert post.id == "t3_test123"
        assert post.title == "Test Post"
    
    def test_from_dict_missing_fields(self):
        """Test handling missing fields."""
        post = Post.from_dict({})
        assert post.id == ""
        assert post.title == ""
    
    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async operations."""
        result = await some_async_function()
        assert result is not None
```

### Test Coverage

Aim for >80% test coverage:

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def calculate_karma(posts: List[Post], comments: List[Comment]) -> int:
    """Calculate total karma from posts and comments.
    
    Args:
        posts: List of user posts
        comments: List of user comments
        
    Returns:
        Total karma score
        
    Raises:
        ValueError: If posts or comments contain invalid data
        
    Example:
        >>> posts = [Post(score=100), Post(score=50)]
        >>> comments = [Comment(score=25), Comment(score=10)]
        >>> calculate_karma(posts, comments)
        185
    """
```

### Documentation Updates

When adding features, update:
1. **README.md** - Overview and quick start
2. **API_REFERENCE.md** - Detailed API documentation
3. **USAGE_EXAMPLES.md** - Practical examples
4. **Inline comments** - Complex logic explanation

### Building Documentation

```bash
# Generate API documentation
pdoc --html --output-dir docs/api .

# Check documentation
python -m doctest -v *.py
```

## Community

### Getting Help

- **GitHub Issues:** For bugs and feature requests
- **Discussions:** For questions and ideas
- **Discord/Slack:** [If applicable]

### Code Reviews

All submissions require review. We use GitHub pull requests for this purpose. Consult [GitHub Help](https://help.github.com/articles/about-pull-requests/) for more information.

**Review checklist:**
- [ ] Code follows project style
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security issues
- [ ] Performance impact considered
- [ ] Breaking changes documented

### Release Process

1. **Version bump** following [Semantic Versioning](https://semver.org/)
2. **Update CHANGELOG.md**
3. **Create release PR**
4. **Tag release after merge**
5. **Publish to PyPI** (if applicable)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Reddit MCP Server! 🎉