import pytest
from fastapi.testclient import TestClient

from task_manager.web.app import create_app
from task_manager.workspace import Workspace

LABEL = "tests/test_label.py::test_label"


@pytest.fixture
def test_run_client(tmp_path, clock):
    root = tmp_path / "projects"
    tests = root / "billing" / "tests"
    tests.mkdir(parents=True)
    (tests / "test_label.py").write_text(
        "def test_label():\n    assert True\n",
        encoding="utf-8",
    )
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    application = create_app(workspace)
    with TestClient(application) as test_client:
        yield test_client
    workspace.close()


def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_run_one_ordinary_test(test_run_client):
    client = test_run_client
    task_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/test-runs",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Run the label test",
            "test": LABEL,
            "assistant_name": "Someone",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    change = body["implementation_changes"][0]
    assert body["status"] == "In Progress"
    assert change["outcome"] == "Carried out"
    assert change["assistant_name"] == "Guide"
    assert change["test"]["path"] == LABEL
    assert change["test"]["result"] == "Passed"
    assert client.get("/api/requirements").json() == []
    blank = client.post(
        f"/api/tasks/{task_id}/test-runs",
        json={"project": "billing", "class": "ordinary", "what_changed": "Run it", "test": "  "},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name the test this change runs."


def test_status_comes_before_a_blank_project(client):
    draft = client.post("/api/tasks", json={"title": "Draft"}).json()["id"]
    status = client.post(
        f"/api/tasks/{draft}/test-runs",
        json={"project": "  ", "class": "ordinary", "what_changed": "Run it", "test": LABEL},
    )
    assert status.status_code == 409
    assert status.json()["message"] == "The task must be In Progress."
