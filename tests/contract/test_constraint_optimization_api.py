def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_optimized_schedule(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Name activity" in shown.text
    assert 'id="opt-activity-name"' in shown.text
    assert 'id="activity-length"' in shown.text
    assert "Add constraint" not in shown.text
    assert "Set capacity" not in shown.text
    assert "Optimize schedule" not in shown.text
    assert "No activities yet." in shown.text

    design = client.post(
        f"/api/tasks/{task_id}/opt-activities",
        json={"name": "design", "length": "1"},
    )
    assert design.status_code == 200
    build = client.post(
        f"/api/tasks/{task_id}/opt-activities",
        json={"name": "build", "length": "2"},
    )
    assert build.status_code == 200
    test = client.post(
        f"/api/tasks/{task_id}/opt-activities",
        json={"name": "test", "length": "1"},
    )
    assert test.status_code == 200
    assert test.json()["status"] == "In Progress"
    assert test.json()["optimization"]["can_constrain"] is True
    assert test.json()["optimization"]["can_bound"] is True
    assert test.json()["optimization"]["can_optimize"] is False

    linked = client.post(
        f"/api/tasks/{task_id}/opt-constraints",
        json={"activity": "test", "after": "build"},
    )
    assert linked.status_code == 200
    assert linked.json()["optimization"]["constraints"] == [
        {"activity": "test", "after": "build"}
    ]

    bounded = client.post(
        f"/api/tasks/{task_id}/opt-capacities",
        json={"capacity": "2"},
    )
    assert bounded.status_code == 200
    assert bounded.json()["optimization"]["can_optimize"] is True

    scheduled = client.post(f"/api/tasks/{task_id}/opt-plans")
    assert scheduled.status_code == 200
    assert scheduled.json()["optimization"]["finish"] == 3
    assert scheduled.json()["optimization"]["activities"] == [
        {"name": "design", "length": 1, "start": 0},
        {"name": "build", "length": 2, "start": 0},
        {"name": "test", "length": 1, "start": 2},
    ]

    page = client.get(f"/tasks/{task_id}")
    assert "design: length 1, starts 0" in page.text
    assert "build: length 2, starts 0" in page.text
    assert "test: length 1, starts 2" in page.text
    assert "test after build" in page.text
    assert "Capacity: 2" in page.text
    assert "Finish day: 3" in page.text
    assert 'id="opt-capacity"' in page.text
    assert "Optimize schedule" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/opt-capacities",
        data={"capacity": "1"},
        follow_redirects=True,
    )
    assert "Capacity: 1" in submitted.text
    assert "Finish day:" not in submitted.text
    assert "In Progress" in submitted.text

    packed = client.post(f"/api/tasks/{task_id}/opt-plans")
    assert packed.json()["optimization"]["finish"] == 4
    shown_again = client.get(f"/tasks/{task_id}")
    assert "Finish day: 4" in shown_again.text
    assert "test: length 1, starts 3" in shown_again.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
