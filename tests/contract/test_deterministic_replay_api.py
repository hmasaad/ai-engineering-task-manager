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


def test_the_page_shows_the_same_execution_report(client, tmp_path):
    task = _in_progress(client)
    task_id = task["id"]
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    (project / "other.txt").write_text("other\n", encoding="utf-8")
    for title, path in (("Read the note", "note.txt"), ("Read the other", "other.txt")):
        client.post(
            f"/api/tasks/{task_id}/workflow-steps",
            json={
                "title": title,
                "action": "read",
                "project": str(project),
                "path": path,
            },
        )
    client.post(f"/api/tasks/{task_id}/workflow/advance", json={})
    page = client.get(f"/tasks/{task_id}")
    assert 'id="workflow-execution"' in page.text
    assert "note.txt" in page.text
    assert "Stopped at Read the other: the step has not run." in page.text
    assert "Replay execution" in page.text

    report = client.post(f"/api/tasks/{task_id}/workflow/replay-execution")
    assert report.status_code == 200
    body = report.json()
    assert body["version"] == 1
    assert body["matched"] == [
        {
            "title": "Read the note",
            "action": "read",
            "state": "Completed",
            "effect": "note.txt",
        }
    ]
    assert body["stopped"] == "Stopped at Read the other: the step has not run."
    again = client.post(f"/api/tasks/{task_id}/workflow/replay-execution")
    assert again.json() == body
    assert isinstance(client.get("/api/tasks").json(), list)
    detail = client.get(f"/api/tasks/{task_id}")
    assert detail.json()["status"] == "In Progress"
    assert [item["path"] for item in detail.json()["file_reads"]] == ["note.txt"]
    shown = client.post(f"/tasks/{task_id}/workflow/replay-execution", follow_redirects=True)
    assert shown.status_code == 200
    assert "Stopped at Read the other: the step has not run." in shown.text
