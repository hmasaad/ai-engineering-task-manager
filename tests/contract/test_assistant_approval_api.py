def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_assistant_actor_cannot_approve_or_decline(client):
    task_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={
            "project": "billing",
            "class": "consequential",
            "what_changed": "Replace the stored export name",
        },
    )
    change_id = recorded.json()["implementation_changes"][0]["id"]
    approve = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/approve",
        json={"evidence": "The page shows the new name", "actor": "assistant"},
    )
    assert approve.status_code == 409
    assert approve.json()["message"] == "The assistant cannot approve a change."
    decline = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/not-carried-out",
        json={"reason": "Not this one", "actor": "assistant"},
    )
    assert decline.status_code == 409
    assert decline.json()["message"] == "The assistant cannot decline a change."
    detail = client.get(f"/api/tasks/{task_id}").json()
    assert detail["implementation_changes"][0]["outcome"] == "Awaiting approval"


def test_engineer_approves_a_stopped_assistant_change(client):
    task_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Rename the export label",
            "stopped": True,
        },
    )
    change = recorded.json()["implementation_changes"][0]
    assert change["outcome"] == "Awaiting approval"
    assert change["stopped"] is True
    assert change["class"] == "consequential"
    approved = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change['id']}/approve",
        json={"evidence": "The page shows the new name"},
    )
    assert approved.status_code == 200
    carried = approved.json()["implementation_changes"][0]
    assert carried["outcome"] == "Carried out"
    assert carried["approval"]["engineer_name"] == "Ada"
    assert approved.json()["status"] == "In Progress"
