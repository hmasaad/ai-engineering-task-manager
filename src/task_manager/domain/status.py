"""Start, complete, cancel, and reopen. Completion is never inferred."""

import sqlite3

from task_manager.domain.capture import CANCELLED, _detail, _leave_completed, mark_ready
from task_manager.domain.implementation import awaiting_accounts
from task_manager.domain.verification import lacking_accounts
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import status_store, task_store

MUST_BE_IN_PROGRESS = "The task must be In Progress before it can be completed."


def _awaiting_sentence(connection: sqlite3.Connection, task_id: int) -> str | None:
    waiting = awaiting_accounts(connection, task_id)
    if not waiting:
        return None
    return "Awaiting approval: " + ", ".join(waiting)


def _check_sentence(connection: sqlite3.Connection, task_id: int) -> str | None:
    lacking = lacking_accounts(connection, task_id)
    if not lacking:
        return None
    return "Needs a passing check: " + ", ".join(lacking)


def _unfinished_message(connection: sqlite3.Connection, task_id: int) -> str | None:
    unmet = [
        row["text"]
        for row in task_store.criteria_for(connection, task_id)
        if not task_store.is_verified(row)
    ]
    unfinished = [
        row
        for row in task_store.children(connection, task_id)
        if row["status"] in ("Draft", "Ready", "In Progress")
    ]
    waiting = _awaiting_sentence(connection, task_id)
    needing = _check_sentence(connection, task_id)
    if not unmet and not unfinished and waiting is None and needing is None:
        return None
    parts: list[str] = []
    if unmet:
        parts.append("Unverified criteria: " + ", ".join(unmet))
    if unfinished:
        named = [f"{row['title']} ({row['status']})" for row in unfinished]
        parts.append("Unfinished subtasks: " + ", ".join(named))
    if waiting is not None:
        parts.append(waiting)
    if needing is not None:
        parts.append(needing)
    return ". ".join(parts) + "."


def transition(
    connection: sqlite3.Connection,
    task_id: int,
    action: str,
    reason: str | None,
    occurred_at: str,
):
    if action == "mark_ready":
        return mark_ready(connection, task_id, occurred_at)
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict(CANCELLED)
    if action == "start":
        return _start(connection, task, occurred_at)
    if action == "complete":
        return _complete(connection, task, occurred_at)
    if action == "cancel":
        return _cancel(connection, task, reason, occurred_at)
    if action == "reopen":
        return _reopen(connection, task, reason, occurred_at)
    return bad_request("The action is not a status change.")


def _start(connection: sqlite3.Connection, task: sqlite3.Row, occurred_at: str):
    if task["status"] != "Ready":
        return conflict("The task must be Ready to start work.")
    task_id = int(task["id"])
    task_store.set_status(connection, task_id, "In Progress", None)
    status_store.append_change(
        connection, task_id, "Ready", "In Progress", occurred_at, "started", None
    )
    return _detail(connection, task_id)


def _complete(connection: sqlite3.Connection, task: sqlite3.Row, occurred_at: str):
    if task["status"] != "In Progress":
        return conflict(MUST_BE_IN_PROGRESS)
    problem = _unfinished_message(connection, int(task["id"]))
    if problem:
        return conflict(problem)
    task_id = int(task["id"])
    task_store.set_status(connection, task_id, "Completed", None)
    status_store.append_change(
        connection, task_id, "In Progress", "Completed", occurred_at, "completed", None
    )
    return _detail(connection, task_id)


def _blocking_children(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return [
        row
        for row in task_store.children(connection, task_id)
        if row["status"] in ("Draft", "Ready", "In Progress")
    ]


def _cancel(
    connection: sqlite3.Connection,
    task: sqlite3.Row,
    reason: str | None,
    occurred_at: str,
):
    if task["status"] == "Completed":
        return conflict("Reopen the task before cancelling it.")
    if task["status"] not in ("Draft", "Ready", "In Progress"):
        return conflict("The task cannot be cancelled from its current status.")
    cleaned = clean(reason)
    if not cleaned:
        return bad_request("A cancellation reason is required.")
    blocking = _blocking_children(connection, int(task["id"]))
    waiting = _awaiting_sentence(connection, int(task["id"]))
    if blocking:
        names = ", ".join(f"{row['title']} ({row['status']})" for row in blocking)
        message = f"Subtasks must be finished or cancelled first: {names}."
        if waiting is not None:
            message = f"{message} {waiting}."
        return conflict(message)
    if waiting is not None:
        return conflict(f"{waiting}.")
    task_id = int(task["id"])
    task_store.set_status(connection, task_id, "Cancelled", cleaned)
    status_store.append_change(
        connection, task_id, task["status"], "Cancelled", occurred_at, "cancelled", cleaned
    )
    return _detail(connection, task_id)


def _reopen(
    connection: sqlite3.Connection,
    task: sqlite3.Row,
    reason: str | None,
    occurred_at: str,
):
    if task["status"] != "Completed":
        return conflict("Only a Completed task can be reopened.")
    cleaned = clean(reason)
    if not cleaned:
        return bad_request("A reopen reason is required.")
    _leave_completed(connection, task, occurred_at, "reopened", cleaned)
    return _detail(connection, int(task["id"]))
