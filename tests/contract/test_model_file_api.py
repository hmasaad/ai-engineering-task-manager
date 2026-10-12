import pytest
from fastapi.testclient import TestClient

from task_manager.model import ScriptedModel
from task_manager.web.app import create_app
from task_manager.workspace import Workspace


@pytest.fixture
def model_client(tmp_path, clock):
    root = tmp_path / "projects"
    notes = root / "billing" / "notes"
    notes.mkdir(parents=True)
    (notes / "label.txt").write_text("Export", encoding="utf-8")
    model = ScriptedModel("Guide-model", "From the model")
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root, model)
    application = create_app(workspace)
    with TestClient(application) as test_client:
        yield test_client, root, model
    workspace.close()


def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    client.post(
        f"/api/tasks/{task_id}/file-reads",
        json={"project": "billing", "file": "notes/label.txt"},
    )
    return task_id


def test_record_model_file(model_client):
    client, root, model = model_client
    task_id = _in_progress(client)
    read_id = client.get(f"/api/tasks/{task_id}").json()["file_reads"][0]["id"]
    recorded = client.post(
        f"/api/tasks/{task_id}/model-files",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Propose the export label",
            "file": "notes/proposed.txt",
            "file_read_id": read_id,
            "model_name": "Someone",
            "assistant_name": "Someone",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    change = body["implementation_changes"][-1]
    assert body["status"] == "In Progress"
    assert change["model"]["name"] == "Guide-model"
    assert change["model"]["output"] == "From the model"
    assert change["file"]["text"] == "From the model"
    assert change["assistant_name"] == "Guide"
    assert (root / "billing" / "notes" / "proposed.txt").read_text(encoding="utf-8") == "From the model"
    assert len(model.prompts) == 1

    missing_read = client.post(
        f"/api/tasks/{task_id}/model-files",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Propose the export label",
            "file": "notes/other.txt",
        },
    )
    assert missing_read.status_code == 400
    assert missing_read.json()["message"] == "Choose the file read this change uses."
    unknown = client.post(
        f"/api/tasks/{task_id}/model-files",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Propose the export label",
            "file": "notes/other.txt",
            "file_read_id": 9999,
        },
    )
    assert unknown.status_code == 404
    assert unknown.json()["message"] == "File read not found."
    wrong = client.post(f"/api/tasks/{task_id}/model-files", json={"file_read_id": "nope"})
    assert wrong.status_code == 400
    assert wrong.json()["message"] == (
        "The request is missing a required field or has the wrong shape."
    )
    assert len(model.prompts) == 1
    plain = client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Rename the export label",
            "file": "notes/hand.txt",
            "file_text": "By hand",
        },
    )
    assert plain.status_code == 200
    assert plain.json()["implementation_changes"][-1]["model"] is None
    assert len(model.prompts) == 1
