# posts/tests_api.py

import pytest
from rest_framework.test import APIClient
from django.urls import reverse

from django.contrib.auth import get_user_model
from posts.models import Post
from user.models import Team


@pytest.mark.django_db
class TestPostAPI:

    def setup_method(self):
        self.client = APIClient()
        self.User = get_user_model()

        # Creamos equipos
        self.team1 = Team.objects.create(name="Team A")
        self.team2 = Team.objects.create(name="Team B")

        # Creamos usuarios
        self.autor = self.User.objects.create_user(
            email="autor@example.com",
            password="123",
            team=self.team1
        )

        self.user_same_team = self.User.objects.create_user(
            email="same@example.com",
            password="123",
            team=self.team1
        )

        self.user_other_team = self.User.objects.create_user(
            email="other@example.com",
            password="123",
            team=self.team2
        )


    # ======================================================
    # 1. LECTURA - usuario NO autenticado
    # ======================================================
    def test_list_posts_anonymous(self):
        # Creamos posts con distintas privacidades
        Post.objects.create(
            author=self.autor,
            title="Publico",
            content="x",
            privacy_read=Post.PRIVACY_PUBLIC
        )

        Post.objects.create(
            author=self.autor,
            title="Privado",
            content="x",
            privacy_read=Post.PRIVACY_AUTHOR
        )

        url = "/api/posts/"

        response = self.client.get(url)

        # Debe responder OK
        assert response.status_code == 200

        # Solo debe devolver 1 post (el público)
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Publico"


    # ======================================================
    # 2. LECTURA - usuario autenticado
    # ======================================================
    def test_list_posts_authenticated(self):
        # Autenticamos al usuario
        self.client.force_authenticate(user=self.user_same_team)

        Post.objects.create(
            author=self.autor,
            title="Publico",
            content="x",
            privacy_read=Post.PRIVACY_PUBLIC
        )

        Post.objects.create(
            author=self.autor,
            title="Solo Team",
            content="x",
            privacy_read=Post.PRIVACY_TEAM
        )

        url = "/api/posts/"
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 2


    # ======================================================
    # 3. CREAR post (solo autenticados)
    # ======================================================
    def test_create_post_unauthenticated(self):
        url = "/api/posts/"

        data = {
            "title": "Nuevo",
            "content": "Contenido"
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == 403  # Prohibido


    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.autor)

        url = "/api/posts/"
        data = {
            "title": "Nuevo post",
            "content": "Contenido"
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == 201
        assert Post.objects.count() == 1
        assert Post.objects.first().author == self.autor


    # ======================================================
    # 4. EDITAR post
    # ======================================================
    def test_edit_post_no_permission(self):
        post = Post.objects.create(
            author=self.autor,
            title="Original",
            content="x",
            privacy_write=Post.PRIVACY_AUTHOR
        )

        self.client.force_authenticate(user=self.user_other_team)

        url = f"/api/posts/{post.id}/"

        data = {
            "title": "Hackeado",
            "content": "nuevo"
        }

        response = self.client.put(url, data, format="json")

        assert response.status_code == 403


    def test_edit_post_with_permission(self):
        post = Post.objects.create(
            author=self.autor,
            title="Original",
            content="x",
            privacy_write=Post.PRIVACY_AUTHOR
        )

        self.client.force_authenticate(user=self.autor)

        url = f"/api/posts/{post.id}/"

        data = {
            "title": "Actualizado",
            "content": "nuevo"
        }

        response = self.client.put(url, data, format="json")

        assert response.status_code == 200
        post.refresh_from_db()
        assert post.title == "Actualizado"
