import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from posts.models import Post
from user.models import Team

@pytest.mark.django_db
class TestPostAPI:
    """
    Integration tests for the Posts API (PostViewSet endpoints).
    Covers:
    - Listing posts (with privacy filtering)
    - Retrieving single posts
    - Creating posts
    - Updating posts
    - Deleting posts
    - Permission rules based on user roles and post privacy
    - Pagination behavior
    """

    def setup_method(self):
        """
        Setup test data before each test method:
        - Create teams
        - Create users
        """
        self.client = APIClient()
        self.User = get_user_model()

        # Create teams
        self.team1 = Team.objects.create(name="Team A")
        self.team2 = Team.objects.create(name="Team B")

        # Create users
        self.author = self.User.objects.create_user(
            email="author@example.com",
            password="123",
            team=self.team1
        )

        self.user_same_team = self.User.objects.create_user(
            email="same@example.com",
            password="123",
            team=self.team1
        )

        self.user_other_team = self.User.objects.create_user(
            email="other@example.com",
            password="123",
            team=self.team2
        )

    # ======================================================
    # 1. LIST POSTS
    # ======================================================
    def test_list_posts_anonymous(self):
        """
        Anonymous users should only see PUBLIC posts.
        """
        Post.objects.create(author=self.author, title="Public", content="x",
                            privacy_read=Post.PrivacyChoices.PUBLIC)
        Post.objects.create(author=self.author, title="Private", content="x",
                            privacy_read=Post.PrivacyChoices.AUTHOR)

        url = "/api/posts/"
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "Public"

    def test_list_posts_authenticated(self):
        """
        Authenticated users should see posts they are allowed to read,
        including public and team-specific posts.
        """
        self.client.force_authenticate(user=self.user_same_team)

        Post.objects.create(author=self.author, title="Public", content="x",
                            privacy_read=Post.PrivacyChoices.PUBLIC)
        Post.objects.create(author=self.author, title="Team Only", content="x",
                            privacy_read=Post.PrivacyChoices.TEAM)

        url = "/api/posts/"
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 2
        titles = [post["title"] for post in response.data["results"]]
        assert "Public" in titles
        assert "Team Only" in titles

    # ======================================================
    # 2. PAGINATION
    # ======================================================
    def test_posts_pagination(self):
        """
        The API should return paginated posts.
        Default page size is 10.
        """
        self.client.force_authenticate(user=self.author)

        # Crear 25 posts públicos
        for i in range(25):
            Post.objects.create(
                author=self.author,
                title=f"Post {i}",
                content="Content",
                privacy_read=Post.PrivacyChoices.PUBLIC
            )

        url = "/api/posts/"
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 25
        assert len(response.data["results"]) == 10  # Página 1 por defecto
        assert "next" in response.data
        assert "previous" in response.data

    # ======================================================
    # 3. CREATE POSTS
    # ======================================================
    def test_create_post_unauthenticated(self):
        """
        Anonymous users should not be able to create posts.
        """
        url = "/api/posts/"
        data = {
            "title": "New",
            "content": "Content",
            "privacy_read": Post.PrivacyChoices.PUBLIC,
            "privacy_write": Post.PrivacyChoices.AUTHOR,
        }
        response = self.client.post(url, data, format="json")
        assert response.status_code == 403

    def test_create_post_authenticated(self):
        """
        Authenticated users can create new posts.
        Author is automatically assigned.
        """
        self.client.force_authenticate(user=self.author)

        url = "/api/posts/"
        data = {
            "title": "New Post",
            "content": "Content",
            "privacy_read": Post.PrivacyChoices.PUBLIC,
            "privacy_write": Post.PrivacyChoices.AUTHOR,
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == 201
        assert Post.objects.count() == 1
        assert Post.objects.first().author == self.author

    # ======================================================
    # 4. UPDATE POSTS
    # ======================================================
    def test_edit_post_no_permission(self):
        """
        Users not allowed to edit should receive 403.
        """
        post = Post.objects.create(author=self.author, title="Original", content="x",
                                    privacy_write=Post.PrivacyChoices.AUTHOR)
        self.client.force_authenticate(user=self.user_other_team)

        url = f"/api/posts/{post.id}/"
        data = {
            "title": "Hacked",
            "content": "new",
            "privacy_read": post.privacy_read,
            "privacy_write": post.privacy_write,
        }
        response = self.client.put(url, data, format="json")
        assert response.status_code == 403

    def test_edit_post_with_permission(self):
        """
        Author can update their post.
        """
        post = Post.objects.create(author=self.author, title="Original", content="x",
                                    privacy_write=Post.PrivacyChoices.AUTHOR)
        self.client.force_authenticate(user=self.author)

        url = f"/api/posts/{post.id}/"
        data = {
            "title": "Updated",
            "content": "new",
            "privacy_read": post.privacy_read,
            "privacy_write": post.privacy_write,
        }
        response = self.client.put(url, data, format="json")

        assert response.status_code == 200
        post.refresh_from_db()
        assert post.title == "Updated"

    # ======================================================
    # 5. DELETE POSTS
    # ======================================================
    def test_delete_post_no_permission(self):
        """
        Users without permission cannot delete posts.
        """
        post = Post.objects.create(author=self.author, title="Original", content="x",
                                    privacy_write=Post.PrivacyChoices.AUTHOR)
        self.client.force_authenticate(user=self.user_other_team)

        url = f"/api/posts/{post.id}/"
        response = self.client.delete(url)
        assert response.status_code == 403

    def test_delete_post_with_permission(self):
        """
        Author can delete their post.
        """
        post = Post.objects.create(author=self.author, title="Original", content="x",
                                    privacy_write=Post.PrivacyChoices.AUTHOR)
        self.client.force_authenticate(user=self.author)

        url = f"/api/posts/{post.id}/"
        response = self.client.delete(url)
        assert response.status_code == 204
        assert Post.objects.count() == 0

    # ======================================================
    # 6. RETRIEVE POSTS
    # ======================================================
    def test_retrieve_public_post_anonymous(self):
        """
        Anonymous users cannot retrieve private posts.
        """
        post = Post.objects.create(author=self.author, title="Public", content="x",
                                    privacy_read=Post.PrivacyChoices.PUBLIC)
        url = f"/api/posts/{post.id}/"
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["title"] == "Public"

    def test_retrieve_private_post_anonymous(self):
        """
        Author can always retrieve their own private posts.
        """
        post = Post.objects.create(author=self.author, title="Private", content="x",
                                    privacy_read=Post.PrivacyChoices.AUTHOR)
        url = f"/api/posts/{post.id}/"
        response = self.client.get(url)

        assert response.status_code == 403

    def test_retrieve_private_post_as_author(self):
        post = Post.objects.create(author=self.author, title="Private", content="x",
                                    privacy_read=Post.PrivacyChoices.AUTHOR)
        self.client.force_authenticate(user=self.author)

        url = f"/api/posts/{post.id}/"
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["title"] == "Private"
