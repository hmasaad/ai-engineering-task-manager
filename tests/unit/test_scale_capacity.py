from task_manager.domain import workers
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _queues(detail):
    return [(worker["name"], worker["jobs"]) for worker in detail["work"]["workers"]]


def test_a_plan_reads_the_queue(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    for name in ("one", "two", "three", " four "):
        queued = workspace.queue_work(task_id, name)
        assert queued["status"] == "In Progress"
    assert queued["work"]["queue"] == ["one", "two", "three", "four"]
    assert queued["work"]["workers"] == []
    assert queued["file_reads"] == []

    planned = workspace.plan_capacity(task_id, " now ")
    assert planned["work"]["plans"] == [
        {"name": "now", "waiting": 4, "held": 0, "active": 0, "needed": 2}
    ]
    assert planned["work"]["needed"] == 2
    assert planned["work"]["active"] == 0
    repeated = workspace.plan_capacity(task_id, "now")
    assert repeated["work"]["plans"] == planned["work"]["plans"]

    held = _in_progress(workspace, "Held plan")
    workspace.add_worker(held["id"], "ada")
    workspace.place_job(held["id"], "one")
    reading = workspace.plan_capacity(held["id"], "later")
    assert reading["work"]["plans"] == [
        {"name": "later", "waiting": 0, "held": 1, "active": 1, "needed": 1}
    ]

    other = _in_progress(workspace, "Other queue")
    other_queued = workspace.queue_work(other["id"], "one")
    assert other_queued["work"]["queue"] == ["one"]
    assert workspace.get_task(task_id)["work"]["queue"] == ["one", "two", "three", "four"]

    blank = workspace.queue_work(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this work."
    blank_plan = workspace.plan_capacity(task_id, " ")
    assert isinstance(blank_plan, Refusal)
    assert blank_plan.message == "Name this plan."
    taken = workspace.queue_work(held["id"], "one")
    assert isinstance(taken, Refusal)
    assert taken.message == "That work is already on this task."

    draft = workspace.create_task("Draft")
    refused = workspace.queue_work(draft["id"], "one")
    refused_plan = workspace.plan_capacity(draft["id"], "now")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert isinstance(refused_plan, Refusal)
    assert refused_plan.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["work"]["queue"] == []


def test_a_scale_fills_spare_room_before_adding_a_worker(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_worker(task_id, "ada")
    for name in ("one", "two", "three", "four"):
        workspace.queue_work(task_id, name)

    filled = workspace.scale_workers(task_id, " fill ")
    assert _queues(filled) == [("ada", ["one"])]
    assert filled["work"]["queue"] == ["two", "three", "four"]
    assert filled["work"]["scales"] == [
        {"name": "fill", "direction": "fill", "worker": "ada", "job": "one"}
    ]
    assert filled["status"] == "In Progress"

    workspace.scale_workers(task_id, "second")
    third = workspace.scale_workers(task_id, "third")
    assert _queues(third) == [("ada", ["one", "two", "three"])]
    blocked = workspace.place_job(task_id, "extra")
    assert isinstance(blocked, Refusal)
    assert blocked.message == "Every worker is full."

    grown = workspace.scale_workers(task_id, "grace")
    assert _queues(grown) == [("ada", ["one", "two", "three"]), ("grace", ["four"])]
    assert grown["work"]["queue"] == []
    assert grown["work"]["needed"] == 2
    assert grown["work"]["active"] == 2
    repeated = workspace.scale_workers(task_id, "grace")
    assert _queues(repeated) == _queues(grown)
    assert repeated["work"]["scales"] == grown["work"]["scales"]

    alone = _in_progress(workspace, "Alone")
    workspace.queue_work(alone["id"], "one")
    added = workspace.scale_workers(alone["id"], "ada")
    assert _queues(added) == [("ada", ["one"])]

    named = _in_progress(workspace, "Named")
    named_id = named["id"]
    workspace.add_worker(named_id, "ada")
    workspace.place_job(named_id, "one")
    workspace.place_job(named_id, "two")
    workspace.place_job(named_id, "three")
    workspace.queue_work(named_id, "four")
    collided = workspace.scale_workers(named_id, "ada")
    assert isinstance(collided, Refusal)
    assert collided.message == "That worker is already on this task."
    assert workspace.get_task(named_id)["work"]["queue"] == ["four"]

    held = _in_progress(workspace, "Held scale")
    held_id = held["id"]
    workspace.queue_work(held_id, "one")

    def _then_refuse(connection):
        workers.scale_workers(connection, held_id, "ada", "2026-10-20T00:00:00Z")
        return bad_request("no")

    rolled = call_in_transaction(workspace.connection, _then_refuse)
    assert isinstance(rolled, Refusal)
    opened = workspace.get_task(held_id)
    assert opened["work"]["queue"] == ["one"]
    assert opened["work"]["workers"] == []
    assert opened["work"]["scales"] == []
    restored = workspace.scale_workers(held_id, "ada")
    assert _queues(restored) == [("ada", ["one"])]

    draft = workspace.create_task("Draft scale")
    refused = workspace.scale_workers(draft["id"], "ada")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."


def test_a_scale_releases_the_newest_idle_worker(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_worker(task_id, "ada")
    workspace.add_worker(task_id, "grace")
    released = workspace.scale_workers(task_id, "trim")
    assert _queues(released) == [("ada", [])]
    assert released["work"]["released"] == ["grace"]
    assert released["work"]["scales"] == [
        {"name": "trim", "direction": "down", "worker": "grace", "job": None}
    ]
    assert released["work"]["needed"] == 0
    assert released["work"]["active"] == 1
    again = workspace.scale_workers(task_id, "again")
    assert again["work"]["workers"] == []
    assert again["work"]["released"] == ["grace", "ada"]

    matched = workspace.scale_workers(task_id, "stop")
    assert isinstance(matched, Refusal)
    assert matched.message == "The queue already has the workers it needs."
    blank = workspace.scale_workers(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this scale."

    busy = _in_progress(workspace, "Busy")
    busy_id = busy["id"]
    workspace.add_worker(busy_id, "ada")
    workspace.add_worker(busy_id, "grace")
    workspace.place_job(busy_id, "one")
    workspace.place_job(busy_id, "two")
    kept = workspace.scale_workers(busy_id, "trim")
    assert isinstance(kept, Refusal)
    assert kept.message == "Every extra worker holds a job."
    assert _queues(workspace.get_task(busy_id)) == [("ada", ["one"]), ("grace", ["two"])]

    held = _in_progress(workspace, "Held release")
    held_id = held["id"]
    workspace.add_worker(held_id, "ada")
    workspace.add_worker(held_id, "grace")

    def _then_refuse(connection):
        workers.scale_workers(connection, held_id, "trim", "2026-10-20T00:00:00Z")
        return bad_request("no")

    rolled = call_in_transaction(workspace.connection, _then_refuse)
    assert isinstance(rolled, Refusal)
    assert _queues(workspace.get_task(held_id)) == [("ada", []), ("grace", [])]
    restored = workspace.scale_workers(held_id, "trim")
    assert _queues(restored) == [("ada", [])]

    other = _in_progress(workspace, "Other scale")
    workspace.add_worker(other["id"], "ada")
    workspace.add_worker(other["id"], "grace")
    other_scale = workspace.scale_workers(other["id"], "trim")
    assert other_scale["work"]["released"] == ["grace"]
    assert workspace.get_task(task_id)["work"]["released"] == ["grace", "ada"]
