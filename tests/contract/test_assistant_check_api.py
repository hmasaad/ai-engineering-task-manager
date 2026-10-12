def _in_progress(client, title="Add export") -> int:
    task_id = client.post("/api/tasks", json={"title": title}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def _change(client, task_id: int, change_class="ordinary", what="Rename the export label") -> int:
    recorded = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": what, "class": change_class},
    )
    return recorded.json()["implementation_changes"][-1]["id"]


def test_assistant_check_ignores_client_names_and_time(client):
    task_id = _in_progress(client)
    change_id = _change(client, task_id)
    criterion_id = client.get(f"/api/tasks/{task_id}").json()["criteria"][0]["id"]
    recorded = client.post(
        f"/api/tasks/{task_id}/assistant-checks",
        json={
            "change_id": change_id,
            "criterion_id": criterion_id,
            "evidence": "The detail page shows the goal in the export",
            "result": "Passed",
            "assistant_name": "Someone",
            "engineer_name": "Someone Else",
            "checked_at": "1999-01-01T00:00:00Z",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    assert body["status"] == "In Progress"
    change = body["implementation_changes"][0]
    assert change["outcome"] == "Carried out"
    check = change["checks"][0]
    assert check["assistant_name"] == "Assistant"
    assert check["engineer_name"] == "Ada"
    assert check["checked_at"] != "1999-01-01T00:00:00Z"
    assert check["result"] == "Passed"
    assert body["criteria"][0]["state"] == "Unverified"


def test_engineer_check_still_has_no_assistant(client):
    task_id = _in_progress(client)
    change_id = _change(client, task_id)
    criterion_id = client.get(f"/api/tasks/{task_id}").json()["criteria"][0]["id"]
    recorded = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/checks",
        json={
            "criterion_id": criterion_id,
            "evidence": "Seen",
            "result": "Passed",
            "assistant_name": "Guide",
        },
    )
    assert recorded.status_code == 200
    check = recorded.json()["implementation_changes"][0]["checks"][0]
    assert check["assistant_name"] is None
    assert check["engineer_name"] == "Ada"


def test_assistant_check_refusal_order(client):
    missing_task = client.post(
        "/api/tasks/99999/assistant-checks",
        json={"change_id": 1, "criterion_id": 1, "evidence": "Seen", "result": "Passed"},
    )
    assert missing_task.status_code == 404
    assert missing_task.json()["message"] == "Task not found."

    draft_id = client.post("/api/tasks", json={"title": "Draft"}).json()["id"]
    draft = client.post(
        f"/api/tasks/{draft_id}/assistant-checks",
        json={"change_id": 1, "evidence": "   ", "result": None},
    )
    assert draft.status_code == 409
    assert draft.json()["message"] == "The task must be In Progress."

    wrong_shape = client.post(
        f"/api/tasks/{draft_id}/assistant-checks",
        json={"change_id": "nope", "evidence": "Seen", "result": "Passed"},
    )
    assert wrong_shape.status_code == 400
    assert wrong_shape.json()["message"] == "The request is missing a required field or has the wrong shape."

    task_id = _in_progress(client)
    other_id = _in_progress(client, "Other")
    change_id = _change(client, task_id)
    other_change = _change(client, other_id, what="Write the export steps")
    criterion_id = client.get(f"/api/tasks/{task_id}").json()["criteria"][0]["id"]
    other_criterion = client.get(f"/api/tasks/{other_id}").json()["criteria"][0]["id"]

    missing_change = client.post(
        f"/api/tasks/{task_id}/assistant-checks",
        json={"change_id": 99999, "criterion_id": criterion_id, "evidence": "Seen", "result": "Passed"},
    )
    assert missing_change.status_code == 404
    assert missing_change.json()["message"] == "Implementation change not found."

    wrong_change = client.post(
        f"/api/tasks/{task_id}/assistant-checks",
        json={
            "change_id": other_change,
            "criterion_id": criterion_id,
            "evidence": "Seen",
            "result": "Passed",
        },
    )
    assert wrong_change.status_code == 409
    assert wrong_change.json()["message"] == "The check must name a change on that task."

    waiting = _change(client, task_id, "consequential", "Replace the stored export name")
    awaiting = client.post(
        f"/api/tasks/{task_id}/assistant-checks",
        json={"change_id": waiting, "criterion_id": criterion_id, "evidence": "Seen", "result": "Passed"},
    )
    assert awaiting.status_code == 409
    assert awaiting.json()["message"] == "The change must be carried out before it can be checked."

    client.post(
        f"/api/tasks/{task_id}/implementation-changes/{waiting}/not-carried-out",
        json={"reason": "Leave the name"},
    )
    declined = client.post(
        f"/api/tasks/{task_id}/assistant-checks",
        json={"change_id": waiting, "criterion_id": criterion_id, "evidence": "Seen", "result": "Passed"},
    )
    assert declined.status_code == 409
    assert declined.json()["message"] == "A change that was not carried out cannot be checked."

    missing_criterion = client.post(
        f"/api/tasks/{task_id}/assistant-checks",
        json={"change_id": change_id, "evidence": "Seen", "result": "Passed"},
    )
    assert missing_criterion.status_code == 400
    assert missing_criterion.json()["message"] == "Choose an acceptance criterion."

    unknown_criterion = client.post(
        f"/api/tasks/{task_id}/assistant-checks",
        json={"change_id": change_id, "criterion_id": 99999, "evidence": "Seen", "result": "Passed"},
    )
    assert unknown_criterion.status_code == 404
    assert unknown_criterion.json()["message"] == "Acceptance criterion not found."

    wrong_criterion = client.post(
        f"/api/tasks/{task_id}/assistant-checks",
        json={
            "change_id": change_id,
            "criterion_id": other_criterion,
            "evidence": "Seen",
            "result": "Passed",
        },
    )
    assert wrong_criterion.status_code == 409
    assert wrong_criterion.json()["message"] == "The check must name a criterion on that task."

    blank = client.post(
        f"/api/tasks/{task_id}/assistant-checks",
        json={"change_id": change_id, "criterion_id": criterion_id, "evidence": "   ", "result": "Maybe"},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "An account of the evidence is required."

    bad_result = client.post(
        f"/api/tasks/{task_id}/assistant-checks",
        json={"change_id": change_id, "criterion_id": criterion_id, "evidence": "Seen", "result": "Maybe"},
    )
    assert bad_result.status_code == 400
    assert bad_result.json()["message"] == "Choose Passed or Failed."
    assert client.get(f"/api/tasks/{task_id}").json()["implementation_changes"][0]["checks"] == []
