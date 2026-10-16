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


def test_the_page_delivers_one_outbox_message(client, tmp_path):
    task = _in_progress(client)
    task_id = task["id"]
    page = client.get(f"/tasks/{task_id}")
    assert "No outbox messages yet." in page.text
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
    shown = client.get(f"/tasks/{task_id}")
    assert 'id="workflow-outbox"' in shown.text
    assert "Pending" in shown.text
    assert 'id="delivery-name"' in shown.text
    assert "Deliver outbox" in shown.text

    empty = client.post(f"/api/tasks/{task_id}/workflow/outbox", json={"name": " "})
    assert empty.status_code == 400
    assert empty.json()["message"] == "Name this delivery."
    delivered = client.post(f"/api/tasks/{task_id}/workflow/outbox", json={"name": "once"})
    assert delivered.status_code == 200
    states = [item["state"] for item in delivered.json()["workflow"]["outbox"]]
    assert states == ["Delivered", "Pending"]
    repeated = client.post(f"/api/tasks/{task_id}/workflow/outbox", json={"name": "once"})
    assert [item["state"] for item in repeated.json()["workflow"]["outbox"]] == states
    assert isinstance(client.get("/api/tasks").json(), list)
    page = client.post(
        f"/tasks/{task_id}/workflow/outbox",
        data={"name": "next"},
        follow_redirects=True,
    )
    assert "Delivered" in page.text
    assert 'id="workflow-inbox"' in page.text
    assert "next" in page.text
    detail = client.get(f"/api/tasks/{task_id}")
    assert detail.json()["status"] == "In Progress"
    assert [item["path"] for item in detail.json()["file_reads"]] == ["note.txt", "extra.txt"]
