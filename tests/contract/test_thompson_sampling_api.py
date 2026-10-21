def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_thompson_draw(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Name arm" in shown.text
    assert 'id="thompson-arm-name"' in shown.text
    assert "Name context" in shown.text
    assert 'id="thompson-context-name"' in shown.text
    assert "Record pull" not in shown.text
    assert "Draw arm" not in shown.text
    assert "No arms yet." in shown.text

    ada = client.post(f"/api/tasks/{task_id}/thompson-arms", json={"name": "ada"})
    assert ada.status_code == 200
    grace = client.post(f"/api/tasks/{task_id}/thompson-arms", json={"name": "grace"})
    assert grace.status_code == 200
    assert grace.json()["status"] == "In Progress"
    assert grace.json()["exploration"]["can_pull"] is False
    rush = client.post(f"/api/tasks/{task_id}/thompson-contexts", json={"name": "rush"})
    assert rush.status_code == 200
    assert rush.json()["exploration"]["can_pull"] is True
    assert rush.json()["exploration"]["can_draw"] is True

    one = client.post(
        f"/api/tasks/{task_id}/thompson-pulls",
        json={"name": "one", "context": "rush", "arm": "ada", "reward": "2"},
    )
    assert one.status_code == 200
    two = client.post(
        f"/api/tasks/{task_id}/thompson-pulls",
        json={"name": "two", "context": "rush", "arm": "ada", "reward": "1"},
    )
    assert two.status_code == 200

    middle = client.post(f"/api/tasks/{task_id}/thompson-draws", json={"context": "rush"})
    assert middle.status_code == 200
    assert middle.json()["exploration"]["draw"] == {
        "context": "rush",
        "arm": "ada",
        "sample": "middle",
    }
    high = client.post(f"/api/tasks/{task_id}/thompson-draws", json={"context": "rush"})
    assert high.json()["exploration"]["draw"] == {
        "context": "rush",
        "arm": "grace",
        "sample": "high",
    }

    page = client.get(f"/tasks/{task_id}")
    assert "ada" in page.text
    assert "grace" in page.text
    assert "rush" in page.text
    assert "one: rush, ada, reward 2" in page.text
    assert "two: rush, ada, reward 1" in page.text
    assert "Draw in rush: grace, high sample" in page.text
    assert 'id="pull-name"' in page.text
    assert 'id="draw-context"' in page.text
    assert "Draw arm" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/thompson-contexts",
        data={"name": "quiet"},
        follow_redirects=True,
    )
    assert "quiet" in submitted.text
    assert "Draw in rush" not in submitted.text
    assert "In Progress" in submitted.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
