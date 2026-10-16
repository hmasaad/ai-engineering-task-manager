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


def test_the_page_compensates_a_failed_saga(client, tmp_path):
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
            "title": "Read the gap",
            "action": "read",
            "project": str(project),
            "path": "missing.txt",
        },
    )
    client.post(f"/api/tasks/{task_id}/workflow/advance", json={})
    client.post(f"/api/tasks/{task_id}/workflow/advance", json={})
    shown = client.get(f"/tasks/{task_id}")
    assert 'id="workflow-saga"' in shown.text
    assert "Saga Failed" in shown.text
    assert 'id="compensation-reason"' in shown.text
    assert "Compensate" in shown.text

    blank = client.post(f"/api/tasks/{task_id}/workflow/compensate", json={"reason": " "})
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name why this step is compensated."
    compensated = client.post(
        f"/api/tasks/{task_id}/workflow/compensate",
        json={"reason": "Withdraw the note"},
    )
    assert compensated.status_code == 200
    assert compensated.json()["workflow"]["saga"] == "Compensated"
    assert compensated.json()["status"] == "In Progress"
    assert isinstance(client.get("/api/tasks").json(), list)
    page = client.post(
        f"/tasks/{task_id}/workflow/compensate",
        data={"reason": "Again"},
        follow_redirects=True,
    )
    assert "Saga Compensated" in page.text
    assert 'id="workflow-compensations"' in page.text
    assert "Read the note" in page.text
    detail = client.get(f"/api/tasks/{task_id}")
    assert [item["path"] for item in detail.json()["file_reads"]] == ["note.txt"]
