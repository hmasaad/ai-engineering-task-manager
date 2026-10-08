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


def test_older_commands_do_not_read_a_file(read_client):
    client, root = read_client
    task_id = _in_progress(client)
    before = (root / "billing" / "notes" / "label.txt").read_bytes()
    assistant = client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Rename the export label",
        },
    )
    assert assistant.status_code == 200
    assert assistant.json()["file_reads"] == []
    engineer = client.post(
        f"/api/tasks/{task_id}/implementation-changes",
        json={
            "what_changed": "Note the date",
            "class": "ordinary",
            "project": "billing",
            "file": "notes/label.txt",
        },
    )
    assert engineer.status_code == 200
    assert engineer.json()["file_reads"] == []
    assert (root / "billing" / "notes" / "label.txt").read_bytes() == before
    read = client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "billing", "file": "notes/label.txt"},
    )
    assert read.status_code == 200
    assert len(read.json()["implementation_changes"]) == len(
        engineer.json()["implementation_changes"]
    )
    assert read.json()["file_reads"][0]["text"] == "Export"
