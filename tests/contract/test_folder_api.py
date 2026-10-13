import pytest
from fastapi.testclient import TestClient

from task_manager.web.app import create_app
from task_manager.workspace import Workspace


@pytest.fixture
def folder_client(tmp_path, clock):
    root = tmp_path / "projects"
    (root / "billing").mkdir(parents=True)
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    application = create_app(workspace)
    with TestClient(application) as test_client:
        yield test_client, root
    workspace.close()


def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_create_one_ordinary_folder(folder_client):
    client, root = folder_client
    task_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/folders",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Add the notes folder",
            "folder": "notes",
            "assistant_name": "Someone",
        },
    )
    assert recorded.status_code == 200
    change = recorded.json()["implementation_changes"][0]
    assert change["outcome"] == "Carried out"
    assert change["folder"] == {"path": "notes"}
    assert change["assistant_name"] == "Guide"
    assert (root / "billing" / "notes").is_dir()
    blank = client.post(
        f"/api/tasks/{task_id}/folders",
        json={"project": "billing", "class": "ordinary", "what_changed": "Add notes", "folder": "  "},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name the folder this change creates."


def test_status_comes_before_a_blank_project(client):
    draft = client.post("/api/tasks", json={"title": "Draft"}).json()["id"]
    status = client.post(
        f"/api/tasks/{draft}/folders",
        json={"project": "  ", "class": "ordinary", "what_changed": "Add notes", "folder": "notes"},
    )
    assert status.status_code == 409
    assert status.json()["message"] == "The task must be In Progress."
