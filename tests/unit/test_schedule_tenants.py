from task_manager.domain import schedule
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_a_tenant_starts_at_zero_of_two(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    admitted = workspace.admit_tenant(task_id, " ada ")
    assert admitted["status"] == "In Progress"
    assert admitted["schedule"]["tenants"] == [{"name": "ada", "used": 0, "quota": 2}]
    assert admitted["file_reads"] == []
    both = workspace.admit_tenant(task_id, "grace")
    assert both["schedule"]["tenants"] == [
        {"name": "ada", "used": 0, "quota": 2},
        {"name": "grace", "used": 0, "quota": 2},
    ]
    repeated = workspace.admit_tenant(task_id, "ada")
    assert repeated["schedule"]["tenants"] == both["schedule"]["tenants"]

    other = _in_progress(workspace, "Other tenant")
    other_admitted = workspace.admit_tenant(other["id"], "ada")
    assert other_admitted["schedule"]["tenants"] == [{"name": "ada", "used": 0, "quota": 2}]
    assert len(workspace.get_task(task_id)["schedule"]["tenants"]) == 2

    blank = workspace.admit_tenant(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this tenant."

    draft = workspace.create_task("Draft")
    refused = workspace.admit_tenant(draft["id"], "ada")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["schedule"]["tenants"] == []


def test_a_turn_goes_to_the_least_used_tenant(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.admit_tenant(task_id, "ada")
    workspace.admit_tenant(task_id, "grace")

    first = workspace.grant_turn(task_id, " one ")
    assert first["schedule"]["turns"] == [{"name": "one", "tenant": "ada"}]
    assert first["schedule"]["tenants"][0] == {"name": "ada", "used": 1, "quota": 2}
    assert first["status"] == "In Progress"

    second = workspace.grant_turn(task_id, "two")
    third = workspace.grant_turn(task_id, "three")
    fourth = workspace.grant_turn(task_id, "four")
    assert [item["tenant"] for item in fourth["schedule"]["turns"]] == [
        "ada",
        "grace",
        "ada",
        "grace",
    ]
    repeated = workspace.grant_turn(task_id, "one")
    assert repeated["schedule"]["turns"] == fourth["schedule"]["turns"]

    empty = _in_progress(workspace, "Empty schedule")
    missing = workspace.grant_turn(empty["id"], "one")
    assert isinstance(missing, Refusal)
    assert missing.message == "Name a tenant first."

    held = _in_progress(workspace, "Held turn")
    held_id = held["id"]
    workspace.admit_tenant(held_id, "ada")

    def _then_refuse(connection):
        schedule.grant_turn(connection, held_id, "one", "2026-10-20T00:00:00Z")
        return bad_request("no")

    rolled = call_in_transaction(workspace.connection, _then_refuse)
    assert isinstance(rolled, Refusal)
    opened = workspace.get_task(held_id)
    assert opened["schedule"]["turns"] == []
    assert opened["schedule"]["tenants"] == [{"name": "ada", "used": 0, "quota": 2}]
    restored = workspace.grant_turn(held_id, "one")
    assert restored["schedule"]["turns"] == [{"name": "one", "tenant": "ada"}]


def test_a_full_quota_refuses_the_next_turn(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.admit_tenant(task_id, "ada")
    workspace.admit_tenant(task_id, "grace")
    for name in ("one", "two", "three"):
        workspace.grant_turn(task_id, name)
    skipped = workspace.grant_turn(task_id, "four")
    assert skipped["schedule"]["turns"][-1] == {"name": "four", "tenant": "grace"}
    assert skipped["schedule"]["tenants"] == [
        {"name": "ada", "used": 2, "quota": 2},
        {"name": "grace", "used": 2, "quota": 2},
    ]
    blocked = workspace.grant_turn(task_id, "five")
    assert isinstance(blocked, Refusal)
    assert blocked.message == "Every tenant is at its quota."
    assert len(workspace.get_task(task_id)["schedule"]["turns"]) == 4

    blank = workspace.grant_turn(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this turn."

    draft = workspace.create_task("Draft turn")
    refused = workspace.grant_turn(draft["id"], "one")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    other = _in_progress(workspace, "Other turn")
    workspace.admit_tenant(other["id"], "ada")
    other_turn = workspace.grant_turn(other["id"], "one")
    assert other_turn["schedule"]["turns"] == [{"name": "one", "tenant": "ada"}]
    assert [item["name"] for item in workspace.get_task(task_id)["schedule"]["turns"]] == [
        "one",
        "two",
        "three",
        "four",
    ]
