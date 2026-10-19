def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_replays_a_dead_letter(client, tmp_path):
    task_id = _in_progress(client)
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    client.post(
        f"/api/tasks/{task_id}/workflow-steps",
        json={
            "title": "Read the note",
            "action": "read",
            "project": str(project),
            "path": "note.txt",
        },
    )
    client.post(f"/api/tasks/{task_id}/workflow/advance", json={})
    for name in ("one", "two", "three"):
        client.post(
            f"/api/tasks/{task_id}/workflow/outbox/reject",
            json={"name": name, "reason": "The reader stopped."},
        )
    shown = client.get(f"/tasks/{task_id}")
    assert "Replay dead letter" in shown.text
    assert 'id="replay-name"' in shown.text
    returned = client.post(
        f"/api/tasks/{task_id}/workflow/dead-letters/replay",
        json={"name": "once"},
    )
    assert returned.status_code == 200
    body = returned.json()
    assert body["workflow"]["outbox"][0]["state"] == "Pending"
    assert body["workflow"]["dead_letters"][0]["reason"] == "The reader stopped."
    assert body["workflow"]["dead_letter_replays"] == [
        {
            "name": "once",
            "outbox_id": body["workflow"]["outbox"][0]["id"],
            "title": "Read the note",
        }
    ]
    page = client.post(
        f"/tasks/{task_id}/workflow/dead-letters/replay",
        data={"name": "once"},
        follow_redirects=True,
    )
    assert 'id="workflow-dead-letter-replays"' in page.text
    assert "once" in page.text
    assert "Replay dead letter" not in page.text
    assert "Pending" in page.text
    delivered = client.post(
        f"/api/tasks/{task_id}/workflow/outbox",
        json={"name": "ship"},
    )
    assert delivered.status_code == 200
    assert delivered.json()["workflow"]["outbox"][0]["state"] == "Delivered"
    assert isinstance(client.get("/api/tasks").json(), list)
