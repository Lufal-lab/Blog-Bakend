import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.utils import IntegrityError

from user.models import Team

@pytest.mark.django_db
class TestUserModel:
    def setup_method(self):
        self.User = get_user_model()

    def test_crear_usuario(self):
        user = self.User.objects.create_user(email="prueba@example.com", password="123456")
        assert user.email == "prueba@example.com"
        assert user.check_password("123456")

    def test_crear_superusuario(self):
        admin = self.User.objects.create_superuser(email="admin@example.com", password="adminpass")
        assert admin.is_staff
        assert admin.is_superuser

    def test_superusuario_tambien_es_usuario_normal(self):
        admin = self.User.objects.create_superuser(email="admin2@example.com", password="mypassword")
        assert admin.is_active
        assert admin.email == "admin2@example.com"
        assert admin.check_password("mypassword")

    def test_no_se_puede_crear_usuario_sin_email(self):
        with pytest.raises(ValueError):
            self.User.objects.create_user(email=None, password="12345")

    def test_email_se_normaliza(self):
        user = self.User.objects.create_user(email="TEST@Example.COM", password="123")
        assert user.email.lower() == "test@example.com"

    def test_create_superuser_error_si_is_staff_false(self):
        with pytest.raises(ValueError):
            self.User.objects.create_superuser(email="a@example.com", password="123", is_staff=False)

    def test_create_superuser_error_si_is_superuser_false(self):
        with pytest.raises(ValueError):
            self.User.objects.create_superuser(email="b@example.com", password="123", is_superuser=False)

    def test_str_devuelve_email(self):
        user = self.User.objects.create_user(email="hola@example.com", password="123")
        assert str(user) == "hola@example.com"

    def test_flags_por_defecto(self):
        user = self.User.objects.create_user(email="flags@example.com", password="123")
        assert user.is_active is True
        assert user.is_staff is False

    def test_usuario_recibe_team_por_defecto(self):
        user = self.User.objects.create_user(email="noteam@example.com", password="123")
        assert user.team.name == "Default"

    def test_cambiar_team_variass_veces(self):
        t1 = Team.objects.create(name="A")
        t2 = Team.objects.create(name="B")
        user = self.User.objects.create_user(email="multi@example.com", password="123", team=t1)
        assert user.team == t1
        user.team = t2
        user.save()
        assert user.team == t2

    def test_email_es_unico(self):
        self.User.objects.create_user(email="unique@example.com", password="123")
        with pytest.raises(IntegrityError):
            self.User.objects.create_user(email="unique@example.com", password="456")

    def test_cambiar_password_funciona(self):
        user = self.User.objects.create_user(email="testpass@example.com", password="123")
        user.set_password("nueva123")
        user.save()
        assert user.check_password("nueva123")

    def test_usuario_inicialmente_activo(self):
        user = self.User.objects.create_user(email="active@example.com", password="123")
        assert user.is_active is True

    def test_desactivar_usuario(self):
        user = self.User.objects.create_user(email="disabled@example.com", password="123")
        user.is_active = False
        user.save()
        assert user.is_active is False
