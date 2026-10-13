import subprocess

import pytest
from fastapi.testclient import TestClient

from task_manager.web.app import create_app
from task_manager.workspace import Workspace


def _git(repo, *args):
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _client(tmp_path, clock):
    root = tmp_path / "projects"
    billing = root / "billing"
    billing.mkdir(parents=True)
    _git(billing, "init", "-b", "main")
    _git(billing, "config", "user.email", "ada@example.com")
    _git(billing, "config", "user.name", "Ada")
    label = billing / "label.txt"
    label.write_text("Old\n", encoding="utf-8")
    _git(billing, "add", "label.txt")
    _git(billing, "commit", "-m", "Add label")
    label.write_text("Export\n", encoding="utf-8")
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    application = create_app(workspace)
    return workspace, application, billing


@pytest.fixture
def branch_client(tmp_path, clock):
    workspace, application, billing = _client(tmp_path, clock)
    with TestClient(application) as test_client:
        yield test_client, billing
    workspace.close()


def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_create_one_branch_after_approval(branch_client):
    client, billing = branch_client
    task_id = _in_progress(client)
    before = int(_git(billing, "rev-list", "--count", "HEAD").stdout.strip())
    recorded = client.post(
        f"/api/tasks/{task_id}/branches",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Create the feature branch",
            "branch": "feature",
            "assistant_name": "Someone",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    change = body["implementation_changes"][0]
    assert body["status"] == "In Progress"
    assert change["class"] == "consequential"
    assert change["outcome"] == "Awaiting approval"
    assert change["assistant_name"] == "Guide"
    assert change["created_branch"]["name"] == "feature"
    assert change["created_branch"]["checked_out"] is False
    assert _git(billing, "branch", "--show-current").stdout.strip() == "main"
    assert client.get("/api/requirements").json() == []
    approved = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change['id']}/approve",
        json={"evidence": "The commit is still the start"},
    )
    assert approved.status_code == 200
    carried = approved.json()["implementation_changes"][0]
    assert carried["outcome"] == "Carried out"
    assert carried["created_branch"]["checked_out"] is True
    assert _git(billing, "branch", "--show-current").stdout.strip() == "feature"
    assert int(_git(billing, "rev-list", "--count", "HEAD").stdout.strip()) == before
    blank = client.post(
        f"/api/tasks/{task_id}/branches",
        json={"project": "billing", "class": "ordinary", "what_changed": "Create it", "branch": "  "},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name the branch this change creates."


def test_status_comes_before_a_blank_project(client):
    draft = client.post("/api/tasks", json={"title": "Draft"}).json()["id"]
    status = client.post(
        f"/api/tasks/{draft}/branches",
        json={"project": "  ", "class": "ordinary", "what_changed": "Create it", "branch": "feature"},
    )
    assert status.status_code == 409
    assert status.json()["message"] == "The task must be In Progress."
