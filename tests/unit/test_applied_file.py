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
    (root / "billing" / "notes").mkdir(parents=True)
    store = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    return store, root


def test_ordinary_new_file_is_written_and_recorded(tmp_path, clock):
    workspace, root = _workspace(tmp_path, clock)
    try:
        started = _started(workspace)
        recorded = workspace.record_assistant_change(
            started["id"],
            " billing ",
            "ordinary",
            " Rename the export label ",
            False,
            "notes/label.txt",
            "Export",
        )
        change = recorded["implementation_changes"][0]
        assert recorded["status"] == "In Progress"
        assert change["class"] == "ordinary"
        assert change["outcome"] == "Carried out"
        assert change["project"] == "billing"
        assert change["assistant_name"] == "Guide"
        assert change["engineer_name"] == "Ada"
        assert change["recorded_by"] == "assistant"
        assert change["stopped"] is False
        assert change["file"]["path"] == "notes/label.txt"
        assert change["file"]["was_new"] is True
        assert change["file"]["previous_text"] is None
        assert change["file"]["text"] == "Export"
        assert (root / "billing" / "notes" / "label.txt").read_text(encoding="utf-8") == "Export"
        assert recorded["criteria"][0]["state"] == "Unverified"
        assert change["checks"] == []
        assert recorded["decisions"] == started["decisions"]
        assert recorded["history"] == started["history"]
        empty = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Add an empty note", False, "notes/empty.txt", ""
        )
        assert (root / "billing" / "notes" / "empty.txt").read_bytes() == b""
        assert empty["implementation_changes"][1]["file"]["text"] == ""
    finally:
        workspace.close()


def test_file_request_refusals_write_nothing(tmp_path, clock):
    workspace, root = _workspace(tmp_path, clock)
    try:
        started = _started(workspace)
        blank_project = workspace.record_assistant_change(
            started["id"], "   ", "ordinary", "Rename the export label", False, "   ", "Export"
        )
        assert isinstance(blank_project, Refusal)
        assert blank_project.message == "Name the project this change is for."
        missing_project = workspace.record_assistant_change(
            started["id"], "missing", "ordinary", "Rename the export label", False, "notes/label.txt", "Export"
        )
        assert isinstance(missing_project, Refusal)
        assert missing_project.message == "The project must already exist."
        blank_account = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "   ", False, "notes/label.txt", "Export"
        )
        assert isinstance(blank_account, Refusal)
        assert blank_account.message == "An account of what changed is required."
        missing_class = workspace.record_assistant_change(
            started["id"], "billing", None, "Rename the export label", False, "notes/label.txt", "Export"
        )
        assert isinstance(missing_class, Refusal)
        assert missing_class.message == "Choose ordinary or consequential."
        blank_file = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Rename the export label", False, "   ", "Export"
        )
        assert isinstance(blank_file, Refusal)
        assert blank_file.message == "Name the file this change writes."
        outside = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Rename the export label", False, "../outside.txt", "Export"
        )
        assert isinstance(outside, Refusal)
        assert outside.message == "The file must stay inside the named project."
        assert not (root / "outside.txt").exists()
        missing_folder = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Rename the export label", False, "absent/label.txt", "Export"
        )
        assert isinstance(missing_folder, Refusal)
        assert missing_folder.message == "The folder for that file must already exist."
        assert not (root / "billing" / "absent").exists()
        assert workspace.get_task(started["id"])["implementation_changes"] == []
    finally:
        workspace.close()


def test_status_is_refused_before_a_blank_file(tmp_path, clock):
    workspace, _root = _workspace(tmp_path, clock)
    try:
        started = _started(workspace)
        workspace.connection.execute(
            "UPDATE task SET status = 'Draft' WHERE id = ?", (started["id"],)
        )
        refused = workspace.record_assistant_change(
            started["id"], "   ", None, "   ", False, "   ", ""
        )
        assert isinstance(refused, Refusal)
        assert refused.message == "The task must be In Progress."
        unknown = workspace.record_assistant_change(
            9999, "billing", "ordinary", "Rename the export label", False, "notes/label.txt", "Export"
        )
        assert isinstance(unknown, Refusal)
        assert unknown.message == "Task not found."
    finally:
        workspace.close()
