import pytest
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from user.models import Team, CustomUser

@pytest.mark.django_db
class TestTeams:
    """
    Test suite for the Team model.

    Validates:
    - Creation of teams
    - String representation
    - Assignment of teams to users
    - Protection against deleting teams with users
    - Field validations (non-empty name, max length)
    """

    def test_create_team(self):
        """Ensure that a team can be created with a valid name."""
        team = Team.objects.create(name="Equipo A")
        assert team.name == "Equipo A"

    def test_str_team(self):
        """Ensure the string representation of a team returns its name."""
        team = Team.objects.create(name="Equipo B")
        assert str(team) == "Equipo B"

    def test_assign_team_to_user(self):
        """Ensure that a user can be assigned to a team."""
        team = Team.objects.create(name="Equipo B")
        user = CustomUser.objects.create_user(email="usuario@example.com", password="123456", team=team)
        assert user.team == team
        assert user.team.name == "Equipo B"

    def test_cannot_delete_team_with_users(self):
        """Ensure that deleting a team with assigned users raises ProtectedError."""
        team = Team.objects.create(name="Equipo Y")
        user = CustomUser.objects.create_user(email="survive@example.com", password="123", team=team)
        with pytest.raises(ProtectedError):
            team.delete()

    def test_team_name_cannot_be_empty(self):
        """Ensure that a team name cannot be empty."""
        team = Team(name="")
        with pytest.raises(ValidationError):
            team.full_clean()  # triggers model validation

    def test_team_name_max_length(self):
        """Ensure that the team name cannot exceed the max length (100)."""
        long_name = "A" * 101
        team = Team(name=long_name)
        with pytest.raises(ValidationError):
            team.full_clean()
