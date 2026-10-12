from task_manager.domain.results import Refusal
from task_manager.model import ScriptedModel
from task_manager.workspace import Workspace


def _started(workspace, title="Add export"):
    task = workspace.create_task(title)
    workspace.set_goal(task["id"], "Take the record")
    task = workspace.add_criterion(task["id"], "The export contains the goal")
    workspace.transition(task["id"], "mark_ready")
    return workspace.transition(task["id"], "start")


def _carried(workspace, title="Add export"):
    started = _started(workspace, title)
    changed = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    change_id = changed["implementation_changes"][-1]["id"]
    return started, change_id, started["criteria"][0]["id"]


def test_a_passed_assistant_check_names_the_workspace_assistant(workspace):
    started, change_id, criterion_id = _carried(workspace)
    recorded = workspace.record_assistant_check(
        started["id"],
        change_id,
        criterion_id,
        "  The detail page shows the goal in the export  ",
        "Passed",
    )
    assert not isinstance(recorded, Refusal)
    assert recorded["status"] == "In Progress"
    assert recorded["criteria"][0]["state"] == "Unverified"
    assert recorded["decisions"] == []
    change = recorded["implementation_changes"][0]
    assert change["outcome"] == "Carried out"
    check = change["checks"][0]
    assert check["criterion_text"] == "The export contains the goal"
    assert check["evidence"] == "The detail page shows the goal in the export"
    assert check["result"] == "Passed"
    assert check["assistant_name"] == "Assistant"
    assert check["engineer_name"] == "Ada"
    assert check["checked_at"].endswith("Z")
    opened = workspace.get_task(started["id"])
    assert len(opened["implementation_changes"][0]["checks"]) == 1


def test_a_failed_assistant_check_stays_on_the_change(workspace):
    started, change_id, criterion_id = _carried(workspace)
    recorded = workspace.record_assistant_check(
        started["id"], change_id, criterion_id, "The label was still old", "Failed"
    )
    check = recorded["implementation_changes"][0]["checks"][0]
    assert check["result"] == "Failed"
    assert check["assistant_name"] == "Assistant"
    assert recorded["status"] == "In Progress"


def test_blank_evidence_wins_over_a_bad_result(workspace):
    started, change_id, criterion_id = _carried(workspace)
    refused = workspace.record_assistant_check(
        started["id"], change_id, criterion_id, "   ", "Maybe"
    )
    assert isinstance(refused, Refusal)
    assert refused.message == "An account of the evidence is required."
    assert workspace.get_task(started["id"])["implementation_changes"][0]["checks"] == []


def test_a_bad_result_is_refused(workspace):
    started, change_id, criterion_id = _carried(workspace)
    refused = workspace.record_assistant_check(
        started["id"], change_id, criterion_id, "Seen", "Maybe"
    )
    assert isinstance(refused, Refusal)
    assert refused.message == "Choose Passed or Failed."


def test_status_is_refused_before_the_change(workspace):
    draft = workspace.create_task("Draft")
    refused = workspace.record_assistant_check(draft["id"], 1, None, "   ", None)
    assert refused.message == "The task must be In Progress."
    created = workspace.create_task("Ready")
    workspace.set_goal(created["id"], "Take the record")
    ready = workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(ready["id"], "mark_ready")
    assert workspace.record_assistant_check(ready["id"], 1, None, "Seen", "Passed").message == (
        "Start the task first."
    )
    plain = _started(workspace, "Plain")
    plain_criterion = plain["criteria"][0]["id"]
    workspace.verify_criterion(plain["id"], plain_criterion, "The page shows the goal", "pass")
    completed = workspace.transition(plain["id"], "complete")
    assert workspace.record_assistant_check(
        completed["id"], 1, plain_criterion, "Seen", "Passed"
    ).message == "Reopen the task first."
    cancelled = workspace.transition(_started(workspace, "Stop")["id"], "cancel", "Stop this work")
    assert workspace.record_assistant_check(
        cancelled["id"], 1, None, "Seen", "Passed"
    ).message == "A cancelled task cannot be changed. Continued work is a new task."


def test_unknown_task_change_and_criterion_are_refused(workspace):
    missing = workspace.record_assistant_check(999, 1, 1, "Seen", "Passed")
    assert missing.message == "Task not found."
    started, change_id, criterion_id = _carried(workspace)
    unknown_change = workspace.record_assistant_check(
        started["id"], 99999, criterion_id, "Seen", "Passed"
    )
    assert unknown_change.message == "Implementation change not found."
    _other, other_change, other_criterion = _carried(workspace, "Other")
    wrong_change = workspace.record_assistant_check(
        started["id"], other_change, criterion_id, "Seen", "Passed"
    )
    assert wrong_change.message == "The check must name a change on that task."
    missing_criterion = workspace.record_assistant_check(
        started["id"], change_id, None, "Seen", "Passed"
    )
    assert missing_criterion.message == "Choose an acceptance criterion."
    unknown_criterion = workspace.record_assistant_check(
        started["id"], change_id, 99999, "Seen", "Passed"
    )
    assert unknown_criterion.message == "Acceptance criterion not found."
    wrong_criterion = workspace.record_assistant_check(
        started["id"], change_id, other_criterion, "Seen", "Passed"
    )
    assert wrong_criterion.message == "The check must name a criterion on that task."
    assert workspace.get_task(started["id"])["implementation_changes"][0]["checks"] == []


