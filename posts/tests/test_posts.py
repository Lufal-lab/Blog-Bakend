import pytest
from django.contrib.auth import get_user_model
from posts.models import Post


# ============================================================
# TODOS LOS TESTS NECESITAN BASE DE DATOS
# ============================================================
@pytest.mark.django_db
class TestPostsModel:

    # ========================================================
    # setup_method → se ejecuta ANTES de cada test
    # Aquí guardamos la referencia al modelo User
    # ========================================================
    def setup_method(self):
        self.User = get_user_model()

    # ========================================================
    # 1. Test de creación básica de Post
    # ========================================================
    def test_crear_post(self):
        """
        Verifica que:
        - Se pueda crear un Post
        - Se asigne correctamente el autor
        - Se guarden todos los campos
        """

        # Crear usuario autor
        user = self.User.objects.create_user(
            email="autor@example.com",
            password="123456"
        )

        # Crear post
        post = Post.objects.create(
            author=user,
            title="Mi primer post",
            content="Contenido del post"
        )

        # Afirmaciones
        assert post.author == user
        assert post.title == "Mi primer post"
        assert post.content == "Contenido del post"

    # ========================================================
    # 2. Las fechas se asignan automáticamente
    # ========================================================
    def test_fechas_auto(self):

        user = self.User.objects.create_user(
            email="fechas@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Con fechas",
            content="Probando fechas"
        )

        assert post.created_at is not None
        assert post.updated_at is not None

    # ========================================================
    # 3. Privacidad por defecto
    # ========================================================
    def test_privacidad_por_defecto(self):

        user = self.User.objects.create_user(
            email="priv@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Privado?",
            content="..."
        )

        # Estos valores vienen del modelo
        assert post.privacy_read == "public"
        assert post.privacy_write == "author"

    # ========================================================
    # 4. Cambiar manualmente la privacidad
    # ========================================================
    def test_cambiar_privacidad(self):

        user = self.User.objects.create_user(
            email="priv2@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Cambios",
            content="Editando privacidad",
            privacy_read="team",           # ✔ válido
            privacy_write="authenticated"  # ✔ válido
        )

        assert post.privacy_read == "team"
        assert post.privacy_write == "authenticated"

    # ========================================================
    # 5. __str__ debe devolver el título
    # ========================================================
    def test_str(self):

        user = self.User.objects.create_user(
            email="str@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Título bonito",
            content="..."
        )

        assert str(post) == "Título bonito"

    # ========================================================
    # 6. Un usuario puede escribir varios posts
    # ========================================================
    def test_usuario_con_varios_posts(self):

        user = self.User.objects.create_user(
            email="multi@example.com",
            password="123"
        )

        p1 = Post.objects.create(author=user, title="P1", content="...")
        p2 = Post.objects.create(author=user, title="P2", content="...")
        p3 = Post.objects.create(author=user, title="P3", content="...")

        # user.posts → related_name
        assert user.posts.count() == 3
        assert p1 in user.posts.all()
        assert p2 in user.posts.all()
        assert p3 in user.posts.all()

    # ========================================================
    # 7. Si se borra el usuario → se borran sus posts
    # ========================================================
    def test_borrado_usuario_elimina_posts(self):

        user = self.User.objects.create_user(
            email="delete@example.com",
            password="123"
        )

        Post.objects.create(author=user, title="X", content="...")
        Post.objects.create(author=user, title="Y", content="...")

        # Eliminamos usuario
        user.delete()

        # Todos sus posts deben desaparecer (CASCADE)
        assert Post.objects.count() == 0

    # ========================================================
    # 8. updated_at se actualiza al guardar cambios
    # ========================================================
    def test_updated_at_cambia(self):

        user = self.User.objects.create_user(
            email="update@example.com",
            password="123"
        )

        post = Post.objects.create(
            author=user,
            title="Update me",
            content="x"
        )

        old_updated = post.updated_at

        # Cambiamos algo y guardamos
        post.content = "nuevo contenido"
        post.save()

        assert post.updated_at > old_updated