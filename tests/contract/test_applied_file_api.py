import pytest
from fastapi.testclient import TestClient

from task_manager.web.app import create_app
from task_manager.workspace import Workspace


@pytest.fixture
def file_client(tmp_path, clock):
    root = tmp_path / "projects"
    (root / "billing" / "notes").mkdir(parents=True)
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    application = create_app(workspace)
    with TestClient(application) as test_client:
        yield test_client, root
    workspace.close()


def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_record_ordinary_file(file_client):
    client, root = file_client
    task_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Rename the export label",
            "file": "notes/label.txt",
            "file_text": "Export",
            "assistant_name": "Someone",
            "engineer_name": "Someone",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    change = body["implementation_changes"][-1]
    assert body["status"] == "In Progress"
    assert change["file"]["text"] == "Export"
    assert change["assistant_name"] == "Guide"
    assert change["engineer_name"] == "Ada"
    assert (root / "billing" / "notes" / "label.txt").read_text(encoding="utf-8") == "Export"

    blank = client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={"project": "billing", "class": "ordinary", "what_changed": "Again", "file": "   "},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name the file this change writes."
    wrong = client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={"stopped": "nope"},
    )
    assert wrong.status_code == 400
    assert wrong.json()["message"] == (
        "The request is missing a required field or has the wrong shape."
    )
