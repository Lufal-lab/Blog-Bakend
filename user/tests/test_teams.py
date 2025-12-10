import pytest
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from user.models import Team, CustomUser

@pytest.mark.django_db
class TestTeams:
    def test_crear_team(self):
        equipo = Team.objects.create(name="Equipo A")
        assert equipo.name == "Equipo A"

    def test_str_team(self):
        equipo = Team.objects.create(name="Equipo B")
        assert str(equipo) == "Equipo B"

    def test_asignar_team_a_usuario(self):
        equipo = Team.objects.create(name="Equipo B")
        user = CustomUser.objects.create_user(email="usuario@example.com", password="123456", team=equipo)
        assert user.team == equipo
        assert user.team.name == "Equipo B"

    def test_no_se_puede_eliminar_team_con_usuarios(self):
        team = Team.objects.create(name="Equipo Y")
        user = CustomUser.objects.create_user(email="survive@example.com", password="123", team=team)
        with pytest.raises(ProtectedError):
            team.delete()


    def test_nombre_team_no_puede_ser_vacio(self):
        t = Team(name="")
        with pytest.raises(ValidationError):
            t.full_clean()

    def test_team_name_max_length(self):
        nombre_largo = "A" * 101
        team = Team(name=nombre_largo)
        with pytest.raises(ValidationError):
            team.full_clean()
