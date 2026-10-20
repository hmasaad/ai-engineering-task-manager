def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_balances_and_steals_work(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Add worker" in shown.text
    assert 'id="worker-name"' in shown.text
    assert "Place job" not in shown.text
    assert "Steal work" not in shown.text
    assert "No workers yet." in shown.text

    ada = client.post(f"/api/tasks/{task_id}/workers", json={"name": "ada"})
    assert ada.status_code == 200
    grace = client.post(f"/api/tasks/{task_id}/workers", json={"name": "grace"})
    assert grace.status_code == 200
    for name in ("one", "two", "three"):
        placed = client.post(f"/api/tasks/{task_id}/jobs", json={"name": name})
        assert placed.status_code == 200
    body = client.post(f"/api/tasks/{task_id}/workers", json={"name": "lin"}).json()
    assert body["status"] == "In Progress"
    assert [worker["name"] for worker in body["work"]["workers"]] == ["ada", "grace", "lin"]
    assert body["work"]["workers"][0]["jobs"] == ["one", "three"]
    assert body["work"]["can_place"] is True
    assert body["work"]["can_steal"] is True

    page = client.get(f"/tasks/{task_id}")
    assert 'id="workers"' in page.text
    assert "ada: one, three" in page.text
    assert "grace: two" in page.text
    assert "lin: idle" in page.text
    assert "Place job" in page.text
    assert 'id="job-name"' in page.text
    assert "Steal work" in page.text
    assert 'id="steal-name"' in page.text
    assert 'id="idle-worker"' in page.text

    stolen = client.post(
        f"/api/tasks/{task_id}/steals", json={"name": "take", "worker": "lin"}
    )
    assert stolen.status_code == 200
    assert stolen.json()["work"]["steals"] == [
        {"name": "take", "job": "one", "from_worker": "ada", "to_worker": "lin"}
    ]
    assert stolen.json()["work"]["can_steal"] is False

    followed = client.post(
        f"/tasks/{task_id}/steals",
        data={"name": "take", "worker": "lin"},
        follow_redirects=True,
    )
    assert 'id="steals"' in followed.text
    assert "take moved one from ada to lin" in followed.text
    assert "Steal work" not in followed.text
    assert "ada: three" in followed.text
    assert "lin: one" in followed.text

    full = _in_progress(client)
    client.post(f"/api/tasks/{full}/workers", json={"name": "ada"})
    for name in ("one", "two", "three"):
        client.post(f"/api/tasks/{full}/jobs", json={"name": name})
    blocked = client.get(f"/tasks/{full}")
    assert "Place job" not in blocked.text
    refused = client.post(f"/api/tasks/{full}/jobs", json={"name": "four"})
    assert refused.status_code == 409
    assert refused.json()["message"] == "Every worker is full."
    assert isinstance(client.get("/api/tasks").json(), list)
