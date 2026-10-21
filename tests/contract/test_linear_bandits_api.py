def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_neural_choice(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Name model arm" in shown.text
    assert 'id="model-arm-name"' in shown.text
    assert "Name model context" in shown.text
    assert 'id="model-context-name"' in shown.text
    assert 'id="model-first"' in shown.text
    assert 'id="model-second"' in shown.text
    assert "Record model pull" not in shown.text
    assert "Choose with model" not in shown.text
    assert "No model arms yet." in shown.text

    ada = client.post(f"/api/tasks/{task_id}/model-arms", json={"name": "ada"})
    assert ada.status_code == 200
    grace = client.post(f"/api/tasks/{task_id}/model-arms", json={"name": "grace"})
    assert grace.status_code == 200
    assert grace.json()["status"] == "In Progress"
    assert grace.json()["models"]["can_pull"] is False
    quiet = client.post(
        f"/api/tasks/{task_id}/model-contexts",
        json={"name": "quiet", "first": "1", "second": "0"},
    )
    assert quiet.status_code == 200
    rush = client.post(
        f"/api/tasks/{task_id}/model-contexts",
        json={"name": "rush", "first": "1", "second": "1"},
    )
    assert rush.status_code == 200
    assert rush.json()["models"]["can_pull"] is True
    assert rush.json()["models"]["can_choose"] is True

    one = client.post(
        f"/api/tasks/{task_id}/model-pulls",
        json={"name": "one", "context": "quiet", "arm": "ada", "reward": "2"},
    )
    assert one.status_code == 200
    two = client.post(
        f"/api/tasks/{task_id}/model-pulls",
        json={"name": "two", "context": "quiet", "arm": "ada", "reward": "2"},
    )
    assert two.status_code == 200
    three = client.post(
        f"/api/tasks/{task_id}/model-pulls",
        json={"name": "three", "context": "rush", "arm": "grace", "reward": "2"},
    )
    assert three.status_code == 200

    linear = client.post(
        f"/api/tasks/{task_id}/model-choices",
        json={"context": "rush", "model": "linear"},
    )
    assert linear.status_code == 200
    assert linear.json()["models"]["choice"] == {
        "context": "rush",
        "model": "linear",
        "arm": "ada",
    }
    neural = client.post(
        f"/api/tasks/{task_id}/model-choices",
        json={"context": "rush", "model": "neural"},
    )
    assert neural.json()["models"]["choice"] == {
        "context": "rush",
        "model": "neural",
        "arm": "grace",
    }

    page = client.get(f"/tasks/{task_id}")
    assert "quiet: 1, 0" in page.text
    assert "rush: 1, 1" in page.text
    assert "one: quiet, ada, reward 2" in page.text
    assert "three: rush, grace, reward 2" in page.text
    assert "Neural choice in rush: grace" in page.text
    assert 'id="model-pull-name"' in page.text
    assert 'id="model-choice-context"' in page.text
    assert 'id="model-choice-model"' in page.text
    assert "Choose with model" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/model-pulls",
        data={"name": "four", "context": "rush", "arm": "ada", "reward": "1"},
        follow_redirects=True,
    )
    assert "four: rush, ada, reward 1" in submitted.text
    assert "Neural choice" not in submitted.text
    assert "In Progress" in submitted.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
