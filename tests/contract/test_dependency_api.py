def _task(client, title):
    return client.post("/api/tasks", json={"title": title}).json()


def _ready(client, title):
    task = _task(client, title)
    task_id = task["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(
        f"/api/tasks/{task_id}/criteria",
        json={"text": "The export contains the goal"},
    )
    return client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"}).json()


def test_prerequisite_commands_and_the_execution_order(client):
    export = _task(client, "Add export")
    label = _task(client, "Write the label")
    missing_field = client.post(f"/api/tasks/{export['id']}/prerequisites", json={})
    assert missing_field.status_code == 400
    assert missing_field.json()["message"] == (
        "The request is missing a required field or has the wrong shape."
    )
    blank = client.post(
        f"/tasks/{export['id']}/prerequisites",
        data={"prerequisite_id": " "},
    )
    assert "Name the prerequisite task." in blank.text

    linked = client.post(
        f"/api/tasks/{export['id']}/prerequisites",
        json={"prerequisite_id": label["id"]},
    )
    assert linked.status_code == 200
    assert linked.json()["prerequisites"] == [
        {"id": label["id"], "title": "Write the label", "status": "Draft"}
    ]
    itself = client.post(
        f"/api/tasks/{export['id']}/prerequisites",
        json={"prerequisite_id": export["id"]},
    )
    assert itself.status_code == 409
    assert itself.json()["message"] == "A task cannot depend on itself."
    unknown = client.post(
        f"/api/tasks/{export['id']}/prerequisites",
        json={"prerequisite_id": 999},
    )
    assert unknown.status_code == 404
    assert unknown.json()["message"] == "Prerequisite not found."

    chosen = _task(client, "Choose the format")
    client.post(
        f"/api/tasks/{label['id']}/prerequisites",
        json={"prerequisite_id": chosen["id"]},
    )
    cycle = client.post(
        f"/api/tasks/{chosen['id']}/prerequisites",
        json={"prerequisite_id": export["id"]},
    )
    assert cycle.status_code == 409
    assert cycle.json()["message"] == "That dependency would form a cycle."

    order = client.get("/api/execution-order")
    assert order.status_code == 200
    titles = [item["title"] for item in order.json()]
    assert titles.index("Choose the format") < titles.index("Write the label")
    assert titles.index("Write the label") < titles.index("Add export")
    listed = client.get("/api/tasks")
    assert [item["title"] for item in listed.json()] == [
        "Add export",
        "Write the label",
        "Choose the format",
    ]

    removed = client.post(f"/api/tasks/{export['id']}/prerequisites/{label['id']}/remove")
    assert removed.status_code == 200
    assert removed.json()["prerequisites"] == []
    absent = client.post(f"/api/tasks/{export['id']}/prerequisites/{label['id']}/remove")
    assert absent.status_code == 409
    assert absent.json()["message"] == "That prerequisite is not linked."


def test_start_names_the_unfinished_prerequisite(client):
    label = _ready(client, "Write the label")
    export = _ready(client, "Add export")
    client.post(
        f"/api/tasks/{export['id']}/prerequisites",
        json={"prerequisite_id": label["id"]},
    )
    held = client.post(f"/api/tasks/{export['id']}/transitions", json={"action": "start"})
    assert held.status_code == 409
    assert held.json()["message"] == (
        "Blocked by Write the label (Ready): unverified The export contains the goal."
    )
    assert client.get(f"/api/tasks/{export['id']}").json()["status"] == "Ready"
