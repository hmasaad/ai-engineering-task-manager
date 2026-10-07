def _in_progress(client, title="Add export") -> int:
    task_id = client.post("/api/tasks", json={"title": title}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def _check(client, task_id: int) -> int:
    change = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": "Rename the export label", "class": "ordinary"},
    )
    change_id = change.json()["implementation_changes"][-1]["id"]
    criterion_id = client.get(f"/api/tasks/{task_id}").json()["criteria"][0]["id"]
    recorded = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/checks",
        json={
            "criterion_id": criterion_id,
            "evidence": "The detail page shows the goal in the export",
            "result": "Passed",
        },
    )
    return recorded.json()["implementation_changes"][0]["checks"][-1]["id"]


def test_supersede_and_the_existing_decision_command(client):
    task_id = _in_progress(client)
    other_id = _in_progress(client, "Other")
    check_id = _check(client, task_id)
    earlier = client.post(
        f"/api/tasks/{task_id}/decisions",
        json={"statement": "Use one file", "rationale": "Because", "check_id": check_id},
    )
    assert earlier.status_code == 200
    assert earlier.json()["decisions"][0]["check"] is None
    earlier_id = earlier.json()["decisions"][0]["id"]

    linked = client.post(
        f"/api/tasks/{task_id}/linked-decisions",
        json={
            "statement": "Keep the export label",
            "rationale": "The check shows the goal is visible",
            "check_id": check_id,
            "supersedes": [earlier_id],
        },
    )
    assert linked.status_code == 200
    decisions = linked.json()["decisions"]
    assert decisions[0]["check"] is None
    assert decisions[1]["check"]["id"] == check_id
    assert decisions[1]["supersedes"] == [earlier_id]

    their_decision = client.post(
        f"/api/tasks/{other_id}/decisions",
        json={"statement": "Theirs", "rationale": "Different task"},
    ).json()["decisions"][0]["id"]
    cross = client.post(
        f"/api/tasks/{task_id}/linked-decisions",
        json={
            "statement": "Keep it",
            "rationale": "Because",
            "check_id": check_id,
            "supersedes": [their_decision],
        },
    )
    assert cross.status_code == 409
    assert cross.json()["message"] == "A decision can only supersede earlier decisions on the same task."

    unknown = client.post(
        f"/api/tasks/{task_id}/linked-decisions",
        json={
            "statement": "Keep it",
            "rationale": "Because",
            "check_id": check_id,
            "supersedes": [99999],
        },
    )
    assert unknown.status_code == 404
    assert unknown.json()["message"] == "Decision not found."


def test_completion_does_not_wait_for_a_decision(client):
    task_id = _in_progress(client)
    _check(client, task_id)
    criterion_id = client.get(f"/api/tasks/{task_id}").json()["criteria"][0]["id"]
    client.post(
        f"/api/tasks/{task_id}/criteria/{criterion_id}/verify",
        json={"observation": "The goal is on the page.", "pass_result": "pass"},
    )
    completed = client.post(f"/api/tasks/{task_id}/transitions", json={"action": "complete"})
    assert completed.status_code == 200
    assert completed.json()["status"] == "Completed"
    assert completed.json()["decisions"] == []
