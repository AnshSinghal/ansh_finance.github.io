import pytest
from rest_framework.test import APIClient
from users.models import User, Role


@pytest.fixture
def client():
    return APIClient()


def make_user(username, email, password, role="viewer"):
    return User.objects.create_user(username=username, email=email, password=password,
                                    first_name="F", last_name="L", role=role)


def auth(client, user, password):
    client.force_authenticate(user=user)


@pytest.mark.django_db
class TestListUsers:
    def test_admin_can_list_users(self, client):
        admin = make_user("adm", "adm@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        resp = client.get("/api/v1/users/")
        assert resp.status_code == 200

    def test_viewer_cannot_list_users(self, client):
        viewer = make_user("vw", "vw@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/users/")
        assert resp.status_code == 403

    def test_unauthenticated_cannot_list_users(self, client):
        resp = client.get("/api/v1/users/")
        assert resp.status_code == 401


@pytest.mark.django_db
class TestGetMe:
    def test_viewer_can_get_me(self, client):
        viewer = make_user("vw2", "vw2@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/users/me/")
        assert resp.status_code == 200
        assert resp.data["username"] == "vw2"


@pytest.mark.django_db
class TestUpdateRole:
    def test_admin_can_change_role(self, client):
        admin = make_user("adm2", "adm2@t.com", "Admin123!", role=Role.ADMIN)
        target = make_user("target", "target@t.com", "Target123!")
        auth(client, admin, "Admin123!")
        resp = client.patch(f"/api/v1/users/{target.pk}/role/", {"role": "analyst"}, format="json")
        assert resp.status_code == 200
        assert resp.data["role"] == "analyst"


@pytest.mark.django_db
class TestDeleteUser:
    def test_admin_can_soft_delete_user(self, client):
        admin = make_user("adm3", "adm3@t.com", "Admin123!", role=Role.ADMIN)
        target = make_user("del_target", "deltarget@t.com", "Target123!")
        auth(client, admin, "Admin123!")
        resp = client.delete(f"/api/v1/users/{target.pk}/")
        assert resp.status_code == 200
        target.refresh_from_db()
        assert target.deleted_at is not None

    def test_admin_cannot_delete_self(self, client):
        admin = make_user("adm4", "adm4@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        resp = client.delete(f"/api/v1/users/{admin.pk}/")
        assert resp.status_code == 400
