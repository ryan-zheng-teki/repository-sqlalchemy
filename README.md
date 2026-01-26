# repository_sqlalchemy

repository_sqlalchemy is a small library that simplifies SQLAlchemy usage with automatic transaction and session management. It provides a base repository pattern implementation, similar to JPA in the Java world.

## Features

- Base repository pattern for common database operations
- Automatic session management using context variables
- Transaction management with a convenient decorator
- Support for nested transactions and savepoints
- No need for manual session commits or rollbacks

## Installation

You can install repository_sqlalchemy using pip:

```bash
pip install repository_sqlalchemy
```

## Development (uv)

```bash
uv sync --dev
uv run pytest
```

## Release (Tag-Based)

We use a tag-based release flow:

```bash
git tag -a v1.2.3 -m "v1.2.3"
git push origin v1.2.3
```

This triggers GitHub Actions to build and publish to PyPI using **Trusted Publishing**
via GitHub OIDC (no token required). Configure the trusted publisher in PyPI once.

## Usage

### Environment Setup

Before using the library, set up the following environment variables:

```bash
export DB_TYPE=postgresql  # or mysql, sqlite
export DB_USER=your_username
export DB_PASSWORD=your_password
export DB_HOST=your_host
export DB_PORT=your_port
export DB_NAME=your_database_name
```

### Example Usage

Here's a comprehensive example demonstrating how to use the repository_sqlalchemy library:

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from repository_sqlalchemy import BaseRepository, Base, transaction
from typing import List, Dict, Any


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)

class PostModel(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String(1000), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

class UserRepository(BaseRepository[UserModel]):
    def find_by_username(self, username: str) -> UserModel:
        return self.session.query(self.model).filter_by(username=username).first()

class PostRepository(BaseRepository[PostModel]):
    def find_by_user_id(self, user_id: int) -> List[PostModel]:
        return self.session.query(self.model).filter_by(user_id=user_id).all()

@transaction()
def create_user_with_posts(username: str, email: str, posts: List[Dict[str, str]]) -> UserModel:
    user_repo = UserRepository()
    post_repo = PostRepository()

    # Create user
    user = user_repo.create(UserModel(username=username, email=email))

    # Create posts for the user
    for post_data in posts:
        post = PostModel(title=post_data['title'], content=post_data['content'], user_id=user.id)
        post_repo.create(post)

    return user

@transaction()
def update_user_and_posts(username: str, user_data: Dict[str, Any], post_updates: List[Dict[str, Any]]) -> UserModel:
    user_repo = UserRepository()
    post_repo = PostRepository()

    user = user_repo.find_by_username(username)
    if not user:
        raise ValueError(f"User {username} not found")

    # Update user
    user_repo.update(user, user_data)

    # Update posts
    posts = post_repo.find_by_user_id(user.id)
    for post, post_data in zip(posts, post_updates):
        post_repo.update(post, post_data)

    return user

# Usage
new_user = create_user_with_posts(
    "john_doe",
    "john@example.com",
    [
        {"title": "First Post", "content": "Hello, world!"},
        {"title": "Second Post", "content": "This is my second post."}
    ]
)
print(f"Created user: {new_user.username} with 2 posts")

updated_user = update_user_and_posts(
    "john_doe",
    {"email": "john.doe@newdomain.com"},
    [
        {"title": "Updated First Post"},
        {"content": "Updated content for second post."}
    ]
)
print(f"Updated user: {updated_user.username}, {updated_user.email}")
```

This example demonstrates:

1. Defining SQLAlchemy models (`UserModel` and `PostModel`).
2. Creating custom repositories (`UserRepository` and `PostRepository`) with additional methods.
3. Using the `@transaction()` decorator for automatic transaction management across multiple operations.
4. Performing create and update operations on multiple entities within a single transaction.
5. Automatic session handling within repository methods, with no need for manual commits or rollbacks.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
