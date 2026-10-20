def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_policy_score(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Record logged step" in shown.text
    assert 'id="log-name"' in shown.text
    assert 'id="log-state"' in shown.text
    assert 'id="log-action"' in shown.text
    assert 'id="log-reward"' in shown.text
    assert "Name policy rule" not in shown.text
    assert "Evaluate policy" not in shown.text
    assert "No logged steps yet." in shown.text

    one = client.post(
        f"/api/tasks/{task_id}/policy-logs",
        json={"name": "one", "state": "rush", "action": "ada", "reward": "1"},
    )
    assert one.status_code == 200
    two = client.post(
        f"/api/tasks/{task_id}/policy-logs",
        json={"name": "two", "state": "rush", "action": "grace", "reward": "2"},
    )
    assert two.status_code == 200
    three = client.post(
        f"/api/tasks/{task_id}/policy-logs",
        json={"name": "three", "state": "quiet", "action": "ada", "reward": "2"},
    )
    assert three.status_code == 200
    assert three.json()["status"] == "In Progress"
    assert three.json()["evaluation"]["can_rule"] is True
    assert three.json()["evaluation"]["can_evaluate"] is False

    rush = client.post(
        f"/api/tasks/{task_id}/policy-rules",
        json={"state": "rush", "action": "grace"},
    )
    assert rush.status_code == 200
    quiet = client.post(
        f"/api/tasks/{task_id}/policy-rules",
        json={"state": "quiet", "action": "ada"},
    )
    assert quiet.status_code == 200
    assert quiet.json()["evaluation"]["can_evaluate"] is True

    scored = client.post(f"/api/tasks/{task_id}/policy-scores")
    assert scored.status_code == 200
    assert scored.json()["evaluation"]["score"] == {"total": 4, "count": 2}

    page = client.get(f"/tasks/{task_id}")
    assert "one: rush, ada, reward 1" in page.text
    assert "two: rush, grace, reward 2" in page.text
    assert "three: quiet, ada, reward 2" in page.text
    assert "rush: grace" in page.text
    assert "quiet: ada" in page.text
    assert "Score: 4 from 2" in page.text
    assert 'id="rule-state"' in page.text
    assert "Evaluate policy" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/policy-logs",
        data={"name": "four", "state": "quiet", "action": "ada", "reward": "1"},
        follow_redirects=True,
    )
    assert "four: quiet, ada, reward 1" in submitted.text
    assert "Score:" not in submitted.text
    assert "In Progress" in submitted.text

    again = client.post(f"/api/tasks/{task_id}/policy-scores")
    assert again.json()["evaluation"]["score"] == {"total": 5, "count": 3}
    shown_again = client.get(f"/tasks/{task_id}")
    assert "Score: 5 from 3" in shown_again.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
