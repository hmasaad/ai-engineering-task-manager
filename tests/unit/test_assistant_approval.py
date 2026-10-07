from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def _started(workspace):
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_consequential_and_stopped_ordinary_wait_for_the_engineer(tmp_path, clock):
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide")
    try:
        started = _started(workspace)
        consequential = workspace.record_assistant_change(
            started["id"],
            "billing",
            "consequential",
            "Replace the stored export name",
            True,
        )
        waiting = consequential["implementation_changes"][0]
        assert waiting["class"] == "consequential"
        assert waiting["outcome"] == "Awaiting approval"
        assert waiting["stopped"] is False
        assert waiting["assistant_name"] == "Guide"
        assert consequential["status"] == "In Progress"

        stopped = workspace.record_assistant_change(
            started["id"], "billing", "ordinary", "Rename the export label", True
        )
        halted = stopped["implementation_changes"][1]
        assert halted["class"] == "consequential"
        assert halted["outcome"] == "Awaiting approval"
        assert halted["stopped"] is True
        assert halted["project"] == "billing"

        approved = workspace.approve_change(
            started["id"], halted["id"], "The page shows the new name"
        )
        carried = next(
            item for item in approved["implementation_changes"] if item["id"] == halted["id"]
        )
        assert carried["outcome"] == "Carried out"
        assert carried["approval"]["engineer_name"] == "Ada"
        assert carried["approval"]["evidence"] == "The page shows the new name"
        assert approved["status"] == "In Progress"

        declined = workspace.mark_change_not_carried_out(
            started["id"], waiting["id"], "The old name is still required"
        )
        left = next(
            item for item in declined["implementation_changes"] if item["id"] == waiting["id"]
        )
        assert left["outcome"] == "Not carried out"
        assert left["not_carried_out"]["engineer_name"] == "Ada"
        later = workspace.approve_change(
            started["id"], waiting["id"], "The page shows the new name"
        )
        assert isinstance(later, Refusal)
        assert later.message == "It cannot be carried out."
    finally:
        workspace.close()


def test_assistant_cannot_approve_or_decline(workspace):
    started = _started(workspace)
    recorded = workspace.record_assistant_change(
        started["id"], "billing", "consequential", "Replace the stored export name", False
    )
    change_id = recorded["implementation_changes"][0]["id"]
    approve = workspace.approve_change(
        started["id"], change_id, "The page shows the new name", actor="assistant"
    )
    assert isinstance(approve, Refusal)
    assert approve.message == "The assistant cannot approve a change."
    decline = workspace.mark_change_not_carried_out(
        started["id"], change_id, "Not this one", actor="assistant"
    )
    assert isinstance(decline, Refusal)
    assert decline.message == "The assistant cannot decline a change."
    detail = workspace.get_task(started["id"])
    assert detail["implementation_changes"][0]["outcome"] == "Awaiting approval"
    assert detail["implementation_changes"][0]["approval"] is None
    assert detail["implementation_changes"][0]["not_carried_out"] is None
