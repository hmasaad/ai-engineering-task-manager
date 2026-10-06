"""Create a task, edit its goal and criteria, and mark it Ready."""

import sqlite3

from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import status_store, task_store
from task_manager.storage.connection import engineer_name

CANCELLED = "A cancelled task cannot be changed. Continued work is a new task."
LAST_CRITERION = (
    "The last acceptance criterion cannot be removed while the task is In Progress or Completed."
)
CLEAR_GOAL = "The goal cannot be cleared while the task is In Progress or Completed."


def _detail(connection: sqlite3.Connection, task_id: int) -> dict[str, object] | Refusal:
    detail = task_store.task_detail(connection, task_id)
    if detail is None:
        return missing("Task not found.")
    return detail


def _demote_ready(
    connection: sqlite3.Connection,
    task: sqlite3.Row,
    occurred_at: str,
) -> None:
    if task["status"] != "Ready":
        return
    goal = clean(task["goal"])
    remaining = task_store.criteria_for(connection, int(task["id"]))
    if goal and remaining:
        return
    task_store.set_status(connection, int(task["id"]), "Draft", None)
    status_store.append_change(
        connection,
        int(task["id"]),
        "Ready",
        "Draft",
        occurred_at,
        "goal_or_last_criterion_removed",
        None,
    )


def create_task(connection: sqlite3.Connection, title: str, occurred_at: str):
    cleaned = clean(title)
    if not cleaned:
        return bad_request("A title is required.")
    task_id = task_store.insert_task(connection, cleaned, occurred_at, None)
    return _detail(connection, task_id)


def set_goal(connection: sqlite3.Connection, task_id: int, goal: str | None, occurred_at: str):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict(CANCELLED)
    cleaned = clean(goal)
    if cleaned is None and task["status"] in ("In Progress", "Completed"):
        return conflict(CLEAR_GOAL)
    task_store.set_goal(connection, task_id, cleaned)
    updated = task_store.row_task(connection, task_id)
    assert updated is not None
    _demote_ready(connection, updated, occurred_at)
    return _detail(connection, task_id)


def add_criterion(connection: sqlite3.Connection, task_id: int, text: str):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict(CANCELLED)
    cleaned = clean(text)
    if not cleaned:
        return bad_request("An acceptance criterion is required.")
    task_store.insert_criterion(connection, task_id, cleaned)
    return _detail(connection, task_id)


def update_criterion(
    connection: sqlite3.Connection,
    task_id: int,
    criterion_id: int,
    text: str,
    occurred_at: str,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict(CANCELLED)
    row = task_store.criterion(connection, task_id, criterion_id)
    if row is None:
        return missing("Criterion not found.")
    cleaned = clean(text)
    if not cleaned:
        return bad_request("An acceptance criterion is required.")
    was_verified = task_store.is_verified(row)
    task_store.update_criterion_text(connection, criterion_id, cleaned)
    if was_verified:
        task_store.clear_verification(connection, criterion_id)
        if task["status"] == "Completed":
            _leave_completed(
                connection,
                task,
                occurred_at,
                "criterion_text_edited",
                str(criterion_id),
            )
    return _detail(connection, task_id)


def remove_criterion(
    connection: sqlite3.Connection,
    task_id: int,
    criterion_id: int,
    occurred_at: str,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict(CANCELLED)
    row = task_store.criterion(connection, task_id, criterion_id)
    if row is None:
        return missing("Criterion not found.")
    remaining = task_store.criteria_for(connection, task_id)
    if len(remaining) == 1 and task["status"] in ("In Progress", "Completed"):
        return conflict(LAST_CRITERION)
    task_store.delete_criterion(connection, criterion_id)
    updated = task_store.row_task(connection, task_id)
    assert updated is not None
    _demote_ready(connection, updated, occurred_at)
    return _detail(connection, task_id)


def mark_ready(connection: sqlite3.Connection, task_id: int, occurred_at: str):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict(CANCELLED)
    if task["status"] != "Draft":
        return conflict("The task must be Draft to mark it Ready.")
    has_goal = bool(clean(task["goal"]))
    has_criterion = bool(task_store.criteria_for(connection, task_id))
    if not has_goal and not has_criterion:
        return conflict("A goal and at least one acceptance criterion are required.")
    if not has_goal:
        return conflict("A goal is required.")
    if not has_criterion:
        return conflict("At least one acceptance criterion is required.")
    task_store.set_status(connection, task_id, "Ready", None)
    status_store.append_change(
        connection, task_id, "Draft", "Ready", occurred_at, "marked_ready", None
    )
    return _detail(connection, task_id)


def _leave_completed(
    connection: sqlite3.Connection,
    task: sqlite3.Row,
    occurred_at: str,
    cause_code: str,
    cause_detail: str | None,
) -> None:
    """Move this Completed task, then every Completed ancestor, to In Progress."""
    from task_manager.storage.subtask_store import ancestor_ids

    task_store.set_status(connection, int(task["id"]), "In Progress", None)
    status_store.append_change(
        connection,
        int(task["id"]),
        "Completed",
        "In Progress",
        occurred_at,
        cause_code,
        cause_detail,
    )
    for ancestor_id in ancestor_ids(connection, int(task["id"])):
        ancestor = task_store.row_task(connection, ancestor_id)
        if ancestor is None or ancestor["status"] != "Completed":
            continue
        task_store.set_status(connection, ancestor_id, "In Progress", None)
        status_store.append_change(
            connection,
            ancestor_id,
            "Completed",
            "In Progress",
            occurred_at,
            cause_code,
            cause_detail,
        )


def verify(
    connection: sqlite3.Connection,
    task_id: int,
    criterion_id: int,
    observation: str,
    pass_result: str,
    occurred_at: str,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict(CANCELLED)
    row = task_store.criterion(connection, task_id, criterion_id)
    if row is None:
        return missing("Criterion not found.")
    if task["status"] != "In Progress":
        return conflict("A criterion can be verified only while the task is In Progress.")
    seen = clean(observation)
    if not seen:
        return bad_request("An observation of what was seen is required.")
    if pass_result != "pass":
        return bad_request("An explicit pass result is required.")
    status_store.write_verification(
        connection,
        criterion_id,
        seen,
        occurred_at,
        engineer_name(connection),
    )
    return _detail(connection, task_id)


def unverify(connection: sqlite3.Connection, task_id: int, criterion_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict(CANCELLED)
    row = task_store.criterion(connection, task_id, criterion_id)
    if row is None:
        return missing("Criterion not found.")
    if task["status"] != "In Progress":
        return conflict("A criterion can be marked Unverified only while the task is In Progress.")
    task_store.clear_verification(connection, criterion_id)
    return _detail(connection, task_id)
