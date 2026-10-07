from task_manager.domain.results import Refusal


def _started(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _change_id(detail, what_changed):
    for change in detail["implementation_changes"]:
        if change["what_changed"] == what_changed:
            return change["id"]
    raise AssertionError(what_changed)


def test_approve_stores_evidence_and_leaves_status(workspace):
    started = _started(workspace)
    waiting = workspace.record_change(started["id"], "Replace the stored export name", "consequential")
    assert waiting["implementation_changes"][0]["outcome"] == "Awaiting approval"
    blank = workspace.approve_change(started["id"], waiting["implementation_changes"][0]["id"], "  ")
    assert isinstance(blank, Refusal)
    assert blank.code == 400
    assert blank.message == "An account of the evidence reviewed is required."
    assert workspace.get_task(started["id"])["implementation_changes"][0]["outcome"] == "Awaiting approval"

    approved = workspace.approve_change(
        started["id"],
        waiting["implementation_changes"][0]["id"],
        "  The detail page shows the new export name  ",
    )
    change = approved["implementation_changes"][0]
    assert approved["status"] == "In Progress"
    assert change["outcome"] == "Carried out"
    assert change["approval"]["evidence"] == "The detail page shows the new export name"
    assert change["approval"]["engineer_name"] == "Ada"
    assert change["approval"]["approved_at"]
    assert approved["history"] == started["history"]
    assert approved["decisions"] == []

    again = workspace.approve_change(started["id"], change["id"], "More evidence")
    assert isinstance(again, Refusal)
    assert again.message == "The change is already carried out."
    assert workspace.get_task(started["id"])["implementation_changes"][0]["approval"]["evidence"] == (
        "The detail page shows the new export name"
    )


def test_approve_refusals(workspace):
    started = _started(workspace)
    ordinary = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    refused = workspace.approve_change(
        started["id"], ordinary["implementation_changes"][0]["id"], "Evidence"
    )
    assert isinstance(refused, Refusal)
    assert refused.message == "An ordinary change does not wait for approval."

    other = _started(workspace, "Other")
    waiting = workspace.record_change(other["id"], "Replace the stored export name", "consequential")
    change_id = waiting["implementation_changes"][0]["id"]
    cross = workspace.approve_change(started["id"], change_id, "Evidence")
    assert isinstance(cross, Refusal)
    assert cross.message == "The approval must name a change on that task."

    missing_change = workspace.approve_change(started["id"], 99999, "Evidence")
    assert isinstance(missing_change, Refusal)
    assert missing_change.code == 404
    assert missing_change.message == "Implementation change not found."

    missing_task = workspace.approve_change(99999, change_id, "Evidence")
    assert isinstance(missing_task, Refusal)
    assert missing_task.message == "Task not found."

    workspace.connection.execute(
        "UPDATE task SET status = 'Completed' WHERE id = ?",
        (other["id"],),
    )
    forced = workspace.approve_change(other["id"], change_id, "Evidence")
    assert isinstance(forced, Refusal)
    assert forced.message == "The task must be In Progress."
    assert workspace.get_task(other["id"])["implementation_changes"][0]["outcome"] == "Awaiting approval"


def test_completion_and_cancellation_wait_for_approval(workspace):
    started = _started(workspace)
    criterion_id = started["criteria"][0]["id"]
    workspace.verify_criterion(started["id"], criterion_id, "Seen", "pass")
    workspace.record_change(started["id"], "First waiting change", "consequential")
    recorded = workspace.record_change(started["id"], "Second waiting change", "consequential")
    blocked = workspace.transition(recorded["id"], "complete")
    assert isinstance(blocked, Refusal)
    assert blocked.message == "Awaiting approval: First waiting change, Second waiting change."
    assert workspace.get_task(started["id"])["status"] == "In Progress"
    assert workspace.get_task(started["id"])["history"] == started["history"]

    cancelled = workspace.transition(started["id"], "cancel", "Stop")
    assert isinstance(cancelled, Refusal)
    assert cancelled.message == "Awaiting approval: First waiting change, Second waiting change."

    unmet = _started(workspace, "Unmet")
    workspace.record_change(unmet["id"], "Replace the stored export name", "consequential")
    refused = workspace.transition(unmet["id"], "complete")
    assert refused.message == (
        "Unverified criteria: The file contains the goal. "
        "Awaiting approval: Replace the stored export name."
    )

    parent = _started(workspace, "Parent")
    workspace.add_subtask(parent["id"], "Still drafting")
    workspace.record_change(parent["id"], "Replace the stored export name", "consequential")
    parent_cancel = workspace.transition(parent["id"], "cancel", "Stop")
    assert parent_cancel.message == (
        "Subtasks must be finished or cancelled first: Still drafting (Draft). "
        "Awaiting approval: Replace the stored export name."
    )

    plain = _started(workspace, "Plain")
    plain_refusal = workspace.transition(plain["id"], "complete")
    assert "Awaiting approval" not in plain_refusal.message
    assert plain_refusal.message == "Unverified criteria: The file contains the goal."

    carried = _started(workspace, "Carried")
    criterion = carried["criteria"][0]["id"]
    workspace.verify_criterion(carried["id"], criterion, "Seen", "pass")
    ordinary = workspace.record_change(carried["id"], "Rename the export label", "ordinary")
    assert "Awaiting approval" not in str(ordinary)
    workspace.record_check(
        carried["id"],
        ordinary["implementation_changes"][0]["id"],
        criterion,
        "Seen",
        "Passed",
    )
    completed = workspace.transition(carried["id"], "complete")
    assert completed["status"] == "Completed"

    finished = _started(workspace, "Finished")
    finished_criterion = finished["criteria"][0]["id"]
    workspace.verify_criterion(finished["id"], finished_criterion, "Seen", "pass")
    waiting = workspace.record_change(finished["id"], "Replace the stored export name", "consequential")
    change_id = _change_id(waiting, "Replace the stored export name")
    workspace.approve_change(finished["id"], change_id, "The detail page shows the new export name")
    workspace.record_check(finished["id"], change_id, finished_criterion, "Seen", "Passed")
    done = workspace.transition(finished["id"], "complete")
    assert done["status"] == "Completed"
