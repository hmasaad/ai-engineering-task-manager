import hashlib
import subprocess
from pathlib import Path

from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def _started(workspace, title):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Keep the label in the record")
    with_criterion = workspace.add_criterion(created["id"], "The label is recorded")
    ready = workspace.transition(created["id"], "mark_ready")
    started = workspace.transition(ready["id"], "start")
    return started, int(with_criterion["criteria"][0]["id"])


def test_two_workspaces_stay_separate_and_a_restart_keeps_the_evidence(tmp_path, clock):
    path_a = tmp_path / "a" / "workspace.db"
    path_b = tmp_path / "b" / "workspace.db"
    workspace_a = Workspace(path_a, clock, "Ada", "Guide", tmp_path)
    workspace_b = Workspace(path_b, clock, "Bea", "Guide", tmp_path)
    try:
        started, criterion_id = _started(workspace_a, "Record the label")
        verified = workspace_a.verify_criterion(
            started["id"], criterion_id, "The label text was read.", "pass"
        )
        decided = workspace_a.add_decision(
            started["id"], "Keep the recorded label", "The label was read."
        )
        assert verified["status"] == "In Progress"
        assert workspace_b.list_tasks() == []
        assert workspace_b.list_requirements() == []
        missing = workspace_b.get_task(started["id"])
        assert isinstance(missing, Refusal)
        assert missing.message == "Task not found."
        other = workspace_b.create_task("A different label")
        assert other["title"] == "A different label"
        assert [task["title"] for task in workspace_a.list_tasks()] == ["Record the label"]
        assert decided["decisions"][0]["statement"] == "Keep the recorded label"
    finally:
        workspace_a.close()
        workspace_b.close()

    reopened = Workspace(path_a, clock, "Ada", "Guide", tmp_path)
    try:
        task = reopened.get_task(1)
        assert task["title"] == "Record the label"
        assert task["status"] == "In Progress"
        assert task["criteria"][0]["observation"] == "The label text was read."
        assert task["criteria"][0]["provider_name"] == "Ada"
        assert task["decisions"][0]["statement"] == "Keep the recorded label"
    finally:
        reopened.close()

    renamed = Workspace(path_a, clock, "Bea", "Guide", tmp_path)
    try:
        task = renamed.get_task(1)
        assert task["criteria"][0]["observation"] == "The label text was read."
        assert task["criteria"][0]["provider_name"] == "Ada"
        assert task["decisions"][0]["statement"] == "Keep the recorded label"
    finally:
        renamed.close()


def _git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )


def _snapshot(root: Path) -> dict[str, str]:
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            files[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def test_task_records_leave_the_repository_unchanged(tmp_path, clock, monkeypatch):
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
    before = _snapshot(billing)
    head = _git(billing, "rev-parse", "HEAD").stdout.strip()
    branch = _git(billing, "branch", "--show-current").stdout.strip()
    calls = []
    real_run = subprocess.run

    def spy(*args, **kwargs):
        command = args[0] if args else kwargs.get("args")
        calls.append([str(part) for part in command])
        return real_run(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", spy)
    workspace = Workspace(tmp_path / "a.db", clock, "Ada", "Guide", root)
    other = Workspace(tmp_path / "b.db", clock, "Bea", "Guide", root)
    try:
        started, criterion_id = _started(workspace, "Record the label")
        workspace.verify_criterion(started["id"], criterion_id, "The label text was read.", "pass")
        workspace.record_change(started["id"], "Noted the label", "ordinary", project="billing")
        workspace.record_assistant_change(started["id"], "billing", "ordinary", "Described the label", False)
        workspace.add_decision(started["id"], "Keep the recorded label", "The label was read.")
        workspace.record_requirement("The label stays recorded", "functional")
        workspace.get_task(started["id"])
        assert other.list_requirements() == []
        assert other.list_tasks() == []
    finally:
        workspace.close()
        other.close()
    assert calls == []
    assert _snapshot(billing) == before
    assert _git(billing, "rev-parse", "HEAD").stdout.strip() == head
    assert _git(billing, "branch", "--show-current").stdout.strip() == branch
    assert label.read_text(encoding="utf-8") == "Export\n"
