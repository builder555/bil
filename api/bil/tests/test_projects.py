import random


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


def test_can_update_project_name(client_with_project):
    client, project_id = client_with_project
    new_name = f"updated project {random.randint(0, 1000)}"
    update_resp = client.put(f"/projects/{project_id}", json={"name": new_name})
    assert update_resp.status_code == 200
    updated_project = client.get(f"/projects/{project_id}").json()
    assert updated_project["name"] == new_name


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
