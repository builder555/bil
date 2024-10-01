import random


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


def test_can_update_payment(client_with_payment):
    client, project_id, group_id, pay_id = client_with_payment
    random_number = random.randint(0, 1000)
    updated_payment = {
        "name": f"updated payment {random_number}",
        "asset": random.randint(0, 1000),
        "liability": random.randint(0, 1000),
        "date": "1990-05-15",
        "currency": "CAD",
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
    assert payment["currency"] == updated_payment["currency"]


def test_can_add_files_to_payment(client_with_payment, small_pdf, small_jpeg):
    client, project_id, group_id, payment_id = client_with_payment
    url = f"/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}/files"
    added_pdf_resp = client.post(url, files={"file": ("test.pdf", small_pdf, "application/pdf")})
    assert added_pdf_resp.status_code == 200
    added_jpeg_resp = client.post(url, files={"file": ("test.jpeg", small_jpeg, "image/jpeg")})
    assert added_jpeg_resp.status_code == 200


def test_can_get_files_from_payment(client_with_payment, small_pdf):
    client, project_id, group_id, payment_id = client_with_payment
    url = f"/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}/files"
    client.post(url, files={"file": ("test.pdf", small_pdf, "application/pdf")})
    project_resp = client.get(f"/projects/{project_id}").json()
    payments = project_resp["paygroups"][0]["payments"]
    assert payments[0]["attachment"] == "1_1.pdf"
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.content == small_pdf


def test_can_remove_files_from_payment(client_with_payment, small_pdf):
    client, project_id, group_id, payment_id = client_with_payment
    url = f"/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}/files"
    client.post(url, files={"file": ("test.pdf", small_pdf, "application/pdf")})
    resp = client.delete(url)
    assert resp.status_code == 200
    project_resp = client.get(f"/projects/{project_id}").json()
    assert not project_resp["paygroups"][0]["payments"][0]["attachment"]


def test_cannot_add_payment_to_nonexistent_paygroup(client_with_project, mock_payment):
    client, project_id = client_with_project
    resp = client.post(f"/projects/{project_id}/paygroups/42/payments", json=mock_payment)
    print(resp.json())
    assert resp.status_code == 404


def test_cannot_delete_nonexistent_payment(client_with_paygroup):
    client, project_id, group_id = client_with_paygroup
    resp = client.delete(f"/projects/{project_id}/paygroups/{group_id}/payments/42")
    assert resp.status_code == 404


def test_cannot_add_files_to_nonexistent_payment(client_with_payment, small_pdf):
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
