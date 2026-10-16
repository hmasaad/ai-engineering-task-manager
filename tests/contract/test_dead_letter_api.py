def _task(client, title):
    return client.post("/api/tasks", json={"title": title}).json()


def _in_progress(client, title="Add export"):
    task = _task(client, title)
    task_id = task["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(
        f"/api/tasks/{task_id}/criteria",
        json={"text": "The export contains the goal"},
    )
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    return client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"}).json()


def test_the_page_shows_a_dead_letter(client, tmp_path):
    task = _in_progress(client)
    task_id = task["id"]
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
    shown = client.get(f"/tasks/{task_id}")
    assert 'id="rejection-name"' in shown.text
    assert 'id="rejection-reason"' in shown.text
    assert "Reject message" in shown.text

    blank = client.post(
        f"/api/tasks/{task_id}/workflow/outbox/reject",
        json={"name": " ", "reason": "The reader stopped."},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name this rejection."
    for name in ("one", "two", "three"):
        rejected = client.post(
            f"/api/tasks/{task_id}/workflow/outbox/reject",
            json={"name": name, "reason": "The reader stopped."},
        )
        assert rejected.status_code == 200
    detail = rejected.json()
    assert detail["workflow"]["outbox"][0]["state"] == "Dead"
    assert detail["workflow"]["dead_letters"][0]["reason"] == "The reader stopped."
    assert detail["status"] == "In Progress"
    assert isinstance(client.get("/api/tasks").json(), list)
    page = client.get(f"/tasks/{task_id}")
    assert 'id="workflow-dead-letters"' in page.text
    assert "Dead" in page.text
    assert "The reader stopped." in page.text
    assert 'id="workflow-poison"' in page.text
    assert "Reject message" not in page.text
    assert [item["path"] for item in detail["file_reads"]] == ["note.txt"]
