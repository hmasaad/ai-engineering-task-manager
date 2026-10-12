from task_manager.domain.results import Refusal


def _started(workspace):
    task = workspace.create_task("Add export")
    workspace.set_goal(task["id"], "Take the record")
    task = workspace.add_criterion(task["id"], "The export contains the goal")
    workspace.transition(task["id"], "mark_ready")
    return workspace.transition(task["id"], "start")


def _linked(workspace):
    started = _started(workspace)
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    workspace.link_requirement_task(requirement["id"], started["id"])
    criterion_id = started["criteria"][0]["id"]
    requirement = workspace.link_requirement_criterion(requirement["id"], started["id"], criterion_id)
    return started, requirement, criterion_id


def test_a_named_check_and_its_latest_run(workspace):
    _started_task, requirement, _criterion_id = _linked(workspace)
    named = workspace.name_requirement_check(requirement["id"], "export shows the goal")
    duplicate = workspace.name_requirement_check(requirement["id"], "export shows the goal")
    assert isinstance(duplicate, Refusal)
    assert duplicate.message == "That check is already named on this requirement."
    blank = workspace.name_requirement_check(requirement["id"], "  ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name the check this requirement uses."
    passed = workspace.record_requirement_run(
        named["id"], "export shows the goal", "Passed", "local-1"
    )
    assert passed["checks"][0]["current_result"] == "Passed"
    assert passed["checks"][0]["runs"][0]["engineer_name"] == "Ada"
    assert passed["checks"][0]["runs"][0]["run_identifier"] == "local-1"
    failed = workspace.record_requirement_run(
        named["id"], "export shows the goal", "Failed", "local-2"
    )
    assert len(failed["checks"][0]["runs"]) == 2
    assert failed["checks"][0]["current_result"] == "Failed"


def test_run_refusals(workspace):
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    workspace.name_requirement_check(requirement["id"], "export shows the goal")
    blank_run = workspace.record_requirement_run(
        requirement["id"], "export shows the goal", "Passed", "  "
    )
    assert isinstance(blank_run, Refusal)
    assert blank_run.message == "A run identifier is required."
    bad_result = workspace.record_requirement_run(
        requirement["id"], "export shows the goal", "Maybe", "local-1"
    )
    assert isinstance(bad_result, Refusal)
    assert bad_result.message == "Choose Passed or Failed."
    unknown = workspace.record_requirement_run(requirement["id"], "missing", "Passed", "local-1")
    assert isinstance(unknown, Refusal)
    assert unknown.message == "Check not found."
    assert workspace.get_requirement(requirement["id"])["checks"][0]["runs"] == []


def test_a_failed_check_blocks_verification_and_completion(workspace):
    started, requirement, criterion_id = _linked(workspace)
    workspace.name_requirement_check(requirement["id"], "export shows the goal")
    refused = workspace.verify_criterion(
        started["id"], criterion_id, "The page shows the goal", "pass"
    )
    assert isinstance(refused, Refusal)
    assert refused.message == "A required check has not passed."
    assert workspace.get_task(started["id"])["criteria"][0]["state"] == "Unverified"
    workspace.record_requirement_run(requirement["id"], "export shows the goal", "Failed", "local-1")
    refused = workspace.verify_criterion(
        started["id"], criterion_id, "The page shows the goal", "pass"
    )
    assert isinstance(refused, Refusal)
    assert refused.message == "A required check has not passed."
    held = workspace.transition(started["id"], "complete")
    assert isinstance(held, Refusal)
    assert "A required check has not passed: REQ-1" in held.message


def test_completion_sentence_follows_the_existing_sentences(workspace):
    started, requirement, _criterion_id = _linked(workspace)
    workspace.name_requirement_check(requirement["id"], "export shows the goal")
    workspace.record_requirement_run(requirement["id"], "export shows the goal", "Failed", "local-1")
    workspace.add_subtask(started["id"], "Write the note")
    workspace.record_change(started["id"], "Rename the export label", "ordinary")
    workspace.record_change(started["id"], "Wait for review", "consequential")
    refused = workspace.transition(started["id"], "complete")
    assert isinstance(refused, Refusal)
    assert refused.message == (
        "Unverified criteria: The export contains the goal. "
        "Unfinished subtasks: Write the note (Draft). "
        "Awaiting approval: Wait for review. "
        "Needs a passing check: Rename the export label. "
        "A required check has not passed: REQ-1."
    )


def test_an_unlinked_criterion_can_still_be_verified(workspace):
    started = _started(workspace)
    verified = workspace.verify_criterion(
        started["id"], started["criteria"][0]["id"], "The page shows the goal", "pass"
    )
    assert verified["criteria"][0]["state"] == "Verified"


def test_removing_a_check_ends_the_hold_and_a_new_name_starts_empty(workspace):
    started, requirement, criterion_id = _linked(workspace)
    named = workspace.name_requirement_check(requirement["id"], "export shows the goal")
    workspace.record_requirement_run(requirement["id"], "export shows the goal", "Failed", "local-1")
    check_id = named["checks"][0]["id"]
    removed = workspace.remove_requirement_check(requirement["id"], check_id)
    assert removed["checks"] == []
    assert removed["removed_checks"][0]["runs"][0]["run_identifier"] == "local-1"
    verified = workspace.verify_criterion(
        started["id"], criterion_id, "The page shows the goal", "pass"
    )
    assert verified["criteria"][0]["state"] == "Verified"
    again = workspace.name_requirement_check(requirement["id"], "export shows the goal")
    assert again["checks"][0]["current_result"] is None
    assert again["checks"][0]["runs"] == []
    assert again["removed_checks"][0]["runs"][0]["result"] == "Failed"
    unknown = workspace.remove_requirement_check(requirement["id"], check_id)
    assert isinstance(unknown, Refusal)
    assert unknown.message == "Check not found."


def test_a_requirement_on_a_subtask_does_not_block_the_parent(workspace):
    parent = workspace.create_task("Ship the export")
    workspace.set_goal(parent["id"], "Take the record")
    parent = workspace.add_criterion(parent["id"], "The parent still holds")
    workspace.transition(parent["id"], "mark_ready")
    parent = workspace.transition(parent["id"], "start")
    child = workspace.add_subtask(parent["id"], "Add export")
    workspace.set_goal(child["id"], "Take the record")
    child = workspace.add_criterion(child["id"], "The export contains the goal")
    workspace.transition(child["id"], "mark_ready")
    child = workspace.transition(child["id"], "start")
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    workspace.link_requirement_task(requirement["id"], child["id"])
    workspace.link_requirement_criterion(
        requirement["id"], child["id"], child["criteria"][0]["id"]
    )
    workspace.name_requirement_check(requirement["id"], "export shows the goal")
    workspace.record_requirement_run(
        requirement["id"], "export shows the goal", "Failed", "local-1"
    )
    child_held = workspace.transition(child["id"], "complete")
    assert isinstance(child_held, Refusal)
    assert "A required check has not passed: REQ-1" in child_held.message
    parent_held = workspace.transition(parent["id"], "complete")
    assert isinstance(parent_held, Refusal)
    assert "A required check has not passed" not in parent_held.message
