"""Named workers. A job goes to the least busy worker. An idle worker can steal one."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import task_store, worker_store

NAME_WORKER = "Name this worker."
NAME_JOB = "Name this job."
NAME_STEAL = "Name this steal."
NAME_IDLE = "Name the idle worker."
NAME_FIRST = "Name a worker first."
FULL = "Every worker is full."
NOT_ON_TASK = "That worker is not on this task."
NOT_IDLE = "That worker is not idle."
NO_WORK = "There is no work to steal."
NOT_IN_PROGRESS = "The task must be In Progress."
NAME_WORK = "Name this work."
NAME_PLAN = "Name this plan."
NAME_SCALE = "Name this scale."
ALREADY_WORK = "That work is already on this task."
ALREADY_WORKER = "That worker is already on this task."
EXTRA_HOLDS = "Every extra worker holds a job."
MATCHED = "The queue already has the workers it needs."
BOUND = 3


def add_worker(
    connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_WORKER)
    if worker_store.worker_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    worker_store.insert_worker(connection, int(task["id"]), kept, occurred_at)
    return _detail(connection, int(task["id"]))


def place_job(
    connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_JOB)
    if worker_store.job_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    if worker_store.queue_by_name(connection, int(task["id"]), kept) is not None:
        return conflict(ALREADY_WORK)
    roster = worker_store.active_workers(connection, int(task["id"]))
    if not roster:
        return conflict(NAME_FIRST)
    counts = _counts(connection, int(task["id"]))
    chosen = roster[0]
    chosen_count = counts[int(chosen["id"])]
    for worker in roster[1:]:
        count = counts[int(worker["id"])]
        if count < chosen_count:
            chosen = worker
            chosen_count = count
    if chosen_count >= BOUND:
        return conflict(FULL)
    worker_store.insert_job(
        connection, int(task["id"]), int(chosen["id"]), kept, occurred_at
    )
    return _detail(connection, int(task["id"]))


def steal_work(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    worker: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_STEAL)
    idle_name = clean(worker)
    if not idle_name:
        return bad_request(NAME_IDLE)
    if worker_store.steal_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    thief = worker_store.worker_by_name(connection, int(task["id"]), idle_name)
    if thief is None or worker_store.is_released(connection, int(thief["id"])):
        return conflict(NOT_ON_TASK)
    counts = _counts(connection, int(task["id"]))
    if counts[int(thief["id"])] > 0:
        return conflict(NOT_IDLE)
    victim = None
    victim_count = 0
    for row in worker_store.active_workers(connection, int(task["id"])):
        if int(row["id"]) == int(thief["id"]):
            continue
        count = counts[int(row["id"])]
        if count > victim_count:
            victim = row
            victim_count = count
    if victim is None:
        return conflict(NO_WORK)
    job = worker_store.oldest_job(connection, int(victim["id"]))
    worker_store.move_job(connection, int(job["id"]), int(thief["id"]))
    worker_store.insert_steal(
        connection,
        int(task["id"]),
        int(job["id"]),
        int(victim["id"]),
        int(thief["id"]),
        kept,
        occurred_at,
    )
    return _detail(connection, int(task["id"]))


def queue_work(
    connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_WORK)
    if worker_store.queue_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    if worker_store.job_by_name(connection, int(task["id"]), kept) is not None:
        return conflict(ALREADY_WORK)
    worker_store.insert_queue(connection, int(task["id"]), kept, occurred_at)
    return _detail(connection, int(task["id"]))


def plan_capacity(
    connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_PLAN)
    if worker_store.plan_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    reading = _reading(connection, int(task["id"]))
    worker_store.insert_plan(
        connection,
        int(task["id"]),
        kept,
        reading["waiting"],
        reading["held"],
        reading["active"],
        reading["needed"],
        occurred_at,
    )
    return _detail(connection, int(task["id"]))


def scale_workers(
    connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_SCALE)
    if worker_store.scale_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    reading = _reading(connection, int(task["id"]))
    if reading["room"]:
        _assign(connection, int(task["id"]), int(reading["chosen"]["id"]), occurred_at)
        job = worker_store.job_by_name(connection, int(task["id"]), reading["oldest"])
        worker_store.insert_scale(
            connection,
            int(task["id"]),
            kept,
            "fill",
            int(reading["chosen"]["id"]),
            int(job["id"]),
            occurred_at,
        )
        return _detail(connection, int(task["id"]))
    if reading["active"] < reading["needed"]:
        if worker_store.worker_by_name(connection, int(task["id"]), kept) is not None:
            return conflict(ALREADY_WORKER)
        worker_store.insert_worker(connection, int(task["id"]), kept, occurred_at)
        added = worker_store.worker_by_name(connection, int(task["id"]), kept)
        _assign(connection, int(task["id"]), int(added["id"]), occurred_at)
        job = worker_store.job_by_name(connection, int(task["id"]), reading["oldest"])
        worker_store.insert_scale(
            connection,
            int(task["id"]),
            kept,
            "up",
            int(added["id"]),
            int(job["id"]),
            occurred_at,
        )
        return _detail(connection, int(task["id"]))
    if reading["active"] > reading["needed"]:
        if reading["idle"] is None:
            return conflict(EXTRA_HOLDS)
        scale_id = worker_store.insert_scale(
            connection,
            int(task["id"]),
            kept,
            "down",
            int(reading["idle"]["id"]),
            None,
            occurred_at,
        )
        worker_store.insert_release(
            connection, int(task["id"]), int(reading["idle"]["id"]), scale_id, occurred_at
        )
        return _detail(connection, int(task["id"]))
    return conflict(MATCHED)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    roster = worker_store.active_workers(connection, task_id)
    counts = _counts(connection, task_id)
    held = {int(worker["id"]): [] for worker in roster}
    for job in worker_store.jobs(connection, task_id):
        if int(job["worker_id"]) in held:
            held[int(job["worker_id"])].append(job["name"])
    in_progress = task is not None and task["status"] == "In Progress"
    least = min(counts.values()) if counts else None
    idle = any(count == 0 for count in counts.values())
    busy = any(count > 0 for count in counts.values())
    reading = _reading(connection, task_id)
    return {
        "workers": [
            {"name": worker["name"], "jobs": held[int(worker["id"])]} for worker in roster
        ],
        "steals": [
            {
                "name": row["name"],
                "job": row["job"],
                "from_worker": row["from_worker"],
                "to_worker": row["to_worker"],
            }
            for row in worker_store.steals(connection, task_id)
        ],
        "queue": [row["name"] for row in worker_store.waiting(connection, task_id)],
        "plans": [
            {
                "name": row["name"],
                "waiting": int(row["waiting"]),
                "held": int(row["held"]),
                "active": int(row["active"]),
                "needed": int(row["needed"]),
            }
            for row in worker_store.plans(connection, task_id)
        ],
        "scales": [
            {
                "name": row["name"],
                "direction": row["direction"],
                "worker": row["worker"],
                "job": row["job"],
            }
            for row in worker_store.scales(connection, task_id)
        ],
        "released": [row["name"] for row in worker_store.released(connection, task_id)],
        "needed": reading["needed"],
        "active": reading["active"],
        "can_place": in_progress and least is not None and least < BOUND,
        "can_steal": in_progress and idle and busy,
        "can_queue": in_progress,
        "can_plan": in_progress,
        "can_scale": in_progress
        and (reading["room"] or reading["active"] < reading["needed"] or reading["idle"] is not None and reading["active"] > reading["needed"]),
    }


def _open(connection: sqlite3.Connection, task_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] != "In Progress":
        return conflict(NOT_IN_PROGRESS)
    return task


def _counts(connection: sqlite3.Connection, task_id: int) -> dict[int, int]:
    counts = {
        int(worker["id"]): 0 for worker in worker_store.active_workers(connection, task_id)
    }
    for job in worker_store.jobs(connection, task_id):
        worker_id = int(job["worker_id"])
        if worker_id in counts:
            counts[worker_id] += 1
    return counts


def _needed(total: int) -> int:
    if total <= 0:
        return 0
    return (total + BOUND - 1) // BOUND


def _reading(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    roster = worker_store.active_workers(connection, task_id)
    counts = _counts(connection, task_id)
    waiting_rows = worker_store.waiting(connection, task_id)
    held = sum(counts.values())
    waiting_count = len(waiting_rows)
    needed = _needed(held + waiting_count)
    chosen = None
    idle = None
    if roster:
        chosen = roster[0]
        chosen_count = counts[int(chosen["id"])]
        for worker in roster[1:]:
            count = counts[int(worker["id"])]
            if count < chosen_count:
                chosen = worker
                chosen_count = count
        for worker in reversed(roster):
            if counts[int(worker["id"])] == 0:
                idle = worker
                break
    else:
        chosen_count = None
    return {
        "waiting": waiting_count,
        "held": held,
        "active": len(roster),
        "needed": needed,
        "room": chosen_count is not None and chosen_count < BOUND and waiting_count > 0,
        "chosen": chosen,
        "idle": idle if len(roster) > needed else None,
        "oldest": waiting_rows[0]["name"] if waiting_rows else None,
    }


def _assign(
    connection: sqlite3.Connection, task_id: int, worker_id: int, occurred_at: str
) -> None:
    waiting_row = worker_store.oldest_waiting(connection, task_id)
    worker_store.insert_job(connection, task_id, worker_id, waiting_row["name"], occurred_at)
    job = worker_store.job_by_name(connection, task_id, waiting_row["name"])
    worker_store.mark_queued(connection, int(waiting_row["id"]), int(job["id"]))
