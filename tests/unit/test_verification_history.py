import task_manager.domain.verification as verification
from task_manager.domain.results import Refusal


def _started(workspace, criteria):
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    for text in criteria:
        workspace.add_criterion(created["id"], text)
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _verify_all(workspace, detail):
    current = detail
    for criterion in list(current["criteria"]):
        current = workspace.verify_criterion(current["id"], criterion["id"], "Seen", "pass")
    return current


def test_a_later_check_keeps_the_earlier_one_and_becomes_current(workspace):
    started = _started(workspace, ("The file contains the goal", "The export lists the date"))
    recorded = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    change_id = recorded["implementation_changes"][0]["id"]
    first_id = recorded["criteria"][0]["id"]
    second_id = recorded["criteria"][1]["id"]
    failed = workspace.record_check(recorded["id"], change_id, first_id, "The label was still old", "Failed")
    earlier = failed["implementation_changes"][0]["checks"][0]
    passed = workspace.record_check(recorded["id"], change_id, first_id, "The label now reads Export", "Passed")
    checks = passed["implementation_changes"][0]["checks"]
    assert checks[0] == earlier
    assert [item["result"] for item in checks] == ["Failed", "Passed"]
    assert passed["implementation_changes"][0]["passing_check"] is True

    both = workspace.record_check(recorded["id"], change_id, second_id, "The date is on the page", "Passed")
    assert both["implementation_changes"][0]["passing_check"] is True
    ready = _verify_all(workspace, both)
    assert workspace.transition(ready["id"], "complete")["status"] == "Completed"


def test_a_current_failure_on_any_checked_criterion_blocks_completion(workspace):
    started = _started(workspace, ("The file contains the goal", "The export lists the date"))
    recorded = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    change_id = recorded["implementation_changes"][0]["id"]
    first_id = recorded["criteria"][0]["id"]
    second_id = recorded["criteria"][1]["id"]
    workspace.record_check(recorded["id"], change_id, first_id, "Seen", "Passed")
    failed = workspace.record_check(recorded["id"], change_id, second_id, "The date is missing", "Failed")
    assert failed["implementation_changes"][0]["passing_check"] is False
    ready = _verify_all(workspace, failed)
    refused = workspace.transition(ready["id"], "complete")
    assert isinstance(refused, Refusal)
    assert refused.message == "Needs a passing check: Rename the export label."

    same = _started(workspace, ("The file contains the goal",))
    same = workspace.record_change(same["id"], "Rename the export label", "ordinary")
    change_id = same["implementation_changes"][0]["id"]
    criterion_id = same["criteria"][0]["id"]
    workspace.record_check(same["id"], change_id, criterion_id, "Seen", "Passed")
    later = workspace.record_check(same["id"], change_id, criterion_id, "It regressed", "Failed")
    assert later["implementation_changes"][0]["checks"][0]["result"] == "Passed"
    assert later["implementation_changes"][0]["passing_check"] is False
    ready = _verify_all(workspace, later)
    refused = workspace.transition(ready["id"], "complete")
    assert refused.message == "Needs a passing check: Rename the export label."


def test_criterion_edits_and_removal_do_not_rewrite_or_delete_checks(workspace):
    started = _started(workspace, ("The file contains the goal", "The export lists the date"))
    recorded = workspace.record_change(started["id"], "Rename the export label", "ordinary")
    change_id = recorded["implementation_changes"][0]["id"]
    first_id = recorded["criteria"][0]["id"]
    checked = workspace.record_check(recorded["id"], change_id, first_id, "Seen", "Passed")
    edited = workspace.update_criterion(checked["id"], first_id, "The export contains the goal now")
    assert edited["implementation_changes"][0]["checks"][0]["criterion_text"] == "The file contains the goal"
    removed = workspace.remove_criterion(edited["id"], first_id)
    assert removed["implementation_changes"][0]["checks"][0]["criterion_text"] == "The file contains the goal"
    assert removed["implementation_changes"][0]["passing_check"] is False
    assert not hasattr(verification, "update_check")
    assert not hasattr(verification, "delete_check")
