import pytest
from fastapi.testclient import TestClient

from task_manager.web.app import create_app
from task_manager.workspace import Workspace


@pytest.fixture
def delete_client(tmp_path, clock):
    root = tmp_path / "projects"
    billing = root / "billing"
    billing.mkdir(parents=True)
    (billing / "label.txt").write_text("Export", encoding="utf-8")
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    application = create_app(workspace)
    with TestClient(application) as test_client:
        yield test_client, billing / "label.txt"
    workspace.close()


def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_delete_one_file_after_approval(delete_client):
    client, label = delete_client
    task_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/deletes",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Remove the old label",
            "file": "label.txt",
            "assistant_name": "Someone",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    change = body["implementation_changes"][0]
    assert body["status"] == "In Progress"
    assert change["class"] == "consequential"
    assert change["outcome"] == "Awaiting approval"
    assert change["assistant_name"] == "Guide"
    assert change["deleted_file"] == {"path": "label.txt", "text": "Export"}
    assert label.read_text() == "Export"
    assert client.get("/api/requirements").json() == []
    approved = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change['id']}/approve",
        json={"evidence": "The file is still Export"},
    )
    assert approved.status_code == 200
    assert approved.json()["implementation_changes"][0]["outcome"] == "Carried out"
    assert not label.exists()
    blank = client.post(
        f"/api/tasks/{task_id}/deletes",
        json={"project": "billing", "class": "ordinary", "what_changed": "Remove it", "file": "  "},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name the file this change deletes."


def test_status_comes_before_a_blank_project(client):
    draft = client.post("/api/tasks", json={"title": "Draft"}).json()["id"]
    status = client.post(
        f"/api/tasks/{draft}/deletes",
        json={"project": "  ", "class": "ordinary", "what_changed": "Remove it", "file": "label.txt"},
    )
    assert status.status_code == 409
    assert status.json()["message"] == "The task must be In Progress."
