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


def test_the_page_takes_and_restores_a_checkpoint(client, tmp_path):
    task = _in_progress(client)
    task_id = task["id"]
    before = client.get(f"/tasks/{task_id}")
    assert "No checkpoints yet." in before.text
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
            "title": "Read the gap",
            "action": "read",
            "project": str(project),
            "path": "missing.txt",
        },
    )
    shown = client.get(f"/tasks/{task_id}")
    assert 'id="checkpoint-name"' in shown.text
    assert "Take checkpoint" in shown.text
    blank = client.post(
        f"/api/tasks/{task_id}/workflow/checkpoints",
        json={"name": " "},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name this checkpoint."
    saved = client.post(
        f"/api/tasks/{task_id}/workflow/checkpoints",
        json={"name": "before the read"},
    )
    assert saved.status_code == 200
    checkpoint_id = saved.json()["workflow"]["checkpoints"][0]["id"]
    client.post(f"/api/tasks/{task_id}/workflow/advance", json={})
    client.post(f"/api/tasks/{task_id}/workflow/advance", json={})
    restored = client.post(
        f"/api/tasks/{task_id}/workflow/checkpoints/{checkpoint_id}/restore"
    )
    assert restored.status_code == 200
    assert [step["state"] for step in restored.json()["workflow"]["steps"]] == [
        "Completed",
        "Pending",
    ]
    assert isinstance(client.get("/api/tasks").json(), list)
    listed = client.get(f"/api/tasks/{task_id}/workflow/checkpoints")
    assert listed.json()["checkpoints"][0]["name"] == "before the read"
    page = client.get(f"/tasks/{task_id}")
    assert 'id="workflow-checkpoints"' in page.text
    assert "before the read" in page.text
    assert "Restore checkpoint" in page.text
    detail = client.get(f"/api/tasks/{task_id}")
    assert detail.json()["status"] == "In Progress"
    assert [item["path"] for item in detail.json()["file_reads"]] == ["note.txt"]
