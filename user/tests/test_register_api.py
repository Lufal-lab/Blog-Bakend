import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from user.models import Team

@pytest.mark.django_db
class TestUserViews:

    def setup_method(self):

        self.User = get_user_model()
        Team.objects.get_or_create(name="Default")

    def test_normal_user_cannot_access_admin(self, client):

        user = self.User.objects.create_user(email="normal@example.com", password="123456")
        client.login(email="normal@example.com", password="123456")
        url_admin = reverse("admin:index")
        response = client.get(url_admin)
        assert response.status_code == 302

    def test_login_with_email_works(self, client):

        email = "login@example.com"
        password = "pass123"
        self.User.objects.create_user(email=email, password=password)
        assert client.login(email=email, password=password) is True

    def test_login_fails_with_wrong_password(self, client):

        email = "fail@example.com"
        self.User.objects.create_user(email=email, password="correct")
        assert client.login(email=email, password="wrong") is False

    def test_login_fails_if_user_inactive(self, client):

        user = self.User.objects.create_user(email="inactive@example.com", password="123")
        user.is_active = False
        user.save()
        result = client.login(email="inactive@example.com", password="123")
        assert result is False

    def test_logout_works(self, client):

        user = self.User.objects.create_user(email="logout@example.com", password="123")
        client.login(email="logout@example.com", password="123")
        client.logout()
        response = client.get(reverse("admin:index"))
        assert response.status_code == 302

    def test_superuser_can_access_admin_with_force_login(self, client):

        user = self.User.objects.create_superuser(email="force@example.com", password="123")
        client.force_login(user)
        res = client.get(reverse("admin:index"))
        assert res.status_code == 200

    def test_register_login_logout_api(self, client):

        # Registration
        register_url = reverse("user-register")
        register_data = {"email": "testapi@example.com", "password": "strongpass123"}
        res = client.post(register_url, register_data, content_type="application/json")
        assert res.status_code == 201
        json_res = res.json()
        assert "id" in json_res
        assert json_res["email"] == "testapi@example.com"
        assert "team" in json_res

        # Login
        login_url = reverse("user-login")
        login_data = {"email": "testapi@example.com", "password": "strongpass123"}
        res = client.post(login_url, login_data, content_type="application/json")
        assert res.status_code == 200
        json_res = res.json()
        assert "message" in json_res
        assert client.session  # Session cookie exists

        # Logout
        logout_url = reverse("user-logout")
        res = client.post(logout_url)
        assert res.status_code == 200
        json_res = res.json()
        assert json_res["message"] == "Logged out successfully"

    def test_session_cookie_creation_and_usage(self, client):

        # Create a test user
        email = "testcookie@example.com"
        password = "mypassword123"
        user = self.User.objects.create_user(email=email, password=password)

        # Login via API
        url = reverse("user-login")
        response = client.post(url, {"email": email, "password": password})

        # Check login success
        assert response.status_code == 200
        assert "message" in response.data
        assert response.data["message"] == "Login successful"

        # Verify session cookie creation
        assert "sessionid" in response.client.cookies
        session_cookie = response.client.cookies["sessionid"].value
        print("Session cookie value:", session_cookie)

        # Simulate authenticated request using the cookie
        response2 = client.get("/api/protected-endpoint/")  # Replace with actual protected endpoint
        assert response2.status_code != 401
