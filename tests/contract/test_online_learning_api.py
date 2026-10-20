def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_learned_schedule(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Record outcome" in shown.text
    assert 'id="outcome-name"' in shown.text
    assert 'id="outcome-kind"' in shown.text
    assert 'id="outcome-length"' in shown.text
    assert "Name forecast" not in shown.text
    assert "Predict schedule" not in shown.text
    assert "No outcomes yet." in shown.text

    past = client.post(
        f"/api/tasks/{task_id}/learn-outcomes",
        json={"name": "past", "kind": "review", "length": "2"},
    )
    assert past.status_code == 200
    again = client.post(
        f"/api/tasks/{task_id}/learn-outcomes",
        json={"name": "again", "kind": "review", "length": "2"},
    )
    assert again.status_code == 200
    once = client.post(
        f"/api/tasks/{task_id}/learn-outcomes",
        json={"name": "once", "kind": "export", "length": "1"},
    )
    assert once.status_code == 200
    assert once.json()["status"] == "In Progress"
    assert once.json()["learning"]["can_forecast"] is True
    assert once.json()["learning"]["can_predict"] is False
    assert once.json()["learning"]["kinds"] == [
        {"kind": "review", "predicted": 2},
        {"kind": "export", "predicted": 1},
    ]

    draft = client.post(
        f"/api/tasks/{task_id}/learn-forecasts",
        json={"name": "draft", "kind": "review"},
    )
    assert draft.status_code == 200
    ship = client.post(
        f"/api/tasks/{task_id}/learn-forecasts",
        json={"name": "ship", "kind": "export"},
    )
    assert ship.status_code == 200
    assert ship.json()["learning"]["can_predict"] is True

    scheduled = client.post(f"/api/tasks/{task_id}/learn-predictions")
    assert scheduled.status_code == 200
    assert scheduled.json()["learning"]["finish"] == 3
    assert scheduled.json()["learning"]["forecasts"] == [
        {"name": "draft", "kind": "review", "predicted": 2, "start": 0},
        {"name": "ship", "kind": "export", "predicted": 1, "start": 2},
    ]

    page = client.get(f"/tasks/{task_id}")
    assert "past: review took 2" in page.text
    assert "again: review took 2" in page.text
    assert "once: export took 1" in page.text
    assert "review: predicted 2" in page.text
    assert "export: predicted 1" in page.text
    assert "draft: review, predicted 2, starts 0" in page.text
    assert "ship: export, predicted 1, starts 2" in page.text
    assert "Finish day: 3" in page.text
    assert 'id="forecast-name"' in page.text
    assert "Predict schedule" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/learn-forecasts",
        data={"name": "note", "kind": "review"},
        follow_redirects=True,
    )
    assert "note: review" in submitted.text
    assert "Finish day:" not in submitted.text
    assert "In Progress" in submitted.text

    extended = client.post(f"/api/tasks/{task_id}/learn-predictions")
    assert extended.json()["learning"]["finish"] == 5
    shown_again = client.get(f"/tasks/{task_id}")
    assert "Finish day: 5" in shown_again.text
    assert "note: review, predicted 2, starts 3" in shown_again.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
