from task_manager.domain import file_read
from task_manager.storage import file_read_store
from task_manager.workspace import Workspace


def _open(tmp_path, clock):
    root = tmp_path / "projects"
    notes = root / "billing" / "notes"
    notes.mkdir(parents=True)
    (notes / "label.txt").write_text("Export", encoding="utf-8")
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    started = workspace.transition(ready["id"], "start")
    return workspace, root, started


def test_stored_text_survives_a_later_edit(tmp_path, clock):
    workspace, root, started = _open(tmp_path, clock)
    try:
        workspace.record_file_read(started["id"], "billing", "notes/label.txt")
        label = root / "billing" / "notes" / "label.txt"
        label.write_text("Newer", encoding="utf-8")
        opened = workspace.get_task(started["id"])
        assert opened["file_reads"][0]["text"] == "Export"
        assert label.read_text(encoding="utf-8") == "Newer"
        label.unlink()
        deleted = workspace.get_task(started["id"])
        assert deleted["file_reads"][0]["text"] == "Export"
        label.write_text("Newer", encoding="utf-8")
        again = workspace.record_file_read(started["id"], "billing", "notes/label.txt")
        assert [item["text"] for item in again["file_reads"]] == ["Export", "Newer"]
        assert not hasattr(file_read, "update_file_read")
        assert not hasattr(file_read, "delete_file_read")
        assert not hasattr(file_read_store, "update_file_read")
        assert not hasattr(file_read_store, "delete_file_read")
    finally:
        workspace.close()


def test_subtask_read_stays_on_the_subtask(tmp_path, clock):
    workspace, _root, parent = _open(tmp_path, clock)
    try:
        child = workspace.add_subtask(parent["id"], "Write the checklist")
        workspace.set_goal(child["id"], "Take the record")
        workspace.add_criterion(child["id"], "The file contains the goal")
        ready = workspace.transition(child["id"], "mark_ready")
        started = workspace.transition(ready["id"], "start")
        workspace.record_file_read(started["id"], "billing", "notes/label.txt")
        assert workspace.get_task(parent["id"])["file_reads"] == []
        child_read = workspace.get_task(started["id"])["file_reads"][0]
        assert child_read["path"] == "notes/label.txt"
        assert child_read["text"] == "Export"
    finally:
        workspace.close()
