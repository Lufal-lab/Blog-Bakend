import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from posts.models import Post
from comments.models import Comment

User = get_user_model()


@pytest.mark.django_db
class TestCommentViewSet:
    """
    Integration tests for the CommentViewSet endpoints.

    Covers:
    - Creation of comments
    - Deletion rules (author/admin/other users)
    - Listing comments per post
    - Pagination behavior
    """

    def setup_method(self):
        """Initialize API client before each test."""
        self.client = APIClient()

    def authenticate(self, user):
        """Helper method to authenticate a user for the API client."""
        self.client.force_authenticate(user=user)

    # ----------------------------
    # 1. COMMENT CREATION
    # ----------------------------
    def test_authenticated_user_can_create_comment(self):
        """Authenticated users can create a comment for a given post."""
        user = User.objects.create_user(email="user@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")
        self.authenticate(user)

        response = self.client.post(
            f"/api/posts/{post.id}/comments/",
            data={"content": "Nice post!"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.count() == 1
        assert Comment.objects.first().content == "Nice post!"

    def test_unauthenticated_user_cannot_create_comment(self):
        """Anonymous users cannot create comments."""
        user = User.objects.create_user(email="user@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")

        response = self.client.post(
            f"/api/posts/{post.id}/comments/",
            data={"content": "Should fail"},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Comment.objects.count() == 0

    # ----------------------------
    # 2. COMMENT DELETION
    # ----------------------------
    def test_author_can_delete_comment(self):
        """Comment authors can delete their own comments."""
        user = User.objects.create_user(email="author@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")
        comment = Comment.objects.create(user=user, post=post, content="My comment")
        self.authenticate(user)

        response = self.client.delete(f"/api/posts/{post.id}/comments/{comment.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Comment.objects.count() == 0

    def test_admin_can_delete_any_comment(self):
        """Staff users can delete any comment."""
        admin = User.objects.create_user(email="admin@test.com", password="123", is_staff=True)
        user = User.objects.create_user(email="user@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")
        comment = Comment.objects.create(user=user, post=post, content="User comment")
        self.authenticate(admin)

        response = self.client.delete(f"/api/posts/{post.id}/comments/{comment.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Comment.objects.count() == 0

    def test_other_user_cannot_delete_comment(self):
        """Users who are not the author or admin cannot delete a comment."""
        author = User.objects.create_user(email="author@test.com", password="123")
        other_user = User.objects.create_user(email="other@test.com", password="123")
        post = Post.objects.create(author=author, title="Post", content="Content")
        comment = Comment.objects.create(user=author, post=post, content="Comment")
        self.authenticate(other_user)

        response = self.client.delete(f"/api/posts/{post.id}/comments/{comment.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Comment.objects.count() == 1

    # ----------------------------
    # 3. LISTING COMMENTS
    # ----------------------------
    def test_list_comments_by_post(self):
        """Retrieve all comments for a specific post."""
        user = User.objects.create_user(email="user@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")
        Comment.objects.create(user=user, post=post, content="Comment 1")
        Comment.objects.create(user=user, post=post, content="Comment 2")
        self.authenticate(user)

        response = self.client.get(f"/api/posts/{post.id}/comments/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    # ----------------------------
    # 4. PAGINATION
    # ----------------------------
    def test_comments_pagination(self):
        """Ensure that comment pagination works as expected."""
        user = User.objects.create_user(email="user@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")

        # Create 25 comments to test pagination
        for i in range(25):
            Comment.objects.create(user=user, post=post, content=f"Comment {i}")

        self.authenticate(user)

        response = self.client.get(f"/api/posts/{post.id}/comments/?page=1")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 25
        assert len(response.data["results"]) == 10  # Assuming CommentPagination.page_size = 20
        assert "next" in response.data
        assert "previous" in response.data
