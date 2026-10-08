from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def _open(tmp_path, clock):
    root = tmp_path / "projects"
    (root / "billing" / "notes").mkdir(parents=True)
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root)
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    started = workspace.transition(ready["id"], "start")
    return workspace, root, started


def test_existing_consequential_and_stopped_do_not_write(tmp_path, clock):
    workspace, root, started = _open(tmp_path, clock)
    try:
        target = root / "billing" / "notes" / "label.txt"
        target.write_text("Old", encoding="utf-8")
        recorded = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Rename the export label", False, "notes/label.txt", "Export"
        )
        change = recorded["implementation_changes"][0]
        assert change["class"] == "consequential"
        assert change["outcome"] == "Awaiting approval"
        assert change["stopped"] is False
        assert change["file"]["was_new"] is False
        assert change["file"]["previous_text"] == "Old"
        assert change["file"]["text"] == "Export"
        assert target.read_text(encoding="utf-8") == "Old"

        waiting = workspace.record_assistant_change(
            started["id"], "billing", "consequential", "Add the other note", False, "notes/other.txt", "Export"
        )
        proposed = waiting["implementation_changes"][1]
        assert proposed["class"] == "consequential"
        assert proposed["stopped"] is False
        assert proposed["file"]["was_new"] is True
        assert not (root / "billing" / "notes" / "other.txt").exists()

        stopped = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Hold the note", True, "notes/held.txt", "Export"
        )
        held = stopped["implementation_changes"][2]
        assert held["class"] == "consequential"
        assert held["stopped"] is True
        assert not (root / "billing" / "notes" / "held.txt").exists()
    finally:
        workspace.close()


def test_not_text_is_refused(tmp_path, clock):
    workspace, root, started = _open(tmp_path, clock)
    try:
        target = root / "billing" / "notes" / "label.txt"
        target.write_bytes(b"\x00")
        refused = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Rename the export label", False, "notes/label.txt", "Export"
        )
        assert isinstance(refused, Refusal)
        assert refused.message == "The file is not text."
        assert target.read_bytes() == b"\x00"
        assert workspace.get_task(started["id"])["implementation_changes"] == []
    finally:
        workspace.close()


def test_engineer_approval_writes_and_assistant_cannot(tmp_path, clock):
    workspace, root, started = _open(tmp_path, clock)
    try:
        recorded = workspace.record_assistant_change(
            started["id"], "billing", "consequential", "Add the note", False, "notes/other.txt", "Export"
        )
        change_id = recorded["implementation_changes"][0]["id"]
        assistant = workspace.approve_change(
            started["id"], change_id, "The page shows the new name", actor="assistant"
        )
        assert isinstance(assistant, Refusal)
        assert assistant.message == "The assistant cannot approve a change."
        assert not (root / "billing" / "notes" / "other.txt").exists()
        decline = workspace.mark_change_not_carried_out(
            started["id"], change_id, "Not this one", actor="assistant"
        )
        assert isinstance(decline, Refusal)
        assert decline.message == "The assistant cannot decline a change."
        approved = workspace.approve_change(started["id"], change_id, "The page shows the new name")
        carried = approved["implementation_changes"][0]
        assert carried["outcome"] == "Carried out"
        assert carried["approval"]["engineer_name"] == "Ada"
        assert (root / "billing" / "notes" / "other.txt").read_text(encoding="utf-8") == "Export"

        target = root / "billing" / "notes" / "label.txt"
        target.write_text("Old", encoding="utf-8")
        replacement = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Replace the label", False, "notes/label.txt", "Export"
        )
        replacement_id = replacement["implementation_changes"][1]["id"]
        target.write_text("Newer", encoding="utf-8")
        mismatch = workspace.approve_change(started["id"], replacement_id, "The page shows the new name")
        assert isinstance(mismatch, Refusal)
        assert mismatch.message == "The file no longer matches the text this change was proposed against."
        assert target.read_text(encoding="utf-8") == "Newer"
        target.write_text("Old", encoding="utf-8")
        replaced = workspace.approve_change(started["id"], replacement_id, "The page shows the new name")
        assert replaced["implementation_changes"][1]["outcome"] == "Carried out"
        assert target.read_text(encoding="utf-8") == "Export"

        again = workspace.approve_change(started["id"], recorded["implementation_changes"][0]["id"], "Again")
        assert isinstance(again, Refusal)
        assert again.message == "The change is already carried out."
    finally:
        workspace.close()
