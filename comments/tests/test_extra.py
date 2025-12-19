import pytest
from user.models import CustomUser, Team
from posts.models import Post
from comments.models import Comment
from django.core.exceptions import ValidationError


@pytest.mark.django_db
class TestComments:

    def setup_method(self):
        self.team = Team.objects.create(name="Team X")

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
            title="Post",
            content="Content",
            privacy_read=Post.PrivacyChoices.TEAM
        )

    def test_authenticated_user_with_read_access_can_comment(self):
        assert self.post.can_user_read(self.user) is True

        comment = Comment.objects.create(
            user=self.user,
            post=self.post,
            content="Nice post"
        )

        assert comment.post == self.post
        assert comment.user == self.user

    def test_comment_content_cannot_be_empty(self):
        comment = Comment(
            user=self.user,
            post=self.post,
            content="   "
        )

        with pytest.raises(ValidationError):
            comment.full_clean()

    def test_comments_deleted_when_post_is_deleted(self):
        Comment.objects.create(
            user=self.user,
            post=self.post,
            content="Comment 1"
        )

        assert Comment.objects.count() == 1

        self.post.delete()

        assert Comment.objects.count() == 0
