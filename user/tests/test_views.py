import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from user.models import Team

@pytest.mark.django_db
class TestUserViews:
    def setup_method(self):
        self.User = get_user_model()

    def test_usuario_normal_no_accede_admin(self, client):
        user = self.User.objects.create_user(email="normal@example.com", password="123456")
        client.login(email="normal@example.com", password="123456")
        url_admin = reverse("admin:index")
        response = client.get(url_admin)
        assert response.status_code == 302

    def test_login_con_email_funciona(self, client):
        email = "login@example.com"
        password = "pass123"
        self.User.objects.create_user(email=email, password=password)
        assert client.login(email=email, password=password) is True

    def test_login_falla_si_password_incorrecto(self, client):
        email = "fail@example.com"
        self.User.objects.create_user(email=email, password="correct")
        assert client.login(email=email, password="wrong") is False

    def test_login_falla_si_usuario_inactivo(self, client):
        user = self.User.objects.create_user(email="inactive@example.com", password="123")
        user.is_active = False
        user.save()
        result = client.login(email="inactive@example.com", password="123")
        assert result is False

    def test_logout_funciona(self, client):
        user = self.User.objects.create_user(email="logout@example.com", password="123")
        client.login(email="logout@example.com", password="123")
        client.logout()
        response = client.get(reverse("admin:index"))
        assert response.status_code == 302

    def test_usuario_superuser_accede_sin_login_con_force(self, client):
        user = self.User.objects.create_superuser(email="force@example.com", password="123")
        client.force_login(user)
        res = client.get(reverse("admin:index"))
        assert res.status_code == 200
