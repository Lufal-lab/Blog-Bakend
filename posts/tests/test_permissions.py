import pytest
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

from posts.models import Post
from posts.permissions import CanReadPost, CanEditPost
from user.models import Team


@pytest.mark.django_db
class TestPostPermissions:

    def setup_method(self):

        self.factory = APIRequestFactory()
        self.User = get_user_model()

        # Teams
        self.team_a = Team.objects.create(name="Team A")
        self.team_b = Team.objects.create(name="Team B")

        # Users
        self.author = self.User.objects.create_user(
            email="author@test.com",
            password="123",
            team=self.team_a
        )
        self.same_team = self.User.objects.create_user(
            email="same@test.com",
            password="123",
            team=self.team_a
        )
        self.other_team = self.User.objects.create_user(
            email="other@test.com",
            password="123",
            team=self.team_b
        )
        self.superuser = self.User.objects.create_superuser(
            email="admin@test.com",
            password="123"
        )
        self.anon = AnonymousUser()

        # Fake view object for .action attribute
        self.view = type("View", (), {})()

    def test_create_post_unauthenticated_forbidden(self):

        request = self.factory.post("/api/posts/")
        request.user = self.anon
        self.view.action = "create"

        permission = CanEditPost()
        assert permission.has_permission(request, self.view) is False

    def test_create_post_authenticated_allowed(self):

        request = self.factory.post("/api/posts/")
        request.user = self.author
        self.view.action = "create"

        permission = CanEditPost()
        assert permission.has_permission(request, self.view) is True


    def test_read_public(self):

        post = Post.objects.create(
            author=self.author,
            title="P",
            content="C",
            privacy_read=Post.PrivacyChoices.PUBLIC
        )
        request = self.factory.get("/api/posts/")
        request.user = self.anon

        permission = CanReadPost()
        assert permission.has_object_permission(request, self.view, post) is True

    def test_read_team_denied_other_team(self):

        post = Post.objects.create(
            author=self.author,
            title="P",
            content="C",
            privacy_read=Post.PrivacyChoices.TEAM
        )
        request = self.factory.get("/api/posts/")
        request.user = self.other_team

        permission = CanReadPost()
        assert permission.has_object_permission(request, self.view, post) is False

    def test_read_team_allowed_same_team(self):

        post = Post.objects.create(
            author=self.author,
            title="P",
            content="C",
            privacy_read=Post.PrivacyChoices.TEAM
        )
        request = self.factory.get("/api/posts/")
        request.user = self.same_team

        permission = CanReadPost()
        assert permission.has_object_permission(request, self.view, post) is True

    def test_edit_author_allowed(self):

        post = Post.objects.create(
            author=self.author,
            title="P",
            content="C",
            privacy_write=Post.PrivacyChoices.AUTHOR
        )
        request = self.factory.patch("/api/posts/1/")
        request.user = self.author

        permission = CanEditPost()
        assert permission.has_object_permission(request, self.view, post) is True

    def test_edit_author_denied_other_user(self):

        post = Post.objects.create(
            author=self.author,
            title="P",
            content="C",
            privacy_write=Post.PrivacyChoices.AUTHOR
        )
        request = self.factory.patch("/api/posts/1/")
        request.user = self.same_team

        permission = CanEditPost()
        assert permission.has_object_permission(request, self.view, post) is False

    def test_edit_public_blocked(self):

        post = Post.objects.create(
            author=self.author,
            title="P",
            content="C",
            privacy_write=Post.PrivacyChoices.PUBLIC
        )
        request = self.factory.patch("/api/posts/1/")
        request.user = self.author

        permission = CanEditPost()
        assert permission.has_object_permission(request, self.view, post) is False

    def test_superuser_can_do_anything(self):

        post = Post.objects.create(
            author=self.author,
            title="P",
            content="C",
            privacy_write=Post.PrivacyChoices.AUTHOR
        )
        request = self.factory.delete("/api/posts/1/")
        request.user = self.superuser

        permission = CanEditPost()
        assert permission.has_object_permission(request, self.view, post) is True
