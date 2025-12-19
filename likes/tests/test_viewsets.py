import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from posts.models import Post
from likes.models import Like

User = get_user_model()

@pytest.mark.django_db
class TestLikeViewSet:
    """
    Tests for LikeViewSet endpoints:
    - Create a like
    - List likes for a post
    - Delete a like
    """

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@test.com", password="123")
        self.other_user = User.objects.create_user(email="other@test.com", password="123")
        self.post = Post.objects.create(
            author=self.user,
            title="Post 1",
            content="Content",
            privacy_read=Post.PrivacyChoices.PUBLIC
        )

    # ======================================================
    # CREATE LIKE
    # ======================================================
    def test_authenticated_user_can_create_like(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"/api/posts/{self.post.id}/likes/", format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Like.objects.count() == 1
        like = Like.objects.first()
        assert like.user == self.user
        assert like.post == self.post

    def test_unauthenticated_user_cannot_create_like(self):
        response = self.client.post(f"/api/posts/{self.post.id}/likes/", format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Like.objects.count() == 0

    def test_cannot_like_same_post_twice(self):
        self.client.force_authenticate(user=self.user)
        Like.objects.create(user=self.user, post=self.post)
        response = self.client.post(f"/api/posts/{self.post.id}/likes/", format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Like.objects.count() == 1

    # ======================================================
    # LIST LIKES
    # ======================================================
    def test_list_likes_for_post(self):
        Like.objects.create(user=self.user, post=self.post)
        Like.objects.create(user=self.other_user, post=self.post)

        response = self.client.get(f"/api/posts/{self.post.id}/likes/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2  # Assuming pagination is applied

    # ======================================================
    # DELETE LIKE
    # ======================================================
    def test_user_can_delete_own_like(self):
        like = Like.objects.create(user=self.user, post=self.post)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/posts/{self.post.id}/likes/{like.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Like.objects.count() == 0

    def test_user_cannot_delete_others_like(self):
        like = Like.objects.create(user=self.other_user, post=self.post)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/posts/{self.post.id}/likes/{like.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Like.objects.count() == 1

