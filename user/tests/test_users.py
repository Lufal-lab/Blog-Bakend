import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.utils import IntegrityError
from user.models import Team

@pytest.mark.django_db
class TestUserModel:
    """
    Test suite for the CustomUser model.

    Validates:
    - User creation (normal and superuser)
    - Email normalization and uniqueness
    - Default flags and team assignment
    - Password setting and changing
    - Superuser constraints
    """

    def setup_method(self):
        """Setup method to get the CustomUser model."""
        self.User = get_user_model()

    def test_create_user(self):
        """Ensure a normal user is created with correct email and password."""
        user = self.User.objects.create_user(email="prueba@example.com", password="123456")
        assert user.email == "prueba@example.com"
        assert user.check_password("123456")

    def test_create_superuser(self):
        """Ensure a superuser is created with is_staff and is_superuser flags True."""
        admin = self.User.objects.create_superuser(email="admin@example.com", password="adminpass")
        assert admin.is_staff
        assert admin.is_superuser

    def test_superuser_also_is_normal_user(self):
        """Superuser should have is_active=True and behave like a normal user."""
        admin = self.User.objects.create_superuser(email="admin2@example.com", password="mypassword")
        assert admin.is_active
        assert admin.email == "admin2@example.com"
        assert admin.check_password("mypassword")

    def test_cannot_create_user_without_email(self):
        """Creating a user without an email should raise ValueError."""
        with pytest.raises(ValueError):
            self.User.objects.create_user(email=None, password="12345")

    def test_email_is_normalized(self):
        """Emails should be stored in lowercase."""
        user = self.User.objects.create_user(email="TEST@Example.COM", password="123")
        assert user.email.lower() == "test@example.com"

    def test_superuser_error_if_is_staff_false(self):
        """Creating a superuser with is_staff=False should raise ValueError."""
        with pytest.raises(ValueError):
            self.User.objects.create_superuser(email="a@example.com", password="123", is_staff=False)

    def test_superuser_error_if_is_superuser_false(self):
        """Creating a superuser with is_superuser=False should raise ValueError."""
        with pytest.raises(ValueError):
            self.User.objects.create_superuser(email="b@example.com", password="123", is_superuser=False)

    def test_str_returns_email(self):
        """The string representation of a user should return the email."""
        user = self.User.objects.create_user(email="hola@example.com", password="123")
        assert str(user) == "hola@example.com"

    def test_default_flags(self):
        """New users should have is_active=True and is_staff=False by default."""
        user = self.User.objects.create_user(email="flags@example.com", password="123")
        assert user.is_active is True
        assert user.is_staff is False

    def test_user_gets_default_team(self):
        """New users should be assigned the default team automatically."""
        user = self.User.objects.create_user(email="noteam@example.com", password="123")
        assert user.team.name == "Default"

    def test_change_team_multiple_times(self):
        """Users can change their team multiple times and it should update correctly."""
        t1 = Team.objects.create(name="A")
        t2 = Team.objects.create(name="B")
        user = self.User.objects.create_user(email="multi@example.com", password="123", team=t1)
        assert user.team == t1
        user.team = t2
        user.save()
        assert user.team == t2

    def test_email_uniqueness(self):
        """Creating a user with an email that already exists should raise IntegrityError."""
        self.User.objects.create_user(email="unique@example.com", password="123")
        with pytest.raises(IntegrityError):
            self.User.objects.create_user(email="unique@example.com", password="456")

    def test_change_password_works(self):
        """User password can be changed and should be validated correctly."""
        user = self.User.objects.create_user(email="testpass@example.com", password="123")
        user.set_password("nueva123")
        user.save()
        assert user.check_password("nueva123")

    def test_user_initially_active(self):
        """New users should be active by default."""
        user = self.User.objects.create_user(email="active@example.com", password="123")
        assert user.is_active is True

    def test_deactivate_user(self):
        """Users can be deactivated by setting is_active=False."""
        user = self.User.objects.create_user(email="disabled@example.com", password="123")
        user.is_active = False
        user.save()
        assert user.is_active is False

    def test_superuser_has_default_team(self):
        """Superusers should also receive the default team automatically."""
        admin = self.User.objects.create_superuser(email="ADMIN@EXAMPLE.COM", password="123")
        assert admin.team.name == "Default"

    def test_email_saved_lowercase_in_db(self):
        """Ensure that the email saved in the database is in lowercase."""
        user = self.User.objects.create_user(email="MiXeD@ExAmPlE.Com", password="123")
        retrieved = self.User.objects.get(pk=user.pk)
        assert retrieved.email == "mixed@example.com"
