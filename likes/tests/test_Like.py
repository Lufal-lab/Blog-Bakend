import pytest
from django.contrib.auth import get_user_model
from posts.models import Post
from likes.models import Like  # tu app se llama 'likes'

User = get_user_model()


@pytest.mark.django_db
class TestLikeModel:

    def test_create_like(self):
        user = User.objects.create_user(email="user@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")
        
        like = Like.objects.create(user=user, post=post)
        
        assert like.id is not None
        assert like.user == user
        assert like.post == post

    def test_like_unique_per_user_post(self):
        user = User.objects.create_user(email="user@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")
        
        Like.objects.create(user=user, post=post)
        
        with pytest.raises(Exception):  # IntegrityError por unique_together
            Like.objects.create(user=user, post=post)

    def test_like_relations(self):
        user = User.objects.create_user(email="user@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")
        like = Like.objects.create(user=user, post=post)
        
        # Relaciones inversas usando el related_name definido
        assert post.likes.first() == like
        assert user.likes.first() == like

    def test_like_str(self):
        user = User.objects.create_user(email="user@test.com", password="123")
        post = Post.objects.create(author=user, title="Post", content="Content")
        like = Like.objects.create(user=user, post=post)
        
        # Cambiado para que coincida con tu __str__ en español
        assert str(like) == f"{user.email} dio like a {post.title}"
