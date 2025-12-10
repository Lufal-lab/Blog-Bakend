import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from posts.models import Post
from comments.models import Comment


@pytest.mark.django_db
class TestComments:

    # Se ejecuta antes de cada test
    def setup_method(self):
        self.User = get_user_model()

    # ---------------------------------------------------------
    # 1. Crear un comentario básico
    # ---------------------------------------------------------
    def test_crear_comentario(self):
        """
        Verifica que:
        - Se pueda crear un comentario
        - Se vincule correctamente al usuario y al post
        """
        user = self.User.objects.create_user(
            email="coment@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Post comentable",
            content="Contenido"
        )

        comment = Comment.objects.create(
            user=user,
            post=post,
            content="Primer comentario"
        )

        assert comment.user == user
        assert comment.post == post
        assert comment.content == "Primer comentario"

    # ---------------------------------------------------------
    # 2. Fechas automáticas
    # ---------------------------------------------------------
    def test_fecha_auto(self):
        user = self.User.objects.create_user(
            email="fecha@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Fechas",
            content="x"
        )

        comment = Comment.objects.create(
            user=user,
            post=post,
            content="Hola"
        )

        assert comment.created_at is not None

    # ---------------------------------------------------------
    # 3. Un usuario puede hacer varios comentarios
    # ---------------------------------------------------------
    def test_usuario_con_varios_comentarios(self):
        user = self.User.objects.create_user(
            email="multi@example.com",
            password="123"
        )

        post = Post.objects.create(author=user, title="P", content="...")

        c1 = Comment.objects.create(user=user, post=post, content="C1")
        c2 = Comment.objects.create(user=user, post=post, content="C2")
        c3 = Comment.objects.create(user=user, post=post, content="C3")

        # related_name="comments"
        assert user.comments.count() == 3
        assert c1 in user.comments.all()
        assert c2 in user.comments.all()
        assert c3 in user.comments.all()

    # ---------------------------------------------------------
    # 4. Un post recibe varios comentarios
    # ---------------------------------------------------------
    def test_post_con_varios_comentarios(self):
        user = self.User.objects.create_user(
            email="postmulti@example.com",
            password="123"
        )

        post = Post.objects.create(author=user, title="P", content="...")

        Comment.objects.create(user=user, post=post, content="Hola1")
        Comment.objects.create(user=user, post=post, content="Hola2")

        assert post.comments.count() == 2

    # ---------------------------------------------------------
    # 5. Borrar usuario borra sus comentarios
    # ---------------------------------------------------------
    def test_borrar_usuario_elimina_comentarios(self):
        user = self.User.objects.create_user(
            email="delete@example.com",
            password="123"
        )

        post = Post.objects.create(author=user, title="X", content="Y")

        Comment.objects.create(user=user, post=post, content="C1")
        Comment.objects.create(user=user, post=post, content="C2")

        # Borrar usuario
        user.delete()

        assert Comment.objects.count() == 0

    # ---------------------------------------------------------
    # 6. Borrar post borra comentarios
    # ---------------------------------------------------------
    def test_borrar_post_elimina_comentarios(self):
        user = self.User.objects.create_user(
            email="delete2@example.com",
            password="123"
        )

        post = Post.objects.create(author=user, title="P", content="...")

        Comment.objects.create(user=user, post=post, content="C1")
        Comment.objects.create(user=user, post=post, content="C2")

        # Borrar el post
        post.delete()

        assert Comment.objects.count() == 0

    # ---------------------------------------------------------
    # 7. __str__
    # ---------------------------------------------------------
    def test_str(self):
        user = self.User.objects.create_user(
            email="strcomment@example.com",
            password="123"
        )
        post = Post.objects.create(author=user, title="P", content="...")

        comment = Comment.objects.create(
            user=user, post=post, content="Probando str"
        )

        assert str(comment) == "Probando str"

    # ---------------------------------------------------------
    # 8. (Opcional) No permitir comentarios vacíos
    # ---------------------------------------------------------
    def test_no_permitir_contenido_vacio(self):
        """
        Si tu modelo usa blank=False, null=False,
        este test verifica que NO deje guardar contenido vacío.
        """
        user = self.User.objects.create_user(
            email="empty@example.com",
            password="123"
        )

        post = Post.objects.create(author=user, title="P", content="...")

        with pytest.raises(Exception):
            Comment.objects.create(
                user=user,
                post=post,
                content=""  # no permitido
            )
