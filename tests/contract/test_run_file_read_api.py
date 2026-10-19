def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_runs_one_file_read(client, tmp_path):
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
    client.post(
        f"/api/tasks/{task_id}/workflow-steps",
        json={
            "title": "Create the folder",
            "action": "folder",
            "project": str(project),
            "path": "notes",
            "what_changed": "Add notes",
            "class": "ordinary",
        },
    )
    shown = client.get(f"/tasks/{task_id}")
    assert "Run file read" in shown.text
    assert 'id="run-name"' in shown.text
    ran = client.post(f"/api/tasks/{task_id}/workflow/runs", json={"name": "once"})
    assert ran.status_code == 200
    body = ran.json()
    assert [step["state"] for step in body["workflow"]["steps"]] == ["Completed", "Pending"]
    assert [item["path"] for item in body["file_reads"]] == ["note.txt"]
    assert body["workflow"]["runs"] == [{"name": "once", "title": "Read the note"}]
    assert body["status"] == "In Progress"
    page = client.post(
        f"/tasks/{task_id}/workflow/runs",
        data={"name": "once"},
        follow_redirects=True,
    )
    assert 'id="workflow-runs"' in page.text
    assert "once read Read the note" in page.text
    assert "Run file read" not in page.text
    assert not (project / "notes").exists()
    assert isinstance(client.get("/api/tasks").json(), list)
