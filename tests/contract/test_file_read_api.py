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


def test_record_file_read(read_client):
    client, root = read_client
    task_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={
            "project": "billing",
            "file": "notes/label.txt",
            "assistant_name": "Someone",
            "engineer_name": "Someone",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    read = body["file_reads"][-1]
    assert body["status"] == "In Progress"
    assert body["implementation_changes"] == []
    assert read["project"] == "billing"
    assert read["path"] == "notes/label.txt"
    assert read["text"] == "Export"
    assert read["assistant_name"] == "Guide"
    assert (root / "billing" / "notes" / "label.txt").read_text(encoding="utf-8") == "Export"

    blank = client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "   ", "file": "notes/label.txt"},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name the project this change is for."
    missing_project = client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "missing", "file": "notes/label.txt"},
    )
    assert missing_project.status_code == 400
    assert missing_project.json()["message"] == "The project must already exist."
    blank_file = client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "billing", "file": "   "},
    )
    assert blank_file.status_code == 400
    assert blank_file.json()["message"] == "Name the file this change reads."
    outside = client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "billing", "file": "../outside.txt"},
    )
    assert outside.status_code == 409
    assert outside.json()["message"] == "The file must stay inside the named project."
    assert outside.json()["refused"] is True
    missing_file = client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "billing", "file": "notes/missing.txt"},
    )
    assert missing_file.status_code == 400
    assert missing_file.json()["message"] == "The file must already exist."
    (root / "billing" / "notes" / "binary.txt").write_bytes(b"\xff")
    not_text = client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "billing", "file": "notes/binary.txt"},
    )
    assert not_text.status_code == 400
    assert not_text.json()["message"] == "The file is not text."
    wrong = client.post(f"/api/tasks/{task_id}/file-reads", json={"stopped": "nope"})
    assert wrong.status_code == 400
    assert wrong.json()["message"] == (
        "The request is missing a required field or has the wrong shape."
    )
    unknown = client.post(
        "/api/tasks/9999/file-reads",
        json={"project": "billing", "file": "notes/label.txt"},
    )
    assert unknown.status_code == 404
    assert unknown.json()["message"] == "Task not found."
    draft = client.post("/api/tasks", json={"title": "Still a draft"}).json()["id"]
    refused = client.post(
        f"/api/tasks/{draft}/file-reads",
        json={"project": "   ", "file": "   "},
    )
    assert refused.status_code == 409
    assert refused.json()["message"] == "The task must be In Progress."
    assert (root / "billing" / "notes" / "label.txt").read_text(encoding="utf-8") == "Export"
    assert len(client.get(f"/api/tasks/{task_id}").json()["file_reads"]) == 1
