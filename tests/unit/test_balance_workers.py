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


def test_a_job_goes_to_the_least_busy_worker(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    ada = workspace.add_worker(task_id, " ada ")
    grace = workspace.add_worker(task_id, "grace")
    assert _queues(grace) == [("ada", []), ("grace", [])]
    assert ada["status"] == "In Progress"
    assert ada["file_reads"] == []
    assert ada["workflow"]["steps"] == []

    one = workspace.place_job(task_id, "one")
    two = workspace.place_job(task_id, "two")
    three = workspace.place_job(task_id, " three ")
    assert _queues(three) == [("ada", ["one", "three"]), ("grace", ["two"])]
    assert three["work"]["steals"] == []
    assert three["status"] == "In Progress"

    repeated_worker = workspace.add_worker(task_id, "ada")
    repeated_job = workspace.place_job(task_id, "one")
    assert _queues(repeated_worker) == _queues(three)
    assert _queues(repeated_job) == _queues(three)

    other = _in_progress(workspace, "Other")
    other_ada = workspace.add_worker(other["id"], "ada")
    other_job = workspace.place_job(other["id"], "one")
    assert _queues(other_job) == [("ada", ["one"])]
    assert _queues(workspace.get_task(task_id)) == [
        ("ada", ["one", "three"]),
        ("grace", ["two"]),
    ]
    assert other_ada["id"] == other["id"]


def test_a_full_queue_refuses_another_job(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_worker(task_id, "ada")
    for name in ("one", "two", "three"):
        workspace.place_job(task_id, name)
    refused = workspace.place_job(task_id, "four")
    assert isinstance(refused, Refusal)
    assert refused.message == "Every worker is full."
    assert _queues(workspace.get_task(task_id)) == [("ada", ["one", "two", "three"])]

    workspace.add_worker(task_id, "grace")
    for name in ("four", "five", "six"):
        workspace.place_job(task_id, name)
    both = workspace.place_job(task_id, "seven")
    assert isinstance(both, Refusal)
    assert both.message == "Every worker is full."
    assert _queues(workspace.get_task(task_id)) == [
        ("ada", ["one", "two", "three"]),
        ("grace", ["four", "five", "six"]),
    ]

    blank_job = workspace.place_job(task_id, "  ")
    assert isinstance(blank_job, Refusal)
    assert blank_job.message == "Name this job."
    blank_worker = workspace.add_worker(task_id, " ")
    assert isinstance(blank_worker, Refusal)
    assert blank_worker.message == "Name this worker."

    empty = _in_progress(workspace, "Empty")
    missing = workspace.place_job(empty["id"], "one")
    assert isinstance(missing, Refusal)
    assert missing.message == "Name a worker first."
    assert workspace.get_task(empty["id"])["work"]["workers"] == []

    held = _in_progress(workspace, "Held")
    held_id = held["id"]
    workspace.add_worker(held_id, "ada")

    def _then_refuse(connection):
        workers.place_job(connection, held_id, "once", "2026-10-20T00:00:00Z")
        return bad_request("no")

    rolled = call_in_transaction(workspace.connection, _then_refuse)
    assert isinstance(rolled, Refusal)
    assert workspace.get_task(held_id)["work"]["workers"] == [{"name": "ada", "jobs": []}]
    restored = workspace.place_job(held_id, "once")
    assert _queues(restored) == [("ada", ["once"])]

    draft = workspace.create_task("Draft")
    refused_worker = workspace.add_worker(draft["id"], "ada")
    refused_job = workspace.place_job(draft["id"], "one")
    assert isinstance(refused_worker, Refusal)
    assert refused_worker.message == "The task must be In Progress."
    assert isinstance(refused_job, Refusal)
    assert refused_job.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["work"]["workers"] == []


def test_an_idle_worker_takes_the_oldest_job(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_worker(task_id, "ada")
    workspace.add_worker(task_id, "grace")
    for name in ("one", "two", "three"):
        workspace.place_job(task_id, name)
    workspace.add_worker(task_id, "lin")

    stolen = workspace.steal_work(task_id, " take ", "lin")
    assert _queues(stolen) == [
        ("ada", ["three"]),
        ("grace", ["two"]),
        ("lin", ["one"]),
    ]
    assert stolen["work"]["steals"] == [
        {"name": "take", "job": "one", "from_worker": "ada", "to_worker": "lin"}
    ]
    assert stolen["status"] == "In Progress"
    assert stolen["file_reads"] == []

    repeated = workspace.steal_work(task_id, "take", "ada")
    assert _queues(repeated) == _queues(stolen)
    assert repeated["work"]["steals"] == stolen["work"]["steals"]

    busy = workspace.steal_work(task_id, "again", "ada")
    assert isinstance(busy, Refusal)
    assert busy.message == "That worker is not idle."
    absent = workspace.steal_work(task_id, "missing", "nope")
    assert isinstance(absent, Refusal)
    assert absent.message == "That worker is not on this task."
    blank = workspace.steal_work(task_id, " ", "lin")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this steal."
    unnamed = workspace.steal_work(task_id, "later", " ")
    assert isinstance(unnamed, Refusal)
    assert unnamed.message == "Name the idle worker."
    assert workspace.get_task(task_id)["work"]["steals"] == stolen["work"]["steals"]

    workspace.add_worker(task_id, "mae")
    tied = workspace.steal_work(task_id, "next", "mae")
    assert _queues(tied) == [
        ("ada", []),
        ("grace", ["two"]),
        ("lin", ["one"]),
        ("mae", ["three"]),
    ]
    assert tied["work"]["steals"][-1] == {
        "name": "next",
        "job": "three",
        "from_worker": "ada",
        "to_worker": "mae",
    }

    alone = _in_progress(workspace, "Alone")
    alone_id = alone["id"]
    workspace.add_worker(alone_id, "ada")
    nowhere = workspace.steal_work(alone_id, "take", "ada")
    assert isinstance(nowhere, Refusal)
    assert nowhere.message == "There is no work to steal."

    held = _in_progress(workspace, "Held steal")
    held_id = held["id"]
    workspace.add_worker(held_id, "ada")
    workspace.place_job(held_id, "one")
    workspace.add_worker(held_id, "lin")

    def _then_refuse(connection):
        workers.steal_work(connection, held_id, "once", "lin", "2026-10-20T00:00:00Z")
        return bad_request("no")

    rolled = call_in_transaction(workspace.connection, _then_refuse)
    assert isinstance(rolled, Refusal)
    opened = workspace.get_task(held_id)
    assert _queues(opened) == [("ada", ["one"]), ("lin", [])]
    assert opened["work"]["steals"] == []
    restored = workspace.steal_work(held_id, "once", "lin")
    assert _queues(restored) == [("ada", []), ("lin", ["one"])]

    draft = workspace.create_task("Draft steal")
    refused = workspace.steal_work(draft["id"], "take", "lin")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["work"]["steals"] == []

    other = _in_progress(workspace, "Other steal")
    workspace.add_worker(other["id"], "ada")
    workspace.place_job(other["id"], "one")
    workspace.add_worker(other["id"], "lin")
    other_steal = workspace.steal_work(other["id"], "take", "lin")
    assert other_steal["work"]["steals"] == [
        {"name": "take", "job": "one", "from_worker": "ada", "to_worker": "lin"}
    ]
    assert workspace.get_task(task_id)["work"]["steals"][0]["name"] == "take"
