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


def test_the_page_replays_a_sealed_effect(client, tmp_path):
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
    client.post(
        f"/api/tasks/{task_id}/workflow-steps",
        json={
            "title": "Read the extra",
            "action": "read",
            "project": str(project),
            "path": "extra.txt",
        },
    )
    client.post(f"/api/tasks/{task_id}/workflow/advance", json={})
    shown = client.get(f"/tasks/{task_id}")
    assert 'id="workflow-isolated"' in shown.text
    assert "note.txt" in shown.text
    assert "Replay isolated effects" in shown.text
    assert "Stopped at Read the extra: the step has not run." in shown.text
    replayed = client.post(f"/api/tasks/{task_id}/workflow/replay-isolated")
    assert replayed.status_code == 200
    assert replayed.json()["matched"] == [{"title": "Read the note", "effect": "note.txt"}]
    assert isinstance(client.get("/api/tasks").json(), list)
    page = client.post(
        f"/tasks/{task_id}/workflow/replay-isolated",
        follow_redirects=True,
    )
    assert "Replay isolated effects" in page.text
    detail = client.get(f"/api/tasks/{task_id}")
    assert detail.json()["status"] == "In Progress"
    assert [item["path"] for item in detail.json()["file_reads"]] == ["note.txt"]
