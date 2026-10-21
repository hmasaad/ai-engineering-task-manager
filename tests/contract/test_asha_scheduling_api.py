def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_assignment(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Name trial" in shown.text
    assert "Name runner" in shown.text
    assert 'id="hyperband-trial-name"' in shown.text
    assert 'id="hyperband-runner-name"' in shown.text
    assert "Record rung" not in shown.text
    assert "Schedule the next trial" not in shown.text
    assert "No trials yet." in shown.text

    red = client.post(f"/api/tasks/{task_id}/hyperband-trials", json={"name": "red"})
    assert red.status_code == 200
    assert red.json()["status"] == "In Progress"
    assert red.json()["hyperband"]["can_record"] is True
    assert red.json()["hyperband"]["can_schedule"] is False
    blue = client.post(f"/api/tasks/{task_id}/hyperband-trials", json={"name": "blue"})
    assert blue.status_code == 200
    ada = client.post(f"/api/tasks/{task_id}/hyperband-runners", json={"name": "ada"})
    assert ada.status_code == 200

    one = client.post(
        f"/api/tasks/{task_id}/hyperband-rungs",
        json={"name": "one", "trial": "red", "rung": "1", "score": "1"},
    )
    assert one.status_code == 200
    assert one.json()["hyperband"]["can_schedule"] is False
    two = client.post(
        f"/api/tasks/{task_id}/hyperband-rungs",
        json={"name": "two", "trial": "blue", "rung": "1", "score": "2"},
    )
    assert two.status_code == 200
    assert two.json()["hyperband"]["can_schedule"] is True

    scheduled = client.post(f"/api/tasks/{task_id}/hyperband-schedules")
    assert scheduled.status_code == 200
    assert scheduled.json()["hyperband"]["promoted"] == [{"name": "blue"}]
    assert scheduled.json()["hyperband"]["assignments"] == [
        {"trial": "blue", "runner": "ada"}
    ]
    assert scheduled.json()["hyperband"]["winner"] is None

    page = client.get(f"/tasks/{task_id}")
    assert "one: red, rung 1, score 1" in page.text
    assert "blue: ada" in page.text
    assert 'id="hyperband-rung-name"' in page.text
    assert 'id="hyperband-rung-score"' in page.text
    assert "Schedule the next trial" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/hyperband-trials",
        data={"name": "gold"},
        follow_redirects=True,
    )
    assert "gold" in submitted.text
    assert "blue: ada" not in submitted.text
    assert "In Progress" in submitted.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
