import random
import pytest
from fastapi.testclient import TestClient
from bil.main import app, get_db
from bil.dbfile import DBAdaptor
import os, shutil
import base64


@pytest.fixture
def client(fs):
    def in_memory_db():
        return DBAdaptor("test_data")

    app.dependency_overrides[get_db] = in_memory_db
    yield TestClient(app)
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")


@pytest.fixture
def fake_payment():
    return {"name": "Test Payment", "date": "2022-01-01", "asset": 10000}


small_pdf = b"""%PDF-1.1
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Count 0 /Kids [ ] >>
endobj
xref
0 3
0000000000 65535 f 
0000000009 00000 n 
0000000051 00000 n 
trailer
<< /Size 3 /Root 1 0 R >>
startxref
83
%%EOF"""

small_jpeg = base64.b64decode(
    "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP////////////////////////////////////////////////////////////////"
    + "//////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
)


def test_read_main(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == "pong"


def test_getting_projects_from_blank_db_returns_empty_list(client):
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_can_add_new_project(client):
    response = client.post("/projects", json={"name": "Test Project"})
    assert response.status_code == 200
    assert response.json() == {"id": 1}
    response = client.get("/projects")
    assert len(response.json()) == 1


def test_can_get_all_projects(client):
    client.post("/projects", json={"name": "Test Project 1"})
    client.post("/projects", json={"name": "Test Project 2"})
    response = client.get("/projects")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_can_delete_project(client):
    resp = client.post("/projects", json={"name": "Test Project 2"})
    new_id = resp.json()["id"]
    client.delete(f"/projects/{new_id}")
    response = client.get("/projects")
    assert len(response.json()) == 0


def test_deleting_nonexistent_project_raises_error(client):
    resp = client.delete("/projects/42")
    assert resp.status_code == 404


def test_deleting_same_project_twice_raises_error(client):
    resp = client.post("/projects", json={"name": "Test Project 2"})
    new_id = resp.json()["id"]
    client.delete(f"/projects/{new_id}")
    assert resp.status_code == 200
    resp = client.delete(f"/projects/{new_id}")
    assert resp.status_code == 404


def test_can_add_new_paygroup(client):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    response = client.post(f"/projects/{new_id}/paygroups", json={"name": "Test Paygroup"})
    assert response.status_code == 200
    assert response.json() == {"id": 1}


def test_can_get_paygroups_from_project(client):
    resp = client.post("/projects", json={"name": "Test Project"})
    new_id = resp.json()["id"]
    client.post(f"/projects/{new_id}/paygroups", json={"name": "Test Paygroup"})
    response = client.get(f"/projects/{new_id}")
    project = response.json()
    group = project["paygroups"][0]
    assert response.status_code == 200
    assert len(project["paygroups"]) == 1
    assert group["id"] == 1
    assert group["name"] == "Test Paygroup"


def test_getting_nonexistent_project_raises_error(client):
    resp = client.get("/projects/42")
    assert resp.status_code == 404


def test_deleting_nonexistent_paygroup_raises_error(client):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    resp = client.delete(f"/projects/{new_id}/paygroups/42")
    assert resp.status_code == 404


def test_can_delete_paygroup(client):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    resp = client.post(f"/projects/{new_id}/paygroups", json={"name": "Test Paygroup"})
    new_group_id = resp.json()["id"]
    resp = client.delete(f"/projects/{new_id}/paygroups/{new_group_id}")
    assert resp.status_code == 200
    resp = client.get(f"/projects/{new_id}")
    assert len(resp.json()["paygroups"]) == 0


def test_cannot_add_payment_without_asset_or_liability(client):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    resp = client.post(f"/projects/{new_id}/paygroups", json={"name": "Test Paygroup"})
    new_group_id = resp.json()["id"]
    resp = client.post(f"/projects/{new_id}/paygroups/{new_group_id}/payments", json={})
    assert resp.status_code == 422


def test_cannot_add_payment_to_nonexistent_paygroup(client, fake_payment):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    client.post(f"/projects/{new_id}/paygroups", json={"name": "Test Paygroup"})
    resp = client.post(f"/projects/{new_id}/paygroups/42/payments", json=fake_payment)
    assert resp.status_code == 404


def test_can_add_payment_with_asset_or_liability_only(client, fake_payment):
    fake_payment.pop("liability", None)
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    resp = client.post(f"/projects/{new_id}/paygroups", json={"name": "Test Paygroup"})
    new_group_id = resp.json()["id"]
    fake_payment["asset"] = 10000
    resp = client.post(f"/projects/{new_id}/paygroups/{new_group_id}/payments", json=fake_payment)
    assert resp.status_code == 200

    fake_payment.pop("asset", None)
    fake_payment["liability"] = 10000
    resp = client.post(f"/projects/{new_id}/paygroups/{new_group_id}/payments", json=fake_payment)
    assert resp.status_code == 200

    project_resp = client.get(f"/projects/{new_id}")
    payments = project_resp.json()["paygroups"][0]["payments"]
    assert len(payments) == 2
    assert payments[0]["asset"] == 10000
    assert payments[0]["liability"] == 0
    assert payments[1]["asset"] == 0
    assert payments[1]["liability"] == 10000


def test_cannot_delete_nonexistent_payment(client):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    resp = client.post(f"/projects/{new_id}/paygroups", json={"name": "Test Paygroup"})
    new_group_id = resp.json()["id"]
    resp = client.delete(f"/projects/{new_id}/paygroups/{new_group_id}/payments/42")
    assert resp.status_code == 404


def test_can_delete_payment(client, fake_payment):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    resp = client.post(f"/projects/{new_id}/paygroups", json={"name": "Test Paygroup"})
    new_group_id = resp.json()["id"]
    resp = client.post(f"/projects/{new_id}/paygroups/{new_group_id}/payments", json=fake_payment)
    new_payment_id = resp.json()["id"]
    resp = client.delete(f"/projects/{new_id}/paygroups/{new_group_id}/payments/{new_payment_id}")
    assert resp.status_code == 200
    project_resp = client.get(f"/projects/{new_id}")
    assert len(project_resp.json()["paygroups"][0]["payments"]) == 0


def test_cannot_update_nonexistent_paygroup(client):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    resp = client.put(f"/projects/{new_id}/paygroups/42", json={"name": "Test Paygroup"})
    assert resp.status_code == 404


def test_can_update_paygroup(client):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    resp = client.post(f"/projects/{new_id}/paygroups", json={"name": "Test Paygroup"})
    new_group_id = resp.json()["id"]
    random_number = random.randint(0, 1000)
    new_name = f"updated group {random_number}"
    resp = client.put(f"/projects/{new_id}/paygroups/{new_group_id}", json={"name": new_name})
    assert resp.status_code == 200
    resp = client.get(f"/projects/{new_id}")
    assert resp.json()["paygroups"][0]["name"] == new_name


def test_cannot_update_nonexistent_project(client):
    resp = client.put("/projects/42", json={"name": "Test Project"})
    assert resp.status_code == 404


def test_can_update_project_name(client):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    random_number = random.randint(0, 1000)
    new_name = f"updated project {random_number}"
    update_resp = client.put(f"/projects/{new_id}", json={"name": new_name})
    assert update_resp.status_code == 200
    resp = client.get(f"/projects/{new_id}")
    assert resp.json()["name"] == new_name


def test_can_update_payment(client, fake_payment):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    new_paygroup_resp = client.post(f"/projects/{new_id}/paygroups", json={"name": "Test Paygroup"})
    new_group_id = new_paygroup_resp.json()["id"]
    new_paymen_resp = client.post(f"/projects/{new_id}/paygroups/{new_group_id}/payments", json=fake_payment)
    new_payment_id = new_paymen_resp.json()["id"]
    random_number = random.randint(0, 1000)
    updated_payment = {
        "name": f"updated payment {random_number}",
        "asset": random.randint(0, 1000),
        "liability": random.randint(0, 1000),
        "date": "1990-05-15",
    }
    update_payments_resp = client.put(
        f"/projects/{new_id}/paygroups/{new_group_id}/payments/{new_payment_id}", json=updated_payment
    )
    assert update_payments_resp.status_code == 200
    updated_project = client.get(f"/projects/{new_id}")
    payment = updated_project.json()["paygroups"][0]["payments"][0]
    assert payment["name"] == updated_payment["name"]
    assert payment["asset"] == updated_payment["asset"]
    assert payment["liability"] == updated_payment["liability"]
    assert payment["date"] == updated_payment["date"]


def test_cannot_upload_files_invalid_mimetype(client, fake_payment):
    client.post("/projects", json={"name": "Test Project"})
    client.post("/projects/1/paygroups", json={"name": "Test Paygroup"})
    client.post("/projects/1/paygroups/1/payments", json=fake_payment)
    adding_js_resp = client.post(
        "/projects/1/paygroups/1/payments/1/files", files={"file": ("bad-file.js", b"test-data", "text/plain")}
    )
    assert adding_js_resp.status_code == 415

    adding_fake_pdf_resp = client.post(
        "/projects/1/paygroups/1/payments/1/files", files={"file": ("test.pdf", b"test-data", "application/pdf")}
    )
    assert adding_fake_pdf_resp.status_code == 415


def test_cannot_add_files_to_nonexistent_payment(client):
    client.post("/projects", json={"name": "Test Project"})
    client.post("/projects/1/paygroups", json={"name": "Test Paygroup"})
    resp = client.post(
        "/projects/1/paygroups/1/payments/1/files", files={"file": ("test.pdf", small_pdf, "application/pdf")}
    )
    assert resp.status_code == 404


def test_can_add_files_to_payment(client, fake_payment):
    client.post("/projects", json={"name": "Test Project"})
    client.post("/projects/1/paygroups", json={"name": "Test Paygroup"})
    client.post("/projects/1/paygroups/1/payments", json=fake_payment)
    added_pdf_resp = client.post(
        "/projects/1/paygroups/1/payments/1/files", files={"file": ("test.pdf", small_pdf, "application/pdf")}
    )
    assert added_pdf_resp.status_code == 200
    added_jpeg_resp = client.post(
        "/projects/1/paygroups/1/payments/1/files", files={"file": ("test.jpeg", small_jpeg, "image/jpeg")}
    )
    assert added_jpeg_resp.status_code == 200


def test_cannot_get_files_from_nonexistent_payment(client):
    client.post("/projects", json={"name": "Test Project"})
    client.post("/projects/1/paygroups", json={"name": "Test Paygroup"})
    resp = client.get("/projects/1/paygroups/1/payments/1/files")
    assert resp.status_code == 404


def test_cannot_get_files_from_when_none_added(client, fake_payment):
    client.post("/projects", json={"name": "Test Project"})
    client.post("/projects/1/paygroups", json={"name": "Test Paygroup"})
    client.post("/projects/1/paygroups/1/payments", json=fake_payment)
    project_resp = client.get("/projects/1").json()
    assert not project_resp["paygroups"][0]["payments"][0]["attachment"]
    resp = client.get("/projects/1/paygroups/1/payments/1/files")
    assert resp.status_code == 404


def test_can_get_files_from_payment(client, fake_payment):
    client.post("/projects", json={"name": "Test Project"})
    client.post("/projects/1/paygroups", json={"name": "Test Paygroup"})
    client.post("/projects/1/paygroups/1/payments", json=fake_payment)
    client.post("/projects/1/paygroups/1/payments/1/files", files={"file": ("test.pdf", small_pdf, "application/pdf")})
    project_resp = client.get("/projects/1").json()
    payments = project_resp["paygroups"][0]["payments"]
    assert payments[0]["attachment"] == "1_1.pdf"
    resp = client.get("/projects/1/paygroups/1/payments/1/files")
    assert resp.status_code == 200
    assert resp.content == small_pdf


def test_can_remove_files_from_payment(client, fake_payment):
    client.post("/projects", json={"name": "Test Project"})
    client.post("/projects/1/paygroups", json={"name": "Test Paygroup"})
    client.post("/projects/1/paygroups/1/payments", json=fake_payment)
    client.post("/projects/1/paygroups/1/payments/1/files", files={"file": ("test.pdf", small_pdf, "application/pdf")})
    resp = client.delete("/projects/1/paygroups/1/payments/1/files")
    assert resp.status_code == 200
    project_resp = client.get("/projects/1").json()
    assert not project_resp["paygroups"][0]["payments"][0]["attachment"]


@pytest.mark.skip
def test_can_view_previous_states_of_project(client):
    pass
