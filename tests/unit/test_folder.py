from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def _started(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _open(tmp_path, clock):
    root = tmp_path / "projects"
    (root / "billing").mkdir(parents=True)
    store = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    return store, root


def test_an_ordinary_folder_is_created(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        recorded = workspace.record_folder(
            started["id"], " billing ", "ordinary", " Add the notes folder ", False, " notes "
        )
        change = recorded["implementation_changes"][0]
        assert recorded["status"] == "In Progress"
        assert change["class"] == "ordinary"
        assert change["outcome"] == "Carried out"
        assert change["folder"] == {"path": "notes"}
        assert change["assistant_name"] == "Guide"
        assert (root / "billing" / "notes").is_dir()
        again = workspace.get_task(started["id"])
        assert len(again["implementation_changes"]) == 1
        assert (root / "billing" / "notes").is_dir()
    finally:
        workspace.close()


def test_a_missing_parent_and_an_existing_folder_are_refused(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        missing_parent = workspace.record_folder(
            started["id"], "billing", "ordinary", "Add nested", False, "notes/export"
        )
        assert isinstance(missing_parent, Refusal)
        assert missing_parent.message == "The folder that holds this one must already exist."
        (root / "billing" / "notes").mkdir()
        exists = workspace.record_folder(
            started["id"], "billing", "ordinary", "Add notes", False, "notes"
        )
        assert exists.message == "The folder already exists."
        (root / "billing" / "label.txt").write_text("Export", encoding="utf-8")
        blocked = workspace.record_folder(
            started["id"], "billing", "ordinary", "Add label", False, "label.txt"
        )
        assert blocked.message == "A file is already at that path."
        outside = workspace.record_folder(
            started["id"], "billing", "ordinary", "Escape", False, "../outside"
        )
        assert outside.message == "The folder must stay inside the named project."
        assert workspace.get_task(started["id"])["implementation_changes"] == []
    finally:
        workspace.close()


def test_a_consequential_folder_waits_until_approval(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        waiting = workspace.record_folder(
            started["id"], "billing", "consequential", "Add notes", False, "notes"
        )
        change = waiting["implementation_changes"][0]
        assert change["class"] == "consequential"
        assert change["outcome"] == "Awaiting approval"
        assert not (root / "billing" / "notes").exists()
        refused = workspace.approve_change(started["id"], change["id"], "Seen", actor="assistant")
        assert refused.message == "The assistant cannot approve a change."
        assert not (root / "billing" / "notes").exists()
        approved = workspace.approve_change(started["id"], change["id"], "The folder is still absent")
        assert approved["implementation_changes"][0]["outcome"] == "Carried out"
        assert (root / "billing" / "notes").is_dir()
    finally:
        workspace.close()


def test_a_stopped_ordinary_request_does_not_create_the_folder(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        waiting = workspace.record_folder(
            started["id"], "billing", "ordinary", "Add notes", True, "notes"
        )
        change = waiting["implementation_changes"][0]
        assert change["class"] == "consequential"
        assert change["stopped"] is True
        assert change["outcome"] == "Awaiting approval"
        assert not (root / "billing" / "notes").exists()
    finally:
        workspace.close()
