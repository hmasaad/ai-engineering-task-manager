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


def test_the_page_shows_the_trace(client, tmp_path):
    task = _in_progress(client)
    task_id = task["id"]
    before = client.get(f"/tasks/{task_id}")
    assert "No trace yet." in before.text
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    (project / "extra.txt").write_text("extra\n", encoding="utf-8")
    for title, path in (("Read the note", "note.txt"), ("Read the extra", "extra.txt")):
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
    client.post(f"/api/tasks/{task_id}/workflow/advance", json={})
    trace = client.get(f"/api/tasks/{task_id}/workflow/trace")
    assert trace.status_code == 200
    body = trace.json()
    assert body["spans"][1]["parent_id"] == body["spans"][0]["id"]
    assert isinstance(client.get("/api/tasks").json(), list)
    page = client.get(f"/tasks/{task_id}")
    assert 'id="workflow-trace"' in page.text
    assert 'id="workflow-spans"' in page.text
    assert "Read the note" in page.text
    assert f"follows {body['spans'][0]['id']}" in page.text
    detail = client.get(f"/api/tasks/{task_id}")
    assert detail.json()["status"] == "In Progress"
    assert [item["path"] for item in detail.json()["file_reads"]] == ["note.txt", "extra.txt"]
