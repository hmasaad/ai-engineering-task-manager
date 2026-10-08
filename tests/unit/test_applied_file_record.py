from task_manager.domain import implementation
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


def test_omitted_file_and_engineer_record_write_nothing(tmp_path, clock):
    workspace, root, started = _open(tmp_path, clock)
    try:
        recorded = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Rename the export label", False
        )
        change = recorded["implementation_changes"][0]
        assert change["file"] is None
        assert change["recorded_by"] == "assistant"
        assert list((root / "billing").rglob("*")) == [(root / "billing" / "notes")]
        engineer = workspace.record_change(
            started["id"],
            "Note the date",
            "ordinary",
            project="billing",
            assistant_name="Guide",
        )
        assert engineer["implementation_changes"][1]["file"] is None
        assert engineer["implementation_changes"][1]["recorded_by"] == "engineer"
        assert not hasattr(implementation, "update_applied_file")
        assert not hasattr(implementation, "delete_applied_file")
    finally:
        workspace.close()


def test_subtask_file_stays_on_the_subtask(tmp_path, clock):
    workspace, root, parent = _open(tmp_path, clock)
    try:
        child = workspace.add_subtask(parent["id"], "Write the checklist")
        workspace.set_goal(child["id"], "Take the record")
        workspace.add_criterion(child["id"], "The file contains the goal")
        ready = workspace.transition(child["id"], "mark_ready")
        started = workspace.transition(ready["id"], "start")
        workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Rename the export label", False, "notes/label.txt", "Export"
        )
        assert workspace.get_task(parent["id"])["implementation_changes"] == []
        child_change = workspace.get_task(started["id"])["implementation_changes"][0]
        assert child_change["file"]["path"] == "notes/label.txt"
        before = (root / "billing" / "notes" / "label.txt").read_bytes()
        workspace.get_task(started["id"])
        assert (root / "billing" / "notes" / "label.txt").read_bytes() == before
    finally:
        workspace.close()


def test_completion_still_requires_a_passing_check(tmp_path, clock):
    workspace, _root, started = _open(tmp_path, clock)
    try:
        recorded = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Rename the export label", False, "notes/label.txt", "Export"
        )
        criterion_id = recorded["criteria"][0]["id"]
        verified = workspace.verify_criterion(
            recorded["id"], criterion_id, "The file included the goal.", "pass"
        )
        refused = workspace.transition(verified["id"], "complete")
        assert isinstance(refused, Refusal)
        assert refused.message == "Needs a passing check: Rename the export label."
    finally:
        workspace.close()
