import subprocess

from task_manager.workspace import Workspace


def _git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )


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


def _started(workspace):
    created = workspace.create_task("Record the label")
    workspace.set_goal(created["id"], "Keep the label in the record")
    workspace.add_criterion(created["id"], "The label is recorded")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_one_approval_carries_out_only_that_change(tmp_path, clock):
    root = tmp_path / "projects"
    billing = root / "billing"
    label = _prepare(billing)
    before = label.read_bytes()
    commits = int(_git(billing, "rev-list", "--count", "HEAD").stdout.strip())
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    try:
        started = _started(workspace)
        waiting = workspace.record_branch(
            started["id"], "billing", "ordinary", "Create the feature branch", False, "feature"
        )
        branch_id = waiting["implementation_changes"][0]["id"]
        recorded = workspace.record_commit(
            started["id"], "billing", "ordinary", "Record the label", False, "label.txt"
        )
        commit = recorded["implementation_changes"][1]
        assert commit["outcome"] == "Awaiting approval"
        approved = workspace.approve_change(started["id"], branch_id, "The commit is still the start")
        assert approved["implementation_changes"][0]["outcome"] == "Carried out"
        assert approved["implementation_changes"][1]["outcome"] == "Awaiting approval"
        assert _git(billing, "branch", "--show-current").stdout.strip() == "feature"
        assert int(_git(billing, "rev-list", "--count", "HEAD").stdout.strip()) == commits
        read = workspace.record_file_read(started["id"], "billing", "label.txt")
        assert read["file_reads"][0]["text"] == "Export\n"
        assert label.read_bytes() == before
        refused = workspace.approve_change(
            started["id"], commit["id"], "The file is still Export", actor="assistant"
        )
        assert refused.message == "The assistant cannot approve a change."
        assert int(_git(billing, "rev-list", "--count", "HEAD").stdout.strip()) == commits
        assert workspace.get_task(started["id"])["implementation_changes"][1]["outcome"] == "Awaiting approval"
        files_before = {path.relative_to(billing) for path in billing.rglob("*") if path.is_file()}
        created = workspace.record_folder(
            started["id"], "billing", "ordinary", "Create the notes folder", False, "notes"
        )
        folder = created["implementation_changes"][2]
        assert folder["outcome"] == "Carried out"
        assert folder["folder"]["path"] == "notes"
        assert (billing / "notes").is_dir()
        files_after = {path.relative_to(billing) for path in billing.rglob("*") if path.is_file()}
        assert files_after == files_before
    finally:
        workspace.close()
