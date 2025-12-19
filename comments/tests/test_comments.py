import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from posts.models import Post
from comments.models import Comment

User = get_user_model()

@pytest.mark.django_db
class TestCommentModel:
    """
    Test suite for the Comment model.

    Covers:
    - Creation of comments
    - Automatic timestamps
    - Required fields (user and post)
    - Cascade deletions when post or user is deleted
    - Validation of empty content
    - String representation
    """

    def test_create_comment_successfully(self):
        """
        Should create a comment with a valid user, post, and content.
        """
        user = User.objects.create_user(email="user@test.com", password="password123")
        post = Post.objects.create(author=user, title="Test Post", content="Test content")

        comment = Comment.objects.create(user=user, post=post, content="This is a comment")

        # Assertions
        assert comment.id is not None
        assert comment.user == user
        assert comment.post == post
        assert comment.content == "This is a comment"

    def test_comment_has_created_at_timestamp(self):
        """
        Comment should automatically store creation timestamp.
        """
        user = User.objects.create_user(email="user2@test.com", password="password123")
        post = Post.objects.create(author=user, title="Another Post", content="More content")

        comment = Comment.objects.create(user=user, post=post, content="Timestamp test")

        # The created_at field should be set and <= now
        assert comment.created_at is not None
        assert comment.created_at <= timezone.now()

    def test_comment_requires_user(self):
        """
        Comment cannot be created without a user.
        """
        user = User.objects.create_user(email="user3@test.com", password="password123")
        post = Post.objects.create(author=user, title="Post", content="Content")

        with pytest.raises(Exception):
            Comment.objects.create(user=None, post=post, content="Invalid comment")

    def test_comment_requires_post(self):
        """
        Comment cannot be created without a post.
        """
        user = User.objects.create_user(email="user4@test.com", password="password123")

        with pytest.raises(Exception):
            Comment.objects.create(user=user, post=None, content="Invalid comment")

    def test_comments_are_deleted_when_post_is_deleted(self):
        """
        Deleting a post should also delete all related comments (CASCADE behavior).
        """
        user = User.objects.create_user(email="user5@test.com", password="password123")
        post = Post.objects.create(author=user, title="Post to delete", content="Content")

        Comment.objects.create(user=user, post=post, content="Comment 1")
        Comment.objects.create(user=user, post=post, content="Comment 2")

        assert Comment.objects.count() == 2

        # Delete post
        post.delete()

        # All comments for this post should also be deleted
        assert Comment.objects.count() == 0

    def test_comments_are_deleted_when_user_is_deleted(self):
        """
        Deleting a user should also delete all comments authored by that user.
        """
        user = User.objects.create_user(email="user6@test.com", password="password123")
        post = Post.objects.create(author=user, title="Post", content="Content")

        Comment.objects.create(user=user, post=post, content="User comment")

        assert Comment.objects.count() == 1

        # Delete user
        user.delete()

        # All comments by this user should also be deleted
        assert Comment.objects.count() == 0

    def test_comment_content_not_empty(self):
        """ValidationError should be raised if comment content is empty or only whitespace."""
        user = User.objects.create_user(email="user7@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")

        comment = Comment(user=user, post=post, content="   ")  # Only spaces
        with pytest.raises(ValidationError):
            comment.full_clean()  # Calls model clean()

    def test_comment_str(self):
        """__str__ should return a concise string identifying the comment."""
        user = User.objects.create_user(email="user8@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")

        comment = Comment.objects.create(user=user, post=post, content="Test")
        assert str(comment).startswith("Comment #")
