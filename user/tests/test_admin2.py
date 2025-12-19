import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from user.admin import CustomUserCreationForm, CustomUserChangeForm, CustomUserAdmin
from user.models import CustomUser, Team

@pytest.mark.django_db
class TestCustomUserAdmin:
    def setup_method(self):
        self.site = AdminSite()
        # Creamos un equipo "Default" si no existe
        self.team, _ = Team.objects.get_or_create(name="Default")

    def test_admin_creation_lowercase_email(self):
        form_data = {
            "email": "Admin@GMAIL.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
            "team": self.team.id,
            "is_staff": True,
            "is_active": True
        }
        form = CustomUserCreationForm(data=form_data)
        assert form.is_valid(), form.errors
        user = form.save()
        # Verificamos que el email se guarda en minúsculas
        assert user.email == "admin@gmail.com"

    def test_admin_creation_unique_email(self):
        # Creamos un usuario previo para probar unicidad
        get_user_model().objects.create_user(
            email="test@gmail.com",
            password="StrongPass123!"
        )
        form_data = {
            "email": "TEST@GMAIL.com",
            "password1": "AnotherPass123!",
            "password2": "AnotherPass123!",
            "team": self.team.id,
            "is_staff": True,
            "is_active": True
        }
        form = CustomUserCreationForm(data=form_data)
        # Debe fallar porque el email ya existe
        assert not form.is_valid()
        assert "email" in form.errors
