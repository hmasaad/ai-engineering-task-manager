from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def _started(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _workspace(tmp_path, clock):
    root = tmp_path / "projects"
    notes = root / "billing" / "notes"
    notes.mkdir(parents=True)
    (notes / "label.txt").write_text("Export", encoding="utf-8")
    store = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    return store, root


def test_existing_text_file_is_stored_and_unchanged(tmp_path, clock):
    workspace, root = _workspace(tmp_path, clock)
    try:
        started = _started(workspace)
        recorded = workspace.record_file_read(started["id"], " billing ", "notes/label.txt")
        read = recorded["file_reads"][0]
        label = root / "billing" / "notes" / "label.txt"
        assert recorded["status"] == "In Progress"
        assert recorded["implementation_changes"] == []
        assert read["project"] == "billing"
        assert read["path"] == "notes/label.txt"
        assert read["text"] == "Export"
        assert read["assistant_name"] == "Guide"
        assert label.read_text(encoding="utf-8") == "Export"
        assert recorded["criteria"][0]["state"] == "Unverified"
        assert recorded["decisions"] == started["decisions"]
        assert recorded["history"] == started["history"]
        empty = root / "billing" / "notes" / "empty.txt"
        empty.write_text("", encoding="utf-8")
        spaced = root / "billing" / "notes" / "spaced.txt"
        spaced.write_text("Export ", encoding="utf-8")
        after_empty = workspace.record_file_read(started["id"], "billing", "notes/empty.txt")
        after_space = workspace.record_file_read(started["id"], "billing", "notes/spaced.txt")
        assert after_empty["file_reads"][1]["text"] == ""
        assert empty.read_bytes() == b""
        assert after_space["file_reads"][2]["text"] == "Export "
        assert spaced.read_text(encoding="utf-8") == "Export "
        alias = root / "billing" / "notes" / "alias.txt"
        alias.symlink_to(label)
        linked = workspace.record_file_read(started["id"], "billing", "notes/alias.txt")
        assert linked["file_reads"][3]["path"] == "notes/alias.txt"
        assert linked["file_reads"][3]["text"] == "Export"
        ignored = workspace.record_file_read(
            started["id"], "billing", "notes/label.txt", assistant_name="Someone"
        )
        assert ignored["file_reads"][4]["assistant_name"] == "Guide"
    finally:
        workspace.close()


def test_file_read_refusals_store_nothing(tmp_path, clock):
    workspace, root = _workspace(tmp_path, clock)
    try:
        started = _started(workspace)
        blank_project = workspace.record_file_read(started["id"], "   ", "   ")
        assert isinstance(blank_project, Refusal)
        assert blank_project.message == "Name the project this change is for."
        missing_project = workspace.record_file_read(started["id"], "missing", "notes/label.txt")
        assert isinstance(missing_project, Refusal)
        assert missing_project.message == "The project must already exist."
        blank_file = workspace.record_file_read(started["id"], "billing", "   ")
        assert isinstance(blank_file, Refusal)
        assert blank_file.message == "Name the file this change reads."
        outside = workspace.record_file_read(started["id"], "billing", "../outside.txt")
        assert isinstance(outside, Refusal)
        assert outside.message == "The file must stay inside the named project."
        assert not (root / "outside.txt").exists()
        secret = root / "secret.txt"
        secret.write_text("Secret", encoding="utf-8")
        escape = root / "billing" / "notes" / "escape.txt"
        escape.symlink_to(secret)
        linked_out = workspace.record_file_read(started["id"], "billing", "notes/escape.txt")
        assert isinstance(linked_out, Refusal)
        assert linked_out.message == "The file must stay inside the named project."
        assert secret.read_text(encoding="utf-8") == "Secret"
        missing_file = workspace.record_file_read(started["id"], "billing", "absent/label.txt")
        assert isinstance(missing_file, Refusal)
        assert missing_file.message == "The file must already exist."
        assert not (root / "billing" / "absent").exists()
        (root / "billing" / "notes" / "binary.txt").write_bytes(b"a\x00b")
        binary = workspace.record_file_read(started["id"], "billing", "notes/binary.txt")
        assert isinstance(binary, Refusal)
        assert binary.message == "The file is not text."
        (root / "billing" / "notes" / "folder").mkdir()
        folder = workspace.record_file_read(started["id"], "billing", "notes/folder")
        assert isinstance(folder, Refusal)
        assert folder.message == "The file is not text."
        assert workspace.get_task(started["id"])["file_reads"] == []
        assert (root / "billing" / "notes" / "label.txt").read_text(encoding="utf-8") == "Export"
    finally:
        workspace.close()


def test_status_is_refused_before_a_blank_file(tmp_path, clock):
    workspace, _root = _workspace(tmp_path, clock)
    try:
        created = workspace.create_task("Add export")
        workspace.set_goal(created["id"], "Take the record")
        workspace.add_criterion(created["id"], "The file contains the goal")
        ready = workspace.transition(created["id"], "mark_ready")
        refused_ready = workspace.record_file_read(ready["id"], "   ", "   ")
        assert isinstance(refused_ready, Refusal)
        assert refused_ready.message == "Start the task first."
        started = _started(workspace, "Finish the export")
        workspace.connection.execute(
            "UPDATE task SET status = 'Draft' WHERE id = ?", (started["id"],)
        )
        refused_draft = workspace.record_file_read(started["id"], "   ", "   ")
        assert isinstance(refused_draft, Refusal)
        assert refused_draft.message == "The task must be In Progress."
        done = _started(workspace, "Close the export")
        criterion_id = done["criteria"][0]["id"]
        verified = workspace.verify_criterion(
            done["id"], criterion_id, "The file included the goal.", "pass"
        )
        completed = workspace.transition(verified["id"], "complete")
        refused_completed = workspace.record_file_read(completed["id"], "   ", "   ")
        assert isinstance(refused_completed, Refusal)
        assert refused_completed.message == "Reopen the task first."
        cancelled_task = _started(workspace, "Drop the export")
        cancelled = workspace.transition(cancelled_task["id"], "cancel", "No longer needed")
        refused_cancelled = workspace.record_file_read(cancelled["id"], "   ", "   ")
        assert isinstance(refused_cancelled, Refusal)
        assert (
            refused_cancelled.message
            == "A cancelled task cannot be changed. Continued work is a new task."
        )
        unknown = workspace.record_file_read(9999, "billing", "notes/label.txt")
        assert isinstance(unknown, Refusal)
        assert unknown.message == "Task not found."
    finally:
        workspace.close()
