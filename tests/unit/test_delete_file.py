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
    billing = root / "billing"
    billing.mkdir(parents=True)
    (billing / "label.txt").write_text("Export", encoding="utf-8")
    store = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    return store, root


def _label(root):
    return root / "billing" / "label.txt"


def test_a_delete_waits_until_the_engineer_approves(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        waiting = workspace.record_deletion(
            started["id"], " billing ", "ordinary", " Remove the old label ", False, " label.txt "
        )
        change = waiting["implementation_changes"][0]
        assert waiting["status"] == "In Progress"
        assert change["class"] == "consequential"
        assert change["outcome"] == "Awaiting approval"
        assert change["assistant_name"] == "Guide"
        assert change["stopped"] is False
        assert change["deleted_file"] == {"path": "label.txt", "text": "Export"}
        assert _label(root).read_text() == "Export"
        assert workspace.list_requirements() == []
        refused = workspace.approve_change(started["id"], change["id"], "Seen", actor="assistant")
        assert refused.message == "The assistant cannot approve a change."
        assert _label(root).read_text() == "Export"
        approved = workspace.approve_change(started["id"], change["id"], "The file is still Export")
        carried = approved["implementation_changes"][0]
        assert carried["outcome"] == "Carried out"
        assert carried["deleted_file"]["text"] == "Export"
        assert not _label(root).exists()
        again = workspace.get_task(started["id"])
        assert again["implementation_changes"][0]["outcome"] == "Carried out"
        assert not _label(root).exists()
        assert not (root / "billing").joinpath("notes.txt").exists()
    finally:
        workspace.close()


def test_decline_and_a_changed_file_do_not_delete(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        waiting = workspace.record_deletion(
            started["id"], "billing", "consequential", "Remove the label", False, "label.txt"
        )
        change_id = waiting["implementation_changes"][0]["id"]
        declined = workspace.mark_change_not_carried_out(started["id"], change_id, "Keep the label")
        assert declined["implementation_changes"][0]["outcome"] == "Not carried out"
        assert _label(root).read_text() == "Export"
        replacement = workspace.record_deletion(
            started["id"], "billing", "ordinary", "Remove it later", False, "label.txt"
        )
        second = replacement["implementation_changes"][1]["id"]
        _label(root).write_text("Changed", encoding="utf-8")
        mismatched = workspace.approve_change(started["id"], second, "The file should still say Export")
        assert isinstance(mismatched, Refusal)
        assert mismatched.message == "The file no longer matches the text this change was proposed against."
        assert _label(root).read_text() == "Changed"
        still = workspace.get_task(started["id"])["implementation_changes"][1]
        assert still["outcome"] == "Awaiting approval"
    finally:
        workspace.close()


def test_a_blank_missing_outside_folder_link_and_non_text_are_refused(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        blank = workspace.record_deletion(started["id"], "billing", "ordinary", "Remove it", False, "  ")
        assert isinstance(blank, Refusal)
        assert blank.message == "Name the file this change deletes."
        missing = workspace.record_deletion(
            started["id"], "billing", "ordinary", "Remove it", False, "missing.txt"
        )
        assert missing.message == "The file must already exist."
        outside = workspace.record_deletion(
            started["id"], "billing", "ordinary", "Remove it", False, "../outside.txt"
        )
        assert outside.message == "The file must stay inside the named project."
        (root / "billing" / "notes").mkdir()
        folder = workspace.record_deletion(
            started["id"], "billing", "ordinary", "Remove notes", False, "notes"
        )
        assert folder.message == "The path is a folder."
        target = root / "billing" / "kept.txt"
        target.write_text("Keep", encoding="utf-8")
        link = root / "billing" / "alias.txt"
        link.symlink_to(target)
        linked = workspace.record_deletion(
            started["id"], "billing", "ordinary", "Remove the alias", False, "alias.txt"
        )
        assert linked.message == "A link cannot be deleted by this change."
        assert link.is_symlink()
        assert target.read_text() == "Keep"
        binary = root / "billing" / "raw.bin"
        binary.write_bytes(b"not\x00text")
        refused = workspace.record_deletion(
            started["id"], "billing", "ordinary", "Remove raw", False, "raw.bin"
        )
        assert refused.message == "The file is not text."
        assert binary.read_bytes() == b"not\x00text"
        assert workspace.get_task(started["id"])["implementation_changes"] == []
        assert _label(root).read_text() == "Export"
    finally:
        workspace.close()


def test_a_stopped_request_does_not_delete_the_file(tmp_path, clock):
    workspace, root = _open(tmp_path, clock)
    try:
        started = _started(workspace)
        waiting = workspace.record_deletion(
            started["id"], "billing", "ordinary", "Remove the label", True, "label.txt"
        )
        change = waiting["implementation_changes"][0]
        assert change["class"] == "consequential"
        assert change["stopped"] is True
        assert change["outcome"] == "Awaiting approval"
        assert _label(root).read_text() == "Export"
    finally:
        workspace.close()
