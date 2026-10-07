def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_later_check_leaves_the_named_check_on_the_decision(client):
    task_id = _in_progress(client)
    change = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": "Rename the export label", "class": "ordinary"},
    )
    change_id = change.json()["implementation_changes"][0]["id"]
    criterion_id = client.get(f"/api/tasks/{task_id}").json()["criteria"][0]["id"]
    checks = f"/api/tasks/{task_id}/implementation-changes/{change_id}/checks"
    failed = client.post(
        checks,
        json={"criterion_id": criterion_id, "evidence": "The label was still old", "result": "Failed"},
    )
    check_id = failed.json()["implementation_changes"][0]["checks"][0]["id"]
    client.post(
        f"/api/tasks/{task_id}/linked-decisions",
        json={
            "statement": "Wait for the label",
            "rationale": "The first check failed",
            "check_id": check_id,
        },
    )
    later = client.post(
        checks,
        json={
            "criterion_id": criterion_id,
            "evidence": "The label now reads Export",
            "result": "Passed",
        },
    )
    assert later.status_code == 200
    body = client.get(f"/api/tasks/{task_id}").json()
    decision = body["decisions"][0]
    assert decision["check"]["id"] == check_id
    assert decision["check"]["evidence"] == "The label was still old"
    assert decision["check"]["result"] == "Failed"
    assert [item["result"] for item in body["implementation_changes"][0]["checks"]] == [
        "Failed",
        "Passed",
    ]

    edited = client.patch(f"/api/tasks/{task_id}/decisions/{decision['id']}", json={"statement": "Changed"})
    removed = client.delete(f"/api/tasks/{task_id}/decisions/{decision['id']}")
    assert edited.status_code in {404, 405}
    assert removed.status_code in {404, 405}
    again = client.get(f"/api/tasks/{task_id}").json()["decisions"][0]
    assert again["statement"] == "Wait for the label"
    assert again["check"]["evidence"] == "The label was still old"
