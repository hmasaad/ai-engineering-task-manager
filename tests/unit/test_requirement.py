from task_manager.domain.results import Refusal


def _started(workspace, title="Add export"):
    task = workspace.create_task(title)
    workspace.set_goal(task["id"], "Take the record")
    task = workspace.add_criterion(task["id"], "The export contains the goal")
    workspace.transition(task["id"], "mark_ready")
    return workspace.transition(task["id"], "start")


def test_a_requirement_keeps_its_identifier(workspace):
    first = workspace.record_requirement("The export contains the goal", "functional")
    second = workspace.record_requirement("The export page opens promptly", "non-functional")
    assert first["identifier"] == "REQ-1"
    assert first["kind"] == "functional"
    assert first["statement"] == "The export contains the goal"
    assert second["identifier"] == "REQ-2"
    assert second["kind"] == "non-functional"
    again = workspace.get_requirement(first["id"])
    assert again["identifier"] == "REQ-1"
    assert again["statement"] == "The export contains the goal"


def test_blank_statement_is_refused_before_kind(workspace):
    refused = workspace.record_requirement("  ", "nope")
    assert isinstance(refused, Refusal)
    assert refused.message == "A requirement statement is required."
    assert workspace.list_requirements() == []


def test_unknown_kind_is_refused(workspace):
    refused = workspace.record_requirement("The export contains the goal", "maybe")
    assert isinstance(refused, Refusal)
    assert refused.message == "Choose functional or non-functional."


def test_link_a_task_and_a_criterion(workspace):
    started = _started(workspace)
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    linked = workspace.link_requirement_task(requirement["id"], started["id"])
    criterion_id = started["criteria"][0]["id"]
    linked = workspace.link_requirement_criterion(requirement["id"], started["id"], criterion_id)
    assert linked["tasks"][0]["title"] == "Add export"
    assert linked["criteria"][0]["text"] == "The export contains the goal"
    task = workspace.get_task(started["id"])
    assert task["requirements"][0]["identifier"] == "REQ-1"


def test_a_criterion_from_another_task_is_refused(workspace):
    first = _started(workspace, "Add export")
    second = _started(workspace, "Add import")
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    workspace.link_requirement_task(requirement["id"], first["id"])
    refused = workspace.link_requirement_criterion(
        requirement["id"], first["id"], second["criteria"][0]["id"]
    )
    assert isinstance(refused, Refusal)
    assert refused.message == "The criterion must be on that task."


def test_a_criterion_requires_the_task_link_first(workspace):
    started = _started(workspace)
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    refused = workspace.link_requirement_criterion(
        requirement["id"], started["id"], started["criteria"][0]["id"]
    )
    assert isinstance(refused, Refusal)
    assert refused.message == "The criterion must be on that task."


def test_unknown_requirement_and_task(workspace):
    started = _started(workspace)
    missing_requirement = workspace.link_requirement_task(999, started["id"])
    assert isinstance(missing_requirement, Refusal)
    assert missing_requirement.message == "Requirement not found."
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    missing_task = workspace.link_requirement_task(requirement["id"], 999)
    assert isinstance(missing_task, Refusal)
    assert missing_task.message == "Task not found."


def test_duplicate_links(workspace):
    started = _started(workspace)
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    workspace.link_requirement_task(requirement["id"], started["id"])
    again = workspace.link_requirement_task(requirement["id"], started["id"])
    assert len(again["tasks"]) == 1
    criterion_id = started["criteria"][0]["id"]
    workspace.link_requirement_criterion(requirement["id"], started["id"], criterion_id)
    duplicate = workspace.link_requirement_criterion(requirement["id"], started["id"], criterion_id)
    assert isinstance(duplicate, Refusal)
    assert duplicate.message == "That criterion is already linked to this requirement."


def test_an_unlinked_task_still_completes(workspace):
    started = _started(workspace)
    workspace.record_requirement("The export contains the goal", "functional")
    criterion_id = started["criteria"][0]["id"]
    workspace.verify_criterion(started["id"], criterion_id, "The page shows the goal", "pass", "inspection", "local-1")
    completed = workspace.transition(started["id"], "complete")
    assert completed["status"] == "Completed"


def test_removing_a_criterion_removes_only_that_link(workspace):
    started = _started(workspace)
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    workspace.link_requirement_task(requirement["id"], started["id"])
    criterion_id = started["criteria"][0]["id"]
    workspace.link_requirement_criterion(requirement["id"], started["id"], criterion_id)
    workspace.add_criterion(started["id"], "A second criterion")
    workspace.remove_criterion(started["id"], criterion_id)
    remaining = workspace.get_requirement(requirement["id"])
    assert remaining["criteria"] == []
    assert remaining["tasks"][0]["id"] == started["id"]
