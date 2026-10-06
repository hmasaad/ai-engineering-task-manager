def test_add_subtask_and_block_parent_completion(client):
    parent_id = client.post("/api/tasks", json={"title": "Parent"}).json()["id"]
    client.patch("/api/tasks/{0}".format(parent_id), json={"goal": "Parent goal"})
    parent = client.post(
        f"/api/tasks/{parent_id}/criteria",
        json={"text": "Parent criterion"},
    ).json()
    client.post(f"/api/tasks/{parent_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{parent_id}/transitions", json={"action": "start"})
    criterion_id = parent["criteria"][0]["id"]
    client.post(
        f"/api/tasks/{parent_id}/criteria/{criterion_id}/verify",
        json={"observation": "Seen", "pass_result": "pass"},
    )

    created = client.post("/api/tasks/{0}/subtasks".format(parent_id), json={"title": "Child"})
    assert created.status_code == 200
    assert created.json()["status"] == "Draft"
    assert created.json()["parent_id"] == parent_id

    refused = client.post(f"/api/tasks/{parent_id}/transitions", json={"action": "complete"})
    assert refused.status_code == 409
    assert "Child" in refused.json()["message"]

    cancel = client.post(
        f"/api/tasks/{parent_id}/transitions",
        json={"action": "cancel", "reason": "Stop"},
    )
    assert cancel.status_code == 409
    assert "Child" in cancel.json()["message"]
