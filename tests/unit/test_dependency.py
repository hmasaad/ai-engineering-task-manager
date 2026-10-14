from task_manager.domain.results import Refusal


def _task(workspace, title):
    return workspace.create_task(title)


def _ready(workspace, title, criterion="The export contains the goal"):
    created = _task(workspace, title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], criterion)
    return workspace.transition(created["id"], "mark_ready")


def _complete(workspace, title, criterion="The label is recorded"):
    ready = _ready(workspace, title, criterion)
    started = workspace.transition(ready["id"], "start")
    criterion_id = started["criteria"][0]["id"]
    workspace.verify_criterion(
        started["id"], criterion_id, criterion, "pass", "inspection", "local-1"
    )
    return workspace.transition(started["id"], "complete")


def test_a_prerequisite_is_stored_once_and_a_cycle_is_refused(workspace):
    export = _task(workspace, "Add export")
    label = _task(workspace, "Write the label")
    linked = workspace.add_prerequisite(export["id"], label["id"])
    assert linked["status"] == "Draft"
    assert label["status"] == "Draft"
    assert linked["prerequisites"] == [
        {"id": label["id"], "title": "Write the label", "status": "Draft"}
    ]
    again = workspace.add_prerequisite(export["id"], label["id"])
    assert again["prerequisites"] == linked["prerequisites"]
    opened = workspace.get_task(export["id"])
    assert opened["prerequisites"] == linked["prerequisites"]

    itself = workspace.add_prerequisite(export["id"], export["id"])
    assert isinstance(itself, Refusal)
    assert itself.message == "A task cannot depend on itself."
    missing = workspace.add_prerequisite(export["id"], 999)
    assert missing.message == "Prerequisite not found."
    unknown = workspace.add_prerequisite(999, label["id"])
    assert unknown.message == "Task not found."

    chosen = _task(workspace, "Choose the format")
    workspace.add_prerequisite(label["id"], chosen["id"])
    cycle = workspace.add_prerequisite(chosen["id"], export["id"])
    assert isinstance(cycle, Refusal)
    assert cycle.message == "That dependency would form a cycle."
    assert workspace.get_task(chosen["id"])["prerequisites"] == []
    assert workspace.get_task(export["id"])["prerequisites"][0]["id"] == label["id"]

    removed = workspace.remove_prerequisite(export["id"], label["id"])
    assert removed["prerequisites"] == []
    absent = workspace.remove_prerequisite(export["id"], label["id"])
    assert absent.message == "That prerequisite is not linked."

    cancelled = workspace.transition(chosen["id"], "cancel", "Not needed")
    refused = workspace.add_prerequisite(cancelled["id"], label["id"])
    assert refused.message == "A cancelled task cannot be changed. Continued work is a new task."


def test_execution_order_places_each_prerequisite_first(workspace):
    export = _task(workspace, "Add export")
    label = _task(workspace, "Write the label")
    chosen = _task(workspace, "Choose the format")
    other = _task(workspace, "Note the owner")
    workspace.add_prerequisite(export["id"], label["id"])
    workspace.add_prerequisite(label["id"], chosen["id"])
    order = workspace.execution_order()
    titles = [item["title"] for item in order]
    assert titles.index("Choose the format") < titles.index("Write the label")
    assert titles.index("Write the label") < titles.index("Add export")
    assert titles == ["Choose the format", "Write the label", "Add export", "Note the owner"]
    assert other["id"] == order[-1]["id"]
    again = workspace.execution_order()
    assert again == order
    assert workspace.get_task(export["id"])["status"] == "Draft"


def test_start_is_held_until_every_prerequisite_is_completed(workspace):
    label = _ready(workspace, "Write the label", "The label is recorded")
    export = _ready(workspace, "Add export")
    workspace.add_prerequisite(export["id"], label["id"])
    assert export["status"] == "Ready"
    held = workspace.transition(export["id"], "start")
    assert isinstance(held, Refusal)
    assert held.message == "Blocked by Write the label (Ready): unverified The label is recorded."
    assert workspace.get_task(export["id"])["status"] == "Ready"
    assert workspace.get_task(export["id"])["blocked_by"] == held.message

    started_label = workspace.transition(label["id"], "start")
    held = workspace.transition(export["id"], "start")
    assert held.message == "Blocked by Write the label (In Progress): unverified The label is recorded."

    draft = _task(workspace, "Leave a note")
    workspace.add_prerequisite(draft["id"], label["id"])
    too_soon = workspace.transition(draft["id"], "start")
    assert too_soon.message == "The task must be Ready to start work."

    criterion_id = started_label["criteria"][0]["id"]
    workspace.verify_criterion(
        started_label["id"],
        criterion_id,
        "The label is recorded",
        "pass",
        "inspection",
        "local-1",
    )
    completed = workspace.transition(started_label["id"], "complete")
    assert completed["status"] == "Completed"
    started = workspace.transition(export["id"], "start")
    assert started["status"] == "In Progress"
    assert started["blocked_by"] is None

    reopened = workspace.transition(completed["id"], "reopen", "A missed case was found")
    assert reopened["status"] == "In Progress"
    current = workspace.get_task(export["id"])
    assert current["status"] == "In Progress"
    assert current["blocked_by"] == "Blocked by Write the label (In Progress): incomplete."


def test_an_incomplete_prerequisite_without_unverified_criteria_is_named(workspace):
    label = _complete(workspace, "Write the label")
    export = _ready(workspace, "Add export")
    other = _task(workspace, "Choose the format")
    workspace.add_prerequisite(export["id"], label["id"])
    workspace.add_prerequisite(export["id"], other["id"])
    workspace.transition(label["id"], "reopen", "A missed case was found")
    held = workspace.transition(export["id"], "start")
    assert held.message == (
        "Blocked by Write the label (In Progress): incomplete. "
        "Blocked by Choose the format (Draft): incomplete."
    )
    assert workspace.get_task(export["id"])["status"] == "Ready"

    cancelled = workspace.transition(other["id"], "cancel", "Not needed")
    held = workspace.transition(export["id"], "start")
    assert "Blocked by Choose the format (Cancelled): incomplete." in held.message
    assert cancelled["status"] == "Cancelled"

    workspace.remove_prerequisite(export["id"], label["id"])
    workspace.remove_prerequisite(export["id"], other["id"])
    started = workspace.transition(export["id"], "start")
    assert started["status"] == "In Progress"
