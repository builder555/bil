import random
import pytest
from fastapi.testclient import TestClient
from bil.main import app, get_db
from bil.dbfile import DBAdaptor
import os, shutil
import base64
import platform
import subprocess


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


@pytest.fixture
def client():
    test_data_path = os.path.join("/tmp/ramdisk", "test_data")

    def temp_db():
        return DBAdaptor(test_data_path)

    app.dependency_overrides[get_db] = temp_db
    yield TestClient(app)
    if os.path.exists(test_data_path):
        shutil.rmtree(test_data_path)


@pytest.fixture
def mock_payment():
    return {"name": "Test Payment", "date": "2022-01-01", "asset": 10000, "liability": 15000}


@pytest.fixture
def paygroup_name():
    return "Test Paygroup"


@pytest.fixture
def client_with_project(client):
    resp = client.post("/projects", json={"name": "Test Project"})
    project_id = resp.json()["id"]
    return client, project_id


@pytest.fixture
def client_with_paygroup(client_with_project, paygroup_name):
    client, project_id = client_with_project
    resp = client.post(f"/projects/{project_id}/paygroups", json={"name": paygroup_name})
    group_id = resp.json()["id"]
    return client, project_id, group_id


@pytest.fixture
def client_with_payment(client_with_paygroup, mock_payment):
    client, project_id, group_id = client_with_paygroup
    resp = client.post(f"/projects/{project_id}/paygroups/{group_id}/payments", json=mock_payment)
    pay_id = resp.json()["id"]
    return client, project_id, group_id, pay_id


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
    assert response.json()[0]["name"] == "Test Project 1"
    assert response.json()[1]["name"] == "Test Project 2"


def test_can_delete_project(client_with_project):
    client, project_id = client_with_project
    delete_response = client.delete(f"/projects/{project_id}")
    assert delete_response.status_code == 200
    response = client.get("/projects")
    assert len(response.json()) == 0


def test_can_add_new_paygroup(client_with_project):
    client, project_id = client_with_project
    response = client.post(f"/projects/{project_id}/paygroups", json={"name": "Test Paygroup"})
    assert response.status_code == 200
    assert response.json() == {"id": 1}


def test_can_get_paygroups_from_project(client_with_paygroup, paygroup_name):
    client, project_id, _ = client_with_paygroup
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    project = response.json()
    assert len(project["paygroups"]) == 1
    assert project["paygroups"][0]["name"] == paygroup_name


def test_can_delete_paygroup(client_with_paygroup):
    client, project_id, group_id = client_with_paygroup
    delete_response = client.delete(f"/projects/{project_id}/paygroups/{group_id}")
    assert delete_response.status_code == 200
    project = client.get(f"/projects/{project_id}").json()
    assert len(project["paygroups"]) == 0


def test_can_add_payment_with_asset_or_liability_only(client_with_paygroup, mock_payment):
    mock_payment.pop("liability", None)
    mock_payment["asset"] = 10000
    client, project_id, group_id = client_with_paygroup
    resp = client.post(f"/projects/{project_id}/paygroups/{group_id}/payments", json=mock_payment)
    assert resp.status_code == 200

    mock_payment.pop("asset", None)
    mock_payment["liability"] = 10000
    resp = client.post(f"/projects/{project_id}/paygroups/{group_id}/payments", json=mock_payment)
    assert resp.status_code == 200

    project_resp = client.get(f"/projects/{project_id}")
    payments = project_resp.json()["paygroups"][0]["payments"]
    assert len(payments) == 2
    assert payments[0]["asset"] == 10000
    assert payments[0]["liability"] == 0
    assert payments[1]["asset"] == 0
    assert payments[1]["liability"] == 10000


def test_can_delete_payment(client_with_payment):
    client, project_id, group_id, pay_id = client_with_payment
    delete_response = client.delete(f"/projects/{project_id}/paygroups/{group_id}/payments/{pay_id}")
    assert delete_response.status_code == 200
    project = client.get(f"/projects/{project_id}").json()
    assert len(project["paygroups"][0]["payments"]) == 0


