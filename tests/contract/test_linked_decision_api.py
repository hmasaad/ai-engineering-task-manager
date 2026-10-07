def _in_progress(client, title="Add export") -> int:
    task_id = client.post("/api/tasks", json={"title": title}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def _check(client, task_id: int, result="Passed", evidence="The detail page shows the goal in the export") -> int:
    change = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": "Rename the export label", "class": "ordinary"},
    )
    change_id = change.json()["implementation_changes"][-1]["id"]
    criterion_id = client.get(f"/api/tasks/{task_id}").json()["criteria"][0]["id"]
    recorded = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/checks",
        json={"criterion_id": criterion_id, "evidence": evidence, "result": result},
    )
    return recorded.json()["implementation_changes"][0]["checks"][-1]["id"]


def test_record_linked_decision_and_ignore_engineer_name(client):
    task_id = _in_progress(client)
    check_id = _check(client, task_id)
    path = f"/api/tasks/{task_id}/linked-decisions"

    blank = client.post(
        path,
        json={"statement": "   ", "rationale": "Because", "check_id": check_id},
    )
    assert blank.status_code == 400
    assert blank.json() == {
        "refused": True,
        "message": "Both a statement and a rationale are required.",
    }

    missing_check = client.post(path, json={"statement": "Keep it", "rationale": "Because"})
    assert missing_check.status_code == 400
    assert missing_check.json()["message"] == "Choose the check this decision rests on."

    wrong_shape = client.post(path, json={"check_id": "nope"})
    assert wrong_shape.status_code == 400
    assert wrong_shape.json()["message"] == "The request is missing a required field or has the wrong shape."

    recorded = client.post(
        path,
        json={
            "statement": "Keep the export label",
            "rationale": "The check shows the goal is visible",
            "check_id": check_id,
            "engineer_name": "Someone Else",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    assert body["status"] == "In Progress"
    assert body["implementation_changes"][0]["outcome"] == "Carried out"
    assert body["implementation_changes"][0]["checks"][0]["result"] == "Passed"
    decision = body["decisions"][-1]
    assert decision["statement"] == "Keep the export label"
    assert decision["check"]["id"] == check_id
    assert decision["check"]["criterion_text"] == "The export contains the goal"
    assert decision["check"]["what_changed"] == "Rename the export label"
    assert decision["check"]["evidence"] == "The detail page shows the goal in the export"
    assert decision["check"]["result"] == "Passed"
    assert decision["check"]["engineer_name"] == "Ada"
    detail = client.get(f"/api/tasks/{task_id}")
    assert detail.json()["decisions"][-1]["check"]["id"] == check_id


def test_linked_decision_refuses_unknown_and_wrong_task(client):
    missing = client.post(
        "/api/tasks/99999/linked-decisions",
        json={"statement": "Keep it", "rationale": "Because", "check_id": 1},
    )
    assert missing.status_code == 404
    assert missing.json()["message"] == "Task not found."

    task_id = _in_progress(client)
    other_id = _in_progress(client, "Other")
    check_id = _check(client, task_id)
    other_check = _check(client, other_id, evidence="The other page shows the goal")

    unknown = client.post(
        f"/api/tasks/{task_id}/linked-decisions",
        json={"statement": "Keep it", "rationale": "Because", "check_id": 99999},
    )
    assert unknown.status_code == 404
    assert unknown.json()["message"] == "Check not found."

    wrong_task = client.post(
        f"/api/tasks/{task_id}/linked-decisions",
        json={"statement": "Keep it", "rationale": "Because", "check_id": other_check},
    )
    assert wrong_task.status_code == 409
    assert wrong_task.json()["message"] == "The decision must name a check on that task."
    assert client.get(f"/api/tasks/{task_id}").json()["decisions"] == []

    client.post(
        f"/api/tasks/{task_id}/transitions",
        json={"action": "cancel", "reason": "Stop this work"},
    )
    cancelled = client.post(
        f"/api/tasks/{task_id}/linked-decisions",
        json={"statement": "Keep it", "rationale": "Because", "check_id": check_id},
    )
    assert cancelled.status_code == 409
    assert cancelled.json()["message"] == "Decisions cannot be added to a cancelled task."
