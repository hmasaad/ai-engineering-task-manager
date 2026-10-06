from task_manager.domain.results import Refusal


def _in_progress(workspace, title, criterion="Done when checked"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], f"Goal for {title}")
    workspace.add_criterion(created["id"], criterion)
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_subtask_is_draft_with_one_parent_and_listed_in_creation_order(workspace):
    parent = _in_progress(workspace, "Parent")
    first = workspace.add_subtask(parent["id"], "Write the checklist")
    second = workspace.add_subtask(parent["id"], "Record the result")
    assert first["status"] == "Draft"
    assert first["parent_id"] == parent["id"]
    detail = workspace.get_task(parent["id"])
    assert [item["title"] for item in detail["subtasks"]] == [
        "Write the checklist",
        "Record the result",
    ]


def test_cycle_and_second_parent_are_refused(workspace):
    parent = workspace.create_task("Parent")
    child = workspace.add_subtask(parent["id"], "Child")
    cycle = workspace.attach(parent["id"], child["id"])
    assert isinstance(cycle, Refusal)
    assert "ancestor" in cycle.message.lower()
    assert workspace.get_task(parent["id"])["parent_id"] is None

    other = workspace.create_task("Other")
    second = workspace.attach(child["id"], other["id"])
    assert isinstance(second, Refusal)
    assert "one parent" in second.message.lower()
    assert workspace.get_task(child["id"])["parent_id"] == parent["id"]


def test_parent_completion_names_unfinished_subtask(workspace):
    parent = _in_progress(workspace, "Parent", "Parent criterion")
    child = workspace.add_subtask(parent["id"], "Still ready")
    workspace.set_goal(child["id"], "Child goal")
    workspace.add_criterion(child["id"], "Child criterion")
    workspace.transition(child["id"], "mark_ready")
    criterion_id = parent["criteria"][0]["id"]
    workspace.verify_criterion(parent["id"], criterion_id, "Parent seen", "pass")
    refused = workspace.transition(parent["id"], "complete")
    assert isinstance(refused, Refusal)
    assert "Still ready" in refused.message
    assert workspace.get_task(parent["id"])["status"] == "In Progress"


def test_completed_subtask_does_not_block_parent(workspace):
    parent = _in_progress(workspace, "Parent", "Parent criterion")
    child = workspace.add_subtask(parent["id"], "Finished child")
    workspace.set_goal(child["id"], "Child goal")
    workspace.add_criterion(child["id"], "Child criterion")
    child = workspace.transition(child["id"], "mark_ready")
    child = workspace.transition(child["id"], "start")
    workspace.verify_criterion(child["id"], child["criteria"][0]["id"], "Child seen", "pass")
    workspace.transition(child["id"], "complete")
    workspace.verify_criterion(parent["id"], parent["criteria"][0]["id"], "Parent seen", "pass")
    completed = workspace.transition(parent["id"], "complete")
    assert completed["status"] == "Completed"


def test_unfinished_grandchild_blocks_the_chain(workspace):
    parent = _in_progress(workspace, "Parent", "Parent criterion")
    child = workspace.add_subtask(parent["id"], "Child")
    workspace.set_goal(child["id"], "Child goal")
    workspace.add_criterion(child["id"], "Child criterion")
    child = workspace.transition(child["id"], "mark_ready")
    child = workspace.transition(child["id"], "start")
    grandchild = workspace.add_subtask(child["id"], "Grandchild")
    workspace.set_goal(grandchild["id"], "Grandchild goal")
    workspace.add_criterion(grandchild["id"], "Grandchild criterion")
    workspace.transition(grandchild["id"], "mark_ready")
    workspace.verify_criterion(child["id"], child["criteria"][0]["id"], "Child seen", "pass")
    refused = workspace.transition(child["id"], "complete")
    assert isinstance(refused, Refusal)
    assert "Grandchild" in refused.message
    workspace.verify_criterion(parent["id"], parent["criteria"][0]["id"], "Parent seen", "pass")
    parent_refused = workspace.transition(parent["id"], "complete")
    assert isinstance(parent_refused, Refusal)
    assert workspace.get_task(parent["id"])["status"] == "In Progress"


def test_completed_parent_refuses_a_new_subtask(workspace):
    parent = _in_progress(workspace, "Parent", "Parent criterion")
    workspace.verify_criterion(parent["id"], parent["criteria"][0]["id"], "Seen", "pass")
    completed = workspace.transition(parent["id"], "complete")
    refused = workspace.add_subtask(completed["id"], "Too late")
    assert isinstance(refused, Refusal)
    assert "reopen" in refused.message.lower()
    assert workspace.get_task(completed["id"])["subtasks"] == []
