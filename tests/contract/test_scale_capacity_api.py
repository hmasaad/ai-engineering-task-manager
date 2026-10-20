def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_plans_and_scales_the_queue(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Queue work" in shown.text
    assert 'id="queue-name"' in shown.text
    assert "Plan capacity" in shown.text
    assert 'id="plan-name"' in shown.text
    assert "Scale workers" not in shown.text
    assert "Workers needed: 0. Active workers: 0." in shown.text

    for name in ("one", "two", "three", "four"):
        queued = client.post(f"/api/tasks/{task_id}/queue", json={"name": name})
        assert queued.status_code == 200
    planned = client.post(f"/api/tasks/{task_id}/plans", json={"name": "now"})
    assert planned.status_code == 200
    body = planned.json()
    assert body["status"] == "In Progress"
    assert body["work"]["plans"] == [
        {"name": "now", "waiting": 4, "held": 0, "active": 0, "needed": 2}
    ]
    assert body["work"]["can_scale"] is True

    grown = client.post(f"/api/tasks/{task_id}/scales", json={"name": "ada"})
    assert grown.status_code == 200
    assert grown.json()["work"]["workers"] == [{"name": "ada", "jobs": ["one"]}]
    assert grown.json()["work"]["scales"] == [
        {"name": "ada", "direction": "up", "worker": "ada", "job": "one"}
    ]

    page = client.get(f"/tasks/{task_id}")
    assert 'id="work-queue"' in page.text
    assert "two" in page.text
    assert "Workers needed: 2. Active workers: 1." in page.text
    assert "now — waiting 4, held 0, needed 2, active 0" in page.text
    assert "ada scaled up with one" in page.text
    assert "Scale workers" in page.text
    assert 'id="scale-name"' in page.text

    followed = client.post(
        f"/tasks/{task_id}/plans",
        data={"name": "now"},
        follow_redirects=True,
    )
    assert 'id="capacity-plans"' in followed.text
    assert isinstance(client.get("/api/tasks").json(), list)

    spare = _in_progress(client)
    client.post(f"/api/tasks/{spare}/workers", json={"name": "ada"})
    client.post(f"/api/tasks/{spare}/workers", json={"name": "grace"})
    released = client.post(f"/tasks/{spare}/scales", data={"name": "trim"}, follow_redirects=True)
    assert "trim released grace" in released.text
    assert "grace" in released.text
    assert "Scale workers" in released.text
