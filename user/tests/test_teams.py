import pytest
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from user.models import Team, CustomUser

@pytest.mark.django_db
class TestTeams:

    def test_create_team(self):

        team = Team.objects.create(name="Equipo A")
        assert team.name == "Equipo A"

    def test_str_team(self):

        team = Team.objects.create(name="Equipo B")
        assert str(team) == "Equipo B"

    def test_assign_team_to_user(self):

        team = Team.objects.create(name="Equipo B")
        user = CustomUser.objects.create_user(email="usuario@example.com", password="123456", team=team)
        assert user.team == team
        assert user.team.name == "Equipo B"

    def test_cannot_delete_team_with_users(self):

        team = Team.objects.create(name="Equipo Y")
        user = CustomUser.objects.create_user(email="survive@example.com", password="123", team=team)
        with pytest.raises(ProtectedError):
            team.delete()

    def test_team_name_cannot_be_empty(self):

        team = Team(name="")
        with pytest.raises(ValidationError):
            team.full_clean()  # triggers model validation

    def test_team_name_max_length(self):

        long_name = "A" * 101
        team = Team(name=long_name)
        with pytest.raises(ValidationError):
            team.full_clean()
