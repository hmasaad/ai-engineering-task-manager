"""Named objectives are served by the earliest deadline. The service records met or missed."""

import sqlite3
from datetime import datetime

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import slo_store, task_store

NAME_OBJECTIVE = "Name this objective."
NAME_DEADLINE = "Name a deadline."
NAME_SERVICE = "Name this service."
NAME_FIRST = "Name an objective first."
ALL_SERVED = "Every objective has been served."
NOT_IN_PROGRESS = "The task must be In Progress."
_DEADLINE = "%Y-%m-%dT%H:%M:%SZ"


def set_objective(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    deadline: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_OBJECTIVE)
    if slo_store.objective_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    stored = _deadline(deadline)
    if stored is None:
        return bad_request(NAME_DEADLINE)
    slo_store.insert_objective(connection, int(task["id"]), kept, stored, occurred_at)
    return _detail(connection, int(task["id"]))


def serve_objective(
    connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_SERVICE)
    if slo_store.service_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    roster = slo_store.waiting(connection, int(task["id"]))
    chosen = _choose(roster)
    if chosen is None:
        if not slo_store.objectives(connection, int(task["id"])):
            return conflict(NAME_FIRST)
        return conflict(ALL_SERVED)
    result = "met" if occurred_at <= chosen["deadline"] else "missed"
    slo_store.insert_service(
        connection, int(task["id"]), kept, int(chosen["id"]), result, occurred_at
    )
    return _detail(connection, int(task["id"]))


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = slo_store.waiting(connection, task_id)
    return {
        "waiting": [
            {"name": row["name"], "deadline": row["deadline"]} for row in roster
        ],
        "services": [
            {"name": row["name"], "objective": row["objective"], "result": row["result"]}
            for row in slo_store.services(connection, task_id)
        ],
        "can_set": in_progress,
        "can_serve": in_progress and bool(roster),
    }


def _open(connection: sqlite3.Connection, task_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] != "In Progress":
        return conflict(NOT_IN_PROGRESS)
    return task


def _deadline(value: str | None) -> str | None:
    if value is None:
        return None
    kept = value.strip()
    try:
        datetime.strptime(kept, _DEADLINE)
    except ValueError:
        return None
    return kept


def _choose(rows: list[sqlite3.Row]) -> sqlite3.Row | None:
    chosen = None
    best = None
    for row in rows:
        deadline = row["deadline"]
        if chosen is None or deadline < best:
            chosen = row
            best = deadline
    return chosen
