import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from posts.models import Post
from user.models import Team

@pytest.mark.django_db
class TestPostPrivacy:

    def setup_method(self):
        self.User = get_user_model()

        # Creamos dos equipos
        self.team1 = Team.objects.create(name="Team A")
        self.team2 = Team.objects.create(name="Team B")

        # Usuarios
        self.autor = self.User.objects.create_user(
            email="autor@example.com", password="123", team=self.team1
        )
        self.user_same_team = self.User.objects.create_user(
            email="same@example.com", password="123", team=self.team1
        )
        self.user_other_team = self.User.objects.create_user(
            email="other@example.com", password="123", team=self.team2
        )
        self.invited = AnonymousUser()

    # ==========================================================
    # TESTS DE LECTURA
    # ==========================================================

    def test_read_public(self):
        post = Post.objects.create(
            author=self.autor,
            title="P",
            content="C",
            privacy_read=Post.PRIVACY_PUBLIC
        )

        assert post.can_user_read(self.invited) is True
        assert post.can_user_read(self.user_same_team) is True
        assert post.can_user_read(self.user_other_team) is True

    def test_read_authenticated(self):
        post = Post.objects.create(
            author=self.autor,
            title="P",
            content="C",
            privacy_read=Post.PRIVACY_AUTH
        )

        assert post.can_user_read(self.invited) is False
        assert post.can_user_read(self.user_same_team) is True
        assert post.can_user_read(self.user_other_team) is True

    def test_read_team(self):
        post = Post.objects.create(
            author=self.autor,
            title="P",
            content="C",
            privacy_read=Post.PRIVACY_TEAM
        )

        assert post.can_user_read(self.invited) is False
        assert post.can_user_read(self.user_same_team) is True
        assert post.can_user_read(self.user_other_team) is False

    def test_read_author(self):
        post = Post.objects.create(
            author=self.autor,
            title="P",
            content="C",
            privacy_read=Post.PRIVACY_AUTHOR
        )

        assert post.can_user_read(self.invited) is False
        assert post.can_user_read(self.user_same_team) is False
        assert post.can_user_read(self.user_other_team) is False
        assert post.can_user_read(self.autor) is True

    # ==========================================================
    # TESTS DE EDICIÓN
    # ==========================================================

    def test_edit_public(self):
        post = Post.objects.create(
            author=self.autor,
            title="P",
            content="C",
            privacy_write=Post.PRIVACY_PUBLIC
        )

        assert post.can_user_edit(self.invited) is True
        assert post.can_user_edit(self.user_same_team) is True
        assert post.can_user_edit(self.user_other_team) is True

    def test_edit_authenticated(self):
        post = Post.objects.create(
            author=self.autor,
            title="P",
            content="C",
            privacy_write=Post.PRIVACY_AUTH
        )

        assert post.can_user_edit(self.invited) is False
        assert post.can_user_edit(self.user_same_team) is True
        assert post.can_user_edit(self.user_other_team) is True

    def test_edit_team(self):
        post = Post.objects.create(
            author=self.autor,
            title="P",
            content="C",
            privacy_write=Post.PRIVACY_TEAM
        )

        assert post.can_user_edit(self.invited) is False
        assert post.can_user_edit(self.user_same_team) is True
        assert post.can_user_edit(self.user_other_team) is False

    def test_edit_author(self):
        post = Post.objects.create(
            author=self.autor,
            title="P",
            content="C",
            privacy_write=Post.PRIVACY_AUTHOR
        )

        assert post.can_user_edit(self.invited) is False
        assert post.can_user_edit(self.user_same_team) is False
        assert post.can_user_edit(self.user_other_team) is False
        assert post.can_user_edit(self.autor) is True