from task_manager.domain.results import Refusal


def test_blank_title_creates_nothing(workspace):
    refused = workspace.create_task("   ")
    assert isinstance(refused, Refusal)
    assert refused.code == 400
    assert "title" in refused.message.lower()
    assert workspace.list_tasks() == []


def test_created_task_is_draft_and_duplicate_titles_stay_distinct(workspace):
    first = workspace.create_task("Add export")
    second = workspace.create_task("Add export")
    assert first["status"] == "Draft"
    assert second["status"] == "Draft"
    assert first["id"] != second["id"]
    assert [item["id"] for item in workspace.list_tasks()] == [first["id"], second["id"]]


def test_new_criterion_is_unverified(workspace):
    created = workspace.create_task("Add export")
    updated = workspace.add_criterion(created["id"], "The file contains the goal")
    criterion = updated["criteria"][0]
    assert criterion["state"] == "Unverified"
    assert criterion["observation"] is None
    assert criterion["pass_result"] is None
    assert criterion["verified_at"] is None
    assert criterion["provider_name"] is None


def test_mark_ready_requires_goal_and_criterion(workspace):
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "An engineer can take a finished task record with them")
    refused = workspace.transition(created["id"], "mark_ready")
    assert isinstance(refused, Refusal)
    assert refused.code == 409
    assert "acceptance criterion" in refused.message.lower()
    assert workspace.get_task(created["id"])["status"] == "Draft"

    ready = workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(ready["id"], "mark_ready")
    assert ready["status"] == "Ready"


def test_removing_last_criterion_returns_ready_task_to_draft(workspace):
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    updated = workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(updated["id"], "mark_ready")
    criterion_id = ready["criteria"][0]["id"]
    demoted = workspace.remove_criterion(ready["id"], criterion_id)
    assert demoted["status"] == "Draft"
    assert demoted["history"][-1]["cause_code"] == "goal_or_last_criterion_removed"


def test_clearing_goal_returns_ready_task_to_draft(workspace):
    created = workspace.create_task("Add export")
    workspace.set_goal(created["id"], "Take the record")
    updated = workspace.add_criterion(created["id"], "The file contains the goal")
    ready = workspace.transition(updated["id"], "mark_ready")
    demoted = workspace.set_goal(ready["id"], "   ")
    assert demoted["status"] == "Draft"
    assert demoted["goal"] is None
    assert demoted["history"][-1]["cause_code"] == "goal_or_last_criterion_removed"
