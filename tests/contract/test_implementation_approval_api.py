def _in_progress(client, title="Add export") -> tuple[int, int]:
    task_id = client.post("/api/tasks", json={"title": title}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    body = client.post(
        f"/api/tasks/{task_id}/criteria",
        json={"text": "The file contains the goal"},
    ).json()
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id, body["criteria"][0]["id"]


def test_approve_contract(client):
    task_id, _criterion_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": "Replace the stored export name", "class": "consequential"},
    )
    change_id = recorded.json()["implementation_changes"][0]["id"]
    blank = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/approve",
        json={"evidence": "  ", "engineer_name": "Someone Else"},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "An account of the evidence reviewed is required."

    approved = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/approve",
        json={"evidence": "The detail page shows the new export name"},
    )
    assert approved.status_code == 200
    change = approved.json()["implementation_changes"][0]
    assert approved.json()["status"] == "In Progress"
    assert change["outcome"] == "Carried out"
    assert change["approval"]["engineer_name"] == "Ada"
    assert change["approval"]["evidence"] == "The detail page shows the new export name"


def test_complete_and_cancel_name_waiting_changes(client):
    task_id, criterion_id = _in_progress(client)
    client.post(
        f"/api/tasks/{task_id}/criteria/{criterion_id}/verify",
        json={"observation": "Seen", "pass_result": "pass"},
    )
    client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": "Replace the stored export name", "class": "consequential"},
    )
    blocked = client.post(f"/api/tasks/{task_id}/transitions", json={"action": "complete"})
    assert blocked.status_code == 409
    assert blocked.json()["message"] == "Awaiting approval: Replace the stored export name."
    cancelled = client.post(
        f"/api/tasks/{task_id}/transitions",
        json={"action": "cancel", "reason": "Stop"},
    )
    assert cancelled.status_code == 409
    assert cancelled.json()["message"] == "Awaiting approval: Replace the stored export name."

    plain_id, _plain_criterion = _in_progress(client, "Plain")
    plain = client.post(f"/api/tasks/{plain_id}/transitions", json={"action": "complete"})
    assert plain.status_code == 409
    assert plain.json()["message"] == "Unverified criteria: The file contains the goal."
    assert "Awaiting approval" not in plain.json()["message"]
