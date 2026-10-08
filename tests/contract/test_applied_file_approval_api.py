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


def test_replacement_waits_and_engineer_approval_writes(file_client):
    client, root = file_client
    task_id = _in_progress(client)
    target = root / "billing" / "notes" / "label.txt"
    target.write_text("Old", encoding="utf-8")
    recorded = client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Rename the export label",
            "file": "notes/label.txt",
            "file_text": "Export",
        },
    )
    assert recorded.status_code == 200
    change = recorded.json()["implementation_changes"][0]
    assert change["class"] == "consequential"
    assert change["outcome"] == "Awaiting approval"
    change_id = change["id"]
    assistant = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/approve",
        json={"evidence": "The page shows the new name", "actor": "assistant"},
    )
    assert assistant.status_code == 409
    assert assistant.json()["message"] == "The assistant cannot approve a change."
    target.write_text("Newer", encoding="utf-8")
    mismatch = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/approve",
        json={"evidence": "The page shows the new name"},
    )
    assert mismatch.status_code == 409
    assert mismatch.json()["message"] == (
        "The file no longer matches the text this change was proposed against."
    )
    assert target.read_text(encoding="utf-8") == "Newer"
    target.write_text("Old", encoding="utf-8")
    approved = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change_id}/approve",
        json={"evidence": "The page shows the new name"},
    )
    assert approved.status_code == 200
    carried = approved.json()["implementation_changes"][0]
    assert carried["outcome"] == "Carried out"
    assert carried["approval"]["engineer_name"] == "Ada"
    assert target.read_text(encoding="utf-8") == "Export"


def test_stopped_and_consequential_do_not_create_the_file(file_client):
    client, root = file_client
    task_id = _in_progress(client)
    stopped = client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Hold the note",
            "stopped": True,
            "file": "notes/held.txt",
            "file_text": "Export",
        },
    )
    assert stopped.status_code == 200
    assert stopped.json()["implementation_changes"][0]["class"] == "consequential"
    assert stopped.json()["implementation_changes"][0]["stopped"] is True
    assert not (root / "billing" / "notes" / "held.txt").exists()
    consequential = client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={
            "project": "billing",
            "class": "consequential",
            "what_changed": "Add the other note",
            "file": "notes/other.txt",
            "file_text": "Export",
        },
    )
    assert consequential.status_code == 200
    assert not (root / "billing" / "notes" / "other.txt").exists()
