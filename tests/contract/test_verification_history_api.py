def _in_progress(client) -> tuple[int, int, int, int]:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    first = client.post(
        f"/api/tasks/{task_id}/criteria", json={"text": "The file contains the goal"}
    ).json()["criteria"][0]["id"]
    second = client.post(
        f"/api/tasks/{task_id}/criteria", json={"text": "The export lists the date"}
    ).json()["criteria"][1]["id"]
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    change_id = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={"what_changed": "Rename the export label", "class": "ordinary"},
    ).json()["implementation_changes"][0]["id"]
    return task_id, change_id, first, second


def test_later_checks_stay_and_passing_check_requires_every_current_result(client):
    task_id, change_id, first_id, second_id = _in_progress(client)
    path = f"/api/tasks/{task_id}/implementation-changes/{change_id}/checks"
    first = client.post(
        path, json={"criterion_id": first_id, "evidence": "The label was still old", "result": "Failed"}
    )
    assert first.status_code == 200
    earlier = first.json()["implementation_changes"][0]["checks"][0]
    second = client.post(
        path, json={"criterion_id": first_id, "evidence": "The label now reads Export", "result": "Passed"}
    )
    checks = second.json()["implementation_changes"][0]["checks"]
    assert checks[0]["evidence"] == earlier["evidence"]
    assert checks[0]["result"] == "Failed"
    assert [item["result"] for item in checks] == ["Failed", "Passed"]
    assert second.json()["implementation_changes"][0]["passing_check"] is True

    client.post(path, json={"criterion_id": second_id, "evidence": "The date is missing", "result": "Failed"})
    detail = client.get(f"/api/tasks/{task_id}").json()
    assert detail["implementation_changes"][0]["passing_check"] is False

    client.post(path, json={"criterion_id": second_id, "evidence": "The date is on the page", "result": "Passed"})
    detail = client.get(f"/api/tasks/{task_id}").json()
    assert detail["implementation_changes"][0]["passing_check"] is True
    assert detail["implementation_changes"][0]["checks"][0]["evidence"] == "The label was still old"

    rewritten = client.patch(path, json={"evidence": "rewritten", "result": "Failed"})
    removed = client.delete(f"{path}/{earlier['id']}")
    assert rewritten.status_code in (404, 405)
    assert removed.status_code in (404, 405)
    again = client.get(f"/api/tasks/{task_id}").json()
    assert again["implementation_changes"][0]["checks"][0]["evidence"] == "The label was still old"
