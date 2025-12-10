import pytest
from django.contrib.auth import get_user_model
from posts.models import Post
from likes.models import Like


@pytest.mark.django_db
class TestLikes:

    # Setup que corre antes de cada test
    def setup_method(self):
        self.User = get_user_model()

    # ---------------------------------------------------------
    # 1. Crear un like
    # ---------------------------------------------------------
    def test_crear_like(self):
        """
        Verifica que se pueda crear un LIKE y que se relacione
        correctamente con el usuario y el post.
        """
        user = self.User.objects.create_user(
            email="like@example.com", password="123"
        )
        post = Post.objects.create(
            author=user, title="Post", content="Contenido"
        )

        like = Like.objects.create(user=user, post=post)

        assert like.user == user
        assert like.post == post
        assert like.created_at is not None  # Fecha automática

    # ---------------------------------------------------------
    # 2. Un usuario puede dar likes a varios posts
    # ---------------------------------------------------------
    def test_usuario_varios_likes(self):
        user = self.User.objects.create_user(
            email="multi@example.com", password="123"
        )

        post1 = Post.objects.create(author=user, title="P1", content="...")
        post2 = Post.objects.create(author=user, title="P2", content="...")

        Like.objects.create(user=user, post=post1)
        Like.objects.create(user=user, post=post2)

        # user.likes → viene de related_name="likes"
        assert user.likes.count() == 2

    # ---------------------------------------------------------
    # 3. Un post puede recibir muchos likes
    # ---------------------------------------------------------
    def test_post_muchos_likes(self):
        owner = self.User.objects.create_user(
            email="owner@example.com", password="123"
        )

        post = Post.objects.create(author=owner, title="P", content="...")

        u1 = self.User.objects.create_user(email="u1@example.com", password="123")
        u2 = self.User.objects.create_user(email="u2@example.com", password="123")
        u3 = self.User.objects.create_user(email="u3@example.com", password="123")

        Like.objects.create(user=u1, post=post)
        Like.objects.create(user=u2, post=post)
        Like.objects.create(user=u3, post=post)

        assert post.likes.count() == 3

    # ---------------------------------------------------------
    # 4. Un usuario NO puede dar like dos veces al mismo post
    # ---------------------------------------------------------
    def test_like_unico_por_usuario(self):
        """
        Verifica el UNIQUE(usuario, post)
        Si intenta crear un like duplicado → debe lanzar error.
        """
        user = self.User.objects.create_user(
            email="unique@example.com", password="123"
        )
        post = Post.objects.create(author=user, title="P", content="...")

        Like.objects.create(user=user, post=post)

        # Intentar duplicar debe fallar
        with pytest.raises(Exception):
            Like.objects.create(user=user, post=post)

    # ---------------------------------------------------------
    # 5. Borrar usuario elimina sus likes
    # ---------------------------------------------------------
    def test_borrar_usuario_elimina_likes(self):
        user = self.User.objects.create_user(
            email="deleteu@example.com", password="123"
        )

        post = Post.objects.create(author=user, title="P", content="...")

        Like.objects.create(user=user, post=post)

        user.delete()

        assert Like.objects.count() == 0

    # ---------------------------------------------------------
    # 6. Borrar post elimina sus likes
    # ---------------------------------------------------------
    def test_borrar_post_elimina_likes(self):
        user = self.User.objects.create_user(
            email="deletep@example.com", password="123"
        )

        post = Post.objects.create(author=user, title="P", content="...")

        Like.objects.create(user=user, post=post)

        post.delete()

        assert Like.objects.count() == 0

    # ---------------------------------------------------------
    # 7. __str__
    # ---------------------------------------------------------
    def test_str(self):
        user = self.User.objects.create_user(
            email="strlike@example.com", password="123"
        )
        post = Post.objects.create(author=user, title="P", content="...")

        like = Like.objects.create(user=user, post=post)

        # str(like) lo puedes definir tú, por ejemplo:
        # return f"{self.user.email} → {self.post.title}"
        assert str(like) != ""  # Solo verifica que existe un __str__
