from task_manager.domain.results import Refusal


def _started(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_blank_what_changed_and_missing_class_write_nothing(workspace):
    started = _started(workspace)
    blank = workspace.record_change(started["id"], "   ", "ordinary")
    assert isinstance(blank, Refusal)
    assert blank.code == 400
    assert blank.message == "An account of what changed is required."
    missing_class = workspace.record_change(started["id"], "Rename the export label", None)
    assert isinstance(missing_class, Refusal)
    assert missing_class.message == "Choose ordinary or consequential."
    unknown = workspace.record_change(started["id"], "Rename the export label", "later")
    assert isinstance(unknown, Refusal)
    assert unknown.message == "Choose ordinary or consequential."
    assert workspace.get_task(started["id"])["implementation_changes"] == []


def test_ordinary_change_is_carried_out_without_touching_the_task(workspace):
    started = _started(workspace)
    before_history = list(started["history"])
    recorded = workspace.record_change(started["id"], "  Rename the export label  ", "ordinary")
    change = recorded["implementation_changes"][0]
    assert recorded["status"] == "In Progress"
    assert change["what_changed"] == "Rename the export label"
    assert change["class"] == "ordinary"
    assert change["outcome"] == "Carried out"
    assert change["engineer_name"] == "Ada"
    assert change["recorded_at"]
    assert change["approval"] is None
    assert change["not_carried_out"] is None
    assert recorded["criteria"][0]["state"] == "Unverified"
    assert recorded["decisions"] == []
    assert recorded["history"] == before_history
    missing = workspace.record_change(99999, "Rename the export label", "ordinary")
    assert isinstance(missing, Refusal)
    assert missing.code == 404
    assert missing.message == "Task not found."


def test_consequential_change_waits_and_changes_are_ordered(workspace):
    started = _started(workspace)
    first = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    second = workspace.record_change(started["id"], "Write the export steps", "consequential")
    changes = second["implementation_changes"]
    assert [item["what_changed"] for item in changes] == [
        "Rename the export label",
        "Write the export steps",
    ]
    assert changes[1]["outcome"] == "Awaiting approval"
    assert changes[1]["approval"] is None
    assert second["status"] == "In Progress"
    other = workspace.create_task("Other")
    assert workspace.get_task(other["id"])["implementation_changes"] == []
    assert first["implementation_changes"][0]["id"] != changes[1]["id"]


def test_record_is_refused_unless_the_task_is_in_progress(workspace):
    draft = workspace.create_task("Draft task")
    refused = workspace.record_change(draft["id"], "Rename the export label", "ordinary")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    ready = workspace.create_task("Ready task")
    workspace.set_goal(ready["id"], "Take the record")
    workspace.add_criterion(ready["id"], "Visible")
    ready = workspace.transition(ready["id"], "mark_ready")
    refused = workspace.record_change(ready["id"], "Rename the export label", "ordinary")
    assert refused.message == "Start the task first."

    completed = _started(workspace, "Done task")
    criterion_id = completed["criteria"][0]["id"]
    workspace.verify_criterion(completed["id"], criterion_id, "Seen", "pass")
    completed = workspace.transition(completed["id"], "complete")
    refused = workspace.record_change(completed["id"], "Rename the export label", "ordinary")
    assert refused.message == "Reopen the task first."

    cancelled = _started(workspace, "Cancelled task")
    cancelled = workspace.transition(cancelled["id"], "cancel", "Superseded by another task")
    refused = workspace.record_change(cancelled["id"], "Rename the export label", "ordinary")
    assert refused.message == "A cancelled task cannot be changed. Continued work is a new task."
