"""One ordered workflow on a task. Each advance performs one stored step."""

import sqlite3
from pathlib import Path

from task_manager.domain.capture import _detail
from task_manager.domain.file_read import NAME_FILE
from task_manager.domain.folder import FOLDER_MISMATCH, FOLDER_OUTSIDE, NAME_FOLDER
from task_manager.domain.implementation import (
    CHANGE_NOT_FOUND,
    CHOOSE_CLASS,
    EVIDENCE_REQUIRED,
    NAME_PROJECT,
    WHAT_CHANGED_REQUIRED,
    _inside,
    _project_dir,
    _record_status,
    _relative_inside,
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
NOT_RUN = "The workflow has not run yet."
DRAFT_EXISTS = "A draft version already exists."
NO_WORKFLOW = "There is no workflow to revise."
NO_DRAFT = "There is no draft version to migrate."
NAME_REASON = "Name why this workflow is migrating."
KEEP_RAN = "A step that already ran must stay in the new version."
NO_REPLAY = "There is no step to replay."
MISSING_EFFECT = "the stored effect is missing."
STEP_NOT_RUN = "the step has not run."
NAME_DELIVERY = "Name this delivery."
NO_OUTBOX = "There is no outbox message to deliver."
NAME_COMPENSATION = "Name why this step is compensated."
NO_COMPENSATE = "There is no step to compensate."
NOT_FAILED = "The workflow has not failed."
WAITING_COMPENSATION = "Finish the waiting compensation first."
FOLDER_NONEMPTY = "The folder must be empty to compensate."
NOT_WAITING = "That compensation is not waiting."
NOT_ON_TASK = "That compensation is not on this task."
NAME_DECLINE = "Name why this compensation will not be carried out."
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
    if workflow_store.draft_version(connection, int(task["id"])) is None and (
        workflow_store.any_started(connection, int(task["id"]))
    ):
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
    draft = workflow_store.draft_version(connection, int(task["id"]))
    if draft is None:
        version_id = _ensure_current(connection, int(task["id"]))
    else:
        version_id = int(draft["id"])
    step_id = workflow_store.insert_step(
        connection,
        int(task["id"]),
        kept_title,
        kept_action,
        kept_project,
        kept_path,
        kept_what,
        kept_class,
    )
    workflow_store.link_step(
        connection,
        version_id,
        step_id,
        workflow_store.next_position(connection, version_id),
    )
    return _detail(connection, int(task["id"]))


def remove(connection: sqlite3.Connection, task_id: int, step_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    row = workflow_store.row_step(connection, step_id)
    if row is None or int(row["task_id"]) != int(task["id"]):
        return conflict(STEP_NOT_ON_TASK)
    draft = workflow_store.draft_version(connection, int(task["id"]))
    if draft is not None and workflow_store.step_on_version(
        connection, int(draft["id"]), int(row["id"])
    ):
        if row["state"] != "Pending":
            return conflict(KEEP_RAN)
        workflow_store.delete_step(connection, int(row["id"]))
        return _detail(connection, int(task["id"]))
    if workflow_store.any_started(connection, int(task["id"])):
        return conflict(REMOVE_ONLY_BEFORE)
    workflow_store.delete_step(connection, int(row["id"]))
    current = workflow_store.current_version(connection, int(task["id"]))
    if current is not None:
        workflow_store.delete_version_if_empty(connection, int(current["id"]))
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


def replay_execution(connection: sqlite3.Connection, task_id: int):
    if task_store.row_task(connection, task_id) is None:
        return missing("Task not found.")
    rows = workflow_store.steps(connection, task_id)
    if not rows:
        return conflict(NO_REPLAY)
    if any(row["state"] == "Running" for row in rows):
        return conflict(RECOVER_FIRST)
    current = workflow_store.current_version(connection, task_id)
    version = int(current["number"]) if current is not None else 1
    from task_manager.storage import file_read_store

    read_paths = [
        item["path"] for item in file_read_store.file_reads_for(connection, task_id)
    ]
    used: dict[str, int] = {}
    matched: list[dict[str, str]] = []
    stopped = None
    for row in rows:
        if row["state"] == "Completed":
            if not _effect_matches(connection, row, read_paths, used):
                stopped = f"Stopped at {row['title']}: {MISSING_EFFECT}"
                break
            matched.append(
                {
                    "title": row["title"],
                    "action": row["action"],
                    "state": "Completed",
                    "effect": row["path"],
                }
            )
            continue
        if row["state"] == "Pending":
            stopped = f"Stopped at {row['title']}: {STEP_NOT_RUN}"
        elif row["state"] == "Waiting":
            stopped = f"Stopped at {row['title']}: {WAITING}"
        else:
            stopped = f"Stopped at {row['title']}: {row['detail']}"
        break
    return {"version": version, "matched": matched, "stopped": stopped}


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    current = workflow_store.current_version(connection, task_id)
    rows = workflow_store.steps(connection, task_id)
    draft_row = workflow_store.draft_version(connection, task_id)
    draft = None
    if draft_row is not None:
        draft = {
            "number": int(draft_row["number"]),
            "steps": [
                _public(row)
                for row in workflow_store.steps_for_version(connection, int(draft_row["id"]))
            ],
        }
    if current is not None:
        version: int | None = int(current["number"])
    elif rows:
        version = 1
    else:
        version = None
    return {
        "steps": [_public(row) for row in rows],
        "version": version,
        "draft": draft,
        "migrations": [
            {
                "from_version": int(row["from_version"]),
                "to_version": int(row["to_version"]),
                "reason": row["reason"],
                "recorded_at": row["recorded_at"],
            }
            for row in workflow_store.migrations(connection, task_id)
        ],
        "stopped": _stopped(rows),
        "started": any(row["state"] != "Pending" for row in rows),
        "finished": bool(rows) and all(row["state"] == "Completed" for row in rows),
        "interrupted": any(row["state"] == "Running" for row in rows),
        "replay": _events(connection, task_id),
        "execution": _execution(connection, task_id, rows),
        "saga": _saga(rows, workflow_store.compensations(connection, task_id)),
        "compensations": [
            {
                "id": int(row["id"]),
                "title": row["title"],
                "state": row["state"],
                "reason": row["reason"],
            }
            for row in workflow_store.compensations(connection, task_id)
        ],
        "outbox": [
            {
                "id": int(row["id"]),
                "title": row["title"],
                "effect": row["effect"],
                "state": row["state"],
            }
            for row in workflow_store.outbox_messages(connection, task_id)
        ],
        "inbox": [
            {"name": row["name"], "outbox_id": int(row["outbox_id"])}
            for row in workflow_store.inbox_entries(connection, task_id)
        ],
    }


def revise(connection: sqlite3.Connection, task_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    if not workflow_store.stored_steps(connection, int(task["id"])):
        return conflict(NO_WORKFLOW)
    current_steps = workflow_store.steps(connection, int(task["id"]))
    if any(row["state"] == "Running" for row in current_steps):
        return conflict(RECOVER_FIRST)
    if workflow_store.draft_version(connection, int(task["id"])) is not None:
        return conflict(DRAFT_EXISTS)
    if not any(row["state"] != "Pending" for row in current_steps):
        return conflict(NOT_RUN)
    _ensure_current(connection, int(task["id"]))
    current = workflow_store.current_version(connection, int(task["id"]))
    draft_id = workflow_store.insert_version(
        connection, int(task["id"]), int(current["number"]) + 1, "Draft"
    )
    position = 1
    for row in workflow_store.steps(connection, int(task["id"])):
        if row["state"] == "Pending":
            continue
        workflow_store.link_step(connection, draft_id, int(row["id"]), position)
        position += 1
    return _detail(connection, int(task["id"]))


def migrate(
    connection: sqlite3.Connection,
    task_id: int,
    reason: str | None,
    occurred_at: str,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    draft = workflow_store.draft_version(connection, int(task["id"]))
    if draft is None:
        return conflict(NO_DRAFT)
    kept = clean(reason)
    if not kept:
        return bad_request(NAME_REASON)
    current = workflow_store.current_version(connection, int(task["id"]))
    current_steps = workflow_store.steps(connection, int(task["id"]))
    if any(row["state"] == "Running" for row in current_steps):
        return conflict(RECOVER_FIRST)
    draft_ids = {
        int(row["id"])
        for row in workflow_store.steps_for_version(connection, int(draft["id"]))
    }
    for row in current_steps:
        if row["state"] != "Pending" and int(row["id"]) not in draft_ids:
            return conflict(KEEP_RAN)
    workflow_store.set_version_state(connection, int(current["id"]), "Superseded")
    workflow_store.set_version_state(connection, int(draft["id"]), "Current")
    workflow_store.insert_migration(
        connection,
        int(task["id"]),
        int(current["id"]),
        int(draft["id"]),
        kept,
        occurred_at,
    )
    return _detail(connection, int(task["id"]))


def deliver(connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    kept = clean(name)
    if not kept:
        return bad_request(NAME_DELIVERY)
    if workflow_store.inbox_entry(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    pending = workflow_store.oldest_pending_outbox(connection, int(task["id"]))
    if pending is None:
        return conflict(NO_OUTBOX)
    workflow_store.mark_outbox_delivered(connection, int(pending["id"]))
    workflow_store.insert_inbox(
        connection, int(task["id"]), kept, int(pending["id"]), occurred_at
    )
    return _detail(connection, int(task["id"]))


def compensate(
    connection: sqlite3.Connection, task_id: int, reason: str | None, occurred_at: str
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    kept = clean(reason)
    if not kept:
        return bad_request(NAME_COMPENSATION)
    detail = _detail(connection, int(task["id"]))
    saga = detail["workflow"]["saga"]
    if detail["workflow"]["interrupted"]:
        return conflict(RECOVER_FIRST)
    if saga == "Waiting":
        return conflict(WAITING_COMPENSATION)
    if saga == "Compensated":
        return conflict(NO_COMPENSATE)
    if saga != "Failed":
        return conflict(NOT_FAILED)
    taken = {
        int(row["step_id"]) for row in workflow_store.compensations(connection, int(task["id"]))
    }
    chosen = None
    for row in reversed(workflow_store.steps(connection, int(task["id"]))):
        if row["state"] == "Completed" and int(row["id"]) not in taken:
            chosen = row
            break
    if chosen is None:
        return conflict(NO_COMPENSATE)
    state = "Waiting" if chosen["action"] == "folder" else "Compensated"
    workflow_store.insert_compensation(
        connection, int(task["id"]), int(chosen["id"]), kept, state, occurred_at
    )
    return _detail(connection, int(task["id"]))


def approve_compensation(
    connection: sqlite3.Connection,
    task_id: int,
    compensation_id: int,
    evidence: str | None,
    occurred_at: str,
    project_root: Path,
):
    del occurred_at
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    kept = clean(evidence)
    if not kept:
        return bad_request(EVIDENCE_REQUIRED)
    row = workflow_store.compensation_on_task(connection, int(task["id"]), compensation_id)
    if row is None:
        return conflict(NOT_ON_TASK)
    if row["state"] != "Waiting":
        return conflict(NOT_WAITING)
    removed = _remove_empty_folder(row, project_root)
    if isinstance(removed, Refusal):
        return removed
    workflow_store.settle_compensation(connection, int(row["id"]), "Compensated", kept, None)
    return _detail(connection, int(task["id"]))


def decline_compensation(
    connection: sqlite3.Connection,
    task_id: int,
    compensation_id: int,
    reason: str | None,
    occurred_at: str,
):
    del occurred_at
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    kept = clean(reason)
    if not kept:
        return bad_request(NAME_DECLINE)
    row = workflow_store.compensation_on_task(connection, int(task["id"]), compensation_id)
    if row is None:
        return conflict(NOT_ON_TASK)
    if row["state"] != "Waiting":
        return conflict(NOT_WAITING)
    workflow_store.settle_compensation(connection, int(row["id"]), "Not carried out", None, kept)
    return _detail(connection, int(task["id"]))


def _saga(rows: list[sqlite3.Row], compensations: list[sqlite3.Row]) -> str | None:
    if not rows:
        return None
    if any(row["state"] == "Waiting" for row in compensations):
        return "Waiting"
    completed = [row for row in rows if row["state"] == "Completed"]
    settled = {
        int(row["step_id"])
        for row in compensations
        if row["state"] in ("Compensated", "Not carried out")
    }
    failed = any(row["state"] == "Failed" for row in rows)
    if failed and completed and all(int(row["id"]) in settled for row in completed):
        return "Compensated"
    if failed:
        return "Failed"
    return "Open"


def _remove_empty_folder(row: sqlite3.Row, project_root: Path):
    relative = _relative_inside(row["path"])
    project_dir = _project_dir(row["project"], project_root)
    if relative is None or not project_dir.is_dir():
        return conflict(FOLDER_MISMATCH)
    target = (project_dir / relative).resolve()
    if not _inside(target, project_dir):
        return conflict(FOLDER_OUTSIDE)
    if not target.exists():
        return None
    if not target.is_dir():
        return conflict(FOLDER_MISMATCH)
    if any(target.iterdir()):
        return conflict(FOLDER_NONEMPTY)
    target.rmdir()
    return None


def _ensure_current(connection: sqlite3.Connection, task_id: int) -> int:
    current = workflow_store.current_version(connection, task_id)
    if current is not None:
        return int(current["id"])
    version_id = workflow_store.insert_version(connection, task_id, 1, "Current")
    for index, row in enumerate(workflow_store.stored_steps(connection, task_id), start=1):
        workflow_store.link_step(connection, version_id, int(row["id"]), index)
    return version_id


def _execution(
    connection: sqlite3.Connection, task_id: int, rows: list[sqlite3.Row]
) -> dict[str, object] | None:
    if not rows or any(row["state"] == "Running" for row in rows):
        return None
    report = replay_execution(connection, task_id)
    if isinstance(report, Refusal):
        return None
    return report


def _effect_matches(
    connection: sqlite3.Connection,
    step: sqlite3.Row,
    read_paths: list[str],
    used: dict[str, int],
) -> bool:
    if step["action"] == "read":
        path = step["path"]
        seen = used.get(path, 0) + 1
        if read_paths.count(path) < seen:
            return False
        used[path] = seen
        return True
    if step["change_id"] is None:
        return False
    change = implementation_store.row_change(connection, int(step["change_id"]))
    return change is not None and int(change["task_id"]) == int(step["task_id"])


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
    if state == "Completed":
        workflow_store.insert_outbox(
            connection,
            int(step["task_id"]),
            int(step["id"]),
            step["path"],
            occurred_at,
        )


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
