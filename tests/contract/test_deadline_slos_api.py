def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_serves_the_earliest_deadline(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Set objective" in shown.text
    assert 'id="objective-name"' in shown.text
    assert 'id="objective-deadline"' in shown.text
    assert "Serve objective" not in shown.text
    assert "No objectives yet." in shown.text

    export = client.post(
        f"/api/tasks/{task_id}/objectives",
        json={"name": "export", "deadline": "2026-12-01T00:00:00Z"},
    )
    assert export.status_code == 200
    rush = client.post(
        f"/api/tasks/{task_id}/objectives",
        json={"name": "rush", "deadline": "2026-10-01T00:00:00Z"},
    )
    assert rush.status_code == 200
    assert rush.json()["status"] == "In Progress"
    assert rush.json()["slo"]["can_serve"] is True

    first = client.post(f"/api/tasks/{task_id}/objective-services", json={"name": "one"})
    assert first.status_code == 200
    assert first.json()["slo"]["services"] == [
        {"name": "one", "objective": "rush", "result": "missed"}
    ]
    assert first.json()["slo"]["waiting"] == [
        {"name": "export", "deadline": "2026-12-01T00:00:00Z"}
    ]

    page = client.get(f"/tasks/{task_id}")
    assert 'id="objectives"' in page.text
    assert "export: due 2026-12-01T00:00:00Z" in page.text
    assert "one missed rush" in page.text
    assert "Serve objective" in page.text
    assert 'id="service-name"' in page.text

    followed = client.post(
        f"/tasks/{task_id}/objective-services",
        data={"name": "two"},
        follow_redirects=True,
    )
    assert "two met export" in followed.text
    assert isinstance(client.get("/api/tasks").json(), list)
