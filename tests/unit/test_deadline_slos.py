from task_manager.domain import slo
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_an_objective_keeps_its_deadline(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    set_export = workspace.set_objective(task_id, " export ", "2026-12-01T00:00:00Z")
    assert set_export["status"] == "In Progress"
    assert set_export["slo"]["waiting"] == [
        {"name": "export", "deadline": "2026-12-01T00:00:00Z"}
    ]
    assert set_export["file_reads"] == []
    assert set_export["priority"]["waiting"] == []
    rush = workspace.set_objective(task_id, "rush", " 2026-10-01T00:00:00Z ")
    assert rush["slo"]["waiting"] == [
        {"name": "export", "deadline": "2026-12-01T00:00:00Z"},
        {"name": "rush", "deadline": "2026-10-01T00:00:00Z"},
    ]
    repeated = workspace.set_objective(task_id, "export", "2026-01-01T00:00:00Z")
    assert repeated["slo"]["waiting"] == rush["slo"]["waiting"]

    other = _in_progress(workspace, "Other objective")
    other_set = workspace.set_objective(other["id"], "export", "2026-11-01T00:00:00Z")
    assert other_set["slo"]["waiting"] == [
        {"name": "export", "deadline": "2026-11-01T00:00:00Z"}
    ]
    assert len(workspace.get_task(task_id)["slo"]["waiting"]) == 2

    blank = workspace.set_objective(task_id, " ", "2026-12-01T00:00:00Z")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this objective."

    bad_deadline = workspace.set_objective(task_id, "late", "tomorrow")
    assert isinstance(bad_deadline, Refusal)
    assert bad_deadline.message == "Name a deadline."
    assert len(workspace.get_task(task_id)["slo"]["waiting"]) == 2

    impossible = workspace.set_objective(task_id, "late", "2026-13-01T00:00:00Z")
    assert isinstance(impossible, Refusal)
    assert impossible.message == "Name a deadline."

    draft = workspace.create_task("Draft")
    refused = workspace.set_objective(draft["id"], "export", "2026-12-01T00:00:00Z")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["slo"]["waiting"] == []


def test_a_service_takes_the_earliest_deadline(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.set_objective(task_id, "export", "2026-12-01T00:00:00Z")
    workspace.set_objective(task_id, "rush", "2026-10-01T00:00:00Z")

    first = workspace.serve_objective(task_id, " one ")
    assert first["slo"]["services"] == [
        {"name": "one", "objective": "rush", "result": "missed"}
    ]
    assert first["slo"]["waiting"] == [
        {"name": "export", "deadline": "2026-12-01T00:00:00Z"}
    ]
    assert first["status"] == "In Progress"

    second = workspace.serve_objective(task_id, "two")
    assert second["slo"]["services"][-1] == {
        "name": "two",
        "objective": "export",
        "result": "met",
    }
    assert second["slo"]["waiting"] == []

    tied = _in_progress(workspace, "Tied deadlines")
    workspace.set_objective(tied["id"], "ada", "2026-12-01T00:00:00Z")
    workspace.set_objective(tied["id"], "grace", "2026-12-01T00:00:00Z")
    chosen = workspace.serve_objective(tied["id"], "one")
    assert chosen["slo"]["services"] == [
        {"name": "one", "objective": "ada", "result": "met"}
    ]

    repeated = workspace.serve_objective(task_id, "one")
    assert repeated["slo"]["services"] == second["slo"]["services"]

    empty = _in_progress(workspace, "Empty objectives")
    missing = workspace.serve_objective(empty["id"], "one")
    assert isinstance(missing, Refusal)
    assert missing.message == "Name an objective first."

    held = _in_progress(workspace, "Held service")
    held_id = held["id"]
    workspace.set_objective(held_id, "export", "2026-12-01T00:00:00Z")

    def _then_refuse(connection):
        slo.serve_objective(connection, held_id, "one", "2026-10-20T00:00:00Z")
        return bad_request("no")

    rolled = call_in_transaction(workspace.connection, _then_refuse)
    assert isinstance(rolled, Refusal)
    opened = workspace.get_task(held_id)
    assert opened["slo"]["services"] == []
    assert opened["slo"]["waiting"] == [
        {"name": "export", "deadline": "2026-12-01T00:00:00Z"}
    ]
    restored = workspace.serve_objective(held_id, "one")
    assert restored["slo"]["services"] == [
        {"name": "one", "objective": "export", "result": "met"}
    ]


def test_a_finished_schedule_refuses_the_next_service(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.set_objective(task_id, "rush", "2026-10-01T00:00:00Z")
    workspace.set_objective(task_id, "export", "2026-12-01T00:00:00Z")
    workspace.serve_objective(task_id, "one")
    workspace.serve_objective(task_id, "two")

    blocked = workspace.serve_objective(task_id, "three")
    assert isinstance(blocked, Refusal)
    assert blocked.message == "Every objective has been served."
    assert len(workspace.get_task(task_id)["slo"]["services"]) == 2
    assert workspace.get_task(task_id)["status"] == "In Progress"
    assert workspace.get_task(task_id)["priority"]["waiting"] == []

    blank = workspace.serve_objective(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this service."

    draft = workspace.create_task("Draft service")
    refused = workspace.serve_objective(draft["id"], "one")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    other = _in_progress(workspace, "Other service")
    workspace.set_objective(other["id"], "export", "2026-12-01T00:00:00Z")
    other_service = workspace.serve_objective(other["id"], "one")
    assert other_service["slo"]["services"] == [
        {"name": "one", "objective": "export", "result": "met"}
    ]
    assert len(workspace.get_task(task_id)["slo"]["services"]) == 2
