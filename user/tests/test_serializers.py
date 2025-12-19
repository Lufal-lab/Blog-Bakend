import pytest
from django.core.exceptions import ValidationError
from user.serializers import UserSerializer, LoginSerializer, RegisterSerializer
from user.models import CustomUser, Team

@pytest.mark.django_db
class TestUserSerializer:

    def setup_method(self):

        self, _ = Team.objects.get_or_create(name="Default")

    # -------------------------------------------
    # 1. Test: successfully creates a user
    # -------------------------------------------
    def test_serializer_creates_user(self):

        data = {
            "email": "TEST@EMAIL.COM",
            "password": "12345678"
        }

        serializer = UserSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        user = serializer.save()

        # Email should be lowercase
        assert user.email == "test@email.com"

        # Password should be encrypted (not plain text)
        assert user.password != "12345678"
        assert user.check_password("12345678") is True

        # User should be assigned to the default team
        assert user.team.name == "Default"

    def test_serializer_email_required(self):

        data = {
            "password": "12345678"
        }

        serializer = UserSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_serializer_password_required(self):

        data = {
            "email": "test@email.com"
        }

        serializer = UserSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_email_saved_lowercase(self):
        data = {"email": "Luisa@GMAIL.com", "password": "StrongPass123!"}
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.email == "luisa@gmail.com"

    def test_email_unique(self):
        CustomUser.objects.create_user(email="test@gmail.com", password="StrongPass123!")
        data = {"email": "Test@GMAIL.com", "password": "AnotherPass123!"}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors or "non_field_errors" in serializer.errors

    @pytest.mark.parametrize(
        "password,error_msg",
        [
            ("12345678", "entirely numeric"),
            ("password", "This password is too common"),
            ("short", "at least 8 characters"),
        ]
    )
    def test_password_validations(self, password, error_msg):
        data = {"email": "unique@gmail.com", "password": password}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert any(error_msg.lower() in e.lower() for errors in serializer.errors.values() for e in errors)
