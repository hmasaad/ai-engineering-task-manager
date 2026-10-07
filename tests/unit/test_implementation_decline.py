from task_manager.domain.results import Refusal


def _started(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_mark_not_carried_out_keeps_the_change_visible(workspace):
    started = _started(workspace)
    waiting = workspace.record_change(started["id"], "Drop the old export path", "consequential")
    change_id = waiting["implementation_changes"][0]["id"]
    blank = workspace.mark_change_not_carried_out(started["id"], change_id, "   ")
    assert isinstance(blank, Refusal)
    assert blank.code == 400
    assert blank.message == "A reason is required."
    assert workspace.get_task(started["id"])["implementation_changes"][0]["outcome"] == (
        "Awaiting approval"
    )

    declined = workspace.mark_change_not_carried_out(
        started["id"], change_id, "  The old path is still required  "
    )
    change = declined["implementation_changes"][0]
    assert declined["status"] == "In Progress"
    assert change["outcome"] == "Not carried out"
    assert change["not_carried_out"]["reason"] == "The old path is still required"
    assert change["not_carried_out"]["engineer_name"] == "Ada"
    assert change["not_carried_out"]["declined_at"]
    assert change["approval"] is None

    again = workspace.mark_change_not_carried_out(started["id"], change_id, "Another reason")
    assert isinstance(again, Refusal)
    assert again.message == "It cannot be carried out."
    approved = workspace.approve_change(started["id"], change_id, "Evidence")
    assert isinstance(approved, Refusal)
    assert approved.message == "It cannot be carried out."


def test_cannot_decline_a_carried_out_change_or_the_wrong_task(workspace):
    started = _started(workspace)
    ordinary = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    ordinary_id = ordinary["implementation_changes"][0]["id"]
    refused = workspace.mark_change_not_carried_out(started["id"], ordinary_id, "Wrong fix")
    assert isinstance(refused, Refusal)
    assert refused.message == "A carried-out change stays in the record."

    consequential = workspace.record_change(started["id"], "Replace the stored export name", "consequential")
    change_id = consequential["implementation_changes"][1]["id"]
    workspace.approve_change(started["id"], change_id, "The detail page shows the new export name")
    kept = workspace.mark_change_not_carried_out(started["id"], change_id, "Changed my mind")
    assert isinstance(kept, Refusal)
    assert kept.message == "A carried-out change stays in the record."
    assert (
        workspace.get_task(started["id"])["implementation_changes"][1]["approval"]["evidence"]
        == "The detail page shows the new export name"
    )

    other = _started(workspace, "Other")
    foreign = workspace.record_change(other["id"], "Drop the old export path", "consequential")
    foreign_id = foreign["implementation_changes"][0]["id"]
    cross = workspace.mark_change_not_carried_out(started["id"], foreign_id, "No")
    assert isinstance(cross, Refusal)
    assert cross.message == "The change must be on that task."
    missing = workspace.mark_change_not_carried_out(started["id"], 99999, "No")
    assert isinstance(missing, Refusal)
    assert missing.message == "Implementation change not found."

    workspace.connection.execute(
        "UPDATE task SET status = 'Completed' WHERE id = ?",
        (other["id"],),
    )
    forced = workspace.mark_change_not_carried_out(other["id"], foreign_id, "No")
    assert isinstance(forced, Refusal)
    assert forced.message == "The task must be In Progress."


def test_not_carried_out_does_not_block_cancel_or_complete(workspace):
    started = _started(workspace)
    waiting = workspace.record_change(started["id"], "Drop the old export path", "consequential")
    change_id = waiting["implementation_changes"][0]["id"]
    workspace.mark_change_not_carried_out(started["id"], change_id, "The old path is still required")
    cancelled = workspace.transition(started["id"], "cancel", "Superseded by another task")
    assert cancelled["status"] == "Cancelled"

    finished = _started(workspace, "Finished")
    criterion_id = finished["criteria"][0]["id"]
    workspace.verify_criterion(finished["id"], criterion_id, "Seen", "pass")
    recorded = workspace.record_change(finished["id"], "Drop the old export path", "consequential")
    workspace.mark_change_not_carried_out(
        finished["id"],
        recorded["implementation_changes"][0]["id"],
        "The old path is still required",
    )
    completed = workspace.transition(finished["id"], "complete")
    assert completed["status"] == "Completed"
