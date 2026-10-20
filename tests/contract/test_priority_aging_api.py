def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_ranks_work_and_serves_the_highest_score(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Rank work" in shown.text
    assert 'id="priority-name"' in shown.text
    assert 'id="work-rank"' in shown.text
    assert "Serve next" not in shown.text
    assert "No ranked work yet." in shown.text

    quiet = client.post(
        f"/api/tasks/{task_id}/priorities", json={"name": "quiet", "rank": "1"}
    )
    assert quiet.status_code == 200
    rush = client.post(
        f"/api/tasks/{task_id}/priorities", json={"name": "rush", "rank": "3"}
    )
    assert rush.status_code == 200
    assert rush.json()["status"] == "In Progress"
    assert rush.json()["priority"]["can_serve"] is True

    first = client.post(f"/api/tasks/{task_id}/serves", json={"name": "one"})
    assert first.status_code == 200
    assert first.json()["priority"]["serves"] == [{"name": "one", "work": "rush"}]
    assert first.json()["priority"]["waiting"] == [{"name": "quiet", "rank": 1, "age": 1}]

    page = client.get(f"/tasks/{task_id}")
    assert 'id="priority-work"' in page.text
    assert "quiet: rank 1, age 1" in page.text
    assert "one served rush" in page.text
    assert "Serve next" in page.text
    assert 'id="serve-name"' in page.text

    followed = client.post(
        f"/tasks/{task_id}/serves",
        data={"name": "two"},
        follow_redirects=True,
    )
    assert "two served quiet" in followed.text
    assert isinstance(client.get("/api/tasks").json(), list)
