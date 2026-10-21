def _in_progress(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_shows_the_next_design(client):
    task_id = _in_progress(client)
    shown = client.get(f"/tasks/{task_id}")
    assert "Name design" in shown.text
    assert 'id="search-design-name"' in shown.text
    assert 'id="search-first"' in shown.text
    assert 'id="search-second"' in shown.text
    assert "Record observation" not in shown.text
    assert "Recommend a design" not in shown.text
    assert "No designs yet." in shown.text

    ada = client.post(
        f"/api/tasks/{task_id}/search-designs",
        json={"name": "ada", "first": "1", "second": "1"},
    )
    assert ada.status_code == 200
    assert ada.json()["status"] == "In Progress"
    assert ada.json()["search"]["can_observe"] is True
    assert ada.json()["search"]["can_recommend"] is False
    for name, first, second in (("grace", "2", "2"), ("mina", "1", "2"), ("nora", "2", "1")):
        created = client.post(
            f"/api/tasks/{task_id}/search-designs",
            json={"name": name, "first": first, "second": second},
        )
        assert created.status_code == 200

    one = client.post(
        f"/api/tasks/{task_id}/search-observations",
        json={
            "name": "one",
            "design": "ada",
            "first": "2",
            "second": "1",
            "constraint": "1",
        },
    )
    assert one.status_code == 200
    assert one.json()["search"]["can_recommend"] is True
    two = client.post(
        f"/api/tasks/{task_id}/search-observations",
        json={
            "name": "two",
            "design": "grace",
            "first": "2",
            "second": "2",
            "constraint": "2",
        },
    )
    assert two.status_code == 200

    recommended = client.post(f"/api/tasks/{task_id}/search-recommendations")
    assert recommended.status_code == 200
    assert recommended.json()["search"]["front"] == [
        {"design": "ada", "first": 2, "second": 1}
    ]
    assert recommended.json()["search"]["next"] == "mina"

    page = client.get(f"/tasks/{task_id}")
    assert "ada: 1, 1" in page.text
    assert "one: ada, objectives 2 and 1, constraint 1" in page.text
    assert "ada: 2, 1" in page.text
    assert "Next design: mina" in page.text
    assert 'id="search-observation-name"' in page.text
    assert 'id="search-constraint"' in page.text
    assert "Recommend a design" in page.text

    submitted = client.post(
        f"/tasks/{task_id}/search-observations",
        data={
            "name": "three",
            "design": "nora",
            "first": "1",
            "second": "1",
            "constraint": "1",
        },
        follow_redirects=True,
    )
    assert "three: nora, objectives 1 and 1, constraint 1" in submitted.text
    assert "Next design" not in submitted.text
    assert "In Progress" in submitted.text

    listed = client.get("/api/tasks")
    assert isinstance(listed.json(), list)
    assert listed.json()[0]["title"] == "Add export"
