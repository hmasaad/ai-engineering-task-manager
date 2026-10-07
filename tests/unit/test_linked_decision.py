from task_manager.domain.results import Refusal


def _started(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _checked(workspace, title="Add export", result="Passed", evidence="The detail page shows the goal in the export"):
    started = _started(workspace, title)
    recorded = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    criterion_id = recorded["criteria"][0]["id"]
    change_id = recorded["implementation_changes"][0]["id"]
    checked = workspace.record_check(recorded["id"], change_id, criterion_id, evidence, result)
    check_id = checked["implementation_changes"][0]["checks"][-1]["id"]
    return checked, check_id


def _link_count(workspace) -> int:
    return int(workspace.connection.execute("SELECT COUNT(*) FROM decision_check").fetchone()[0])


def test_blank_statement_and_missing_check_write_nothing(workspace):
    checked, check_id = _checked(workspace)
    task_id = checked["id"]
    before = workspace.get_task(task_id)

    blank = workspace.add_linked_decision(task_id, "   ", "The check shows the goal", check_id)
    assert isinstance(blank, Refusal)
    assert blank.code == 400
    assert blank.message == "Both a statement and a rationale are required."

    blank_rationale = workspace.add_linked_decision(task_id, "Keep the export label", "  ", check_id)
    assert isinstance(blank_rationale, Refusal)
    assert blank_rationale.message == "Both a statement and a rationale are required."

    missing_check = workspace.add_linked_decision(task_id, "Keep the export label", "Because", None)
    assert isinstance(missing_check, Refusal)
    assert missing_check.message == "Choose the check this decision rests on."

    both = workspace.add_linked_decision(task_id, "  ", "  ", None)
    assert isinstance(both, Refusal)
    assert both.message == "Both a statement and a rationale are required."
    assert workspace.get_task(task_id)["decisions"] == before["decisions"]
    assert _link_count(workspace) == 0


def test_passed_and_failed_decisions_name_that_check(workspace):
    checked, check_id = _checked(workspace)
    task_id = checked["id"]
    before_history = list(checked["history"])
    before_check = checked["implementation_changes"][0]["checks"][0]

    recorded = workspace.add_linked_decision(
        task_id,
        "  Keep the export label  ",
        "The check shows the goal is visible",
        check_id,
    )
    decision = recorded["decisions"][-1]
    assert recorded["status"] == "In Progress"
    assert recorded["implementation_changes"][0]["outcome"] == "Carried out"
    assert recorded["criteria"][0]["state"] == "Unverified"
    assert recorded["history"] == before_history
    assert recorded["implementation_changes"][0]["checks"][0] == before_check
    assert decision["statement"] == "Keep the export label"
    assert decision["rationale"] == "The check shows the goal is visible"
    assert decision["recorded_at"]
    assert decision["check"]["id"] == check_id
    assert decision["check"]["criterion_text"] == "The export contains the goal"
    assert decision["check"]["what_changed"] == "Rename the export label"
    assert decision["check"]["evidence"] == "The detail page shows the goal in the export"
    assert decision["check"]["result"] == "Passed"
    assert decision["check"]["engineer_name"] == "Ada"
    assert _link_count(workspace) == 1

    failed_task, failed_check = _checked(
        workspace, title="Other export", result="Failed", evidence="The label was still old"
    )
    failed = workspace.add_linked_decision(
        failed_task["id"], "Stop the rename", "The label was still old", failed_check
    )
    assert failed["status"] == "In Progress"
    assert failed["implementation_changes"][0]["outcome"] == "Carried out"
    assert failed["implementation_changes"][0]["checks"][0]["result"] == "Failed"
    assert failed["decisions"][-1]["check"]["result"] == "Failed"
    assert failed["decisions"][-1]["check"]["evidence"] == "The label was still old"


def test_linked_decision_follows_status_and_task_link(workspace):
    checked, check_id = _checked(workspace)
    task_id = checked["id"]

    missing_task = workspace.add_linked_decision(99999, "Keep it", "Because", check_id)
    assert isinstance(missing_task, Refusal)
    assert missing_task.code == 404
    assert missing_task.message == "Task not found."

    missing_check = workspace.add_linked_decision(task_id, "Keep it", "Because", 99999)
    assert isinstance(missing_check, Refusal)
    assert missing_check.code == 404
    assert missing_check.message == "Check not found."

    other, other_check = _checked(workspace, title="Other")
    wrong_task = workspace.add_linked_decision(task_id, "Keep it", "Because", other_check)
    assert isinstance(wrong_task, Refusal)
    assert wrong_task.code == 409
    assert wrong_task.message == "The decision must name a check on that task."
    assert workspace.get_task(task_id)["decisions"] == []

    workspace.connection.execute("UPDATE task SET status = 'Draft' WHERE id = ?", (task_id,))
    drafted = workspace.add_linked_decision(task_id, "Keep it", "The check is already stored", check_id)
    assert drafted["status"] == "Draft"
    assert drafted["decisions"][-1]["check"]["id"] == check_id

    ready_task, ready_check = _checked(workspace, title="Ready export")
    workspace.connection.execute(
        "UPDATE task SET status = 'Ready' WHERE id = ?", (ready_task["id"],)
    )
    readied = workspace.add_linked_decision(
        ready_task["id"], "Keep it", "The check is already stored", ready_check
    )
    assert readied["status"] == "Ready"

    done_task, done_check = _checked(workspace, title="Done export")
    verified = workspace.verify_criterion(
        done_task["id"], done_task["criteria"][0]["id"], "The goal is on the page.", "pass"
    )
    completed = workspace.transition(verified["id"], "complete")
    linked = workspace.add_linked_decision(
        completed["id"], "Keep the export label", "The check shows the goal is visible", done_check
    )
    assert linked["status"] == "Completed"
    assert linked["decisions"][-1]["check"]["result"] == "Passed"

    cancelled_task, cancelled_check = _checked(workspace, title="Cancelled export")
    cancelled = workspace.transition(cancelled_task["id"], "cancel", "Stop this work")
    refused = workspace.add_linked_decision(cancelled["id"], "   ", "   ", None)
    assert isinstance(refused, Refusal)
    assert refused.code == 409
    assert refused.message == "Decisions cannot be added to a cancelled task."
    assert _link_count(workspace) == 3
    assert workspace.connection.execute(
        "SELECT COUNT(*) FROM decision_check WHERE check_id = ?", (cancelled_check,)
    ).fetchone()[0] == 0
