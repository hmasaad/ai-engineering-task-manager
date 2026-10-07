from task_manager.domain.results import Refusal


def _started(workspace, title="Add export", criteria=("The file contains the goal",)):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    for text in criteria:
        workspace.add_criterion(created["id"], text)
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _verify_all(workspace, detail):
    current = detail
    for criterion in current["criteria"]:
        current = workspace.verify_criterion(current["id"], criterion["id"], "Seen", "pass")
    return current


def test_completion_names_a_carried_out_change_without_a_passing_check(workspace):
    started = _started(workspace)
    recorded = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    ready = _verify_all(workspace, recorded)
    before = list(ready["history"])
    refused = workspace.transition(ready["id"], "complete")
    assert isinstance(refused, Refusal)
    assert refused.code == 409
    assert refused.message == "Needs a passing check: Rename the export label."
    after = workspace.get_task(ready["id"])
    assert after["status"] == "In Progress"
    assert after["history"] == before

    change_id = after["implementation_changes"][0]["id"]
    criterion_id = after["criteria"][0]["id"]
    failed = workspace.record_check(ready["id"], change_id, criterion_id, "The label was still old", "Failed")
    refused = workspace.transition(failed["id"], "complete")
    assert refused.message == "Needs a passing check: Rename the export label."
    assert workspace.get_task(ready["id"])["status"] == "In Progress"

    passed = workspace.record_check(ready["id"], change_id, criterion_id, "The label now reads Export", "Passed")
    # The later pass is User Story 3. This story's single Passed check is the first one,
    # so replace the failed path with a fresh task below.
    assert passed["implementation_changes"][0]["checks"][-1]["result"] == "Passed"


def test_one_passed_check_completes_and_a_missing_check_does_not_block_cancel(workspace):
    started = _started(workspace, "Finish")
    recorded = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    change_id = recorded["implementation_changes"][0]["id"]
    criterion_id = recorded["criteria"][0]["id"]
    checked = workspace.record_check(recorded["id"], change_id, criterion_id, "Seen", "Passed")
    ready = _verify_all(workspace, checked)
    completed = workspace.transition(ready["id"], "complete")
    assert completed["status"] == "Completed"

    abandoned = _started(workspace, "Abandon")
    abandoned = workspace.record_change(abandoned["id"], "Rename the export label", "ordinary")
    cancelled = workspace.transition(abandoned["id"], "cancel", "Superseded by another task")
    assert cancelled["status"] == "Cancelled"

    plain = _started(workspace, "No changes")
    plain = _verify_all(workspace, plain)
    assert workspace.transition(plain["id"], "complete")["status"] == "Completed"


def test_not_carried_out_and_awaiting_approval_keep_their_existing_rules(workspace):
    started = _started(workspace)
    waiting = workspace.record_change(started["id"], "Replace the stored export name", "consequential")
    declined = workspace.mark_change_not_carried_out(
        waiting["id"], waiting["implementation_changes"][0]["id"], "The old path is still required"
    )
    ready = _verify_all(workspace, declined)
    assert workspace.transition(ready["id"], "complete")["status"] == "Completed"

    blocked = _started(workspace, "Waiting")
    blocked = workspace.record_change(blocked["id"], "Replace the stored export name", "consequential")
    blocked = _verify_all(workspace, blocked)
    refused = workspace.transition(blocked["id"], "complete")
    assert refused.message == "Awaiting approval: Replace the stored export name."
    assert "Needs a passing check:" not in refused.message

    mixed = _started(workspace, "Mixed")
    mixed = workspace.record_change(mixed["id"], "Rename the export label", "ordinary")
    mixed = workspace.record_change(mixed["id"], "Replace the stored export name", "consequential")
    mixed = _verify_all(workspace, mixed)
    refused = workspace.transition(mixed["id"], "complete")
    assert refused.message == (
        "Awaiting approval: Replace the stored export name. "
        "Needs a passing check: Rename the export label."
    )


def test_completion_names_only_the_changes_that_lack_a_passing_check(workspace):
    started = _started(workspace)
    started = workspace.record_change(started["id"], "First change", "ordinary")
    started = workspace.record_change(started["id"], "Second change", "ordinary")
    second_id = started["implementation_changes"][1]["id"]
    criterion_id = started["criteria"][0]["id"]
    started = workspace.record_check(started["id"], second_id, criterion_id, "Seen", "Passed")
    started = _verify_all(workspace, started)
    refused = workspace.transition(started["id"], "complete")
    assert refused.message == "Needs a passing check: First change."


def test_completion_keeps_the_earlier_sentences_and_ignores_subtask_checks(workspace):
    started = _started(workspace)
    started = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    refused = workspace.transition(started["id"], "complete")
    assert refused.message == (
        "Unverified criteria: The file contains the goal. "
        "Needs a passing check: Rename the export label."
    )

    with_sub = _started(workspace, "Parent")
    with_sub = _verify_all(workspace, with_sub)
    with_sub = workspace.record_change(with_sub["id"], "Rename the export label", "ordinary")
    workspace.add_subtask(with_sub["id"], "Write the checklist")
    refused = workspace.transition(with_sub["id"], "complete")
    assert refused.message == (
        "Unfinished subtasks: Write the checklist (Draft). "
        "Needs a passing check: Rename the export label."
    )

    parent = _started(workspace, "Top")
    parent = _verify_all(workspace, parent)
    child = workspace.add_subtask(parent["id"], "Write the checklist")
    workspace.set_goal(child["id"], "Take the record")
    workspace.add_criterion(child["id"], "Visible")
    child = workspace.transition(child["id"], "mark_ready")
    child = workspace.transition(child["id"], "start")
    child = workspace.record_change(child["id"], "Child-only export tweak", "ordinary")
    refused = workspace.transition(parent["id"], "complete")
    assert "Child-only export tweak" not in refused.message
    assert refused.message == "Unfinished subtasks: Write the checklist (In Progress)."

    alone = _started(workspace, "Criteria only")
    refused = workspace.transition(alone["id"], "complete")
    assert refused.message == "Unverified criteria: The file contains the goal."
