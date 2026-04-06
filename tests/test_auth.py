import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def register_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123!",
        "first_name": "Test",
        "last_name": "User",
        "role": "viewer",
    }


@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, client, register_data):
        resp = client.post("/api/v1/auth/register/", register_data, format="json")
        assert resp.status_code == 201
        assert resp.data["username"] == "testuser"
        assert resp.data["role"] == "viewer"

    def test_register_duplicate_email(self, client, register_data):
        client.post("/api/v1/auth/register/", register_data, format="json")
        register_data["username"] = "other"
        resp = client.post("/api/v1/auth/register/", register_data, format="json")
        assert resp.status_code == 400

    def test_register_duplicate_username(self, client, register_data):
        client.post("/api/v1/auth/register/", register_data, format="json")
        register_data["email"] = "other@example.com"
        resp = client.post("/api/v1/auth/register/", register_data, format="json")
        assert resp.status_code == 400

    def test_register_weak_password(self, client, register_data):
        register_data["password"] = "weak"
        resp = client.post("/api/v1/auth/register/", register_data, format="json")
        assert resp.status_code == 400

    def test_register_invalid_email(self, client, register_data):
        register_data["email"] = "not-an-email"
        resp = client.post("/api/v1/auth/register/", register_data, format="json")
        assert resp.status_code == 400


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, client, register_data):
        client.post("/api/v1/auth/register/", register_data, format="json")
        resp = client.post("/api/v1/auth/login/", {"username": register_data["username"], "password": register_data["password"]}, format="json")
        assert resp.status_code == 200
        assert "access" in resp.data
        assert "refresh" in resp.data

    def test_login_wrong_password(self, client, register_data):
        client.post("/api/v1/auth/register/", register_data, format="json")
        resp = client.post("/api/v1/auth/login/", {"username": register_data["username"], "password": "Wrong123!"}, format="json")
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/v1/auth/login/", {"username": "nobody", "password": "Nobody123!"}, format="json")
        assert resp.status_code == 401


@pytest.mark.django_db
class TestRefresh:
    def test_refresh_success(self, client, register_data):
        client.post("/api/v1/auth/register/", register_data, format="json")
        login = client.post("/api/v1/auth/login/", {"username": register_data["username"], "password": register_data["password"]}, format="json")
        resp = client.post("/api/v1/auth/refresh/", {"refresh": login.data["refresh"]}, format="json")
        assert resp.status_code == 200
        assert "access" in resp.data

    def test_refresh_invalid_token(self, client):
        resp = client.post("/api/v1/auth/refresh/", {"refresh": "invalid"}, format="json")
        assert resp.status_code == 401
