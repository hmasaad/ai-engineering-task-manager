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
    _git(billing, "init")
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


def _count(repo):
    return int(_git(repo, "rev-list", "--count", "HEAD").stdout.strip())


def test_a_commit_waits_until_the_engineer_approves(tmp_path, clock):
    workspace, root, label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        started = _started(workspace)
        before = _count(billing)
        waiting = workspace.record_commit(
            started["id"], " billing ", "ordinary", " Record the label ", False, " label.txt "
        )
        change = waiting["implementation_changes"][0]
        assert waiting["status"] == "In Progress"
        assert change["class"] == "consequential"
        assert change["outcome"] == "Awaiting approval"
        assert change["assistant_name"] == "Guide"
        assert change["stopped"] is False
        assert change["commit"]["path"] == "label.txt"
        assert change["commit"]["text"] == "Export\n"
        assert change["commit"]["hash"] is None
        assert _count(billing) == before
        assert workspace.list_requirements() == []
        refused = workspace.approve_change(started["id"], change["id"], "Seen", actor="assistant")
        assert refused.message == "The assistant cannot approve a change."
        assert _count(billing) == before
        approved = workspace.approve_change(started["id"], change["id"], "The file is still Export")
        carried = approved["implementation_changes"][0]
        assert carried["outcome"] == "Carried out"
        assert carried["commit"]["hash"] == _git(billing, "rev-parse", "HEAD").stdout.strip()
        assert _git(billing, "log", "-1", "--format=%s").stdout.strip() == "Record the label"
        assert _git(billing, "show", "--name-only", "--format=", "HEAD").stdout.strip() == "label.txt"
        assert label.read_text() == "Export\n"
        assert _count(billing) == before + 1
        again = workspace.get_task(started["id"])
        assert again["implementation_changes"][0]["commit"]["hash"] == carried["commit"]["hash"]
        assert _count(billing) == before + 1
    finally:
        workspace.close()


def test_another_file_stays_uncommitted(tmp_path, clock):
    workspace, root, _label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        other = billing / "other.txt"
        other.write_text("Other\n", encoding="utf-8")
        _git(billing, "add", "other.txt")
        started = _started(workspace)
        waiting = workspace.record_commit(
            started["id"], "billing", "consequential", "Record the label", False, "label.txt"
        )
        change_id = waiting["implementation_changes"][0]["id"]
        workspace.approve_change(started["id"], change_id, "The file is still Export")
        assert _git(billing, "show", "--name-only", "--format=", "HEAD").stdout.strip() == "label.txt"
        assert "other.txt" in _git(billing, "status", "--porcelain").stdout
    finally:
        workspace.close()


def test_an_untracked_file_can_be_committed(tmp_path, clock):
    workspace, root, _label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        notes = billing / "notes.txt"
        notes.write_text("Note\n", encoding="utf-8")
        started = _started(workspace)
        waiting = workspace.record_commit(
            started["id"], "billing", "ordinary", "Record the note", False, "notes.txt"
        )
        assert waiting["implementation_changes"][0]["outcome"] == "Awaiting approval"
        assert "?? notes.txt" in _git(billing, "status", "--porcelain").stdout
        approved = workspace.approve_change(
            started["id"], waiting["implementation_changes"][0]["id"], "The note is still Note"
        )
        assert approved["implementation_changes"][0]["outcome"] == "Carried out"
        assert _git(billing, "show", "--name-only", "--format=", "HEAD").stdout.strip() == "notes.txt"
    finally:
        workspace.close()


