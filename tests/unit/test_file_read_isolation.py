from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def _open(tmp_path, clock):
    root = tmp_path / "projects"
    notes = root / "billing" / "notes"
    notes.mkdir(parents=True)
    (notes / "label.txt").write_text("Old", encoding="utf-8")
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    started = workspace.transition(ready["id"], "start")
    return workspace, root, started


def test_a_read_is_not_an_implementation_change(tmp_path, clock):
    workspace, root, started = _open(tmp_path, clock)
    try:
        waiting = workspace.record_assistant_change(
            started["id"],
            "billing",
            "ordinary",
            "Replace the label",
            False,
            "notes/label.txt",
            "Export",
        )
        recorded = workspace.record_file_read(started["id"], "billing", "notes/label.txt")
        label = root / "billing" / "notes" / "label.txt"
        assert recorded["implementation_changes"] == waiting["implementation_changes"]
        assert recorded["implementation_changes"][0]["outcome"] == "Awaiting approval"
        assert "class" not in recorded["file_reads"][0]
        assert recorded["file_reads"][0]["text"] == "Old"
        assert label.read_text(encoding="utf-8") == "Old"
        omitted = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Rename the export label", False
        )
        assert len(omitted["file_reads"]) == 1
        assert label.read_text(encoding="utf-8") == "Old"
        assert not (root / "billing" / "notes" / "created.txt").exists()
        engineer = workspace.record_change(
            started["id"],
            "Note the date",
            "ordinary",
            project="billing",
            assistant_name="Guide",
        )
        assert len(engineer["file_reads"]) == 1
        assert engineer["implementation_changes"][2]["recorded_by"] == "engineer"
        assert recorded["file_reads"][0]["text"] == "Old"
        assert engineer["decisions"] == []
        assert engineer["implementation_changes"][0]["checks"] == []
    finally:
        workspace.close()


def test_completion_and_cancellation_leave_the_read(tmp_path, clock):
    workspace, root, started = _open(tmp_path, clock)
    try:
        workspace.record_assistant_change(
            started["id"],
            "billing",
            "ordinary",
            "Rename the export label",
            False,
            "notes/created.txt",
            "Export",
        )
        recorded = workspace.record_file_read(started["id"], "billing", "notes/created.txt")
        criterion_id = recorded["criteria"][0]["id"]
        verified = workspace.verify_criterion(
            recorded["id"], criterion_id, "The file included the goal.", "pass"
        )
        refused = workspace.transition(verified["id"], "complete")
        assert isinstance(refused, Refusal)
        assert refused.message == "Needs a passing check: Rename the export label."
        cancelled = workspace.transition(verified["id"], "cancel", "No longer needed")
        assert cancelled["status"] == "Cancelled"
        assert cancelled["file_reads"][0]["text"] == "Export"
    finally:
        workspace.close()