def test_can_update_project_name(client_with_project):
    client, project_id = client_with_project
    new_name = f"updated project {random.randint(0, 1000)}"
    update_resp = client.put(f"/projects/{project_id}", json={"name": new_name})
    assert update_resp.status_code == 200
    updated_project = client.get(f"/projects/{project_id}").json()
    assert updated_project["name"] == new_name


def test_can_update_paygroup(client_with_paygroup):
    client, project_id, group_id = client_with_paygroup
    random_number = random.randint(0, 1000)
    new_name = f"updated group {random_number}"
    update_response = client.put(f"/projects/{project_id}/paygroups/{group_id}", json={"name": new_name})
    assert update_response.status_code == 200
    project = client.get(f"/projects/{project_id}").json()
    assert project["paygroups"][0]["name"] == new_name


def test_can_update_payment(client_with_payment):
    client, project_id, group_id, pay_id = client_with_payment
    random_number = random.randint(0, 1000)
    updated_payment = {
        "name": f"updated payment {random_number}",
        "asset": random.randint(0, 1000),
        "liability": random.randint(0, 1000),
        "date": "1990-05-15",
    }
    update_payments_resp = client.put(
        f"/projects/{project_id}/paygroups/{group_id}/payments/{pay_id}", json=updated_payment
    )
    assert update_payments_resp.status_code == 200
    updated_project = client.get(f"/projects/{project_id}")
    payment = updated_project.json()["paygroups"][0]["payments"][0]
    assert payment["name"] == updated_payment["name"]
    assert payment["asset"] == updated_payment["asset"]
    assert payment["liability"] == updated_payment["liability"]
    assert payment["date"] == updated_payment["date"]


def test_can_add_files_to_payment(client_with_payment):
    client, project_id, group_id, payment_id = client_with_payment
    url = f"/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}/files"
    added_pdf_resp = client.post(url, files={"file": ("test.pdf", small_pdf, "application/pdf")})
    assert added_pdf_resp.status_code == 200
    added_jpeg_resp = client.post(url, files={"file": ("test.jpeg", small_jpeg, "image/jpeg")})
    assert added_jpeg_resp.status_code == 200


def test_can_get_files_from_payment(client_with_payment):
    client, project_id, group_id, payment_id = client_with_payment
    url = f"/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}/files"
    client.post(url, files={"file": ("test.pdf", small_pdf, "application/pdf")})
    project_resp = client.get(f"/projects/{project_id}").json()
    payments = project_resp["paygroups"][0]["payments"]
    assert payments[0]["attachment"] == "1_1.pdf"
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.content == small_pdf


def test_can_remove_files_from_payment(client_with_payment):
    client, project_id, group_id, payment_id = client_with_payment
    url = f"/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}/files"
    client.post(url, files={"file": ("test.pdf", small_pdf, "application/pdf")})
    resp = client.delete(url)
    assert resp.status_code == 200
    project_resp = client.get(f"/projects/{project_id}").json()
    assert not project_resp["paygroups"][0]["payments"][0]["attachment"]


def test_can_list_previous_states_of_project(client_with_paygroup):
    client, project_id, _ = client_with_paygroup
    client.post(f"/projects/{project_id}/paygroups", json={"name": "Test Paygroup updated"})
    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["paygroups"][1]["name"] == "Test Paygroup updated"
    resp = client.get(f"/projects/{project_id}/history")
    states = resp.json()
    assert len(states) == 2


def test_get_project_at_previous_state(client_with_paygroup, paygroup_name):
    client, project_id, _ = client_with_paygroup
    client.post(f"/projects/{project_id}/paygroups", json={"name": "Test new paygroup"})
    resp = client.get("/projects/1")
    assert resp.status_code == 200
    assert resp.json()["paygroups"][1]["name"] == "Test new paygroup"
    history_states = client.get(f"/projects/{project_id}/history").json()
    assert len(history_states) == 2
    history_id = history_states[-1]["id"]
    project_last_state_resp = client.get(f"/projects/{project_id}/history/{history_id}")
    assert project_last_state_resp.status_code == 200
    paygroups = project_last_state_resp.json()["paygroups"]
    assert len(paygroups) == 1
    assert paygroups[0]["name"] == paygroup_name


