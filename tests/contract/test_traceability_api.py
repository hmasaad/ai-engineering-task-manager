def test_traceability_lists_an_unlinked_task_without_making_it_a_requirement(client):
    task = client.post("/api/tasks", json={"title": "Add export"}).json()
    task_id = task["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    with_criterion = client.post(
        f"/api/tasks/{task_id}/criteria",
        json={"text": "The export contains the goal"},
    ).json()
    criterion_id = with_criterion["criteria"][0]["id"]

    listed = client.get("/api/traceability")
    assert listed.status_code == 200
    assert listed.json()["tasks_without_requirement"] == [
        {"id": task_id, "title": "Add export", "status": "Draft"}
    ]
    assert listed.json()["criteria_without_verification"] == [
        {
            "id": criterion_id,
            "task_id": task_id,
            "task_title": "Add export",
            "text": "The export contains the goal",
        }
    ]
    requirements = client.get("/api/requirements")
    assert requirements.status_code == 200
    assert requirements.json() == []

    requirement = client.post(
        "/api/requirements",
        json={"statement": "The export contains the goal", "kind": "functional"},
    ).json()
    client.post(f"/api/requirements/{requirement['id']}/tasks", json={"task_id": task_id})
    after_link = client.get("/api/traceability").json()
    assert after_link["tasks_without_requirement"] == []
    assert after_link["criteria_without_verification"][0]["id"] == criterion_id

    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    client.post(
        f"/api/tasks/{task_id}/criteria/{criterion_id}/verify",
        json={
            "observation": "The export contains the goal",
            "pass_result": "pass",
            "method": "inspection",
            "run_identifier": "local-1",
        },
    )
    assert client.get("/api/traceability").json()["criteria_without_verification"] == []
