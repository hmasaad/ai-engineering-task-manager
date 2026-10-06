def _ready_id(client) -> tuple[int, int]:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch("/api/tasks/{0}".format(task_id), json={"goal": "Take the record"})
    body = client.post(
        f"/api/tasks/{task_id}/criteria",
        json={"text": "The file contains the goal"},
    ).json()
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    return task_id, body["criteria"][0]["id"]


def test_verify_uses_workspace_engineer_not_request_body(client):
    task_id, criterion_id = _ready_id(client)
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    response = client.post(
        f"/api/tasks/{task_id}/criteria/{criterion_id}/verify",
        json={
            "observation": "The file included the goal.",
            "pass_result": "pass",
            "provider_name": "Someone Else",
        },
    )
    assert response.status_code == 200
    criterion = response.json()["criteria"][0]
    assert criterion["provider_name"] == "Ada"
    assert criterion["pass_result"] == "pass"


def test_complete_reopen_and_cancel_contract(client):
    task_id, criterion_id = _ready_id(client)
    too_soon = client.post(f"/api/tasks/{task_id}/transitions", json={"action": "complete"})
    assert too_soon.status_code == 409
    assert too_soon.json()["refused"] is True

    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    client.post(
        f"/api/tasks/{task_id}/criteria/{criterion_id}/verify",
        json={"observation": "Seen", "pass_result": "pass"},
    )
    completed = client.post(f"/api/tasks/{task_id}/transitions", json={"action": "complete"})
    assert completed.status_code == 200
    assert completed.json()["status"] == "Completed"

    reopened = client.post(
        f"/api/tasks/{task_id}/transitions",
        json={"action": "reopen", "reason": "A missed case was found"},
    )
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "In Progress"
    assert reopened.json()["criteria"][0]["state"] == "Verified"

    client.post(
        f"/api/tasks/{task_id}/criteria/{criterion_id}/unverify",
    )
    cancelled = client.post(
        f"/api/tasks/{task_id}/transitions",
        json={"action": "cancel", "reason": "Superseded by another task"},
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "Cancelled"

    restored = client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    assert restored.status_code == 409
    assert "new task" in restored.json()["message"].lower()
