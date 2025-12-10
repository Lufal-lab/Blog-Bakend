import pytest
from django.contrib.auth import get_user_model
from posts.models import Post
from posts.serializers import PostSerializer


@pytest.mark.django_db
class TestPostSerializer:

    def test_serializa_post_a_json(self):
        """
        Verifica que el serializer convierte un Post a JSON correctamente
        """
        User = get_user_model()
        user = User.objects.create_user(email="a@a.com", password="123")

        post = Post.objects.create(
            author=user,
            title="Hola",
            content="Contenido"
        )

        serializer = PostSerializer(post)
        data = serializer.data

        assert data["title"] == "Hola"
        assert data["content"] == "Contenido"
        assert "author" in data

    def test_deserializa_json_a_post(self):
        """
        Verifica que convierte JSON → Post
        """
        User = get_user_model()
        user = User.objects.create_user(email="b@b.com", password="123")

        json_data = {
            "title": "Nuevo post",
            "content": "Texto del post",
            "privacy_read": "public",
            "privacy_write": "author",
        }

        serializer = PostSerializer(data=json_data)

        assert serializer.is_valid()
        post = serializer.save(author=user)

        assert post.title == "Nuevo post"
        assert post.author == user

    def test_validacion_de_titulo_corto(self):
        """
        Verifica la validación personalizada del título
        """
        serializer = PostSerializer(data={
            "title": "a",
            "content": "Algo"
        })

        assert serializer.is_valid() is False
        assert "title" in serializer.errors
