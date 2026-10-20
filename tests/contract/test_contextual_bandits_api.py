def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_learned_choice(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Name action" in shown.text
    assert "Name context" in shown.text
    assert 'id="bandit-action-name"' in shown.text
    assert 'id="bandit-context-name"' in shown.text
    assert "Record trial" not in shown.text
    assert "Choose action" not in shown.text
    assert "No actions yet." in shown.text

    ada = client.post(f"/api/tasks/{task_id}/bandit-actions", json={"name": "ada"})
    assert ada.status_code == 200
    grace = client.post(f"/api/tasks/{task_id}/bandit-actions", json={"name": "grace"})
    assert grace.status_code == 200
    rush = client.post(f"/api/tasks/{task_id}/bandit-contexts", json={"name": "rush"})
    assert rush.status_code == 200
    assert rush.json()["status"] == "In Progress"
    assert rush.json()["bandit"]["can_try"] is True
    assert rush.json()["bandit"]["can_choose"] is True

    one = client.post(
        f"/api/tasks/{task_id}/bandit-trials",
        json={"name": "one", "context": "rush", "action": "ada", "reward": "1"},
    )
    assert one.status_code == 200
    two = client.post(
        f"/api/tasks/{task_id}/bandit-trials",
        json={"name": "two", "context": "rush", "action": "grace", "reward": "1"},
    )
    assert two.status_code == 200
    three = client.post(
        f"/api/tasks/{task_id}/bandit-trials",
        json={"name": "three", "context": "rush", "action": "grace", "reward": "2"},
    )
    assert three.status_code == 200
    assert three.json()["bandit"]["values"] == [
        {"context": "rush", "action": "ada", "total": 1, "count": 1},
        {"context": "rush", "action": "grace", "total": 3, "count": 2},
    ]

    chosen = client.post(
        f"/api/tasks/{task_id}/bandit-choices",
        json={"context": "rush"},
    )
    assert chosen.status_code == 200
    assert chosen.json()["bandit"]["choice"] == {"context": "rush", "action": "grace"}

    page = client.get(f"/tasks/{task_id}")
    assert "ada" in page.text
    assert "grace" in page.text
    assert "one: rush, ada, reward 1" in page.text
    assert "two: rush, grace, reward 1" in page.text
    assert "three: rush, grace, reward 2" in page.text
    assert "rush, ada: total 1 from 1" in page.text
    assert "rush, grace: total 3 from 2" in page.text
    assert "Choice for rush: grace" in page.text
    assert 'id="trial-name"' in page.text
    assert 'id="choice-context"' in page.text
    assert "Choose action" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/bandit-trials",
        data={"name": "four", "context": "rush", "action": "ada", "reward": "2"},
        follow_redirects=True,
    )
    assert "four: rush, ada, reward 2" in submitted.text
    assert "Choice for rush:" not in submitted.text
    assert "In Progress" in submitted.text

    again = client.post(f"/api/tasks/{task_id}/bandit-choices", json={"context": "rush"})
    assert again.json()["bandit"]["choice"] == {"context": "rush", "action": "ada"}
    shown_again = client.get(f"/tasks/{task_id}")
    assert "Choice for rush: ada" in shown_again.text
    assert "rush, ada: total 3 from 2" in shown_again.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
