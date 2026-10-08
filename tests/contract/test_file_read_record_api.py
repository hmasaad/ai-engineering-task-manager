import pytest
from fastapi.testclient import TestClient

from task_manager.web.app import create_app
from task_manager.workspace import Workspace


@pytest.fixture
def read_client(tmp_path, clock):
    root = tmp_path / "projects"
    notes = root / "billing" / "notes"
    notes.mkdir(parents=True)
    (notes / "label.txt").write_text("Export", encoding="utf-8")
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


def test_a_later_read_keeps_the_first_text(read_client):
    client, root = read_client
    task_id = _in_progress(client)
    client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "billing", "file": "notes/label.txt"},
    )
    label = root / "billing" / "notes" / "label.txt"
    label.write_text("Newer", encoding="utf-8")
    opened = client.get(f"/api/tasks/{task_id}")
    assert opened.json()["file_reads"][0]["text"] == "Export"
    assert label.read_text(encoding="utf-8") == "Newer"
    again = client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "billing", "file": "notes/label.txt"},
    )
    assert [item["text"] for item in again.json()["file_reads"]] == ["Export", "Newer"]


def test_parent_does_not_list_a_subtask_read(read_client):
    client, _root = read_client
    parent_id = _in_progress(client)
    child_id = client.post(
        f"/api/tasks/{parent_id}/subtasks", json={"title": "Write the checklist"}
    ).json()["id"]
    client.patch(f"/api/tasks/{child_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{child_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{child_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{child_id}/transitions", json={"action": "start"})
    client.post(
        f"/api/tasks/{child_id}/file-reads",
        json={"project": "billing", "file": "notes/label.txt"},
    )
    assert client.get(f"/api/tasks/{parent_id}").json()["file_reads"] == []
    assert client.get(f"/api/tasks/{child_id}").json()["file_reads"][0]["path"] == "notes/label.txt"
