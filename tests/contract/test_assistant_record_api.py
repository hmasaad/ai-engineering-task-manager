def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_engineer_endpoint_ignores_project_and_assistant_name(client):
    task_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={
            "what_changed": "Rename the export label",
            "class": "ordinary",
            "project": "billing",
            "assistant_name": "Guide",
        },
    )
    assert recorded.status_code == 200
    change = recorded.json()["implementation_changes"][0]
    assert change["recorded_by"] == "engineer"
    assert change["project"] is None
    assert change["assistant_name"] is None
    assert change["engineer_name"] == "Ada"
    assert change["outcome"] == "Carried out"


def test_parent_does_not_list_a_subtask_assistant_change(client):
    parent_id = _in_progress(client)
    child_id = client.post(
        f"/api/tasks/{parent_id}/subtasks", json={"title": "Write the checklist"}
    ).json()["id"]
    client.patch(f"/api/tasks/{child_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{child_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{child_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{child_id}/transitions", json={"action": "start"})
    recorded = client.post(
        f"/api/tasks/{child_id}/assistant-changes",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Rename the export label",
        },
    )
    assert recorded.status_code == 200
    parent = client.get(f"/api/tasks/{parent_id}").json()
    assert parent["implementation_changes"] == []
    child = client.get(f"/api/tasks/{child_id}").json()
    assert child["implementation_changes"][0]["project"] == "billing"
