import random


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


def test_can_update_paygroup(client_with_paygroup):
    client, project_id, group_id = client_with_paygroup
    random_number = random.randint(0, 1000)
    new_name = f"updated group {random_number}"
    update_response = client.put(f"/projects/{project_id}/paygroups/{group_id}", json={"name": new_name})
    assert update_response.status_code == 200
    project = client.get(f"/projects/{project_id}").json()
    assert project["paygroups"][0]["name"] == new_name


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

def test_paygroup_cannot_have_empty_name(client_with_project):
    client, project_id = client_with_project
    resp = client.post(f"/projects/{project_id}/paygroups", json={"name": ""})
    assert resp.status_code == 422