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


def _prepare(billing):
    billing.mkdir(parents=True)
    _git(billing, "init", "-b", "main")
    _git(billing, "config", "user.email", "ada@example.com")
    _git(billing, "config", "user.name", "Ada")
    label = billing / "label.txt"
    label.write_text("Old\n", encoding="utf-8")
    _git(billing, "add", "label.txt")
    _git(billing, "commit", "-m", "Add label")
    label.write_text("Export\n", encoding="utf-8")
    return label


def _open(tmp_path, clock):
    root = tmp_path / "projects"
    label = _prepare(root / "billing")
    store = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    return store, root, label


def _current(repo):
    return _git(repo, "branch", "--show-current").stdout.strip()


def _branches(repo):
    return set(_git(repo, "branch", "--format=%(refname:short)").stdout.split())


def _count(repo):
    return int(_git(repo, "rev-list", "--count", "HEAD").stdout.strip())


def test_a_branch_waits_until_the_engineer_approves(tmp_path, clock):
    workspace, root, label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        started = _started(workspace)
        before = _count(billing)
        head = _git(billing, "rev-parse", "HEAD").stdout.strip()
        waiting = workspace.record_branch(
            started["id"], " billing ", "ordinary", " Create the feature branch ", False, " feature "
        )
        change = waiting["implementation_changes"][0]
        assert waiting["status"] == "In Progress"
        assert waiting["criteria"][0]["state"] == "Unverified"
        assert change["class"] == "consequential"
        assert change["outcome"] == "Awaiting approval"
        assert change["assistant_name"] == "Guide"
        assert change["stopped"] is False
        assert change["created_branch"]["name"] == "feature"
        assert change["created_branch"]["commit"] == head
        assert change["created_branch"]["checked_out"] is False
        assert _current(billing) == "main"
        assert "feature" not in _branches(billing)
        assert _count(billing) == before
        assert "label.txt" in _git(billing, "status", "--porcelain").stdout
        assert workspace.list_requirements() == []
        refused = workspace.approve_change(started["id"], change["id"], "Seen", actor="assistant")
        assert refused.message == "The assistant cannot approve a change."
        assert _current(billing) == "main"
        approved = workspace.approve_change(started["id"], change["id"], "The commit is still the start")
        carried = approved["implementation_changes"][0]
        assert carried["outcome"] == "Carried out"
        assert carried["created_branch"]["checked_out"] is True
        assert carried["created_branch"]["commit"] == head
        assert _current(billing) == "feature"
        assert _git(billing, "rev-parse", "HEAD").stdout.strip() == head
        assert {"main", "feature"} <= _branches(billing)
        assert label.read_text() == "Export\n"
        assert "label.txt" in _git(billing, "status", "--porcelain").stdout
        assert _count(billing) == before
        _git(billing, "switch", "main")
        again = workspace.get_task(started["id"])
        assert again["implementation_changes"][0]["created_branch"]["checked_out"] is True
        assert _current(billing) == "main"
        assert _count(billing) == before
    finally:
        workspace.close()


def test_another_branch_stays(tmp_path, clock):
    workspace, root, _label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        _git(billing, "branch", "other")
        started = _started(workspace)
        waiting = workspace.record_branch(
            started["id"], "billing", "consequential", "Create the feature branch", False, "feature"
        )
        workspace.approve_change(
            started["id"], waiting["implementation_changes"][0]["id"], "The commit is still the start"
        )
        assert _current(billing) == "feature"
        assert {"main", "other", "feature"} <= _branches(billing)
    finally:
        workspace.close()


