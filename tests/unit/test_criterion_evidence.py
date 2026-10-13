from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def _started(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_verification_stores_the_method_and_the_run_identifier(workspace):
    started = _started(workspace)
    criterion_id = started["criteria"][0]["id"]
    verified = workspace.verify_criterion(
        started["id"],
        criterion_id,
        "The export contains the goal",
        "pass",
        "  inspection  ",
        "  local-1  ",
    )
    criterion = verified["criteria"][0]
    assert criterion["state"] == "Verified"
    assert criterion["observation"] == "The export contains the goal"
    assert criterion["pass_result"] == "pass"
    assert criterion["method"] == "inspection"
    assert criterion["run_identifier"] == "local-1"
    assert criterion["provider_name"] == "Ada"
    assert criterion["verified_at"]

    again = workspace.get_task(started["id"])
    assert again["criteria"][0]["method"] == "inspection"
    assert again["criteria"][0]["run_identifier"] == "local-1"
    assert again["criteria"][0]["verified_at"] == criterion["verified_at"]


def test_a_later_engineer_does_not_rewrite_the_evidence(tmp_path, clock):
    path = tmp_path / "workspace.db"
    workspace = Workspace(path, clock, "Ada")
    try:
        started = _started(workspace)
        criterion_id = started["criteria"][0]["id"]
        workspace.verify_criterion(
            started["id"],
            criterion_id,
            "The export contains the goal",
            "pass",
            "inspection",
            "local-1",
        )
    finally:
        workspace.close()

    reopened = Workspace(path, clock, "Bea")
    try:
        criterion = reopened.get_task(1)["criteria"][0]
        assert criterion["method"] == "inspection"
        assert criterion["run_identifier"] == "local-1"
        assert criterion["observation"] == "The export contains the goal"
        assert criterion["provider_name"] == "Ada"
    finally:
        reopened.close()


def test_a_blank_method_or_run_identifier_stores_nothing(workspace):
    started = _started(workspace)
    criterion_id = started["criteria"][0]["id"]
    blank_method = workspace.verify_criterion(
        started["id"], criterion_id, "The export contains the goal", "pass", "  ", "local-1"
    )
    assert isinstance(blank_method, Refusal)
    assert blank_method.message == "A verification method is required."
    assert workspace.get_task(started["id"])["criteria"][0]["state"] == "Unverified"

    blank_run = workspace.verify_criterion(
        started["id"], criterion_id, "The export contains the goal", "pass", "inspection", " "
    )
    assert isinstance(blank_run, Refusal)
    assert blank_run.message == "A test-run identifier is required."
    assert workspace.get_task(started["id"])["criteria"][0]["state"] == "Unverified"

    both = workspace.verify_criterion(
        started["id"], criterion_id, "The export contains the goal", "pass", "", ""
    )
    assert both.message == "A verification method is required."


def test_existing_refusals_stay_ahead_of_the_method(workspace):
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    criterion_id = ready["criteria"][0]["id"]
    too_soon = workspace.verify_criterion(ready["id"], criterion_id, "Seen", "pass", "", "")
    assert too_soon.message == "A criterion can be verified only while the task is In Progress."

    started = workspace.transition(ready["id"], "start")
    blank_observation = workspace.verify_criterion(started["id"], criterion_id, "  ", "pass", "", "")
    assert blank_observation.message == "An observation of what was seen is required."

    missing_pass = workspace.verify_criterion(started["id"], criterion_id, "Seen", "no", "", "")
    assert missing_pass.message == "An explicit pass result is required."

    requirement = workspace.record_requirement("The export contains the goal", "functional")
    workspace.link_requirement_task(requirement["id"], started["id"])
    workspace.link_requirement_criterion(requirement["id"], started["id"], criterion_id)
    workspace.name_requirement_check(requirement["id"], "export shows the goal")
    blocked = workspace.verify_criterion(started["id"], criterion_id, "Seen", "pass", "", "")
    assert blocked.message == "A required check has not passed."
    assert workspace.get_task(started["id"])["criteria"][0]["state"] == "Unverified"


def test_clearing_verification_clears_the_method_and_the_run(workspace):
    started = _started(workspace)
    criterion_id = started["criteria"][0]["id"]
    workspace.verify_criterion(
        started["id"], criterion_id, "The export contains the goal", "pass", "inspection", "local-1"
    )
    cleared = workspace.unverify_criterion(started["id"], criterion_id)
    assert cleared["criteria"][0]["state"] == "Unverified"
    assert cleared["criteria"][0]["method"] is None
    assert cleared["criteria"][0]["run_identifier"] is None

    workspace.verify_criterion(
        started["id"], criterion_id, "The export contains the goal", "pass", "inspection", "local-1"
    )
    edited = workspace.update_criterion(started["id"], criterion_id, "The export contains the revised goal")
    assert edited["criteria"][0]["state"] == "Unverified"
    assert edited["criteria"][0]["method"] is None

    workspace.verify_criterion(
        started["id"],
        criterion_id,
        "The export contains the goal",
        "pass",
        "inspection",
        "local-1",
    )
    requirement = workspace.record_requirement("The export contains the goal", "functional")
    workspace.link_requirement_task(requirement["id"], started["id"])
    workspace.link_requirement_criterion(requirement["id"], started["id"], criterion_id)
    changed = workspace.change_requirement(requirement["id"], "The export contains the revised goal", "functional")
    assert changed["criteria"][0]["state"] == "Unverified"
    task = workspace.get_task(started["id"])
    assert task["criteria"][0]["method"] is None
    assert task["criteria"][0]["run_identifier"] is None
