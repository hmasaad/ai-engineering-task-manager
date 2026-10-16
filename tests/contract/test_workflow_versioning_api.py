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


def test_the_page_revises_and_migrates(client, tmp_path):
    task = _in_progress(client)
    task_id = task["id"]
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    (project / "other.txt").write_text("other\n", encoding="utf-8")
    (project / "extra.txt").write_text("extra\n", encoding="utf-8")
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
    assert "Version 1" in page.text
    assert "Revise workflow" in page.text
    missing = client.post(f"/api/tasks/{task_id}/workflow/migrate", json={"reason": "Now"})
    assert missing.status_code == 409
    assert missing.json()["message"] == "There is no draft version to migrate."

    revised = client.post(f"/api/tasks/{task_id}/workflow/revise")
    assert revised.status_code == 200
    assert revised.json()["workflow"]["draft"]["number"] == 2
    assert isinstance(client.get("/api/tasks").json(), list)
    draft_page = client.get(f"/tasks/{task_id}")
    assert "Draft version 2" in draft_page.text
    assert 'id="migration-reason"' in draft_page.text

    client.post(
        f"/api/tasks/{task_id}/workflow-steps",
        json={
            "title": "Read the extra",
            "action": "read",
            "project": str(project),
            "path": "extra.txt",
        },
    )
    blank = client.post(f"/api/tasks/{task_id}/workflow/migrate", json={"reason": " "})
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name why this workflow is migrating."
    migrated = client.post(
        f"/api/tasks/{task_id}/workflow/migrate",
        json={"reason": "Replace the remaining step"},
    )
    assert migrated.status_code == 200
    body = migrated.json()
    assert body["status"] == "In Progress"
    assert body["workflow"]["version"] == 2
    assert [step["title"] for step in body["workflow"]["steps"]] == [
        "Read the note",
        "Read the extra",
    ]
    shown = client.get(f"/tasks/{task_id}")
    assert "Version 2" in shown.text
    assert "Version 1 superseded: Replace the remaining step" in shown.text
