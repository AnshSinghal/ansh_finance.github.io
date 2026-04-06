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


RECORD_DATA = {"amount": "100.00", "type": "income", "category": "Salary", "date": "2024-01-01"}


@pytest.mark.django_db
class TestSummary:
    def test_viewer_can_access_summary(self, client):
        viewer = make_user("vw", "vw@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/dashboard/summary/")
        assert resp.status_code == 200
        assert "total_income" in resp.data

    def test_summary_empty(self, client):
        viewer = make_user("vw2", "vw2@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/dashboard/summary/")
        assert resp.status_code == 200
        assert str(resp.data["total_income"]) == "0.00"

    def test_unauthenticated_cannot_access_summary(self, client):
        resp = client.get("/api/v1/dashboard/summary/")
        assert resp.status_code == 401


@pytest.mark.django_db
class TestCategories:
    def test_viewer_cannot_access_categories(self, client):
        viewer = make_user("vw3", "vw3@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/dashboard/categories/")
        assert resp.status_code == 403

    def test_analyst_can_access_categories(self, client):
        analyst = make_user("an", "an@t.com", "Analyst123!", role=Role.ANALYST)
        auth(client, analyst, "Analyst123!")
        resp = client.get("/api/v1/dashboard/categories/")
        assert resp.status_code == 200


@pytest.mark.django_db
class TestTrends:
    def test_viewer_cannot_access_trends(self, client):
        viewer = make_user("vw4", "vw4@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/dashboard/trends/")
        assert resp.status_code == 403

    def test_analyst_can_access_trends(self, client):
        analyst = make_user("an2", "an2@t.com", "Analyst123!", role=Role.ANALYST)
        auth(client, analyst, "Analyst123!")
        resp = client.get("/api/v1/dashboard/trends/")
        assert resp.status_code == 200
        assert "trends" in resp.data


@pytest.mark.django_db
class TestRecent:
    def test_viewer_can_access_recent(self, client):
        viewer = make_user("vw5", "vw5@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/dashboard/recent/")
        assert resp.status_code == 200
        assert "recent" in resp.data
