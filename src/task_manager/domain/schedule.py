"""Named tenants share one schedule. The least-used tenant takes the next turn."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import schedule_store, task_store

NAME_TENANT = "Name this tenant."
NAME_TURN = "Name this turn."
NAME_FIRST = "Name a tenant first."
AT_QUOTA = "Every tenant is at its quota."
NOT_IN_PROGRESS = "The task must be In Progress."


def admit_tenant(
    connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_TENANT)
    if schedule_store.tenant_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    schedule_store.insert_tenant(connection, int(task["id"]), kept, occurred_at)
    return _detail(connection, int(task["id"]))


def grant_turn(
    connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_TURN)
    if schedule_store.turn_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    chosen = _choose(connection, int(task["id"]))
    if chosen is None:
        roster = schedule_store.tenants(connection, int(task["id"]))
        if not roster:
            return conflict(NAME_FIRST)
        return conflict(AT_QUOTA)
    schedule_store.insert_turn(
        connection, int(task["id"]), kept, int(chosen["id"]), occurred_at
    )
    return _detail(connection, int(task["id"]))


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    used = schedule_store.used_counts(connection, task_id)
    roster = schedule_store.tenants(connection, task_id)
    room = any(used.get(int(row["id"]), 0) < int(row["quota"]) for row in roster)
    return {
        "tenants": [
            {
                "name": row["name"],
                "used": used.get(int(row["id"]), 0),
                "quota": int(row["quota"]),
            }
            for row in roster
        ],
        "turns": [
            {"name": row["name"], "tenant": row["tenant"]}
            for row in schedule_store.turns(connection, task_id)
        ],
        "can_admit": in_progress,
        "can_grant": in_progress and room,
    }


def _open(connection: sqlite3.Connection, task_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] != "In Progress":
        return conflict(NOT_IN_PROGRESS)
    return task


def _choose(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    used = schedule_store.used_counts(connection, task_id)
    chosen = None
    chosen_used = None
    for row in schedule_store.tenants(connection, task_id):
        count = used.get(int(row["id"]), 0)
        if count >= int(row["quota"]):
            continue
        if chosen is None or count < chosen_used:
            chosen = row
            chosen_used = count
    return chosen
