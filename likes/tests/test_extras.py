import pytest
from django.db import IntegrityError
from user.models import CustomUser, Team
from posts.models import Post
from likes.models import Like


@pytest.mark.django_db
class TestLikes:

    def setup_method(self):
        self.team = Team.objects.create(name="Team Likes")

        self.author = CustomUser.objects.create_user(
            email="author@test.com",
            password="pass123",
            team=self.team
        )

        self.user = CustomUser.objects.create_user(
            email="user@test.com",
            password="pass123",
            team=self.team
        )

        self.post = Post.objects.create(
            author=self.author,
            title="Likeable Post",
            content="Content",
            privacy_read=Post.PrivacyChoices.TEAM
        )

    def test_authenticated_user_can_like_post_once(self):
        Like.objects.create(user=self.user, post=self.post)
        assert Like.objects.count() == 1

        with pytest.raises(IntegrityError):
            Like.objects.create(user=self.user, post=self.post)

    def test_user_without_read_access_cannot_like_post(self):
        other_team = Team.objects.create(name="Other Team")
        outsider = CustomUser.objects.create_user(
            email="outsider@test.com",
            password="pass123",
            team=other_team
        )

        assert self.post.can_user_read(outsider) is False

    def test_likes_deleted_when_post_is_deleted(self):
        Like.objects.create(user=self.user, post=self.post)
        assert Like.objects.count() == 1

        self.post.delete()
        assert Like.objects.count() == 0