def test_getting_projects_from_blank_db_returns_empty_list(client):
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_cannot_update_nonexistent_project(client):
    resp = client.put("/projects/42", json={"name": "Test Project"})
    assert resp.status_code == 404


def test_cannot_delete_nonexistent_project(client):
    resp = client.delete("/projects/42")
    assert resp.status_code == 404


def test_cannot_delete_same_project_twice(client_with_project):
    client, project_id = client_with_project
    resp = client.delete(f"/projects/{project_id}")
    assert resp.status_code == 200
    resp = client.delete(f"/projects/{project_id}")
    assert resp.status_code == 404


def test_cannot_get_nonexistent_project(client):
    resp = client.get("/projects/42")
    assert resp.status_code == 404


def test_cannot_add_paygroup_to_nonexistent_project(client):
    resp = client.post(f"/projects/42/paygroups", json={"name": "Test Paygroup"})
    assert resp.status_code == 404


def test_cannot_delete_nonexistent_paygroup(client_with_paygroup):
    client, project_id, _ = client_with_paygroup
    resp = client.delete(f"/projects/{project_id}/paygroups/42")
    assert resp.status_code == 404


def test_cannot_update_nonexistent_paygroup(client_with_project):
    client, project_id = client_with_project
    resp = client.put(f"/projects/{project_id}/paygroups/42", json={"name": "Test Paygroup"})
    assert resp.status_code == 404


def test_cannot_add_payment_to_nonexistent_paygroup(client_with_project, mock_payment):
    client, project_id = client_with_project
    resp = client.post(f"/projects/{project_id}/paygroups/42/payments", json=mock_payment)
    assert resp.status_code == 404


def test_cannot_delete_nonexistent_payment(client_with_paygroup):
    client, project_id, group_id = client_with_paygroup
    resp = client.delete(f"/projects/{project_id}/paygroups/{group_id}/payments/42")
    assert resp.status_code == 404


def test_cannot_add_payment_without_asset_or_liability(client_with_paygroup):
    client, project_id, group_id = client_with_paygroup
    resp = client.post(
        f"/projects/{project_id}/paygroups/{group_id}/payments", json={"name": "Test Payment", "date": "2022-01-01"}
    )
    assert resp.status_code == 422


def test_cannot_add_files_to_nonexistent_payment(client_with_payment):
    client, project_id, group_id, _ = client_with_payment
    resp = client.post(
        f"/projects/{project_id}/paygroups/{group_id}/payments/42/files",
        files={"file": ("test.pdf", small_pdf, "application/pdf")},
    )
    assert resp.status_code == 404


def test_cannot_get_files_from_nonexistent_payment(client_with_payment):
    client, project_id, group_id, _ = client_with_payment
    resp = client.get(f"/projects/{project_id}/paygroups/{group_id}/payments/42/files")
    assert resp.status_code == 404


def test_cannot_get_files_when_none_were_added(client_with_payment):
    client, project_id, group_id, pay_id = client_with_payment
    project_resp = client.get(f"/projects/{project_id}").json()
    assert not project_resp["paygroups"][0]["payments"][0]["attachment"]
    resp = client.get(f"/projects/{project_id}/paygroups/{group_id}/payments/{pay_id}/files")
    assert resp.status_code == 404


def test_cannot_upload_files_of_invalid_type(client_with_payment):
    client, project_id, group_id, payment_id = client_with_payment
    url = f"/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}/files"
    adding_js_resp = client.post(url, files={"file": ("bad-file.js", b"test-data", "text/plain")})
    assert adding_js_resp.status_code == 415

    adding_fake_pdf_resp = client.post(url, files={"file": ("test.pdf", b"test-data", "application/pdf")})
    assert adding_fake_pdf_resp.status_code == 415
