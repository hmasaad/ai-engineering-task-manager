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


def test_workflow_commands_store_one_step_and_stop_on_a_missing_file(client, tmp_path):
    task = _in_progress(client)
    task_id = task["id"]
    missing_field = client.post(f"/api/tasks/{task_id}/workflow-steps", json={})
    assert missing_field.status_code == 400
    assert missing_field.json()["message"] == (
        "The request is missing a required field or has the wrong shape."
    )
    blank = client.post(
        f"/tasks/{task_id}/workflow-steps",
        data={"title": " ", "action": "read", "project": "/tmp/demo", "path": "note.txt"},
    )
    assert "Name the step." in blank.text

    unknown = client.post(
        f"/api/tasks/{task_id}/workflow-steps",
        json={
            "title": "Commit the note",
            "action": "commit",
            "project": "/tmp/demo",
            "path": "note.txt",
        },
    )
    assert unknown.status_code == 400
    assert unknown.json()["message"] == "Choose a step action."

    project = tmp_path / "demo"
    project.mkdir()
    added = client.post(
        f"/api/tasks/{task_id}/workflow-steps",
        json={
            "title": "Read the note",
            "action": "read",
            "project": str(project),
            "path": "note.txt",
        },
    )
    assert added.status_code == 200
    assert added.json()["workflow"]["steps"][0]["title"] == "Read the note"
    assert added.json()["workflow"]["steps"][0]["state"] == "Pending"
    folder = client.post(
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
    assert [step["title"] for step in folder.json()["workflow"]["steps"]] == [
        "Read the note",
        "Create the folder",
    ]

    stopped = client.post(f"/api/tasks/{task_id}/workflow/advance")
    assert stopped.status_code == 200
    body = stopped.json()
    assert body["status"] == "In Progress"
    assert body["workflow"]["stopped"] == (
        "Stopped at Read the note: The file must already exist."
    )
    assert body["workflow"]["steps"][1]["state"] == "Pending"
    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)

    page = client.get(f"/tasks/{task_id}")
    assert "Stopped at Read the note: The file must already exist." in page.text
    assert "Advance workflow" in page.text
