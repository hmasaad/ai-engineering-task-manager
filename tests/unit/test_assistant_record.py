from task_manager.domain import implementation
from task_manager.domain.results import Refusal


def _started(workspace):
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_engineer_record_ignores_project_and_assistant_name(workspace):
    started = _started(workspace)
    recorded = workspace.record_change(
        started["id"],
        "Rename the export label",
        "ordinary",
        project="billing",
        assistant_name="Guide",
    )
    change = recorded["implementation_changes"][0]
    assert change["recorded_by"] == "engineer"
    assert change["project"] is None
    assert change["assistant_name"] is None
    assert change["stopped"] is False
    assert change["engineer_name"] == "Ada"
    assert change["outcome"] == "Carried out"
    assert not hasattr(implementation, "update_assistant_change")
    assert not hasattr(implementation, "delete_assistant_change")


def test_assistant_change_stays_on_the_subtask(workspace):
    parent = _started(workspace)
    child = workspace.add_subtask(parent["id"], "Write the checklist")
    workspace.set_goal(child["id"], "Take the record")
    workspace.add_criterion(child["id"], "The file contains the goal")
    ready = workspace.transition(child["id"], "mark_ready")
    started = workspace.transition(ready["id"], "start")
    workspace.record_assistant_change(
        started["id"], "billing", "ordinary", "Rename the export label", False
    )
    assert workspace.get_task(parent["id"])["implementation_changes"] == []
    child_change = workspace.get_task(started["id"])["implementation_changes"][0]
    assert child_change["project"] == "billing"
    assert child_change["recorded_by"] == "assistant"


def test_completion_still_requires_a_passing_check(workspace):
    started = _started(workspace)
    recorded = workspace.record_assistant_change(
        started["id"], "billing", "ordinary", "Rename the export label", False
    )
    criterion_id = recorded["criteria"][0]["id"]
    verified = workspace.verify_criterion(
        recorded["id"], criterion_id, "The file included the goal.", "pass"
    )
    refused = workspace.transition(verified["id"], "complete")
    assert isinstance(refused, Refusal)
    assert refused.message == "Needs a passing check: Rename the export label."
    assert verified["status"] == "In Progress"