def test_decline_a_moved_commit_and_an_existing_name_do_not_create_a_branch(tmp_path, clock):
    workspace, root, label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        started = _started(workspace)
        waiting = workspace.record_branch(
            started["id"], "billing", "ordinary", "Create the feature branch", False, "feature"
        )
        change_id = waiting["implementation_changes"][0]["id"]
        declined = workspace.mark_change_not_carried_out(started["id"], change_id, "Keep the current branch")
        assert declined["implementation_changes"][0]["outcome"] == "Not carried out"
        assert _current(billing) == "main"
        assert "feature" not in _branches(billing)
        replacement = workspace.record_branch(
            started["id"], "billing", "ordinary", "Create it later", False, "feature"
        )
        second = replacement["implementation_changes"][1]["id"]
        label.write_text("Changed\n", encoding="utf-8")
        _git(billing, "add", "label.txt")
        _git(billing, "commit", "-m", "Change the label")
        moved = _git(billing, "rev-parse", "HEAD").stdout.strip()
        mismatched = workspace.approve_change(started["id"], second, "The commit should still be the start")
        assert isinstance(mismatched, Refusal)
        assert mismatched.message == "The branch no longer matches the commit this change was proposed against."
        assert _current(billing) == "main"
        assert _git(billing, "rev-parse", "HEAD").stdout.strip() == moved
        assert "feature" not in _branches(billing)
        assert workspace.get_task(started["id"])["implementation_changes"][1]["outcome"] == "Awaiting approval"
        taken = workspace.record_branch(
            started["id"], "billing", "ordinary", "Create the later branch", False, "later"
        )
        third = taken["implementation_changes"][2]["id"]
        _git(billing, "branch", "later")
        occupied = workspace.approve_change(started["id"], third, "The name should still be absent")
        assert occupied.message == "The branch no longer matches the commit this change was proposed against."
        assert _current(billing) == "main"
        assert workspace.get_task(started["id"])["implementation_changes"][2]["outcome"] == "Awaiting approval"
    finally:
        workspace.close()


def test_a_refusing_command_creates_nothing(tmp_path, clock, monkeypatch):
    workspace, root, _label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        started = _started(workspace)
        waiting = workspace.record_branch(
            started["id"], "billing", "ordinary", "Create the feature branch", False, "feature"
        )
        change_id = waiting["implementation_changes"][0]["id"]
        from task_manager.domain import branch as branch_module

        original = branch_module._git

        def refuse_switch(project_dir, args):
            if args[:2] == ["switch", "-c"]:
                return subprocess.CompletedProcess(args, 1, "", "refused")
            return original(project_dir, args)

        monkeypatch.setattr(branch_module, "_git", refuse_switch)
        refused = workspace.approve_change(started["id"], change_id, "The command should refuse this")
        assert refused.message == "The branch was refused."
        assert _current(billing) == "main"
        assert "feature" not in _branches(billing)
        assert workspace.get_task(started["id"])["implementation_changes"][0]["outcome"] == "Awaiting approval"
    finally:
        workspace.close()


def test_a_blank_illegal_existing_and_unready_repository_are_refused(tmp_path, clock):
    workspace, root, _label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        started = _started(workspace)
        before = _branches(billing)
        blank = workspace.record_branch(started["id"], "billing", "ordinary", "Create it", False, "  ")
        assert isinstance(blank, Refusal)
        assert blank.message == "Name the branch this change creates."
        illegal = workspace.record_branch(started["id"], "billing", "ordinary", "Create it", False, "../feature")
        assert illegal.message == "Name the branch this change creates."
        existing = workspace.record_branch(started["id"], "billing", "ordinary", "Create it", False, "main")
        assert existing.message == "The branch already exists."
        plain = root / "plain"
        plain.mkdir()
        not_repo = workspace.record_branch(started["id"], "plain", "ordinary", "Create it", False, "feature")
        assert not_repo.message == "The project must already be a repository."
        empty = root / "empty"
        empty.mkdir()
        _git(empty, "init", "-b", "main")
        no_commit = workspace.record_branch(started["id"], "empty", "ordinary", "Create it", False, "feature")
        assert no_commit.message == "The repository must already have a commit."
        missing = workspace.record_branch(started["id"], "missing", "ordinary", "Create it", False, "feature")
        assert missing.message == "The project must already exist."
        assert workspace.get_task(started["id"])["implementation_changes"] == []
        assert _branches(billing) == before
        assert _current(billing) == "main"
    finally:
        workspace.close()


def test_a_stopped_request_does_not_create_a_branch(tmp_path, clock):
    workspace, root, _label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        started = _started(workspace)
        waiting = workspace.record_branch(
            started["id"], "billing", "ordinary", "Create the feature branch", True, "feature"
        )
        change = waiting["implementation_changes"][0]
        assert change["class"] == "consequential"
        assert change["stopped"] is True
        assert change["outcome"] == "Awaiting approval"
        assert change["created_branch"]["checked_out"] is False
        assert "feature" not in _branches(billing)
        assert _current(billing) == "main"
    finally:
        workspace.close()
