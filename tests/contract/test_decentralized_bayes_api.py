def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_agreement(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Name point" in shown.text
    assert "Name node" in shown.text
    assert 'id="consensus-point-name"' in shown.text
    assert 'id="consensus-node-name"' in shown.text
    assert "Record report" not in shown.text
    assert "Agree on a design" not in shown.text
    assert "No points yet." in shown.text

    ada = client.post(
        f"/api/tasks/{task_id}/consensus-points",
        json={"name": "ada", "setting": "1"},
    )
    assert ada.status_code == 200
    assert ada.json()["status"] == "In Progress"
    assert ada.json()["consensus"]["can_report"] is False
    assert ada.json()["consensus"]["can_agree"] is False
    north = client.post(f"/api/tasks/{task_id}/consensus-nodes", json={"name": "north"})
    assert north.status_code == 200
    assert north.json()["consensus"]["can_report"] is True
    assert north.json()["consensus"]["can_agree"] is False
    client.post(f"/api/tasks/{task_id}/consensus-points", json={"name": "grace", "setting": "2"})
    client.post(f"/api/tasks/{task_id}/consensus-points", json={"name": "mina", "setting": "1"})
    client.post(f"/api/tasks/{task_id}/consensus-nodes", json={"name": "south"})

    one = client.post(
        f"/api/tasks/{task_id}/consensus-reports",
        json={"name": "one", "node": "north", "point": "ada", "score": "2"},
    )
    assert one.status_code == 200
    assert one.json()["consensus"]["can_agree"] is True
    client.post(
        f"/api/tasks/{task_id}/consensus-reports",
        json={"name": "two", "node": "south", "point": "ada", "score": "1"},
    )

    agreed = client.post(f"/api/tasks/{task_id}/consensus-agreements")
    assert agreed.status_code == 200
    assert agreed.json()["consensus"]["proposals"] == [
        {"node": "north", "point": "mina"},
        {"node": "south", "point": "mina"},
    ]
    assert agreed.json()["consensus"]["choice"] == {
        "point": "mina",
        "node": "north",
        "suggestions": 2,
    }

    page = client.get(f"/tasks/{task_id}")
    assert "ada: 1" in page.text
    assert "one: north, ada, score 2" in page.text
    assert "north: mina" in page.text
    assert "Agreement: mina on north, 2 suggestions" in page.text
    assert 'id="consensus-report-name"' in page.text
    assert 'id="consensus-report-score"' in page.text
    assert "Agree on a design" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/consensus-reports",
        data={"name": "three", "node": "north", "point": "grace", "score": "1"},
        follow_redirects=True,
    )
    assert "three: north, grace, score 1" in submitted.text
    assert "Agreement:" not in submitted.text
    assert "In Progress" in submitted.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
