def _task(client) -> tuple[int, int]:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    criterion_id = client.post(
        f"/api/tasks/{task_id}/criteria",
        json={"text": "The export contains the goal"},
    ).json()["criteria"][0]["id"]
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id, criterion_id


def test_record_and_link_a_requirement(client):
    task_id, criterion_id = _task(client)
    recorded = client.post(
        "/api/requirements",
        json={
            "statement": "The export contains the goal",
            "kind": "functional",
            "engineer_name": "Someone",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    assert body["identifier"] == "REQ-1"
    requirement_id = body["id"]
    linked = client.post(f"/api/requirements/{requirement_id}/tasks", json={"task_id": task_id})
    assert linked.status_code == 200
    criterion = client.post(
        f"/api/requirements/{requirement_id}/criteria",
        json={"task_id": task_id, "criterion_id": criterion_id},
    )
    assert criterion.status_code == 200
    assert criterion.json()["criteria"][0]["id"] == criterion_id
    task = client.get(f"/api/tasks/{task_id}")
    assert task.json()["requirements"][0]["identifier"] == "REQ-1"
    again = client.post(f"/api/requirements/{requirement_id}/tasks", json={"task_id": task_id})
    assert again.status_code == 200
    assert len(again.json()["tasks"]) == 1


def test_requirement_refusals(client):
    task_id, criterion_id = _task(client)
    blank = client.post("/api/requirements", json={"statement": "  ", "kind": "functional"})
    assert blank.status_code == 400
    assert blank.json()["message"] == "A requirement statement is required."
    kind = client.post("/api/requirements", json={"statement": "The export contains the goal", "kind": "maybe"})
    assert kind.status_code == 400
    assert kind.json()["message"] == "Choose functional or non-functional."
    shape = client.post("/api/requirements", json={"kind": "functional"})
    assert shape.status_code == 400
    assert shape.json()["message"] == "The request is missing a required field or has the wrong shape."
    missing = client.post("/api/requirements/999/tasks", json={"task_id": task_id})
    assert missing.status_code == 404
    assert missing.json()["message"] == "Requirement not found."
    recorded = client.post(
        "/api/requirements",
        json={"statement": "The export contains the goal", "kind": "functional"},
    ).json()
    other = client.post("/api/tasks", json={"title": "Other"}).json()["id"]
    client.patch(f"/api/tasks/{other}", json={"goal": "Take the record"})
    other_criterion = client.post(
        f"/api/tasks/{other}/criteria",
        json={"text": "Somewhere else"},
    ).json()["criteria"][0]["id"]
    client.post(f"/api/requirements/{recorded['id']}/tasks", json={"task_id": task_id})
    wrong = client.post(
        f"/api/requirements/{recorded['id']}/criteria",
        json={"task_id": task_id, "criterion_id": other_criterion},
    )
    assert wrong.status_code == 409
    assert wrong.json()["message"] == "The criterion must be on that task."
    client.post(
        f"/api/requirements/{recorded['id']}/criteria",
        json={"task_id": task_id, "criterion_id": criterion_id},
    )
    duplicate = client.post(
        f"/api/requirements/{recorded['id']}/criteria",
        json={"task_id": task_id, "criterion_id": criterion_id},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["message"] == "That criterion is already linked to this requirement."
