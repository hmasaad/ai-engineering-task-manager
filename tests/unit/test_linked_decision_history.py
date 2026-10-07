import task_manager.domain.decisions as decisions
import task_manager.storage.decision_store as decision_store

from task_manager.domain.results import Refusal


def _started(workspace, criteria=("The export contains the goal", "The export lists the date")):
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    for text in criteria:
        workspace.add_criterion(created["id"], text)
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_later_check_does_not_move_the_decision(workspace):
    started = _started(workspace)
    task_id = started["id"]
    change_id = workspace.record_change(task_id, "Rename the export label", "ordinary")[
        "implementation_changes"
    ][0]["id"]
    first_criterion = started["criteria"][0]["id"]
    second_criterion = started["criteria"][1]["id"]
    failed = workspace.record_check(task_id, change_id, first_criterion, "The label was still old", "Failed")
    check_id = failed["implementation_changes"][0]["checks"][0]["id"]
    linked = workspace.add_linked_decision(
        task_id, "Wait for the label", "The first check failed", check_id
    )
    later = workspace.record_check(
        task_id, change_id, first_criterion, "The label now reads Export", "Passed"
    )
    decision = later["decisions"][0]
    assert decision["statement"] == linked["decisions"][0]["statement"]
    assert decision["check"]["id"] == check_id
    assert decision["check"]["evidence"] == "The label was still old"
    assert decision["check"]["result"] == "Failed"
    checks = later["implementation_changes"][0]["checks"]
    assert [item["result"] for item in checks] == ["Failed", "Passed"]
    assert checks[0]["evidence"] == "The label was still old"

    other = workspace.record_check(task_id, change_id, second_criterion, "The date is on the page", "Passed")
    still = other["decisions"][0]["check"]
    assert still["id"] == check_id
    assert still["criterion_text"] == "The export contains the goal"
    assert still["evidence"] == "The label was still old"
    assert still["result"] == "Failed"


def test_criterion_edits_do_not_rewrite_the_named_check(workspace):
    started = _started(workspace)
    task_id = started["id"]
    change_id = workspace.record_change(task_id, "Rename the export label", "ordinary")[
        "implementation_changes"
    ][0]["id"]
    criterion_id = started["criteria"][0]["id"]
    checked = workspace.record_check(
        task_id, change_id, criterion_id, "The label was still old", "Failed"
    )
    check_id = checked["implementation_changes"][0]["checks"][0]["id"]
    workspace.add_linked_decision(task_id, "Wait for the label", "The first check failed", check_id)
    edited = workspace.update_criterion(task_id, criterion_id, "The export contains the new goal")
    assert edited["decisions"][0]["check"]["criterion_text"] == "The export contains the goal"

    removed = workspace.remove_criterion(task_id, criterion_id)
    assert not isinstance(removed, Refusal)
    assert removed["decisions"][0]["check"]["id"] == check_id
    assert removed["decisions"][0]["check"]["criterion_text"] == "The export contains the goal"
    assert removed["implementation_changes"][0]["checks"][0]["id"] == check_id

    assert not hasattr(decisions, "update_decision")
    assert not hasattr(decisions, "delete_decision")
    assert not hasattr(decision_store, "update_decision_check")
    assert not hasattr(decision_store, "delete_decision_check")
