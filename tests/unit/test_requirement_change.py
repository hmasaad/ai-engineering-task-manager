from task_manager.domain.results import Refusal


def _completed(workspace, title="Add export"):
    task = workspace.create_task(title)
    workspace.set_goal(task["id"], "Take the record")
    task = workspace.add_criterion(task["id"], "The export contains the goal")
    workspace.transition(task["id"], "mark_ready")
    task = workspace.transition(task["id"], "start")
    criterion_id = task["criteria"][0]["id"]
    workspace.verify_criterion(task["id"], criterion_id, "The page shows the goal", "pass", "inspection", "local-1")
    completed = workspace.transition(task["id"], "complete")
    return completed, criterion_id


def test_an_unchanged_save_leaves_a_completed_task(workspace):
    completed, criterion_id = _completed(workspace)
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    workspace.link_requirement_task(requirement["id"], completed["id"])
    workspace.link_requirement_criterion(requirement["id"], completed["id"], criterion_id)
    workspace.name_requirement_check(requirement["id"], "export shows the goal")
    workspace.record_requirement_run(
        requirement["id"], "export shows the goal", "Passed", "local-1"
    )
    saved = workspace.change_requirement(
        requirement["id"], "  The export contains the goal  ", "functional"
    )
    assert saved["statement"] == "The export contains the goal"
    task = workspace.get_task(completed["id"])
    assert task["status"] == "Completed"
    assert task["criteria"][0]["state"] == "Verified"
    assert all(item["cause_code"] != "requirement_changed" for item in task["history"])
    assert saved["checks"][0]["runs"][0]["run_identifier"] == "local-1"


def test_a_blank_replacement_is_refused(workspace):
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    refused = workspace.change_requirement(requirement["id"], "  ", "functional")
    assert isinstance(refused, Refusal)
    assert refused.message == "A requirement statement is required."
    assert workspace.get_requirement(requirement["id"])["statement"] == "The export contains the goal"


def test_a_statement_change_reopens_the_task_and_its_parent(workspace):
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
    child_criterion = child["criteria"][0]["id"]
    workspace.verify_criterion(child["id"], child_criterion, "The page shows the goal", "pass", "inspection", "local-1")
    workspace.transition(child["id"], "complete")
    parent_criterion = parent["criteria"][0]["id"]
    workspace.verify_criterion(parent["id"], parent_criterion, "The parent page shows it", "pass", "inspection", "local-1")
    workspace.transition(parent["id"], "complete")

    requirement = workspace.record_requirement("The export contains the goal", "functional")
    workspace.link_requirement_task(requirement["id"], child["id"])
    workspace.link_requirement_criterion(requirement["id"], child["id"], child_criterion)
    workspace.name_requirement_check(requirement["id"], "export shows the goal")
    workspace.record_requirement_run(
        requirement["id"], "export shows the goal", "Passed", "local-1"
    )
    changed = workspace.change_requirement(
        requirement["id"], "The export contains the revised goal", "functional"
    )
    assert changed["identifier"] == requirement["identifier"]
    assert changed["checks"][0]["runs"][0]["run_identifier"] == "local-1"
    child_after = workspace.get_task(child["id"])
    parent_after = workspace.get_task(parent["id"])
    assert child_after["status"] == "In Progress"
    assert child_after["criteria"][0]["state"] == "Unverified"
    assert any(item["cause_code"] == "requirement_changed" for item in child_after["history"])
    assert parent_after["status"] == "In Progress"
    assert parent_after["criteria"][0]["state"] == "Verified"
