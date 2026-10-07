"""Record, approve, and decline the change that carries out a task."""

import sqlite3

from task_manager.domain.capture import CANCELLED, _detail
from task_manager.domain.results import bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import implementation_store, task_store
from task_manager.storage.connection import assistant_name, engineer_name

WHAT_CHANGED_REQUIRED = "An account of what changed is required."
CHOOSE_CLASS = "Choose ordinary or consequential."
MUST_BE_IN_PROGRESS = "The task must be In Progress."
START_FIRST = "Start the task first."
REOPEN_FIRST = "Reopen the task first."
EVIDENCE_REQUIRED = "An account of the evidence reviewed is required."
ORDINARY_NO_APPROVAL = "An ordinary change does not wait for approval."
ALREADY_CARRIED_OUT = "The change is already carried out."
CANNOT_BE_CARRIED_OUT = "It cannot be carried out."
APPROVAL_SAME_TASK = "The approval must name a change on that task."
CHANGE_NOT_FOUND = "Implementation change not found."
REASON_REQUIRED = "A reason is required."
CARRIED_OUT_STAYS = "A carried-out change stays in the record."
CHANGE_ON_TASK = "The change must be on that task."
NAME_PROJECT = "Name the project this change is for."
ASSISTANT_CANNOT_APPROVE = "The assistant cannot approve a change."
ASSISTANT_CANNOT_DECLINE = "The assistant cannot decline a change."

_CLASSES = {"ordinary", "consequential"}


def record(
    connection: sqlite3.Connection,
    task_id: int,
    what_changed: str | None,
    change_class: str | None,
    occurred_at: str,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    text = clean(what_changed)
    if not text:
        return bad_request(WHAT_CHANGED_REQUIRED)
    if change_class not in _CLASSES:
        return bad_request(CHOOSE_CLASS)
    implementation_store.insert_change(
        connection,
        int(task["id"]),
        text,
        change_class,
        engineer_name(connection),
        occurred_at,
    )
    return _detail(connection, int(task["id"]))


def record_assistant(
    connection: sqlite3.Connection,
    task_id: int,
    project: str | None,
    change_class: str | None,
    what_changed: str | None,
    stopped: bool,
    occurred_at: str,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    named_project = clean(project)
    if not named_project:
        return bad_request(NAME_PROJECT)
    text = clean(what_changed)
    if not text:
        return bad_request(WHAT_CHANGED_REQUIRED)
    if change_class not in _CLASSES:
        return bad_request(CHOOSE_CLASS)
    stored_class = change_class
    stopped_flag = 0
    if change_class == "ordinary" and stopped:
        stored_class = "consequential"
        stopped_flag = 1
    change_id = implementation_store.insert_change(
        connection,
        int(task["id"]),
        text,
        stored_class,
        engineer_name(connection),
        occurred_at,
    )
    implementation_store.insert_assistant_change(
        connection,
        change_id,
        named_project,
        assistant_name(connection),
        stopped_flag,
    )
    return _detail(connection, int(task["id"]))


def approve(
    connection: sqlite3.Connection,
    task_id: int,
    change_id: int,
    evidence: str | None,
    occurred_at: str,
    actor: str | None = None,
):
    if actor == "assistant":
        return conflict(ASSISTANT_CANNOT_APPROVE)
    located = _locate(connection, task_id, change_id, APPROVAL_SAME_TASK)
    if not isinstance(located, tuple):
        return located
    task, change = located
    if change["class"] == "ordinary":
        return conflict(ORDINARY_NO_APPROVAL)
    if change["kind"] == "approved":
        return conflict(ALREADY_CARRIED_OUT)
    if change["kind"] == "not_carried_out":
        return conflict(CANNOT_BE_CARRIED_OUT)
    if task["status"] != "In Progress":
        return conflict(MUST_BE_IN_PROGRESS)
    reviewed = clean(evidence)
    if not reviewed:
        return bad_request(EVIDENCE_REQUIRED)
    implementation_store.insert_resolution(
        connection,
        int(change["id"]),
        "approved",
        reviewed,
        None,
        engineer_name(connection),
        occurred_at,
    )
    return _detail(connection, int(task["id"]))


def mark_not_carried_out(
    connection: sqlite3.Connection,
    task_id: int,
    change_id: int,
    reason: str | None,
    occurred_at: str,
    actor: str | None = None,
):
    if actor == "assistant":
        return conflict(ASSISTANT_CANNOT_DECLINE)
    located = _locate(connection, task_id, change_id, CHANGE_ON_TASK)
    if not isinstance(located, tuple):
        return located
    task, change = located
    if task["status"] != "In Progress":
        return conflict(MUST_BE_IN_PROGRESS)
    if change["class"] == "ordinary" or change["kind"] == "approved":
        return conflict(CARRIED_OUT_STAYS)
    if change["kind"] == "not_carried_out":
        return conflict(CANNOT_BE_CARRIED_OUT)
    kept = clean(reason)
    if not kept:
        return bad_request(REASON_REQUIRED)
    implementation_store.insert_resolution(
        connection,
        int(change["id"]),
        "not_carried_out",
        None,
        kept,
        engineer_name(connection),
        occurred_at,
    )
    return _detail(connection, int(task["id"]))


def awaiting_accounts(connection: sqlite3.Connection, task_id: int) -> list[str]:
    return [
        str(item["what_changed"])
        for item in implementation_store.changes_for(connection, task_id)
        if item["outcome"] == "Awaiting approval"
    ]


def _record_status(status: str):
    if status == "Draft":
        return conflict(MUST_BE_IN_PROGRESS)
    if status == "Ready":
        return conflict(START_FIRST)
    if status == "Completed":
        return conflict(REOPEN_FIRST)
    if status == "Cancelled":
        return conflict(CANCELLED)
    if status != "In Progress":
        return conflict(MUST_BE_IN_PROGRESS)
    return None


def _locate(connection: sqlite3.Connection, task_id: int, change_id: int, other_task_message: str):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    change = implementation_store.row_change(connection, change_id)
    if change is None:
        return missing(CHANGE_NOT_FOUND)
    if int(change["task_id"]) != int(task["id"]):
        return conflict(other_task_message)
    return task, change
