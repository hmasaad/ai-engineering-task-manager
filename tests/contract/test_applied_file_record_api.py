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


def test_omitted_file_and_engineer_command_write_nothing(file_client):
    client, root = file_client
    task_id = _in_progress(client)
    assistant = client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={"project": "billing", "class": "ordinary", "what_changed": "Rename the export label"},
    )
    assert assistant.status_code == 200
    change = assistant.json()["implementation_changes"][0]
    assert change["recorded_by"] == "assistant"
    assert change["file"] is None
    engineer = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={
            "what_changed": "Note the date",
            "class": "ordinary",
            "project": "billing",
            "file": "notes/label.txt",
            "file_text": "Export",
        },
    )
    assert engineer.status_code == 200
    saved = engineer.json()["implementation_changes"][1]
    assert saved["recorded_by"] == "engineer"
    assert saved["file"] is None
    assert not (root / "billing" / "notes" / "label.txt").exists()


def test_parent_does_not_list_a_subtask_file(file_client):
    client, _root = file_client
    parent_id = _in_progress(client)
    child_id = client.post(
        f"/api/tasks/{parent_id}/subtasks", json={"title": "Write the checklist"}
    ).json()["id"]
    client.patch(f"/api/tasks/{child_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{child_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{child_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{child_id}/transitions", json={"action": "start"})
    recorded = client.post(
        f"/api/tasks/{child_id}/assistant-changes",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Rename the export label",
            "file": "notes/label.txt",
            "file_text": "Export",
        },
    )
    assert recorded.status_code == 200
    assert client.get(f"/api/tasks/{parent_id}").json()["implementation_changes"] == []
    assert client.get(f"/api/tasks/{child_id}").json()["implementation_changes"][0]["file"]["path"] == (
        "notes/label.txt"
    )
