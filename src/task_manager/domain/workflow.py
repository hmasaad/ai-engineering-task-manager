"""One ordered workflow on a task. Each advance performs one stored step."""

import sqlite3
from pathlib import Path

from task_manager.domain.capture import _detail
from task_manager.domain.file_read import NAME_FILE
from task_manager.domain.folder import NAME_FOLDER
from task_manager.domain.implementation import (
    CHANGE_NOT_FOUND,
    CHOOSE_CLASS,
    NAME_PROJECT,
    WHAT_CHANGED_REQUIRED,
    _record_status,
)
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import implementation_store, task_store, workflow_store

NAME_STEP = "Name the step."
CHOOSE_ACTION = "Choose a step action."
ADD_ONLY_BEFORE = "A step can be added only before the workflow runs."
REMOVE_ONLY_BEFORE = "A step cannot be removed after the workflow runs."
STEP_NOT_ON_TASK = "That step is not on this task."
NO_STEP = "There is no step to run."
WAITING = "waiting for approval."
_ACTIONS = ("read", "folder")
_CLASSES = ("ordinary", "consequential")


def add(
    connection: sqlite3.Connection,
    task_id: int,
    title: str | None,
    action: str | None,
    project: str | None,
    path: str | None,
    what_changed: str | None,
    change_class: str | None,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    if workflow_store.any_started(connection, task_id):
        return conflict(ADD_ONLY_BEFORE)
    kept_title = clean(title)
    if not kept_title:
        return bad_request(NAME_STEP)
    kept_action = clean(action)
    if kept_action not in _ACTIONS:
        return bad_request(CHOOSE_ACTION)
    kept_project = clean(project)
    if not kept_project:
        return bad_request(NAME_PROJECT)
    kept_path = clean(path)
    kept_what = None
    kept_class = None
    if kept_action == "read":
        if not kept_path:
            return bad_request(NAME_FILE)
    else:
        kept_what = clean(what_changed)
        if not kept_what:
            return bad_request(WHAT_CHANGED_REQUIRED)
        kept_class = clean(change_class)
        if kept_class not in _CLASSES:
            return bad_request(CHOOSE_CLASS)
        if not kept_path:
            return bad_request(NAME_FOLDER)
    workflow_store.insert_step(
        connection,
        int(task["id"]),
        kept_title,
        kept_action,
        kept_project,
        kept_path,
        kept_what,
        kept_class,
    )
    return _detail(connection, int(task["id"]))


def remove(connection: sqlite3.Connection, task_id: int, step_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    if workflow_store.any_started(connection, task_id):
        return conflict(REMOVE_ONLY_BEFORE)
    row = workflow_store.row_step(connection, step_id)
    if row is None or int(row["task_id"]) != int(task["id"]):
        return conflict(STEP_NOT_ON_TASK)
    workflow_store.delete_step(connection, int(row["id"]))
    return _detail(connection, int(task["id"]))


def advance(
    connection: sqlite3.Connection,
    task_id: int,
    occurred_at: str,
    project_root: Path,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    current = _unfinished(connection, int(task["id"]))
    if current is None:
        return conflict(NO_STEP)
    if current["state"] == "Waiting":
        _settle(connection, current)
    else:
        _perform(connection, current, occurred_at, project_root)
    return _detail(connection, int(task["id"]))


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    rows = workflow_store.steps(connection, task_id)
    return {
        "steps": [_public(row) for row in rows],
        "stopped": _stopped(rows),
        "started": any(row["state"] != "Pending" for row in rows),
        "finished": bool(rows) and all(row["state"] == "Completed" for row in rows),
    }


def _unfinished(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    for row in workflow_store.steps(connection, task_id):
        if row["state"] != "Completed":
            return row
    return None


def _perform(
    connection: sqlite3.Connection,
    step: sqlite3.Row,
    occurred_at: str,
    project_root: Path,
) -> None:
    task_id = int(step["task_id"])
    if step["action"] == "read":
        from task_manager.domain.file_read import read_file

        result = read_file(
            connection,
            task_id,
            step["project"],
            step["path"],
            occurred_at,
            project_root,
        )
        if isinstance(result, Refusal):
            workflow_store.update_step(connection, int(step["id"]), "Failed", result.message, None)
        else:
            workflow_store.update_step(connection, int(step["id"]), "Completed", None, None)
        return
    from task_manager.domain.folder import record

    before = {
        int(item["id"]) for item in implementation_store.changes_for(connection, task_id)
    }
    result = record(
        connection,
        task_id,
        step["project"],
        step["change_class"],
        step["what_changed"],
        False,
        step["path"],
        occurred_at,
        project_root,
    )
    if isinstance(result, Refusal):
        workflow_store.update_step(connection, int(step["id"]), "Failed", result.message, None)
        return
    created = [
        item
        for item in implementation_store.changes_for(connection, task_id)
        if int(item["id"]) not in before
    ]
    change = created[-1]
    change_id = int(change["id"])
    if change["outcome"] == "Awaiting approval":
        workflow_store.update_step(connection, int(step["id"]), "Waiting", None, change_id)
    elif change["outcome"] == "Carried out":
        workflow_store.update_step(connection, int(step["id"]), "Completed", None, change_id)
    else:
        reason = ""
        if change["not_carried_out"] is not None:
            reason = str(change["not_carried_out"]["reason"])
        workflow_store.update_step(connection, int(step["id"]), "Failed", reason, change_id)


def _settle(connection: sqlite3.Connection, step: sqlite3.Row) -> None:
    change_id = int(step["change_id"])
    row = implementation_store.row_change(connection, change_id)
    if row is None:
        workflow_store.update_step(
            connection, int(step["id"]), "Failed", CHANGE_NOT_FOUND, change_id
        )
        return
    change = implementation_store.change_payload(row)
    if change["outcome"] == "Awaiting approval":
        return
    if change["outcome"] == "Carried out":
        workflow_store.update_step(connection, int(step["id"]), "Completed", None, change_id)
        return
    reason = ""
    if change["not_carried_out"] is not None:
        reason = str(change["not_carried_out"]["reason"])
    workflow_store.update_step(connection, int(step["id"]), "Failed", reason, change_id)


def _public(row: sqlite3.Row) -> dict[str, object]:
    return {
        "id": int(row["id"]),
        "title": row["title"],
        "action": row["action"],
        "state": row["state"],
        "project": row["project"],
        "path": row["path"],
        "change_id": None if row["change_id"] is None else int(row["change_id"]),
    }


def _stopped(rows: list[sqlite3.Row]) -> str | None:
    for row in rows:
        if row["state"] == "Completed":
            continue
        if row["state"] == "Failed":
            return f"Stopped at {row['title']}: {row['detail']}"
        if row["state"] == "Waiting":
            return f"Stopped at {row['title']}: {WAITING}"
        return None
    return None
