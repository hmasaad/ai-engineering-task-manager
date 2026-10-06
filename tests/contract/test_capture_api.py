def test_blank_title_is_refused(client):
    response = client.post("/api/tasks", json={"title": "   "})
    assert response.status_code == 400
    body = response.json()
    assert body["refused"] is True
    assert "title" in body["message"].lower()
    assert client.get("/api/tasks").json() == []


def test_create_list_goal_criterion_and_ready(client):
    created = client.post("/api/tasks", json={"title": "Add export"})
    assert created.status_code == 200
    task_id = created.json()["id"]
    assert created.json()["status"] == "Draft"

    listed = client.get("/api/tasks")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == task_id

    goal = client.patch(
        f"/api/tasks/{task_id}",
        json={"goal": "An engineer can take a finished task record with them"},
    )
    assert goal.status_code == 200

    refused = client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    assert refused.status_code == 409
    assert refused.json()["refused"] is True
    assert "acceptance criterion" in refused.json()["message"].lower()

    added = client.post(
        f"/api/tasks/{task_id}/criteria",
        json={"text": "The file contains the goal"},
    )
    assert added.status_code == 200
    criterion_id = added.json()["criteria"][0]["id"]

    ready = client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    assert ready.status_code == 200
    assert ready.json()["status"] == "Ready"

    edited = client.patch(
        f"/api/tasks/{task_id}/criteria/{criterion_id}",
        json={"text": "The file contains the goal and the status"},
    )
    assert edited.status_code == 200
    assert edited.json()["criteria"][0]["text"] == "The file contains the goal and the status"

    missing = client.get("/api/tasks/9999")
    assert missing.status_code == 404
    assert missing.json()["refused"] is True


def test_list_page_shows_created_task(client):
    client.post("/api/tasks", json={"title": "Add export"})
    page = client.get("/")
    assert page.status_code == 200
    assert "Add export" in page.text
    assert "Draft" in page.text
