import subprocess

from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def _git(repo, *args, check=True):
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        capture_output=True,
        text=True,
    )


def _started(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _prepare(root):
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
    return billing, bare


def _open(tmp_path, clock, monkeypatch):
    root = tmp_path / "projects"
    billing, bare = _prepare(root)
    calls = []

    def fake(_project_dir, args):
        calls.append(list(args))
        return subprocess.CompletedProcess(args, 0, "https://example.com/pull/7\n", "")

    monkeypatch.setattr("task_manager.domain.pull_request._gh", fake)
    store = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    return store, billing, bare, calls


def _published(bare, branch):
    result = _git(bare, "rev-parse", "--verify", f"refs/heads/{branch}", check=False)
    return result.returncode == 0


def test_a_pull_request_waits_until_the_engineer_approves(tmp_path, clock, monkeypatch):
    workspace, billing, bare, calls = _open(tmp_path, clock, monkeypatch)
    try:
        started = _started(workspace)
        waiting = workspace.record_pull_request(
            started["id"], " billing ", "ordinary", " Open the label pull request ", False, " feature "
        )
        change = waiting["implementation_changes"][0]
        assert waiting["status"] == "In Progress"
        assert change["class"] == "consequential"
        assert change["outcome"] == "Awaiting approval"
        assert change["assistant_name"] == "Guide"
        assert change["stopped"] is False
        assert change["pull_request"] == {"branch": "feature", "base": "main", "url": None}
        assert calls == []
        assert not _published(bare, "feature")
        assert workspace.list_requirements() == []
        refused = workspace.approve_change(started["id"], change["id"], "Seen", actor="assistant")
        assert refused.message == "The assistant cannot approve a change."
        assert calls == []
        assert not _published(bare, "feature")
        approved = workspace.approve_change(started["id"], change["id"], "The branch is still feature")
        carried = approved["implementation_changes"][0]
        assert carried["outcome"] == "Carried out"
        assert carried["pull_request"]["url"] == "https://example.com/pull/7"
        assert calls == [
            [
                "pr",
                "create",
                "--base",
                "main",
                "--head",
                "feature",
                "--title",
                "Open the label pull request",
                "--body",
                "Open the label pull request",
            ]
        ]
        assert _published(bare, "feature")
        again = workspace.get_task(started["id"])
        assert again["implementation_changes"][0]["pull_request"]["url"] == "https://example.com/pull/7"
        assert calls == [
            [
                "pr",
                "create",
                "--base",
                "main",
                "--head",
                "feature",
                "--title",
                "Open the label pull request",
                "--body",
                "Open the label pull request",
            ]
        ]
    finally:
        workspace.close()


def test_another_branch_stays_unpublished(tmp_path, clock, monkeypatch):
    workspace, billing, bare, _calls = _open(tmp_path, clock, monkeypatch)
    try:
        _git(billing, "checkout", "-b", "other")
        (billing / "other.txt").write_text("Other\n", encoding="utf-8")
        _git(billing, "add", "other.txt")
        _git(billing, "commit", "-m", "Add other")
        _git(billing, "checkout", "feature")
        started = _started(workspace)
        waiting = workspace.record_pull_request(
            started["id"], "billing", "consequential", "Open the label pull request", False, "feature"
        )
        workspace.approve_change(started["id"], waiting["implementation_changes"][0]["id"], "Still feature")
        assert _published(bare, "feature")
        assert not _published(bare, "other")
    finally:
        workspace.close()


def test_decline_a_missing_branch_and_a_hook_do_not_publish(tmp_path, clock, monkeypatch):
    workspace, billing, bare, calls = _open(tmp_path, clock, monkeypatch)
    try:
        started = _started(workspace)
        waiting = workspace.record_pull_request(
            started["id"], "billing", "ordinary", "Open the label pull request", False, "feature"
        )
        change_id = waiting["implementation_changes"][0]["id"]
        declined = workspace.mark_change_not_carried_out(started["id"], change_id, "Keep it local")
        assert declined["implementation_changes"][0]["outcome"] == "Not carried out"
        assert calls == []
        assert not _published(bare, "feature")
        replacement = workspace.record_pull_request(
            started["id"], "billing", "ordinary", "Open it later", False, "feature"
        )
        second = replacement["implementation_changes"][1]["id"]
        _git(billing, "checkout", "main")
        _git(billing, "branch", "-D", "feature")
        mismatched = workspace.approve_change(started["id"], second, "The branch should still exist")
        assert isinstance(mismatched, Refusal)
        assert mismatched.message == "The pull request no longer matches the branch this change was proposed against."
        assert not _published(bare, "feature")
        _git(billing, "checkout", "-b", "feature")
        hook = billing / ".git" / "hooks" / "pre-push"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
        hooked = workspace.record_pull_request(
            started["id"], "billing", "ordinary", "Open after the hook", False, "feature"
        )
        third = hooked["implementation_changes"][2]["id"]
        refused = workspace.approve_change(started["id"], third, "The hook should refuse this")
        assert refused.message == "The pull request was refused."
        assert calls == []
        assert not _published(bare, "feature")
        assert workspace.get_task(started["id"])["implementation_changes"][2]["outcome"] == "Awaiting approval"
    finally:
        workspace.close()


def test_a_blank_missing_base_and_unready_project_are_refused(tmp_path, clock, monkeypatch):
    workspace, billing, _bare, calls = _open(tmp_path, clock, monkeypatch)
    root = billing.parent
    try:
        started = _started(workspace)
        blank = workspace.record_pull_request(
            started["id"], "billing", "ordinary", "Open it", False, "  "
        )
        assert isinstance(blank, Refusal)
        assert blank.message == "Name the branch this change proposes."
        missing = workspace.record_pull_request(
            started["id"], "billing", "ordinary", "Open it", False, "missing"
        )
        assert missing.message == "The branch must already exist."
        escaped = workspace.record_pull_request(
            started["id"], "billing", "ordinary", "Open it", False, "../main"
        )
        assert escaped.message == "Name the branch this change proposes."
        base = workspace.record_pull_request(
            started["id"], "billing", "ordinary", "Open it", False, "main"
        )
        assert base.message == "Choose a branch other than the base branch."
        plain = root / "plain"
        plain.mkdir()
        (plain / "label.txt").write_text("Export\n", encoding="utf-8")
        not_repo = workspace.record_pull_request(
            started["id"], "plain", "ordinary", "Open it", False, "feature"
        )
        assert not_repo.message == "The project must already be a repository."
        local = root / "local"
        local.mkdir()
        _git(local, "init", "-b", "main")
        _git(local, "config", "user.email", "ada@example.com")
        _git(local, "config", "user.name", "Ada")
        (local / "label.txt").write_text("Export\n", encoding="utf-8")
        _git(local, "add", "label.txt")
        _git(local, "commit", "-m", "Add label")
        _git(local, "checkout", "-b", "feature")
        no_remote = workspace.record_pull_request(
            started["id"], "local", "ordinary", "Open it", False, "feature"
        )
        assert no_remote.message == "The project must already have a remote."
        assert workspace.get_task(started["id"])["implementation_changes"] == []
        assert calls == []
        assert not _published(root / "bare.git", "feature")
    finally:
        workspace.close()


def test_a_stopped_request_does_not_publish(tmp_path, clock, monkeypatch):
    workspace, _billing, bare, calls = _open(tmp_path, clock, monkeypatch)
    try:
        started = _started(workspace)
        waiting = workspace.record_pull_request(
            started["id"], "billing", "ordinary", "Open the label pull request", True, "feature"
        )
        change = waiting["implementation_changes"][0]
        assert change["class"] == "consequential"
        assert change["stopped"] is True
        assert change["outcome"] == "Awaiting approval"
        assert change["pull_request"]["url"] is None
        assert calls == []
        assert not _published(bare, "feature")
    finally:
        workspace.close()
