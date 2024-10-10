import pytest
from fastapi.testclient import TestClient
from bil.main import app
from bil.main import get_db
from bil.dbfile import DBAdaptor
import os
import shutil
import base64


@pytest.fixture
def small_pdf() -> bytearray:
    return (
        b"%PDF-1.1\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<< /Type /Pages /Count 0 /Kids [] >>\n"
        b"endobj\n"
        b"xref\n"
        b"0 3\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000051 00000 n \n"
        b"trailer\n"
        b"<< /Size 3 /Root 1 0 R >>\n"
        b"startxref\n"
        b"83\n"
        b"%%EOF\n"
    )


@pytest.fixture
def small_jpeg() -> bytearray:
    return base64.b64decode(
        "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP////////////////////////////////////////////////////////////////"
        + "//////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
    )


@pytest.fixture
def client() -> TestClient:
    test_data_path = os.path.join("/tmp/ramdisk", "test_data")

    def temp_db():
        return DBAdaptor(test_data_path)

    app.dependency_overrides[get_db] = temp_db
    yield TestClient(app)
    if os.path.exists(test_data_path):
        shutil.rmtree(test_data_path)


@pytest.fixture(scope="session")
def mock_payment() -> dict:
    return {
        "name": "Test Payment",
        "date": "2022-01-01",
        "asset": 1500000000,  # $15
        "liability": 30000000,  # $0.30
        "currency": "USD",
    }


@pytest.fixture(scope="session")
def paygroup_name() -> str:
    return "Test Paygroup"


@pytest.fixture
def client_with_project(client) -> tuple[TestClient, int]:
    resp = client.post("/projects", json={"name": "Test Project"})
    project_id = resp.json()["id"]
    return client, project_id


@pytest.fixture
def client_with_paygroup(client_with_project, paygroup_name) -> tuple[TestClient, int, int]:
    client, project_id = client_with_project
    resp = client.post(f"/projects/{project_id}/paygroups", json={"name": paygroup_name})
    group_id = resp.json()["id"]
    return client, project_id, group_id


@pytest.fixture
def client_with_payment(client_with_paygroup, mock_payment) -> tuple[TestClient, int, int, int]:
    client, project_id, group_id = client_with_paygroup
    resp = client.post(f"/projects/{project_id}/paygroups/{group_id}/payments", json=mock_payment)
    pay_id = resp.json()["id"]
    return client, project_id, group_id, pay_id
