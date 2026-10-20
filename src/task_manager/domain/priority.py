"""Named work is served by rank plus age. Waiting work ages when it is passed over."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import priority_store, task_store

NAME_WORK = "Name this work."
NAME_RANK = "Name a rank from 1 to 3."
NAME_SERVE = "Name this serve."
NAME_FIRST = "Rank work before serving."
NOT_IN_PROGRESS = "The task must be In Progress."
_RANKS = {"1": 1, "2": 2, "3": 3}


def rank_work(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    rank: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_WORK)
    if priority_store.work_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    stored = _rank(rank)
    if stored is None:
        return bad_request(NAME_RANK)
    priority_store.insert_work(connection, int(task["id"]), kept, stored, occurred_at)
    return _detail(connection, int(task["id"]))


def serve_next(
    connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_SERVE)
    if priority_store.serve_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    chosen = _choose(priority_store.waiting(connection, int(task["id"])))
    if chosen is None:
        return conflict(NAME_FIRST)
    priority_store.insert_serve(
        connection, int(task["id"]), kept, int(chosen["id"]), occurred_at
    )
    return _detail(connection, int(task["id"]))


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = priority_store.waiting(connection, task_id)
    return {
        "waiting": [
            {"name": row["name"], "rank": int(row["rank"]), "age": int(row["age"])}
            for row in roster
        ],
        "serves": [
            {"name": row["name"], "work": row["work"]}
            for row in priority_store.serves(connection, task_id)
        ],
        "can_rank": in_progress,
        "can_serve": in_progress and bool(roster),
    }


def _open(connection: sqlite3.Connection, task_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] != "In Progress":
        return conflict(NOT_IN_PROGRESS)
    return task


def _rank(value: str | None) -> int | None:
    if value is None:
        return None
    return _RANKS.get(value.strip())


def _choose(rows: list[sqlite3.Row]) -> sqlite3.Row | None:
    chosen = None
    best = None
    for row in rows:
        score = int(row["rank"]) + int(row["age"])
        if chosen is None or score > best:
            chosen = row
            best = score
    return chosen