def test_decline_a_changed_file_and_a_hook_do_not_commit(tmp_path, clock):
    workspace, root, label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        started = _started(workspace)
        before = _count(billing)
        waiting = workspace.record_commit(
            started["id"], "billing", "ordinary", "Record the label", False, "label.txt"
        )
        change_id = waiting["implementation_changes"][0]["id"]
        declined = workspace.mark_change_not_carried_out(started["id"], change_id, "Keep it local")
        assert declined["implementation_changes"][0]["outcome"] == "Not carried out"
        assert _count(billing) == before
        replacement = workspace.record_commit(
            started["id"], "billing", "ordinary", "Record it later", False, "label.txt"
        )
        second = replacement["implementation_changes"][1]["id"]
        label.write_text("Changed\n", encoding="utf-8")
        mismatched = workspace.approve_change(started["id"], second, "The file should still say Export")
        assert isinstance(mismatched, Refusal)
        assert mismatched.message == "The file no longer matches the text this change was proposed against."
        assert _count(billing) == before
        assert workspace.get_task(started["id"])["implementation_changes"][1]["outcome"] == "Awaiting approval"
        label.write_text("Export\n", encoding="utf-8")
        hook = billing / ".git" / "hooks" / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
        hooked = workspace.record_commit(
            started["id"], "billing", "ordinary", "Record after the hook", False, "label.txt"
        )
        third = hooked["implementation_changes"][2]["id"]
        refused = workspace.approve_change(started["id"], third, "The hook should refuse this")
        assert refused.message == "The commit was refused."
        assert _count(billing) == before
        assert workspace.get_task(started["id"])["implementation_changes"][2]["outcome"] == "Awaiting approval"
        notes = billing / "notes.txt"
        notes.write_text("Note\n", encoding="utf-8")
        untracked = workspace.record_commit(
            started["id"], "billing", "ordinary", "Record the note", False, "notes.txt"
        )
        fourth = untracked["implementation_changes"][3]["id"]
        refused_note = workspace.approve_change(started["id"], fourth, "The hook should refuse the note")
        assert refused_note.message == "The commit was refused."
        assert "?? notes.txt" in _git(billing, "status", "--porcelain").stdout
        assert "A  notes.txt" not in _git(billing, "status", "--porcelain").stdout
    finally:
        workspace.close()


def test_a_blank_missing_outside_folder_link_and_unchanged_file_are_refused(tmp_path, clock):
    workspace, root, label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        started = _started(workspace)
        before = _count(billing)
        blank = workspace.record_commit(started["id"], "billing", "ordinary", "Record it", False, "  ")
        assert isinstance(blank, Refusal)
        assert blank.message == "Name the file this change commits."
        missing = workspace.record_commit(
            started["id"], "billing", "ordinary", "Record it", False, "missing.txt"
        )
        assert missing.message == "The file must already exist."
        outside = workspace.record_commit(
            started["id"], "billing", "ordinary", "Record it", False, "../outside.txt"
        )
        assert outside.message == "The file must stay inside the named project."
        (billing / "notes").mkdir()
        folder = workspace.record_commit(started["id"], "billing", "ordinary", "Record notes", False, "notes")
        assert folder.message == "The path is a folder."
        kept = billing / "kept.txt"
        kept.write_text("Keep\n", encoding="utf-8")
        link = billing / "alias.txt"
        link.symlink_to(kept)
        linked = workspace.record_commit(
            started["id"], "billing", "ordinary", "Record the alias", False, "alias.txt"
        )
        assert linked.message == "A link cannot be committed by this change."
        binary = billing / "raw.bin"
        binary.write_bytes(b"not\x00text")
        refused = workspace.record_commit(started["id"], "billing", "ordinary", "Record raw", False, "raw.bin")
        assert refused.message == "The file is not text."
        label.write_text("Old\n", encoding="utf-8")
        unchanged = workspace.record_commit(
            started["id"], "billing", "ordinary", "Record the label", False, "label.txt"
        )
        assert unchanged.message == "That file has no change to commit."
        plain = root / "plain"
        plain.mkdir()
        (plain / "label.txt").write_text("Export\n", encoding="utf-8")
        not_repo = workspace.record_commit(
            started["id"], "plain", "ordinary", "Record the label", False, "label.txt"
        )
        assert not_repo.message == "The project must already be a repository."
        assert workspace.get_task(started["id"])["implementation_changes"] == []
        assert _count(billing) == before
    finally:
        workspace.close()


def test_a_stopped_request_does_not_commit(tmp_path, clock):
    workspace, root, _label = _open(tmp_path, clock)
    billing = root / "billing"
    try:
        started = _started(workspace)
        before = _count(billing)
        waiting = workspace.record_commit(
            started["id"], "billing", "ordinary", "Record the label", True, "label.txt"
        )
        change = waiting["implementation_changes"][0]
        assert change["class"] == "consequential"
        assert change["stopped"] is True
        assert change["outcome"] == "Awaiting approval"
        assert change["commit"]["hash"] is None
        assert _count(billing) == before
    finally:
        workspace.close()
