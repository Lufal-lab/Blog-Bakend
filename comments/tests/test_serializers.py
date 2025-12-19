import pytest
from django.contrib.auth import get_user_model

from posts.models import Post
from comments.models import Comment
from comments.serializers import CommentSerializer

User = get_user_model()


@pytest.mark.django_db
class TestCommentSerializer:
    """
    Test suite for the CommentSerializer.

    These tests verify that:
    - A comment is created using request.user and post from serializer context
    - Client-provided user or post fields are ignored (security)
    - The serialized representation exposes only the expected read fields
    - Comment creation is denied if the user cannot read the target post
    """

    def test_serializer_creates_comment_with_valid_data(self):
        """
        The serializer should successfully create a comment when:
        - Valid content is provided
        - request.user is available in the serializer context
        - post is provided through the serializer context

        The user and post must NOT come from the request payload.
        """
        user = User.objects.create_user(
            email="user@test.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Post",
            content="Content"
        )

        data = {
            "content": "This is a comment"
        }

        # Fake request object with a user attribute
        serializer = CommentSerializer(
            data=data,
            context={
                "request": type("Request", (), {"user": user}),
                "post": post,
            }
        )

        assert serializer.is_valid(), serializer.errors

        comment = serializer.save()

        # Comment must be created with correct relations
        assert comment.content == "This is a comment"
        assert comment.user == user
        assert comment.post == post

    def test_serializer_does_not_allow_user_field(self):
        """
        The client must NOT be able to manually set the comment author.

        Even if a 'user' field is injected in the payload,
        the serializer must always use request.user.
        """
        user = User.objects.create_user(
            email="user@test.com",
            password="123"
        )

        other_user = User.objects.create_user(
            email="hacker@test.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Post",
            content="Content"
        )

        data = {
            "content": "Trying to hack",
            "user": other_user.id,  # Attempt to impersonate another user
        }

        serializer = CommentSerializer(
            data=data,
            context={
                "request": type("Request", (), {"user": user}),
                "post": post,
            }
        )

        assert serializer.is_valid(), serializer.errors
        comment = serializer.save()

        # The author must always be request.user
        assert comment.user == user

    def test_serializer_does_not_allow_post_field(self):
        """
        The client must NOT be able to manually set the post.

        Even if a 'post' field is sent in the payload,
        the serializer must always use the post from context.
        """
        user = User.objects.create_user(
            email="user@test.com",
            password="123"
        )

        post_1 = Post.objects.create(
            author=user,
            title="Post 1",
            content="Content"
        )

        post_2 = Post.objects.create(
            author=user,
            title="Post 2",
            content="Content"
        )

        data = {
            "content": "Trying to set post",
            "post": post_2.id,  # Attempt to comment on a different post
        }

        serializer = CommentSerializer(
            data=data,
            context={
                "request": type("Request", (), {"user": user}),
                "post": post_1,
            }
        )

        assert serializer.is_valid(), serializer.errors
        comment = serializer.save()

        # The post must always come from serializer context
        assert comment.post == post_1

    def test_serializer_representation(self):
        """
        The serialized representation should expose only safe, read-only fields.

        Expected fields:
        - id
        - content
        - created_at
        - user_email
        """
        user = User.objects.create_user(
            email="user@test.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Post",
            content="Content"
        )

        comment = Comment.objects.create(
            user=user,
            post=post,
            content="Hello world"
        )

        serializer = CommentSerializer(comment)
        data = serializer.data

        assert data["content"] == "Hello world"
        assert data["user_email"] == user.email
        assert "created_at" in data
        assert "id" in data

    def test_serializer_denies_comment_if_user_cannot_read_post(self):
        """
        A user must NOT be allowed to comment on a post
        if they do not have read permission for that post.

        This enforces the business rule:
        'If you cannot read the post, you cannot comment on it.'
        """
        author = User.objects.create_user(
            email="author@test.com",
            password="123"
        )

        other_user = User.objects.create_user(
            email="other@test.com",
            password="123"
        )

        post = Post.objects.create(
            author=author,
            title="Private post",
            content="Content",
            privacy_read=Post.PrivacyChoices.AUTHOR
        )

        data = {
            "content": "Trying to comment"
        }

        serializer = CommentSerializer(
            data=data,
            context={
                "request": type("Request", (), {"user": other_user}),
                "post": post,
            }
        )

        # Validation must fail due to lack of read permission
        assert not serializer.is_valid()
        assert "permission" in str(serializer.errors).lower()
