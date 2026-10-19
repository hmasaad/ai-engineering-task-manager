import pytest
from fastapi.testclient import TestClient

from task_manager.web.app import create_app
from task_manager.workspace import Workspace


@pytest.fixture
def execution_client(tmp_path, clock):
    root = tmp_path / "projects"
    notes = root / "billing"
    notes.mkdir(parents=True)
    (notes / "note.txt").write_text("hello\n", encoding="utf-8")
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    application = create_app(workspace)
    with TestClient(application) as test_client:
        yield test_client, notes
    workspace.close()


def _in_progress(client, title="Add export"):
    task_id = client.post("/api/tasks", json={"title": title}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_the_page_keeps_one_named_execution(execution_client):
    client, notes = execution_client
    task_id = _in_progress(client)
    empty = client.get(f"/tasks/{task_id}")
    assert "No named executions yet." in empty.text
    recorded = client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "billing", "file": "note.txt", "execution": "once"},
    )
    assert recorded.status_code == 200
    assert recorded.json()["executions"] == [
        {"name": "once", "action": "read", "path": "note.txt"}
    ]
    shown = client.get(f"/tasks/{task_id}")
    assert 'id="command-executions"' in shown.text
    assert "once" in shown.text
    assert "Read a file" in shown.text
    assert "note.txt" in shown.text
    notes.joinpath("note.txt").unlink()
    repeated = client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "billing", "file": "other.txt", "execution": "once"},
    )
    assert repeated.status_code == 200
    assert [item["path"] for item in repeated.json()["file_reads"]] == ["note.txt"]
    page = client.post(
        f"/tasks/{task_id}/file-reads",
        data={"project": "billing", "file": "other.txt", "execution": "once"},
        follow_redirects=True,
    )
    assert "No named executions yet." not in page.text
    assert "once" in page.text
    detail = client.get(f"/api/tasks/{task_id}")
    assert [item["path"] for item in detail.json()["file_reads"]] == ["note.txt"]
    created = client.post(
        f"/api/tasks/{task_id}/folders",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Add the notes folder",
            "folder": "notes",
            "execution": "notes",
        },
    )
    assert created.status_code == 200
    assert created.json()["executions"][-1] == {
        "name": "notes",
        "action": "folder",
        "path": "notes",
    }
    notes.joinpath("notes").rmdir()
    folder_page = client.post(
        f"/tasks/{task_id}/folders",
        data={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Add another folder",
            "folder": "other",
            "execution": "notes",
        },
        follow_redirects=True,
    )
    assert "Create a folder" in folder_page.text
    assert not notes.joinpath("notes").exists()
    assert not notes.joinpath("other").exists()
    assert isinstance(client.get("/api/tasks").json(), list)