def test_an_engineer_check_does_not_name_an_assistant(workspace):
    started, change_id, criterion_id = _carried(workspace)
    recorded = workspace.record_check(
        started["id"], change_id, criterion_id, "The page shows the goal", "Passed"
    )
    check = recorded["implementation_changes"][0]["checks"][0]
    assert check["assistant_name"] is None
    assert check["engineer_name"] == "Ada"


def test_the_command_does_not_call_a_model_or_open_a_project(tmp_path, clock):
    root = tmp_path / "project"
    model = ScriptedModel("Guide-model", "From the model")
    workspace = Workspace(tmp_path / "workspace.db", clock, "Ada", "Guide", root, model)
    try:
        started, change_id, criterion_id = _carried(workspace)
        recorded = workspace.record_assistant_check(
            started["id"], change_id, criterion_id, "Seen", "Passed"
        )
        assert recorded["implementation_changes"][0]["checks"][0]["assistant_name"] == "Guide"
        assert model.prompts == []
        assert not root.exists()
    finally:
        workspace.close()


def test_a_failed_check_blocks_completion_until_a_later_pass(workspace):
    started, change_id, criterion_id = _carried(workspace)
    workspace.verify_criterion(started["id"], criterion_id, "The page shows the goal", "pass")
    failed = workspace.record_assistant_check(
        started["id"], change_id, criterion_id, "The label was still old", "Failed"
    )
    assert failed["criteria"][0]["state"] == "Verified"
    held = workspace.transition(started["id"], "complete")
    assert isinstance(held, Refusal)
    assert held.message == "Needs a passing check: Rename the export label."
    passed = workspace.record_assistant_check(
        started["id"], change_id, criterion_id, "The label now reads Export", "Passed"
    )
    assert passed["implementation_changes"][0]["checks"][0]["evidence"] == "The label was still old"
    assert passed["implementation_changes"][0]["checks"][0]["result"] == "Failed"
    assert passed["implementation_changes"][0]["checks"][1]["result"] == "Passed"
    completed = workspace.transition(started["id"], "complete")
    assert completed["status"] == "Completed"


def test_an_assistant_check_does_not_verify_or_add_a_decision(workspace):
    started, change_id, criterion_id = _carried(workspace)
    checked = workspace.record_assistant_check(
        started["id"], change_id, criterion_id, "The page shows the goal", "Passed"
    )
    assert checked["criteria"][0]["state"] == "Unverified"
    assert checked["decisions"] == []
    check_id = checked["implementation_changes"][0]["checks"][0]["id"]
    decided = workspace.add_linked_decision(
        started["id"], "Keep the export label", "The check shows the goal", check_id
    )
    decision = decided["decisions"][-1]
    assert decision["check"]["assistant_name"] == "Assistant"
    assert decision["check"]["engineer_name"] == "Ada"
    assert len(workspace.get_task(started["id"])["implementation_changes"][0]["checks"]) == 1


def test_a_change_that_is_not_carried_out_cannot_be_checked(workspace):
    started = _started(workspace)
    criterion_id = started["criteria"][0]["id"]
    waiting = workspace.record_change(started["id"], "Replace the stored export name", "consequential")
    waiting_id = waiting["implementation_changes"][-1]["id"]
    awaiting = workspace.record_assistant_check(
        started["id"], waiting_id, criterion_id, "Seen", "Passed"
    )
    assert awaiting.message == "The change must be carried out before it can be checked."
    assert waiting["implementation_changes"][-1]["outcome"] == "Awaiting approval"
    declined = workspace.mark_change_not_carried_out(started["id"], waiting_id, "Leave the name")
    assert declined["implementation_changes"][-1]["outcome"] == "Not carried out"
    refused = workspace.record_assistant_check(
        started["id"], waiting_id, criterion_id, "Seen", "Passed"
    )
    assert refused.message == "A change that was not carried out cannot be checked."


def test_a_subtask_check_stays_on_the_subtask(workspace):
    parent = _started(workspace, "Ship the export")
    child = workspace.add_subtask(parent["id"], "Add export")
    workspace.set_goal(child["id"], "Take the record")
    child = workspace.add_criterion(child["id"], "The export contains the goal")
    workspace.transition(child["id"], "mark_ready")
    child = workspace.transition(child["id"], "start")
    changed = workspace.record_change(child["id"], "Rename the export label", "ordinary")
    change_id = changed["implementation_changes"][-1]["id"]
    workspace.record_assistant_check(
        child["id"], change_id, child["criteria"][0]["id"], "Seen", "Failed"
    )
    parent_detail = workspace.get_task(parent["id"])
    assert parent_detail["implementation_changes"] == []
    child_detail = workspace.get_task(child["id"])
    assert child_detail["implementation_changes"][0]["checks"][0]["assistant_name"] == "Assistant"
