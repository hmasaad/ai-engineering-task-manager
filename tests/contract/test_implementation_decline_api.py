def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_not_carried_out_contract(client):
    task_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": "Drop the old export path", "class": "consequential"},
    )
    change_id = recorded.json()["implementation_changes"][0]["id"]
    blank = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/not-carried-out",
        json={"reason": "   "},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "A reason is required."

    declined = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/not-carried-out",
        json={"reason": "The old path is still required", "engineer_name": "Someone Else"},
    )
    assert declined.status_code == 200
    change = declined.json()["implementation_changes"][0]
    assert declined.json()["status"] == "In Progress"
    assert change["outcome"] == "Not carried out"
    assert change["not_carried_out"]["reason"] == "The old path is still required"
    assert change["not_carried_out"]["engineer_name"] == "Ada"
    assert change["not_carried_out"]["declined_at"]

    approved = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/approve",
        json={"evidence": "Too late"},
    )
    assert approved.status_code == 409
    assert approved.json()["message"] == "It cannot be carried out."
