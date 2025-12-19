import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from user.models import CustomUser

@pytest.mark.django_db
class TestRegisterUserAPIView:

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("user-register")  # Ajusta según tu namespace/url

    def test_register_email_lowercase(self):
        response = self.client.post(self.url, {"email": "Luisa@GMAIL.com", "password": "StrongPass123!"})
        assert response.status_code == 201
        assert response.data["email"] == "luisa@gmail.com"

    def test_register_email_unique(self):
        CustomUser.objects.create_user(email="test@gmail.com", password="StrongPass123!")
        response = self.client.post(self.url, {"email": "Test@GMAIL.com", "password": "AnotherPass123!"})
        assert response.status_code == 400
        assert "email" in response.data or "error" in response.data

    @pytest.mark.parametrize(
        "password,error_msg",
        [
            ("12345678", "entirely numeric"),
            ("password", "This password is too common"),
            ("short", "at least 8 characters"),
        ]
    )
    def test_register_password_validations(self, password, error_msg):
        response = self.client.post(self.url, {"email": "unique2@gmail.com", "password": password})
        assert response.status_code == 400
        assert error_msg.lower() in str(response.data).lower()
