def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_critical_path_and_latest_times(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Name step" in shown.text
    assert 'id="schedule-step-name"' in shown.text
    assert 'id="step-length"' in shown.text
    assert "Add dependency" not in shown.text
    assert "Set deadline" not in shown.text
    assert "No schedule steps yet." in shown.text

    design = client.post(
        f"/api/tasks/{task_id}/schedule-steps",
        json={"name": "design", "length": "1"},
    )
    assert design.status_code == 200
    build = client.post(
        f"/api/tasks/{task_id}/schedule-steps",
        json={"name": "build", "length": "2"},
    )
    assert build.status_code == 200
    assert build.json()["status"] == "In Progress"
    assert build.json()["paths"]["can_link"] is True
    assert build.json()["paths"]["can_deadline"] is True

    linked = client.post(
        f"/api/tasks/{task_id}/schedule-links",
        json={"step": "build", "follows": "design"},
    )
    assert linked.status_code == 200
    assert linked.json()["paths"]["critical"] == ["design", "build"]
    assert linked.json()["paths"]["steps"][1]["follows"] == "design"

    page = client.get(f"/tasks/{task_id}")
    assert "build: length 2, follows design" in page.text
    assert "Critical path: design, build" in page.text
    assert 'id="link-step"' in page.text
    assert 'id="path-deadline"' in page.text

    scheduled = client.post(
        f"/api/tasks/{task_id}/schedule-deadlines",
        json={"deadline": "2026-12-03T00:00:00Z"},
    )
    assert scheduled.status_code == 200
    assert scheduled.json()["paths"]["steps"] == [
        {
            "name": "design",
            "length": 1,
            "follows": None,
            "latest": "2026-12-01T00:00:00Z",
        },
        {
            "name": "build",
            "length": 2,
            "follows": "design",
            "latest": "2026-12-03T00:00:00Z",
        },
    ]

    submitted = client.post(
        f"/tasks/{task_id}/schedule-deadlines",
        data={"deadline": "2026-12-04T00:00:00Z"},
        follow_redirects=True,
    )
    assert "Deadline: 2026-12-04T00:00:00Z" in submitted.text
    assert "design: length 1, latest 2026-12-02T00:00:00Z" in submitted.text
    assert "build: length 2, follows design, latest 2026-12-04T00:00:00Z" in submitted.text
    assert "In Progress" in submitted.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
