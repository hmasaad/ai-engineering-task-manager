from task_manager.domain.results import Refusal


def _started(workspace, title="Add export", criteria=("The file contains the goal",)):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    for text in criteria:
        workspace.add_criterion(created["id"], text)
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _ordinary(workspace, title="Add export", what="Rename the export label"):
    started = _started(workspace, title)
    recorded = workspace.record_change(started["id"], what, "ordinary")
    return recorded


def test_blank_evidence_missing_result_and_missing_criterion_write_nothing(workspace):
    started = _ordinary(workspace)
    task_id = started["id"]
    change_id = started["implementation_changes"][0]["id"]
    criterion_id = started["criteria"][0]["id"]

    blank = workspace.record_check(task_id, change_id, criterion_id, "   ", "Passed")
    assert isinstance(blank, Refusal)
    assert blank.code == 400
    assert blank.message == "An account of the evidence is required."

    missing_result = workspace.record_check(task_id, change_id, criterion_id, "Seen", None)
    assert isinstance(missing_result, Refusal)
    assert missing_result.message == "Choose Passed or Failed."
    unknown_result = workspace.record_check(task_id, change_id, criterion_id, "Seen", "later")
    assert isinstance(unknown_result, Refusal)
    assert unknown_result.message == "Choose Passed or Failed."

    missing_criterion = workspace.record_check(task_id, change_id, None, "Seen", "Passed")
    assert isinstance(missing_criterion, Refusal)
    assert missing_criterion.message == "Choose an acceptance criterion."

    both = workspace.record_check(task_id, change_id, criterion_id, "  ", "later")
    assert isinstance(both, Refusal)
    assert both.message == "An account of the evidence is required."
    assert workspace.get_task(task_id)["implementation_changes"][0]["checks"] == []


def test_passed_and_failed_checks_do_not_touch_the_task(workspace):
    started = _ordinary(workspace)
    task_id = started["id"]
    change_id = started["implementation_changes"][0]["id"]
    criterion_id = started["criteria"][0]["id"]
    before_history = list(started["history"])

    recorded = workspace.record_check(
        task_id, change_id, criterion_id, "  The detail page shows the goal in the export  ", "Passed"
    )
    change = recorded["implementation_changes"][0]
    check = change["checks"][0]
    assert recorded["status"] == "In Progress"
    assert change["outcome"] == "Carried out"
    assert recorded["criteria"][0]["state"] == "Unverified"
    assert recorded["decisions"] == []
    assert recorded["history"] == before_history
    assert check["criterion_id"] == criterion_id
    assert check["criterion_text"] == "The file contains the goal"
    assert check["evidence"] == "The detail page shows the goal in the export"
    assert check["result"] == "Passed"
    assert check["engineer_name"] == "Ada"
    assert check["checked_at"]

    failed = workspace.record_check(task_id, change_id, criterion_id, "The label was still old", "Failed")
    assert failed["status"] == "In Progress"
    assert failed["implementation_changes"][0]["outcome"] == "Carried out"
    assert failed["implementation_changes"][0]["checks"][1]["result"] == "Failed"

    missing_task = workspace.record_check(99999, change_id, criterion_id, "Seen", "Passed")
    assert isinstance(missing_task, Refusal)
    assert missing_task.code == 404
    assert missing_task.message == "Task not found."
    missing_change = workspace.record_check(task_id, 99999, criterion_id, "Seen", "Passed")
    assert isinstance(missing_change, Refusal)
    assert missing_change.message == "Implementation change not found."
    missing_criterion = workspace.record_check(task_id, change_id, 99999, "Seen", "Passed")
    assert isinstance(missing_criterion, Refusal)
    assert missing_criterion.message == "Acceptance criterion not found."


def test_check_is_refused_unless_the_change_is_carried_out_on_that_task(workspace):
    started = _started(workspace)
    task_id = started["id"]
    criterion_id = started["criteria"][0]["id"]
    waiting = workspace.record_change(task_id, "Replace the stored export name", "consequential")
    waiting_id = waiting["implementation_changes"][0]["id"]
    refused = workspace.record_check(task_id, waiting_id, criterion_id, "Seen", "Passed")
    assert isinstance(refused, Refusal)
    assert refused.code == 409
    assert refused.message == "The change must be carried out before it can be checked."
    assert workspace.get_task(task_id)["implementation_changes"][0]["outcome"] == "Awaiting approval"

    declined = workspace.mark_change_not_carried_out(task_id, waiting_id, "The old path is still required")
    refused = workspace.record_check(task_id, waiting_id, criterion_id, "Seen", "Passed")
    assert refused.message == "A change that was not carried out cannot be checked."
    assert declined["implementation_changes"][0]["outcome"] == "Not carried out"

    approved = _started(workspace, "Approved task")
    consequential = workspace.record_change(approved["id"], "Replace the stored export name", "consequential")
    change_id = consequential["implementation_changes"][0]["id"]
    carried = workspace.approve_change(approved["id"], change_id, "The detail page shows the new export name")
    checked = workspace.record_check(
        approved["id"], change_id, approved["criteria"][0]["id"], "Seen on the page", "Passed"
    )
    assert checked["implementation_changes"][0]["outcome"] == "Carried out"
    assert checked["implementation_changes"][0]["checks"][0]["result"] == "Passed"
    assert carried["status"] == "In Progress"


def test_check_names_a_change_and_criterion_on_that_task(workspace):
    first = _ordinary(workspace, "First task")
    second = _ordinary(workspace, "Second task", "Write the export steps")
    refused_change = workspace.record_check(
        second["id"],
        first["implementation_changes"][0]["id"],
        second["criteria"][0]["id"],
        "Seen",
        "Passed",
    )
    assert isinstance(refused_change, Refusal)
    assert refused_change.message == "The check must name a change on that task."
    refused_criterion = workspace.record_check(
        first["id"],
        first["implementation_changes"][0]["id"],
        second["criteria"][0]["id"],
        "Seen",
        "Passed",
    )
    assert refused_criterion.message == "The check must name a criterion on that task."
    assert workspace.get_task(first["id"])["implementation_changes"][0]["checks"] == []


def test_check_is_refused_unless_the_task_is_in_progress(workspace):
    draft = workspace.create_task("Draft task")
    refused = workspace.record_check(draft["id"], 1, 1, "   ", None)
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    ready = workspace.create_task("Ready task")
    workspace.set_goal(ready["id"], "Take the record")
    workspace.add_criterion(ready["id"], "Visible")
    ready = workspace.transition(ready["id"], "mark_ready")
    refused = workspace.record_check(ready["id"], 1, 1, "   ", None)
    assert refused.message == "Start the task first."

    completed = _ordinary(workspace, "Done task")
    criterion_id = completed["criteria"][0]["id"]
    workspace.verify_criterion(completed["id"], criterion_id, "Seen", "pass")
    change_id = completed["implementation_changes"][0]["id"]
    workspace.record_check(completed["id"], change_id, criterion_id, "Seen", "Passed")
    completed = workspace.transition(completed["id"], "complete")
    refused = workspace.record_check(completed["id"], change_id, criterion_id, "   ", None)
    assert refused.message == "Reopen the task first."

    cancelled = _started(workspace, "Cancelled task")
    cancelled = workspace.transition(cancelled["id"], "cancel", "Superseded by another task")
    refused = workspace.record_check(cancelled["id"], 1, 1, "Seen", "Passed")
    assert refused.message == "A cancelled task cannot be changed. Continued work is a new task."
