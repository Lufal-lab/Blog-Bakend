import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from posts.models import Post
from user.models import Team

@pytest.mark.django_db
class TestPostAPI:

    def setup_method(self):

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

    def test_list_posts_anonymous(self):

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

    def test_posts_pagination(self):

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

    def test_create_post_unauthenticated(self):

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

    def test_edit_post_no_permission(self):

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

    def test_delete_post_no_permission(self):

        post = Post.objects.create(author=self.author, title="Original", content="x",
                                    privacy_write=Post.PrivacyChoices.AUTHOR)
        self.client.force_authenticate(user=self.user_other_team)

        url = f"/api/posts/{post.id}/"
        response = self.client.delete(url)
        assert response.status_code == 403

    def test_delete_post_with_permission(self):

        post = Post.objects.create(author=self.author, title="Original", content="x",
                                    privacy_write=Post.PrivacyChoices.AUTHOR)
        self.client.force_authenticate(user=self.author)

        url = f"/api/posts/{post.id}/"
        response = self.client.delete(url)
        assert response.status_code == 204
        assert Post.objects.count() == 0

    def test_retrieve_public_post_anonymous(self):

        post = Post.objects.create(author=self.author, title="Public", content="x",
                                    privacy_read=Post.PrivacyChoices.PUBLIC)
        url = f"/api/posts/{post.id}/"
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["title"] == "Public"

    def test_retrieve_private_post_anonymous(self):

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
