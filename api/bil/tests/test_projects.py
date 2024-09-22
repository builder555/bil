from bil.datamodels import Project
import pytest
from fastapi.testclient import TestClient
from bil.main import app, get_db
from bil.dbfile import DBAdaptor


@pytest.fixture
def client(fs):
    def in_memory_db():
        return DBAdaptor("test_data")

    app.dependency_overrides[get_db] = in_memory_db
    yield TestClient(app)


def test_read_main(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == "pong"


def test_getting_projects_from_blank_db_returns_empty_list(client):
    response = client.get("/projects")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == []


def test_can_add_new_project(client):
    response = client.post("/projects", json={"name": "Test Project"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Test Project"}
