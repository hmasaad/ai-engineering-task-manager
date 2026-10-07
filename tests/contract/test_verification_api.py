def _in_progress(client, title="Add export") -> int:
    task_id = client.post("/api/tasks", json={"title": title}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def _change(client, task_id: int, change_class="ordinary", what="Rename the export label") -> int:
    recorded = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": what, "class": change_class},
    )
    return recorded.json()["implementation_changes"][-1]["id"]


def test_record_check_and_ignore_engineer_name(client):
    task_id = _in_progress(client)
    change_id = _change(client, task_id)
    criterion_id = client.get(f"/api/tasks/{task_id}").json()["criteria"][0]["id"]
    path = f"/api/tasks/{task_id}/implementation-changes/{change_id}/checks"

    blank = client.post(path, json={"criterion_id": criterion_id, "evidence": "   ", "result": "Passed"})
    assert blank.status_code == 400
    assert blank.json() == {"refused": True, "message": "An account of the evidence is required."}

    missing_result = client.post(path, json={"criterion_id": criterion_id, "evidence": "Seen"})
    assert missing_result.status_code == 400
    assert missing_result.json()["message"] == "Choose Passed or Failed."

    missing_criterion = client.post(path, json={"evidence": "Seen", "result": "Passed"})
    assert missing_criterion.status_code == 400
    assert missing_criterion.json()["message"] == "Choose an acceptance criterion."

    wrong_shape = client.post(path, json={"criterion_id": "nope", "evidence": "Seen", "result": "Passed"})
    assert wrong_shape.status_code == 400
    assert wrong_shape.json()["message"] == "The request is missing a required field or has the wrong shape."

    recorded = client.post(
        path,
        json={
            "criterion_id": criterion_id,
            "evidence": "The detail page shows the goal in the export",
            "result": "Passed",
            "engineer_name": "Someone Else",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    assert body["status"] == "In Progress"
    change = body["implementation_changes"][0]
    assert change["outcome"] == "Carried out"
    check = change["checks"][0]
    assert check["criterion_text"] == "The file contains the goal"
    assert check["evidence"] == "The detail page shows the goal in the export"
    assert check["result"] == "Passed"
    assert check["engineer_name"] == "Ada"
    detail = client.get(f"/api/tasks/{task_id}")
    assert detail.json()["implementation_changes"][0]["checks"][0]["id"] == check["id"]


def test_record_check_refuses_the_wrong_status_and_links(client):
    draft_id = client.post("/api/tasks", json={"title": "Draft"}).json()["id"]
    draft = client.post(
        f"/api/tasks/{draft_id}/implementation-changes/1/checks",
        json={"criterion_id": 1, "evidence": "   ", "result": None},
    )
    assert draft.status_code == 409
    assert draft.json()["message"] == "The task must be In Progress."

    task_id = _in_progress(client)
    other_id = _in_progress(client, "Other")
    change_id = _change(client, task_id)
    other_change = _change(client, other_id, what="Write the export steps")
    criterion_id = client.get(f"/api/tasks/{task_id}").json()["criteria"][0]["id"]
    other_criterion = client.get(f"/api/tasks/{other_id}").json()["criteria"][0]["id"]

    wrong_change = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{other_change}/checks",
        json={"criterion_id": criterion_id, "evidence": "Seen", "result": "Passed"},
    )
    assert wrong_change.status_code == 409
    assert wrong_change.json()["message"] == "The check must name a change on that task."

    wrong_criterion = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/checks",
        json={"criterion_id": other_criterion, "evidence": "Seen", "result": "Passed"},
    )
    assert wrong_criterion.status_code == 409
    assert wrong_criterion.json()["message"] == "The check must name a criterion on that task."

    missing_change = client.post(
        f"/api/tasks/{task_id}/implementation-changes/99999/checks",
        json={"criterion_id": criterion_id, "evidence": "Seen", "result": "Passed"},
    )
    assert missing_change.status_code == 404
    assert missing_change.json()["message"] == "Implementation change not found."

    waiting = _change(client, task_id, "consequential", "Replace the stored export name")
    awaiting = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{waiting}/checks",
        json={"criterion_id": criterion_id, "evidence": "Seen", "result": "Passed"},
    )
    assert awaiting.status_code == 409
    assert awaiting.json()["message"] == "The change must be carried out before it can be checked."
    assert client.get(f"/api/tasks/{task_id}").json()["status"] == "In Progress"
