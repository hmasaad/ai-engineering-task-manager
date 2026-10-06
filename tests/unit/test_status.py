from task_manager.domain.results import Refusal


def _ready(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    return workspace.transition(created["id"], "mark_ready")


def test_start_verify_and_complete(workspace):
    ready = _ready(workspace)
    started = workspace.transition(ready["id"], "start")
    assert started["status"] == "In Progress"
    assert started["history"][-1]["cause_code"] == "started"
    assert started["history"][-1]["from_status"] == "Ready"

    criterion_id = started["criteria"][0]["id"]
    missing_pass = workspace.verify_criterion(
        started["id"], criterion_id, "The file included the goal.", "no"
    )
    assert isinstance(missing_pass, Refusal)
    assert workspace.get_task(started["id"])["criteria"][0]["state"] == "Unverified"

    verified = workspace.verify_criterion(
        started["id"], criterion_id, "The file included the goal.", "pass"
    )
    criterion = verified["criteria"][0]
    assert criterion["state"] == "Verified"
    assert criterion["provider_name"] == "Ada"
    assert criterion["pass_result"] == "pass"
    assert criterion["verified_at"]

    blocked = workspace.transition(verified["id"], "complete")
    # one criterion is verified, so this completes
    assert blocked["status"] == "Completed"


def test_complete_from_ready_is_refused(workspace):
    ready = _ready(workspace)
    refused = workspace.transition(ready["id"], "complete")
    assert isinstance(refused, Refusal)
    assert refused.code == 409
    assert "In Progress" in refused.message
    assert workspace.get_task(ready["id"])["status"] == "Ready"


def test_complete_names_unverified_criterion(workspace):
    ready = _ready(workspace)
    started = workspace.transition(ready["id"], "start")
    refused = workspace.transition(started["id"], "complete")
    assert isinstance(refused, Refusal)
    assert "The file contains the goal" in refused.message
    assert workspace.get_task(started["id"])["status"] == "In Progress"


def test_unverify_clears_evidence_without_status_change(workspace):
    ready = _ready(workspace)
    started = workspace.transition(ready["id"], "start")
    criterion_id = started["criteria"][0]["id"]
    workspace.verify_criterion(started["id"], criterion_id, "Seen", "pass")
    cleared = workspace.unverify_criterion(started["id"], criterion_id)
    criterion = cleared["criteria"][0]
    assert cleared["status"] == "In Progress"
    assert criterion["state"] == "Unverified"
    assert criterion["observation"] is None
    assert criterion["provider_name"] is None


def test_editing_verified_text_on_completed_task_reopens_it(workspace):
    ready = _ready(workspace)
    started = workspace.transition(ready["id"], "start")
    criterion_id = started["criteria"][0]["id"]
    workspace.verify_criterion(started["id"], criterion_id, "Seen", "pass")
    completed = workspace.transition(started["id"], "complete")
    edited = workspace.update_criterion(completed["id"], criterion_id, "The file contains the status")
    assert edited["status"] == "In Progress"
    assert edited["criteria"][0]["state"] == "Unverified"
    assert edited["history"][-1]["cause_code"] == "criterion_text_edited"


def test_reopen_keeps_verification_and_moves_completed_ancestors(workspace):
    parent = _ready(workspace, "Parent")
    parent = workspace.transition(parent["id"], "start")
    child = workspace.add_subtask(parent["id"], "Child")
    workspace.set_goal(child["id"], "Check the child")
    workspace.add_criterion(child["id"], "Child criterion")
    child = workspace.transition(child["id"], "mark_ready")
    child = workspace.transition(child["id"], "start")
    child_criterion = child["criteria"][0]["id"]
    workspace.verify_criterion(child["id"], child_criterion, "Child seen", "pass")
    child = workspace.transition(child["id"], "complete")
    parent_criterion = parent["criteria"][0]["id"]
    workspace.verify_criterion(parent["id"], parent_criterion, "Parent seen", "pass")
    parent = workspace.transition(parent["id"], "complete")
    assert parent["status"] == "Completed"

    reopened = workspace.transition(child["id"], "reopen", "A missed case was found")
    assert reopened["status"] == "In Progress"
    assert reopened["criteria"][0]["state"] == "Verified"
    assert reopened["history"][-1]["cause_code"] == "reopened"
    assert reopened["history"][-1]["cause_detail"] == "A missed case was found"
    parent_after = workspace.get_task(parent["id"])
    assert parent_after["status"] == "In Progress"
    assert parent_after["criteria"][0]["state"] == "Verified"
    assert parent_after["history"][-1]["cause_code"] == "reopened"


def test_cancel_is_final(workspace):
    ready = _ready(workspace)
    started = workspace.transition(ready["id"], "start")
    cancelled = workspace.transition(started["id"], "cancel", "Superseded by another task")
    assert cancelled["status"] == "Cancelled"
    assert cancelled["cancel_reason"] == "Superseded by another task"
    restored = workspace.transition(cancelled["id"], "start")
    assert isinstance(restored, Refusal)
    assert "new task" in restored.message.lower()
    assert workspace.get_task(cancelled["id"])["status"] == "Cancelled"
    edited = workspace.set_goal(cancelled["id"], "A different goal")
    assert isinstance(edited, Refusal)


def test_cancel_parent_blocked_by_draft_subtask(workspace):
    parent = _ready(workspace, "Parent")
    parent = workspace.transition(parent["id"], "start")
    workspace.add_subtask(parent["id"], "Still drafting")
    refused = workspace.transition(parent["id"], "cancel", "Stop")
    assert isinstance(refused, Refusal)
    assert "Still drafting" in refused.message
    assert workspace.get_task(parent["id"])["status"] == "In Progress"


def test_verify_requires_in_progress(workspace):
    ready = _ready(workspace)
    criterion_id = ready["criteria"][0]["id"]
    refused = workspace.verify_criterion(ready["id"], criterion_id, "Seen", "pass")
    assert isinstance(refused, Refusal)
    assert workspace.get_task(ready["id"])["criteria"][0]["state"] == "Unverified"
