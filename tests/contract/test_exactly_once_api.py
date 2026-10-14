import re


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


def _advance_name(page_text):
    match = re.search(
        r'id="advance-name" name="name" type="text" value="([^"]+)"',
        page_text,
    )
    assert match is not None
    return match.group(1)


def test_the_same_name_does_not_perform_the_next_step(client, tmp_path):
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
            "title": "Create the folder",
            "action": "folder",
            "project": str(project),
            "path": "notes",
            "what_changed": "Add notes",
            "class": "ordinary",
        },
    )
    once = client.post(f"/api/tasks/{task_id}/workflow/advance", json={"name": "once"})
    assert once.status_code == 200
    assert [step["state"] for step in once.json()["workflow"]["steps"]] == [
        "Completed",
        "Pending",
    ]
    replay = once.json()["workflow"]["replay"]
    again = client.post(f"/api/tasks/{task_id}/workflow/advance", json={"name": "once"})
    assert again.status_code == 200
    assert again.json()["workflow"]["steps"][1]["state"] == "Pending"
    assert again.json()["workflow"]["replay"] == replay
    assert len(again.json()["file_reads"]) == 1
    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)

    page = client.get(f"/tasks/{task_id}")
    assert "Advance name" in page.text
    shown = _advance_name(page.text)
    assert shown
    assert shown != "once"
    posted = client.post(f"/tasks/{task_id}/workflow/advance", data={"name": "once"})
    assert posted.status_code == 200
    assert "Pending" in posted.text
    assert "notes" in posted.text
    fresh = client.get(f"/tasks/{task_id}")
    assert _advance_name(fresh.text) != shown


def test_a_missing_body_still_advances(client, tmp_path):
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
            "title": "Create the folder",
            "action": "folder",
            "project": str(project),
            "path": "notes",
            "what_changed": "Add notes",
            "class": "ordinary",
        },
    )
    first = client.post(f"/api/tasks/{task_id}/workflow/advance")
    assert first.status_code == 200
    assert first.json()["workflow"]["steps"][0]["state"] == "Completed"
    second = client.post(f"/api/tasks/{task_id}/workflow/advance", json={"name": ""})
    assert second.status_code == 200
    assert second.json()["workflow"]["steps"][1]["state"] == "Completed"
