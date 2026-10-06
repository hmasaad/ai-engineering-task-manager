def test_record_and_supersede(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    blank = client.post(
        f"/api/tasks/{task_id}/decisions",
        json={"statement": "Use one file", "rationale": "   "},
    )
    assert blank.status_code == 400
    assert blank.json()["refused"] is True

    first = client.post(
        f"/api/tasks/{task_id}/decisions",
        json={"statement": "Use JSON", "rationale": "Easy to read"},
    )
    assert first.status_code == 200
    first_id = first.json()["decisions"][0]["id"]
    second = client.post(
        f"/api/tasks/{task_id}/decisions",
        json={"statement": "Use one table", "rationale": "Fewer joins"},
    )
    second_id = second.json()["decisions"][1]["id"]
    third = client.post(
        f"/api/tasks/{task_id}/decisions",
        json={
            "statement": "Use SQLite",
            "rationale": "One file",
            "supersedes": [first_id, second_id],
        },
    )
    assert third.status_code == 200
    decisions = client.get(f"/api/tasks/{task_id}").json()["decisions"]
    assert [item["statement"] for item in decisions] == ["Use JSON", "Use one table", "Use SQLite"]
    assert decisions[2]["supersedes"] == [first_id, second_id]


def test_cannot_supersede_a_decision_on_another_task(client):
    first = client.post("/api/tasks", json={"title": "First"}).json()["id"]
    other = client.post("/api/tasks", json={"title": "Other"}).json()["id"]
    other_decision = client.post(
        f"/api/tasks/{other}/decisions",
        json={"statement": "Theirs", "rationale": "Different task"},
    ).json()["decisions"][0]["id"]
    refused = client.post(
        f"/api/tasks/{first}/decisions",
        json={"statement": "Ours", "rationale": "Should fail", "supersedes": [other_decision]},
    )
    assert refused.status_code == 409
    assert "same task" in refused.json()["message"].lower()
