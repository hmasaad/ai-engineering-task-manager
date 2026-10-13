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


@pytest.fixture
def pull_client(tmp_path, clock, monkeypatch):
    root = tmp_path / "projects"
    bare = root / "bare.git"
    billing = root / "billing"
    bare.mkdir(parents=True)
    _git(bare, "init", "--bare", "-b", "main")
    billing.mkdir()
    _git(billing, "init", "-b", "main")
    _git(billing, "config", "user.email", "ada@example.com")
    _git(billing, "config", "user.name", "Ada")
    (billing / "label.txt").write_text("Old\n", encoding="utf-8")
    _git(billing, "add", "label.txt")
    _git(billing, "commit", "-m", "Add label")
    _git(billing, "remote", "add", "origin", str(bare))
    _git(billing, "push", "-u", "origin", "main")
    _git(billing, "remote", "set-head", "origin", "main")
    _git(billing, "checkout", "-b", "feature")
    (billing / "label.txt").write_text("Export\n", encoding="utf-8")
    _git(billing, "commit", "-am", "Update label")
    calls = []

    def fake(_project_dir, args):
        calls.append(list(args))
        return subprocess.CompletedProcess(args, 0, "https://example.com/pull/7\n", "")

    monkeypatch.setattr("task_manager.domain.pull_request._gh", fake)
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    application = create_app(workspace)
    with TestClient(application) as test_client:
        yield test_client, bare, calls
    workspace.close()


def _in_progress(client) -> int:
    task_id = client.post("/api/tasks", json={"title": "Add export"}).json()["id"]
    client.patch(f"/api/tasks/{task_id}", json={"goal": "Take the record"})
    client.post(f"/api/tasks/{task_id}/criteria", json={"text": "The export contains the goal"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "mark_ready"})
    client.post(f"/api/tasks/{task_id}/transitions", json={"action": "start"})
    return task_id


def test_open_one_pull_request_after_approval(pull_client):
    client, bare, calls = pull_client
    task_id = _in_progress(client)
    recorded = client.post(
        f"/api/tasks/{task_id}/pull-requests",
        json={
            "project": "billing",
            "class": "ordinary",
            "what_changed": "Open the label pull request",
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
    assert change["pull_request"] == {"branch": "feature", "base": "main", "url": None}
    assert calls == []
    unpublished = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/heads/feature"],
        cwd=bare,
        capture_output=True,
        text=True,
    )
    assert unpublished.returncode != 0
    assert client.get("/api/requirements").json() == []
    approved = client.post(
        f"/api/tasks/{task_id}/implementation-changes/{change['id']}/approve",
        json={"evidence": "The branch is still feature"},
    )
    assert approved.status_code == 200
    carried = approved.json()["implementation_changes"][0]
    assert carried["outcome"] == "Carried out"
    assert carried["pull_request"]["url"] == "https://example.com/pull/7"
    assert len(calls) == 1
    assert "--force" not in calls[0]
    published = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/heads/feature"],
        cwd=bare,
        check=True,
        capture_output=True,
        text=True,
    )
    assert published.stdout.strip()
    blank = client.post(
        f"/api/tasks/{task_id}/pull-requests",
        json={"project": "billing", "class": "ordinary", "what_changed": "Open it", "branch": "  "},
    )
    assert blank.status_code == 400
    assert blank.json()["message"] == "Name the branch this change proposes."


def test_status_comes_before_a_blank_project(client):
    draft = client.post("/api/tasks", json={"title": "Draft"}).json()["id"]
    status = client.post(
        f"/api/tasks/{draft}/pull-requests",
        json={"project": "  ", "class": "ordinary", "what_changed": "Open it", "branch": "feature"},
    )
    assert status.status_code == 409
    assert status.json()["message"] == "The task must be In Progress."
