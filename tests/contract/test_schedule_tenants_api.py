def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_admits_tenants_and_grants_turns(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Admit tenant" in shown.text
    assert 'id="tenant-name"' in shown.text
    assert "Grant turn" not in shown.text

    ada = client.post(f"/api/tasks/{task_id}/tenants", json={"name": "ada"})
    assert ada.status_code == 200
    grace = client.post(f"/api/tasks/{task_id}/tenants", json={"name": "grace"})
    assert grace.status_code == 200
    assert grace.json()["status"] == "In Progress"
    assert grace.json()["schedule"]["can_grant"] is True

    first = client.post(f"/api/tasks/{task_id}/turns", json={"name": "one"})
    second = client.post(f"/api/tasks/{task_id}/turns", json={"name": "two"})
    assert second.status_code == 200
    assert second.json()["schedule"]["turns"] == [
        {"name": "one", "tenant": "ada"},
        {"name": "two", "tenant": "grace"},
    ]

    page = client.get(f"/tasks/{task_id}")
    assert 'id="tenants"' in page.text
    assert "ada: 1 of 2" in page.text
    assert "grace: 1 of 2" in page.text
    assert "one granted to ada" in page.text
    assert "two granted to grace" in page.text
    assert "Grant turn" in page.text
    assert 'id="turn-name"' in page.text

    followed = client.post(
        f"/tasks/{task_id}/turns",
        data={"name": "three"},
        follow_redirects=True,
    )
    assert "three granted to ada" in followed.text
    assert isinstance(client.get("/api/tasks").json(), list)
