def _requirement(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    criterion_id = client.post(
        f"/api/tasks/{task_id}/criteria",
        json={"text": "The export contains the goal"},
    ).json()["criteria"][0]["id"]
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    requirement_id = client.post(
        "/api/requirements",
        json={"statement": "The export contains the goal", "kind": "functional"},
    ).json()["id"]
    client.post(f"/api/requirements/{requirement_id}/tasks", json={"task_id": task_id})
    client.post(
        f"/api/requirements/{requirement_id}/criteria",
        json={"task_id": task_id, "criterion_id": criterion_id},
    )
    return requirement_id, task_id, criterion_id


def test_name_a_check_and_record_a_run(client):
    requirement_id, task_id, criterion_id = _requirement(client)
    named = client.post(
        f"/api/requirements/{requirement_id}/checks",
        json={"name": "export shows the goal"},
    )
    assert named.status_code == 200
    check_id = named.json()["checks"][0]["id"]
    duplicate = client.post(
        f"/api/requirements/{requirement_id}/checks",
        json={"name": "export shows the goal"},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["message"] == "That check is already named on this requirement."
    blank = client.post(f"/api/requirements/{requirement_id}/checks", json={"name": "  "})
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name the check this requirement uses."
    recorded = client.post(
        f"/api/requirements/{requirement_id}/runs",
        json={
            "check": "export shows the goal",
            "result": "Passed",
            "run_identifier": "local-1",
            "engineer_name": "Someone",
        },
    )
    assert recorded.status_code == 200
    run = recorded.json()["checks"][0]["runs"][0]
    assert run["engineer_name"] == "Ada"
    assert run["run_identifier"] == "local-1"
    unknown = client.post(
        f"/api/requirements/{requirement_id}/runs",
        json={"check": "missing", "result": "Passed", "run_identifier": "local-2"},
    )
    assert unknown.status_code == 404
    assert unknown.json()["message"] == "Check not found."
    blank_run = client.post(
        f"/api/requirements/{requirement_id}/runs",
        json={"check": "export shows the goal", "result": "Passed", "run_identifier": "  "},
    )
    assert blank_run.status_code == 400
    assert blank_run.json()["message"] == "A run identifier is required."
    bad_result = client.post(
        f"/api/requirements/{requirement_id}/runs",
        json={"check": "export shows the goal", "result": "Maybe", "run_identifier": "local-2"},
    )
    assert bad_result.status_code == 400
    assert bad_result.json()["message"] == "Choose Passed or Failed."
    removed = client.post(f"/api/requirements/{requirement_id}/checks/{check_id}/remove")
    assert removed.status_code == 200
    assert removed.json()["removed_checks"][0]["runs"][0]["run_identifier"] == "local-1"
    held = client.post(
        f"/api/tasks/{task_id}/criteria/{criterion_id}/verify",
        json={"observation": "The page shows the goal", "pass_result": "pass", "method": "inspection", "run_identifier": "local-1"},
    )
    assert held.status_code == 200


def test_a_failed_run_refuses_verification(client):
    requirement_id, task_id, criterion_id = _requirement(client)
    client.post(
        f"/api/requirements/{requirement_id}/checks",
        json={"name": "export shows the goal"},
    )
    client.post(
        f"/api/requirements/{requirement_id}/runs",
        json={"check": "export shows the goal", "result": "Failed", "run_identifier": "local-1"},
    )
    refused = client.post(
        f"/api/tasks/{task_id}/criteria/{criterion_id}/verify",
        json={"observation": "The page shows the goal", "pass_result": "pass", "method": "inspection", "run_identifier": "local-1"},
    )
    assert refused.status_code == 409
    assert refused.json()["message"] == "A required check has not passed."
