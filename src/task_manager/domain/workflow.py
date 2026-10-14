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
RECOVER_FIRST = "Recover the interrupted step first."
NO_RECOVER = "There is no step to recover."
INTERRUPTED = "the step was interrupted."
WAITING = "waiting for approval."
_ACTIONS = ("read", "folder")
_CLASSES = ("ordinary", "consequential")


class ReadyToFinish:
    """The running entry is stored. The result is a later transaction."""


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


def prepare(
    connection: sqlite3.Connection,
    task_id: int,
    occurred_at: str,
    name: str | None = None,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    kept_name = clean(name)
    if kept_name:
        prior = workflow_store.row_advance(connection, int(task["id"]), kept_name)
        if prior is not None:
            return _same_advance(connection, prior, occurred_at)
    current = _unfinished(connection, int(task["id"]))
    if current is None:
        return conflict(NO_STEP)
    if current["state"] == "Running":
        return conflict(RECOVER_FIRST)
    if current["state"] == "Waiting":
        if not _claim(connection, int(task["id"]), kept_name, int(current["id"])):
            return _repeat_saved(connection, int(task["id"]), kept_name, occurred_at)
        _settle(connection, current, occurred_at)
        return _detail(connection, int(task["id"]))
    if current["state"] == "Failed" and current["change_id"] is not None:
        if not _claim(connection, int(task["id"]), kept_name, int(current["id"])):
            return _repeat_saved(connection, int(task["id"]), kept_name, occurred_at)
        return _detail(connection, int(task["id"]))
    if not _claim(connection, int(task["id"]), kept_name, int(current["id"])):
        return _repeat_saved(connection, int(task["id"]), kept_name, occurred_at)
    kept_change = None if current["change_id"] is None else int(current["change_id"])
    workflow_store.update_step(connection, int(current["id"]), "Running", None, kept_change)
    workflow_store.insert_attempt(connection, int(current["id"]), _baseline(connection, current))
    _remember(connection, current, "Running", None, occurred_at)
    return ReadyToFinish()


def finish(
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
    if current is None or current["state"] != "Running":
        return _detail(connection, int(task["id"]))
    if not _apply_stored_effect(connection, current, occurred_at):
        if workflow_store.row_attempt(connection, int(current["id"])) is None:
            _set_outcome(connection, current, "Failed", INTERRUPTED, None, occurred_at)
        else:
            _perform(connection, current, occurred_at, project_root)
    workflow_store.delete_attempt(connection, int(current["id"]))
    return _detail(connection, int(task["id"]))


def recover(
    connection: sqlite3.Connection,
    task_id: int,
    occurred_at: str,
    project_root: Path,
):
    del project_root
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    current = _unfinished(connection, int(task["id"]))
    if current is None or current["state"] != "Running":
        return conflict(NO_RECOVER)
    _recover_running(connection, current, occurred_at)
    workflow_store.delete_attempt(connection, int(current["id"]))
    return _detail(connection, int(task["id"]))


def replay(connection: sqlite3.Connection, task_id: int):
    if task_store.row_task(connection, task_id) is None:
        return missing("Task not found.")
    return {"events": _events(connection, task_id)}


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    rows = workflow_store.steps(connection, task_id)
    return {
        "steps": [_public(row) for row in rows],
        "stopped": _stopped(rows),
        "started": any(row["state"] != "Pending" for row in rows),
        "finished": bool(rows) and all(row["state"] == "Completed" for row in rows),
        "interrupted": any(row["state"] == "Running" for row in rows),
        "replay": _events(connection, task_id),
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
            _set_outcome(connection, step, "Failed", result.message, None, occurred_at)
        else:
            _set_outcome(connection, step, "Completed", None, None, occurred_at)
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
        _set_outcome(connection, step, "Failed", result.message, None, occurred_at)
        return
    created = [
        item
        for item in implementation_store.changes_for(connection, task_id)
        if int(item["id"]) not in before
    ]
    _apply_change(connection, step, created[-1], occurred_at)


def _recover_running(
    connection: sqlite3.Connection,
    step: sqlite3.Row,
    occurred_at: str,
) -> None:
    if _apply_stored_effect(connection, step, occurred_at):
        return
    attempt = workflow_store.row_attempt(connection, int(step["id"]))
    if attempt is None or step["action"] == "read":
        _set_outcome(connection, step, "Failed", INTERRUPTED, None, occurred_at)
        return
    kept_change = None if step["change_id"] is None else int(step["change_id"])
    _set_outcome(connection, step, "Failed", INTERRUPTED, kept_change, occurred_at)


def _apply_stored_effect(
    connection: sqlite3.Connection,
    step: sqlite3.Row,
    occurred_at: str,
) -> bool:
    attempt = workflow_store.row_attempt(connection, int(step["id"]))
    if attempt is None:
        return False
    before = int(attempt["effect_before"])
    task_id = int(step["task_id"])
    if step["action"] == "read":
        from task_manager.storage.file_read_store import file_reads_for

        if len(file_reads_for(connection, task_id)) <= before:
            return False
        _set_outcome(connection, step, "Completed", None, None, occurred_at)
        return True
    created = [
        item
        for item in implementation_store.changes_for(connection, task_id)
        if int(item["id"]) > before
    ]
    if not created:
        return False
    _apply_change(connection, step, created[-1], occurred_at)
    return True


def _claim(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    step_id: int,
) -> bool:
    if name is None:
        return True
    return workflow_store.insert_advance(connection, task_id, name, step_id)


def _repeat_saved(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    occurred_at: str,
):
    if name is None:
        return _detail(connection, task_id)
    prior = workflow_store.row_advance(connection, task_id, name)
    if prior is None:
        return _detail(connection, task_id)
    return _same_advance(connection, prior, occurred_at)


def _same_advance(
    connection: sqlite3.Connection,
    prior: sqlite3.Row,
    occurred_at: str,
):
    step = workflow_store.row_step(connection, int(prior["step_id"]))
    if step is None:
        return _detail(connection, int(prior["task_id"]))
    if step["state"] == "Running":
        return conflict(RECOVER_FIRST)
    if step["state"] == "Waiting":
        _settle(connection, step, occurred_at)
    return _detail(connection, int(step["task_id"]))


def _apply_change(
    connection: sqlite3.Connection,
    step: sqlite3.Row,
    change: dict[str, object],
    occurred_at: str,
) -> None:
    change_id = int(change["id"])
    if change["outcome"] == "Awaiting approval":
        _set_outcome(connection, step, "Waiting", None, change_id, occurred_at)
    elif change["outcome"] == "Carried out":
        _set_outcome(connection, step, "Completed", None, change_id, occurred_at)
    else:
        reason = ""
        not_carried = change["not_carried_out"]
        if isinstance(not_carried, dict):
            reason = str(not_carried["reason"])
        _set_outcome(connection, step, "Failed", reason, change_id, occurred_at)


def _settle(connection: sqlite3.Connection, step: sqlite3.Row, occurred_at: str) -> None:
    change_id = int(step["change_id"])
    row = implementation_store.row_change(connection, change_id)
    if row is None:
        _set_outcome(connection, step, "Failed", CHANGE_NOT_FOUND, change_id, occurred_at)
        return
    change = implementation_store.change_payload(row)
    if change["outcome"] == "Awaiting approval":
        return
    _apply_change(connection, step, change, occurred_at)


def _baseline(connection: sqlite3.Connection, step: sqlite3.Row) -> int:
    task_id = int(step["task_id"])
    if step["action"] == "read":
        from task_manager.storage.file_read_store import file_reads_for

        return len(file_reads_for(connection, task_id))
    changes = implementation_store.changes_for(connection, task_id)
    if not changes:
        return 0
    return max(int(item["id"]) for item in changes)


def _set_outcome(
    connection: sqlite3.Connection,
    step: sqlite3.Row,
    state: str,
    detail: str | None,
    change_id: int | None,
    occurred_at: str,
) -> None:
    workflow_store.update_step(connection, int(step["id"]), state, detail, change_id)
    _remember(connection, step, state, detail, occurred_at)


def _remember(
    connection: sqlite3.Connection,
    step: sqlite3.Row,
    state: str,
    detail: str | None,
    occurred_at: str,
) -> None:
    workflow_store.insert_event(
        connection,
        int(step["task_id"]),
        int(step["id"]),
        state,
        detail,
        occurred_at,
    )


def _events(connection: sqlite3.Connection, task_id: int) -> list[dict[str, object]]:
    return [
        {
            "id": int(row["id"]),
            "step_id": int(row["step_id"]),
            "title": row["title"],
            "state": row["state"],
            "detail": row["detail"],
            "recorded_at": row["recorded_at"],
        }
        for row in workflow_store.events(connection, task_id)
    ]


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
        if row["state"] == "Running":
            return f"Stopped at {row['title']}: {INTERRUPTED}"
        return None
    return None
