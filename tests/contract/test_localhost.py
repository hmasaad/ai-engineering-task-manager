from task_manager.__main__ import HOST, main


def test_server_binds_to_localhost_only(tmp_path):
    assert HOST == "127.0.0.1"
    code = main(
        [
            "--workspace",
            str(tmp_path / "workspace.db"),
            "--host",
            "0.0.0.0",
        ]
    )
    assert code == 2


def test_verify_request_cannot_set_provider(client):
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    created = client.post(
        f"/api/tasks/{task_id}/criteria",
        json={"text": "The file contains the goal"},
    ).json()
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    criterion_id = created["criteria"][0]["id"]
    response = client.post(
        f"/api/tasks/{task_id}/criteria/{criterion_id}/verify",
        json={
            "observation": "Seen",
            "pass_result": "pass",
            "provider_name": "Not Ada",
        },
    )
    assert response.json()["criteria"][0]["provider_name"] == "Ada"
