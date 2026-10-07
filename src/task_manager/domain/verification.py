"""Record a check of a carried-out change against one acceptance criterion."""

import sqlite3

from task_manager.domain.capture import CANCELLED, _detail
from task_manager.domain.results import bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import implementation_store, task_store, verification_store
from task_manager.storage.connection import engineer_name

EVIDENCE_REQUIRED = "An account of the evidence is required."
CHOOSE_RESULT = "Choose Passed or Failed."
CHOOSE_CRITERION = "Choose an acceptance criterion."
MUST_BE_IN_PROGRESS = "The task must be In Progress."
START_FIRST = "Start the task first."
REOPEN_FIRST = "Reopen the task first."
CHECK_SAME_TASK = "The check must name a change on that task."
CRITERION_SAME_TASK = "The check must name a criterion on that task."
CHANGE_NOT_FOUND = "Implementation change not found."
CRITERION_NOT_FOUND = "Acceptance criterion not found."
MUST_BE_CARRIED_OUT = "The change must be carried out before it can be checked."
NOT_CARRIED_OUT = "A change that was not carried out cannot be checked."

_RESULTS = {"Passed": "passed", "Failed": "failed"}


def record(
    connection: sqlite3.Connection,
    task_id: int,
    change_id: int,
    criterion_id: int | None,
    evidence: str | None,
    result: str | None,
    occurred_at: str,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _status(task["status"])
    if status_refusal is not None:
        return status_refusal
    change = implementation_store.row_change(connection, change_id)
    if change is None:
        return missing(CHANGE_NOT_FOUND)
    if int(change["task_id"]) != int(task["id"]):
        return conflict(CHECK_SAME_TASK)
    outcome = implementation_store.change_payload(change)["outcome"]
    if outcome == "Awaiting approval":
        return conflict(MUST_BE_CARRIED_OUT)
    if outcome == "Not carried out":
        return conflict(NOT_CARRIED_OUT)
    if criterion_id is None:
        return bad_request(CHOOSE_CRITERION)
    criterion = _criterion(connection, criterion_id)
    if criterion is None:
        return missing(CRITERION_NOT_FOUND)
    if int(criterion["task_id"]) != int(task["id"]):
        return conflict(CRITERION_SAME_TASK)
    seen = clean(evidence)
    if not seen:
        return bad_request(EVIDENCE_REQUIRED)
    stored = _RESULTS.get(result or "")
    if stored is None:
        return bad_request(CHOOSE_RESULT)
    verification_store.insert_check(
        connection,
        int(change["id"]),
        int(criterion["id"]),
        criterion["text"],
        seen,
        stored,
        engineer_name(connection),
        occurred_at,
    )
    return _detail(connection, int(task["id"]))


def lacking_accounts(connection: sqlite3.Connection, task_id: int) -> list[str]:
    live = {int(row["id"]) for row in task_store.criteria_for(connection, task_id)}
    accounts: list[str] = []
    for change in implementation_store.changes_for(connection, task_id):
        if change["outcome"] != "Carried out":
            continue
        checks = verification_store.checks_for(connection, int(change["id"]))
        if not verification_store.passing_check(str(change["outcome"]), checks, live):
            accounts.append(str(change["what_changed"]))
    return accounts


def _status(status: str):
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


def _criterion(connection: sqlite3.Connection, criterion_id: int) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM acceptance_criterion WHERE id = ?",
        (criterion_id,),
    ).fetchone()
