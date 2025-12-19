import pytest
from django.contrib.auth import get_user_model
from user.models import Team
from posts.models import Post

@pytest.fixture
def user_default():

    User = get_user_model()
    return User.objects.create_user(
        email="default@example.com",
        password="123",
        # team = Default (via signals or default)
    )

@pytest.fixture
def user_with_team():

    User = get_user_model()
    team = Team.objects.create(name="Team X")
    return User.objects.create_user(
        email="teamx@example.com",
        password="123",
        team=team
    )

@pytest.mark.django_db
class TestPostsPermissions:

    def setup_method(self):

        self.User = get_user_model()

        # Author with a real team
        team_a = Team.objects.create(name="Team A")
        self.author = self.User.objects.create_user(
            email="author@example.com",
            password="123",
            team=team_a
        )

        # User from another team
        other_team = Team.objects.create(name="Other Team")
        self.other = self.User.objects.create_user(
            email="other@example.com",
            password="123",
            team=other_team
        )

        # User from the same team as author
        self.team_user = self.User.objects.create_user(
            email="team@example.com",
            password="123",
            team=team_a
        )

        # Superuser
        self.staff_user = self.User.objects.create_user(
            email="admin@example.com",
            password="123",
            is_staff=True,
            is_superuser=True
        )

        # Anonymous user simulation
        self.anon_user = type("Anonymous", (), {"is_authenticated": False})()

    def test_can_user_read_public(self):

        post = Post.objects.create(
            author=self.author,
            title="Public",
            content="x",
            privacy_read=Post.PrivacyChoices.PUBLIC
        )

        assert post.can_user_read(self.other)
        assert post.can_user_read(self.team_user)
        assert post.can_user_read(self.staff_user)
        assert post.can_user_read(self.anon_user)

    def test_can_user_read_authenticated(self):

        post = Post.objects.create(
            author=self.author,
            title="Auth",
            content="x",
            privacy_read=Post.PrivacyChoices.AUTHENTICATED
        )

        assert post.can_user_read(self.other)
        assert post.can_user_read(self.team_user)
        assert post.can_user_read(self.staff_user)
        assert post.can_user_read(self.anon_user) is False

    def test_can_user_read_team(self):

        post = Post.objects.create(
            author=self.author,
            title="Team",
            content="x",
            privacy_read=Post.PrivacyChoices.TEAM
        )

        assert post.can_user_read(self.team_user) is True
        assert post.can_user_read(self.other) is False
        assert post.can_user_read(self.staff_user) is True
        assert post.can_user_read(self.anon_user) is False

    def test_can_user_read_author(self):

        post = Post.objects.create(
            author=self.author,
            title="Author",
            content="x",
            privacy_read=Post.PrivacyChoices.AUTHOR
        )

        assert post.can_user_read(self.author) is True
        assert post.can_user_read(self.other) is False
        assert post.can_user_read(self.team_user) is False
        assert post.can_user_read(self.staff_user) is True
        assert post.can_user_read(self.anon_user) is False

    def test_can_user_edit_authenticated(self):

        post = Post.objects.create(
            author=self.author,
            title="Auth Write",
            content="x",
            privacy_write=Post.PrivacyChoices.AUTHENTICATED
        )

        assert post.can_user_edit(self.other)
        assert post.can_user_edit(self.team_user)
        assert post.can_user_edit(self.staff_user)
        assert post.can_user_edit(self.anon_user) is False

    def test_can_user_edit_team(self):

        post = Post.objects.create(
            author=self.author,
            title="Team Write",
            content="x",
            privacy_write=Post.PrivacyChoices.TEAM
        )

        assert post.can_user_edit(self.team_user)
        assert post.can_user_edit(self.other) is False
        assert post.can_user_edit(self.staff_user)
        assert post.can_user_edit(self.anon_user) is False

    def test_can_user_edit_author(self):

        post = Post.objects.create(
            author=self.author,
            title="Author Write",
            content="x",
            privacy_write=Post.PrivacyChoices.AUTHOR
        )

        assert post.can_user_edit(self.author) is True
        assert post.can_user_edit(self.other) is False
        assert post.can_user_edit(self.team_user) is False
        assert post.can_user_edit(self.staff_user)
        assert post.can_user_edit(self.anon_user) is False

    def test_author_always_can_read_own_post(self, user_with_team):

        post = Post(
            author=user_with_team,
            title="My Post",
            content="hello",
            privacy_read=Post.PrivacyChoices.TEAM
        )
        assert post.can_user_read(user_with_team)
