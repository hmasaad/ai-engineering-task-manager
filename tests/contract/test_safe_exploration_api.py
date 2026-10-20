def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_safe_effect(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Name action" in shown.text
    assert 'id="safe-action-name"' in shown.text
    assert 'id="action-risk"' in shown.text
    assert "Record probe" not in shown.text
    assert "Compare actions" not in shown.text
    assert "No actions yet." in shown.text

    ada = client.post(
        f"/api/tasks/{task_id}/safe-actions",
        json={"name": "ada", "risk": "1"},
    )
    assert ada.status_code == 200
    grace = client.post(
        f"/api/tasks/{task_id}/safe-actions",
        json={"name": "grace", "risk": "1"},
    )
    assert grace.status_code == 200
    assert grace.json()["status"] == "In Progress"
    assert grace.json()["safety"]["can_probe"] is True
    assert grace.json()["safety"]["can_compare"] is False

    one = client.post(
        f"/api/tasks/{task_id}/safe-probes",
        json={"name": "one", "state": "rush", "action": "ada", "reward": "1"},
    )
    assert one.status_code == 200
    two = client.post(
        f"/api/tasks/{task_id}/safe-probes",
        json={"name": "two", "state": "rush", "action": "grace", "reward": "2"},
    )
    assert two.status_code == 200
    assert two.json()["safety"]["can_compare"] is True

    compared = client.post(
        f"/api/tasks/{task_id}/safe-effects",
        json={"state": "rush", "action": "grace", "instead": "ada"},
    )
    assert compared.status_code == 200
    assert compared.json()["safety"]["effect"] == {
        "state": "rush",
        "action": "grace",
        "instead": "ada",
        "effect": 1,
    }

    page = client.get(f"/tasks/{task_id}")
    assert "ada: risk 1" in page.text
    assert "grace: risk 1" in page.text
    assert "one: rush, ada, reward 1" in page.text
    assert "two: rush, grace, reward 2" in page.text
    assert "Effect of grace instead of ada in rush: 1" in page.text
    assert 'id="probe-name"' in page.text
    assert 'id="effect-state"' in page.text
    assert "Compare actions" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/safe-probes",
        data={"name": "three", "state": "quiet", "action": "ada", "reward": "1"},
        follow_redirects=True,
    )
    assert "three: quiet, ada, reward 1" in submitted.text
    assert "Effect of grace" not in submitted.text
    assert "In Progress" in submitted.text

    again = client.post(
        f"/api/tasks/{task_id}/safe-effects",
        json={"state": "rush", "action": "ada", "instead": "grace"},
    )
    assert again.json()["safety"]["effect"]["effect"] == -1
    shown_again = client.get(f"/tasks/{task_id}")
    assert "Effect of ada instead of grace in rush: -1" in shown_again.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
