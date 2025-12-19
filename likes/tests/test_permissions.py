import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from likes.permissions import CanLike, CanUnlike
from posts.models import Post
from likes.models import Like

User = get_user_model()


@pytest.mark.django_db
class TestLikePermissions:

    def setup_method(self):
        self.user = User.objects.create_user(email="user@test.com", password="123")
        self.other_user = User.objects.create_user(email="other@test.com", password="123")
        self.post = Post.objects.create(author=self.user, title="Test Post", content="Content")
        self.factory = APIRequestFactory()

    # ======================================================
    # TEST CanLike
    # ======================================================
    def test_can_like_authenticated_user(self):
        request = self.factory.post("/api/likes/")
        request.user = self.user
        perm = CanLike()
        assert perm.has_permission(request, None) is True

    def test_cannot_like_anonymous_user(self):
        request = self.factory.post("/api/likes/")
        request.user = type("AnonymousUser", (), {"is_authenticated": False})()
        perm = CanLike()
        assert perm.has_permission(request, None) is False

    # ======================================================
    # TEST CanUnlike
    # ======================================================
    def test_can_unlike_own_like(self):
        like = Like.objects.create(user=self.user, post=self.post)
        request = self.factory.delete(f"/api/likes/{like.id}/")
        request.user = self.user
        perm = CanUnlike()
        assert perm.has_object_permission(request, None, like) is True

    def test_cannot_unlike_others_like(self):
        like = Like.objects.create(user=self.other_user, post=self.post)
        request = self.factory.delete(f"/api/likes/{like.id}/")
        request.user = self.user
        perm = CanUnlike()
        assert perm.has_object_permission(request, None, like) is False

    def test_can_unlike_as_superuser(self):
        like = Like.objects.create(user=self.other_user, post=self.post)
        superuser = User.objects.create_superuser(email="admin@test.com", password="123")
        request = self.factory.delete(f"/api/likes/{like.id}/")
        request.user = superuser
        perm = CanUnlike()
        assert perm.has_object_permission(request, None, like) is True