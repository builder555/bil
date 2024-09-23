import random
from bil.datamodels import Project
import pytest
from fastapi.testclient import TestClient
from bil.main import app, get_db
from bil.dbfile import DBAdaptor
import os, shutil


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
    resp = client.put(f"/projects/{new_id}", json={"name": new_name})
    assert resp.status_code == 200
    resp = client.get(f"/projects/{new_id}")
    assert resp.json()["name"] == new_name


def test_can_update_payment(client, fake_payment):
    project_resp = client.post("/projects", json={"name": "Test Project"})
    new_id = project_resp.json()["id"]
    resp = client.post(f"/projects/{new_id}/paygroups", json={"name": "Test Paygroup"})
    new_group_id = resp.json()["id"]
    resp = client.post(f"/projects/{new_id}/paygroups/{new_group_id}/payments", json=fake_payment)
    new_payment_id = resp.json()["id"]
    random_number = random.randint(0, 1000)
    updated_payment = {
        "name": f"updated payment {random_number}",
        "asset": random.randint(0, 1000),
        "liability": random.randint(0, 1000),
        "date": "1990-05-15",
    }
    resp = client.put(f"/projects/{new_id}/paygroups/{new_group_id}/payments/{new_payment_id}", json=updated_payment)
    assert resp.status_code == 200
    resp = client.get(f"/projects/{new_id}")
    assert resp.json()["paygroups"][0]["payments"][0] == {**updated_payment, "id": new_payment_id}
