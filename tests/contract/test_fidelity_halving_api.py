def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_winner(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Name candidate" in shown.text
    assert 'id="fidelity-candidate-name"' in shown.text
    assert "Record fidelity" not in shown.text
    assert "Halve the field" not in shown.text
    assert "No candidates yet." in shown.text

    ada = client.post(f"/api/tasks/{task_id}/fidelity-candidates", json={"name": "ada"})
    assert ada.status_code == 200
    assert ada.json()["status"] == "In Progress"
    assert ada.json()["fidelity"]["can_measure"] is True
    assert ada.json()["fidelity"]["can_halve"] is False
    for name in ("grace", "mina", "nora"):
        created = client.post(
            f"/api/tasks/{task_id}/fidelity-candidates", json={"name": name}
        )
        assert created.status_code == 200

    scores = (("one", "ada", "1"), ("two", "grace", "2"), ("three", "mina", "2"), ("four", "nora", "1"))
    for name, candidate, score in scores:
        recorded = client.post(
            f"/api/tasks/{task_id}/fidelity-measurements",
            json={"name": name, "candidate": candidate, "fidelity": "1", "score": score},
        )
        assert recorded.status_code == 200
    assert recorded.json()["fidelity"]["can_halve"] is True

    halved = client.post(f"/api/tasks/{task_id}/fidelity-halves")
    assert halved.status_code == 200
    assert halved.json()["fidelity"]["kept"] == [{"name": "grace"}, {"name": "mina"}]
    assert halved.json()["fidelity"]["winner"] is None

    grace = client.post(
        f"/api/tasks/{task_id}/fidelity-measurements",
        json={"name": "five", "candidate": "grace", "fidelity": "2", "score": "1"},
    )
    assert grace.status_code == 200
    mina = client.post(
        f"/api/tasks/{task_id}/fidelity-measurements",
        json={"name": "six", "candidate": "mina", "fidelity": "2", "score": "2"},
    )
    assert mina.status_code == 200

    chosen = client.post(f"/api/tasks/{task_id}/fidelity-halves")
    assert chosen.status_code == 200
    assert chosen.json()["fidelity"]["winner"] == "mina"

    page = client.get(f"/tasks/{task_id}")
    assert "one: ada, fidelity 1, score 1" in page.text
    assert "Winner: mina" in page.text
    assert 'id="fidelity-measurement-name"' in page.text
    assert 'id="fidelity-score"' in page.text
    assert "Halve the field" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/fidelity-measurements",
        data={"name": "seven", "candidate": "ada", "fidelity": "2", "score": "2"},
        follow_redirects=True,
    )
    assert "This task already has 6 measurements." in submitted.text
    assert "Winner: mina" in submitted.text
    assert "In Progress" in submitted.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
