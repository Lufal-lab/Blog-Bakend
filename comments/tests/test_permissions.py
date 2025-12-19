import pytest
from django.contrib.auth import get_user_model
from posts.models import Post
from comments.models import Comment
from comments.permissions import CanDeleteComment, CanCreateComment
from types import SimpleNamespace

User = get_user_model()


@pytest.mark.django_db
class TestCommentPermissions:
    """
    Test suite for comment permission classes.

    This test module validates:
    - Who can create comments
    - Who can delete comments
    - Enforcement of read permissions on posts when commenting
    """

    # =========================================================
    # DELETE COMMENT PERMISSIONS
    # =========================================================

    def test_author_can_delete_comment(self):
        """
        The author of a comment should be able to delete their own comment.
        """
        user = User.objects.create_user(email="author@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")
        comment = Comment.objects.create(user=user, post=post, content="My comment")

        permission = CanDeleteComment()

        # Simulate a DRF request object with only a user
        dummy_request = SimpleNamespace(user=user)

        assert permission.has_object_permission(dummy_request, None, comment) is True

    def test_admin_can_delete_any_comment(self):
        """
        A staff (admin) user should be able to delete any comment,
        even if they are not the author.
        """
        admin = User.objects.create_user(
            email="admin@test.com",
            password="123",
            is_staff=True
        )
        user = User.objects.create_user(email="user@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")
        comment = Comment.objects.create(user=user, post=post, content="Comment")

        permission = CanDeleteComment()
        dummy_request = SimpleNamespace(user=admin)

        assert permission.has_object_permission(dummy_request, None, comment) is True

    def test_other_user_cannot_delete_comment(self):
        """
        A user who is not the author and not staff
        should NOT be able to delete a comment.
        """
        author = User.objects.create_user(email="author@test.com", password="123")
        other_user = User.objects.create_user(email="other@test.com", password="123")

        post = Post.objects.create(author=author, title="Post", content="Content")
        comment = Comment.objects.create(user=author, post=post, content="Comment")

        permission = CanDeleteComment()
        dummy_request = SimpleNamespace(user=other_user)

        assert permission.has_object_permission(dummy_request, None, comment) is False

    # =========================================================
    # CREATE COMMENT PERMISSIONS
    # =========================================================

    def test_authenticated_user_can_create_comment(self):
        """
        An authenticated user should pass the global permission
        check for creating a comment.
        """
        user = User.objects.create_user(email="user@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")

        permission = CanCreateComment()
        dummy_request = SimpleNamespace(user=user)

        assert permission.has_permission(dummy_request, None) is True

    def test_unauthenticated_user_cannot_create_comment(self):
        """
        An unauthenticated user should NOT be allowed
        to create a comment.
        """
        permission = CanCreateComment()

        # Simulate anonymous request
        dummy_request = SimpleNamespace(user=None)

        assert not permission.has_permission(dummy_request, None)

    def test_user_can_create_comment_only_if_can_read_post(self):
        """
        A user should be able to create a comment ONLY if
        they have read permission on the related post.
        """
        user = User.objects.create_user(email="user@test.com", password="123")

        post = Post.objects.create(
            author=user,
            title="Private Post",
            content="x",
            privacy_read=Post.PrivacyChoices.AUTHOR
        )

        permission = CanCreateComment()
        dummy_request = SimpleNamespace(user=user)

        # The user is the author of the post, so they CAN read it
        assert permission.has_object_permission(dummy_request, None, post) is True
