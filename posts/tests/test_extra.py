import pytest
from user.models import CustomUser, Team
from posts.models import Post


@pytest.mark.django_db
class TestPostsPermissionsAndEdgeCases:

    def setup_method(self):
        self.team_a = Team.objects.create(name="Team A")
        self.team_b = Team.objects.create(name="Team B")

        self.author = CustomUser.objects.create_user(
            email="author@test.com",
            password="pass123",
            team=self.team_a
        )

        self.user_same_team = CustomUser.objects.create_user(
            email="user_same@test.com",
            password="pass123",
            team=self.team_a
        )

        self.user_other_team = CustomUser.objects.create_user(
            email="user_other@test.com",
            password="pass123",
            team=self.team_b
        )

        self.post = Post.objects.create(
            author=self.author,
            title="Secret Post",
            content="A" * 300,
            privacy_read=Post.PrivacyChoices.TEAM,
            privacy_write=Post.PrivacyChoices.TEAM
        )

    # -------------------------
    # Post basics
    # -------------------------
    def test_author_is_set_automatically(self):
        assert self.post.author == self.author

    def test_excerpt_is_first_200_chars(self):
        assert len(self.post.excerpt) == 200
        assert self.post.excerpt == self.post.content[:200]

    # -------------------------
    # Read permissions
    # -------------------------
    def test_user_in_same_team_can_read(self):
        assert self.post.can_user_read(self.user_same_team) is True

    def test_user_in_other_team_cannot_read(self):
        assert self.post.can_user_read(self.user_other_team) is False

    # -------------------------
    # WRITE / DELETE permissions
    # -------------------------
    def test_only_author_can_edit_if_author_only(self):
        self.post.privacy_write = Post.PrivacyChoices.AUTHOR
        self.post.save()

        assert self.post.can_user_edit(self.author) is True
        assert self.post.can_user_edit(self.user_same_team) is False

    # -------------------------
    # EDGE CASE 1 (NUEVO)
    # Autor cambia de team → el post cambia de team
    # -------------------------
    def test_post_visibility_updates_when_author_changes_team(self):
        # Usuario del team original puede leer
        assert self.post.can_user_read(self.user_same_team) is True

        # Autor cambia de team
        self.author.team = self.team_b
        self.author.save()

        # Usuario del team viejo ya NO puede leer
        assert self.post.can_user_read(self.user_same_team) is False

        # Usuario del nuevo team sí puede leer
        assert self.post.can_user_read(self.user_other_team) is True

    # -------------------------
    # EDGE CASE 2 (NUEVO)
    # Usuario cambia de team → pierde acceso al team viejo
    # -------------------------
    def test_user_removed_from_team_loses_access_to_old_team_posts(self):
        assert self.post.can_user_read(self.user_same_team) is True

        self.user_same_team.team = self.team_b
        self.user_same_team.save()

        assert self.post.can_user_read(self.user_same_team) is False

    # -------------------------
    # Admin permissions
    # -------------------------
    def test_admin_can_edit_any_post(self):
        admin = CustomUser.objects.create_user(
            email="admin@test.com",
            password="pass123",
            team=self.team_b,
            is_superuser=True,
            is_staff=True
        )

        assert self.post.can_user_edit(admin) is True
