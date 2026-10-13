def _ready(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    body = client.post(
        f"/api/tasks/{task_id}/criteria",
        json={"text": "The export contains the goal"},
    ).json()
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    return task_id, body["criteria"][0]["id"]


def test_verify_requires_a_method_and_a_run_identifier(client):
    task_id, criterion_id = _ready(client)
    path = f"/api/tasks/{task_id}/criteria/{criterion_id}/verify"
    too_soon = client.post(
        path,
        json={"observation": "Seen", "pass_result": "pass", "method": "", "run_identifier": ""},
    )
    assert too_soon.status_code == 409
    assert too_soon.json()["message"] == "A criterion can be verified only while the task is In Progress."

    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    blank_method = client.post(
        path,
        json={"observation": "Seen", "pass_result": "pass"},
    )
    assert blank_method.status_code == 400
    assert blank_method.json()["message"] == "A verification method is required."
    assert client.get(f"/api/tasks/{task_id}").json()["criteria"][0]["state"] == "Unverified"

    blank_run = client.post(
        path,
        json={"observation": "Seen", "pass_result": "pass", "method": "inspection"},
    )
    assert blank_run.status_code == 400
    assert blank_run.json()["message"] == "A test-run identifier is required."

    verified = client.post(
        path,
        json={
            "observation": "The export contains the goal",
            "pass_result": "pass",
            "method": " inspection ",
            "run_identifier": " local-1 ",
            "provider_name": "Someone Else",
        },
    )
    assert verified.status_code == 200
    criterion = verified.json()["criteria"][0]
    assert criterion["provider_name"] == "Ada"
    assert criterion["method"] == "inspection"
    assert criterion["run_identifier"] == "local-1"
    assert criterion["state"] == "Verified"
