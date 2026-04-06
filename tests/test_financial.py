import pytest
from rest_framework.test import APIClient
from users.models import User, Role
from finance.models import FinancialRecord
import datetime


@pytest.fixture
def client():
    return APIClient()


def make_user(username, email, password, role="viewer"):
    return User.objects.create_user(username=username, email=email, password=password,
                                    first_name="F", last_name="L", role=role)


def auth(client, user, password):
    client.force_authenticate(user=user)


RECORD_DATA = {
    "amount": "150.00",
    "type": "income",
    "category": "Salary",
    "date": "2024-01-15",
    "description": "Monthly salary",
}


@pytest.mark.django_db
class TestCreateRecord:
    def test_admin_can_create_record(self, client):
        admin = make_user("adm", "adm@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        resp = client.post("/api/v1/records/", RECORD_DATA, format="json")
        assert resp.status_code == 201
        assert resp.data["category"] == "Salary"

    def test_viewer_cannot_create_record(self, client):
        viewer = make_user("vw", "vw@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.post("/api/v1/records/", RECORD_DATA, format="json")
        assert resp.status_code == 403

    def test_create_invalid_amount(self, client):
        admin = make_user("adm2", "adm2@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        data = {**RECORD_DATA, "amount": "-10"}
        resp = client.post("/api/v1/records/", data, format="json")
        assert resp.status_code == 400


@pytest.mark.django_db
class TestListRecords:
    def test_viewer_can_list_records(self, client):
        viewer = make_user("vw3", "vw3@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/records/")
        assert resp.status_code == 200

    def test_filter_by_type(self, client):
        admin = make_user("adm3", "adm3@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        client.post("/api/v1/records/", RECORD_DATA, format="json")
        resp = client.get("/api/v1/records/?type=income")
        assert resp.status_code == 200

    def test_search(self, client):
        admin = make_user("adm4", "adm4@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        client.post("/api/v1/records/", RECORD_DATA, format="json")
        resp = client.get("/api/v1/records/?search=Salary")
        assert resp.status_code == 200

    def test_pagination(self, client):
        viewer = make_user("vw4", "vw4@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.get("/api/v1/records/?page=1&page_size=5")
        assert resp.status_code == 200


@pytest.mark.django_db
class TestUpdateRecord:
    def test_admin_can_update_record(self, client):
        admin = make_user("adm5", "adm5@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        cr = client.post("/api/v1/records/", RECORD_DATA, format="json")
        record_id = cr.data["id"]
        resp = client.patch(f"/api/v1/records/{record_id}/", {"amount": "200.00"}, format="json")
        assert resp.status_code == 200

    def test_viewer_cannot_update_record(self, client):
        admin = make_user("adm6", "adm6@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        cr = client.post("/api/v1/records/", RECORD_DATA, format="json")
        record_id = cr.data["id"]
        viewer = make_user("vw5", "vw5@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.patch(f"/api/v1/records/{record_id}/", {"amount": "200.00"}, format="json")
        assert resp.status_code == 403


@pytest.mark.django_db
class TestDeleteRecord:
    def test_admin_can_soft_delete_record(self, client):
        admin = make_user("adm7", "adm7@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        cr = client.post("/api/v1/records/", RECORD_DATA, format="json")
        record_id = cr.data["id"]
        resp = client.delete(f"/api/v1/records/{record_id}/")
        assert resp.status_code == 200
        record = FinancialRecord.objects.get(pk=record_id)
        assert record.deleted_at is not None

    def test_viewer_cannot_delete_record(self, client):
        admin = make_user("adm8", "adm8@t.com", "Admin123!", role=Role.ADMIN)
        auth(client, admin, "Admin123!")
        cr = client.post("/api/v1/records/", RECORD_DATA, format="json")
        record_id = cr.data["id"]
        viewer = make_user("vw6", "vw6@t.com", "Viewer123!")
        auth(client, viewer, "Viewer123!")
        resp = client.delete(f"/api/v1/records/{record_id}/")
        assert resp.status_code == 403
