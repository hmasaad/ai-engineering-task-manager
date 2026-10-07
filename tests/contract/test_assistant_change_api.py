import pytest
from fastapi.testclient import TestClient

from task_manager.web.app import create_app
from task_manager.workspace import Workspace


@pytest.fixture
def guide_client(tmp_path, clock):
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide")
    application = create_app(workspace)
    with TestClient(application) as test_client:
        yield test_client
    workspace.close()


def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The file contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_record_ordinary_assistant_change(guide_client):
    task_id = _in_progress(guide_client)
    recorded = guide_client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Rename the export label",
            "assistant_name": "Someone",
            "engineer_name": "Someone",
            "recorded_at": "1999-01-01T00:00:00Z",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    change = body["implementation_changes"][0]
    assert body["status"] == "In Progress"
    assert change["project"] == "billing"
    assert change["class"] == "ordinary"
    assert change["outcome"] == "Carried out"
    assert change["assistant_name"] == "Guide"
    assert change["engineer_name"] == "Ada"
    assert change["recorded_by"] == "assistant"
    assert change["stopped"] is False
    assert change["what_changed"] == "Rename the export label"


def test_blank_project_account_class_and_wrong_shape(guide_client):
    task_id = _in_progress(guide_client)
    blank_project = guide_client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={"project": "   ", "class": "ordinary", "what_changed": "Rename the export label"},
    )
    assert blank_project.status_code == 400
    assert blank_project.json()["message"] == "Name the project this change is for."

    blank_account = guide_client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={"project": "billing", "class": "ordinary", "what_changed": "   "},
    )
    assert blank_account.status_code == 400
    assert blank_account.json()["message"] == "An account of what changed is required."

    missing_class = guide_client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={"project": "billing", "what_changed": "Rename the export label"},
    )
    assert missing_class.status_code == 400
    assert missing_class.json()["message"] == "Choose ordinary or consequential."

    wrong_shape = guide_client.post(
        f"/api/tasks/{task_id}/assistant-changes",
        json={"stopped": "nope"},
    )
    assert wrong_shape.status_code == 400
    assert wrong_shape.json()["message"] == (
        "The request is missing a required field or has the wrong shape."
    )
    assert guide_client.get(f"/api/tasks/{task_id}").json()["implementation_changes"] == []
