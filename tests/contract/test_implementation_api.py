def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_record_ordinary_change_and_ignore_engineer_name(client):
    task_id = _in_progress(client)
    blank = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": "   ", "class": "ordinary"},
    )
    assert blank.status_code == 400
    assert blank.json() == {
        "refused": True,
        "message": "An account of what changed is required.",
    }

    missing_class = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": "Rename the export label"},
    )
    assert missing_class.status_code == 400
    assert missing_class.json()["message"] == "Choose ordinary or consequential."

    recorded = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={
            "what_changed": "Rename the export label",
            "class": "ordinary",
            "engineer_name": "Someone Else",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    assert body["status"] == "In Progress"
    change = body["implementation_changes"][0]
    assert change["what_changed"] == "Rename the export label"
    assert change["class"] == "ordinary"
    assert change["outcome"] == "Carried out"
    assert change["engineer_name"] == "Ada"
    assert change["approval"] is None

    detail = client.get(f"/api/tasks/{task_id}")
    assert detail.status_code == 200
    assert detail.json()["implementation_changes"][0]["id"] == change["id"]


def test_record_refuses_the_wrong_status(client):
    draft_id = client.post("/api/tasks", json={"title": "Draft"}).json()["id"]
    draft = client.post(
        f"/api/tasks/{draft_id}/implementation-changes",
        json={"what_changed": "Rename the export label", "class": "ordinary"},
    )
    assert draft.status_code == 409
    assert draft.json()["message"] == "The task must be In Progress."

    ready_id = client.post("/api/tasks", json={"title": "Ready"}).json()["id"]
    client.patch(f"/api/tasks/{ready_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{ready_id}/criteria", json={"text": "Visible"})
    client.post(f"/api/tasks/{ready_id}/transitions", json={"action": "mark_ready"})
    ready = client.post(
        f"/api/tasks/{ready_id}/implementation-changes",
        json={"what_changed": "Rename the export label", "class": "ordinary"},
    )
    assert ready.status_code == 409
    assert ready.json()["message"] == "Start the task first."

    missing = client.post(
        "/api/tasks/99999/implementation-changes",
        json={"what_changed": "Rename the export label", "class": "ordinary"},
    )
    assert missing.status_code == 404
    assert missing.json()["message"] == "Task not found."
