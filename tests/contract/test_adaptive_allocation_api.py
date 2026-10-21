def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_shares(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Name agent" in shown.text
    assert 'id="allocation-agent-name"' in shown.text
    assert "Record yield" not in shown.text
    assert "Allocate the pool" not in shown.text
    assert "No agents yet." in shown.text

    ada = client.post(f"/api/tasks/{task_id}/allocation-agents", json={"name": "ada"})
    assert ada.status_code == 200
    assert ada.json()["status"] == "In Progress"
    assert ada.json()["allocation"]["can_record"] is True
    assert ada.json()["allocation"]["can_allocate"] is False
    grace = client.post(f"/api/tasks/{task_id}/allocation-agents", json={"name": "grace"})
    assert grace.status_code == 200

    one = client.post(
        f"/api/tasks/{task_id}/allocation-yields",
        json={"name": "one", "agent": "ada", "value": "2"},
    )
    assert one.status_code == 200
    assert one.json()["allocation"]["can_allocate"] is True
    two = client.post(
        f"/api/tasks/{task_id}/allocation-yields",
        json={"name": "two", "agent": "grace", "value": "1"},
    )
    assert two.status_code == 200

    allocated = client.post(f"/api/tasks/{task_id}/allocation-shares")
    assert allocated.status_code == 200
    assert allocated.json()["allocation"]["shares"] == [
        {"agent": "ada", "units": 3},
        {"agent": "grace", "units": 1},
    ]

    page = client.get(f"/tasks/{task_id}")
    assert "one: ada, yield 2" in page.text
    assert "ada: 3" in page.text
    assert "grace: 1" in page.text
    assert 'id="allocation-yield-name"' in page.text
    assert 'id="allocation-yield-value"' in page.text
    assert "Allocate the pool" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/allocation-agents",
        data={"name": "mina"},
        follow_redirects=True,
    )
    assert "mina" in submitted.text
    assert "ada: 3" not in submitted.text
    assert "In Progress" in submitted.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
