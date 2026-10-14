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


def test_replay_lists_a_failed_read_and_recover_is_refused(client, tmp_path):
    task = _in_progress(client)
    task_id = task["id"]
    empty = client.get(f"/api/tasks/{task_id}/workflow-replay")
    assert empty.status_code == 200
    assert empty.json() == {"events": []}
    missing = client.get("/api/tasks/999/workflow-replay")
    assert missing.status_code == 404
    assert missing.json()["message"] == "Task not found."

    project = tmp_path / "demo"
    project.mkdir()
    client.post(
        f"/api/tasks/{task_id}/workflow-steps",
        json={
            "title": "Read the note",
            "action": "read",
            "project": str(project),
            "path": "note.txt",
        },
    )
    advanced = client.post(f"/api/tasks/{task_id}/workflow/advance")
    assert advanced.status_code == 200
    events = advanced.json()["workflow"]["replay"]
    assert [event["state"] for event in events] == ["Running", "Failed"]
    assert events[1]["detail"] == "The file must already exist."
    replay = client.get(f"/api/tasks/{task_id}/workflow-replay")
    assert replay.json()["events"] == events

    recovered = client.post(f"/api/tasks/{task_id}/workflow/recover")
    assert recovered.status_code == 409
    assert recovered.json()["message"] == "There is no step to recover."
    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)

    page = client.get(f"/tasks/{task_id}")
    assert "Replay" in page.text
    assert "The file must already exist." in page.text
    assert "Recover workflow" not in page.text
