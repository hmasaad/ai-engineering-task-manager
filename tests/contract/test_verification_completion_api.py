def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_complete_names_a_change_that_lacks_a_passing_check(client):
    task_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": "Rename the export label", "class": "ordinary"},
    )
    change = recorded.json()["implementation_changes"][0]
    assert change["passing_check"] is False
    criterion_id = recorded.json()["criteria"][0]["id"]
    client.post(
        f"/api/tasks/{task_id}/criteria/{criterion_id}/verify",
        json={"observation": "Seen", "pass_result": "pass"},
    )
    refused = client.post(f"/api/tasks/{task_id}/transitions", json={"action": "complete"})
    assert refused.status_code == 409
    assert refused.json() == {
        "refused": True,
        "message": "Needs a passing check: Rename the export label.",
    }
    assert client.get(f"/api/tasks/{task_id}").json()["status"] == "In Progress"

    checked = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change['id']}/checks",
        json={"criterion_id": criterion_id, "evidence": "Seen", "result": "Passed"},
    )
    assert checked.json()["implementation_changes"][0]["passing_check"] is True
    completed = client.post(f"/api/tasks/{task_id}/transitions", json={"action": "complete"})
    assert completed.status_code == 200
    assert completed.json()["status"] == "Completed"


def test_cancel_does_not_mention_a_missing_passing_check(client):
    task_id = _in_progress(client)
    client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": "Rename the export label", "class": "ordinary"},
    )
    cancelled = client.post(
        f"/api/tasks/{task_id}/transitions",
        json={"action": "cancel", "reason": "Superseded by another task"},
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "Cancelled"
    assert "Needs a passing check:" not in cancelled.text
