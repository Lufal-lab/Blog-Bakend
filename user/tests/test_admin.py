import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from user.models import Team

@pytest.mark.django_db
class TestAdminAccess:
    """
    Tests related to access to the Django admin panel.

    Verifies that superusers can access admin pages, while normal users cannot.
    Also tests creating a team from the admin panel.
    """

    def setup_method(self):
        self.User = get_user_model()
        self.team = Team.objects.create(name="TestTeam")
        self.admin_user = self.User.objects.create_superuser(
            email="admin@example.com", password="admin123"
        )
        self.normal_user = self.User.objects.create_user(
            email="normal@example.com", password="normal123", team=self.team
        )

    def test_superuser_access_admin(self, client):
        """Superuser can access the admin dashboard."""
        client.force_login(self.admin_user)
        url = reverse("admin:index")
        response = client.get(url)
        assert response.status_code == 200

    def test_normal_user_cannot_access_admin(self, client):
        """Normal users are redirected when trying to access the admin."""
        client.force_login(self.normal_user)
        url = reverse("admin:index")
        response = client.get(url)
        assert response.status_code == 302  # Redirected to login page

    def test_create_team_from_admin(self, client):
        """Superuser can create a new team via admin panel."""
        client.force_login(self.admin_user)
        url = reverse("admin:user_team_add")
        response = client.post(url, {"name": "NuevoTeam"})
        assert response.status_code == 302
        assert Team.objects.filter(name="NuevoTeam").exists()


@pytest.mark.django_db
class TestAdminUserActions:
    """
    Tests for performing CRUD operations on users and teams from the admin panel.

    Verifies editing users, changing teams, and managing teams.
    """

    def setup_method(self):
        self.User = get_user_model()
        self.team_default = Team.objects.get_or_create(name="Default")[0]
        self.team_extra = Team.objects.create(name="ExtraTeam")

    def test_superuser_changes_user_team(self, admin_client):
        """Superuser can change a normal user's team."""
        user = self.User.objects.create_user(
            email="normal@example.com", password="123456", team=self.team_default
        )
        url = reverse("admin:user_customuser_change", args=[user.id])
        response = admin_client.post(url, {
            "email": user.email,
            "is_active": True,
            "is_staff": False,
            "team": self.team_extra.id,
        })
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.team == self.team_extra

    def test_superuser_edits_normal_user(self, admin_client):
        """Superuser can edit normal user's email and active status."""
        user = self.User.objects.create_user(
            email="user2@example.com", password="123", team=self.team_default
        )
        url = reverse("admin:user_customuser_change", args=[user.id])
        response = admin_client.post(url, {
            "email": "user2_edited@example.com",
            "is_active": False,
            "is_staff": False,
            "team": self.team_default.id
        })
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.email == "user2_edited@example.com"
        assert user.is_active is False

    def test_list_display_filters_in_admin(self, admin_client):
        """Check that the user list in admin shows correct headers."""
        url = reverse("admin:user_customuser_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Email" in content
        assert "Staff status" in content
        assert "Active" in content
        assert "Team" in content

    def test_create_team_from_admin(self, admin_client):
        """Superuser can create a team from admin panel."""
        url = reverse("admin:user_team_add")
        response = admin_client.post(url, {"name": "NuevoTeam"})
        assert response.status_code == 302
        assert Team.objects.filter(name="NuevoTeam").exists()

    def test_edit_team_from_admin(self, admin_client):
        """Superuser can edit a team's name from admin panel."""
        team = Team.objects.create(name="TeamToEdit")
        url = reverse("admin:user_team_change", args=[team.id])
        response = admin_client.post(url, {"name": "TeamEdited"})
        assert response.status_code == 302
        team.refresh_from_db()
        assert team.name == "TeamEdited"

    def test_delete_team_from_admin(self, admin_client):
        """Superuser can delete a team from admin panel."""
        team = Team.objects.create(name="TeamToDelete")
        url = reverse("admin:user_team_delete", args=[team.id])
        response = admin_client.post(url, {"post": "yes"})
        assert response.status_code == 302
        assert not Team.objects.filter(id=team.id).exists()
