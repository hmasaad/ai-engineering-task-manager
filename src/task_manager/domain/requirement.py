"""Record a requirement, its trace, and the runs the engineer reports."""

import sqlite3

from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import requirement_store, task_store
from task_manager.storage.connection import engineer_name

STATEMENT_REQUIRED = "A requirement statement is required."
CHOOSE_KIND = "Choose functional or non-functional."
REQUIREMENT_NOT_FOUND = "Requirement not found."
TASK_NOT_FOUND = "Task not found."
CRITERION_NOT_FOUND = "Criterion not found."
CRITERION_ON_TASK = "The criterion must be on that task."
CRITERION_ALREADY_LINKED = "That criterion is already linked to this requirement."
NAME_CHECK = "Name the check this requirement uses."
CHECK_ALREADY_NAMED = "That check is already named on this requirement."
CHECK_NOT_FOUND = "Check not found."
RUN_IDENTIFIER_REQUIRED = "A run identifier is required."
CHOOSE_RESULT = "Choose Passed or Failed."
CHECK_NOT_PASSED = "A required check has not passed."

_RESULTS = {"Passed": "passed", "Failed": "failed"}


def record(connection: sqlite3.Connection, statement: str | None, kind: str | None, occurred_at: str):
    cleaned = clean(statement)
    if not cleaned:
        return bad_request(STATEMENT_REQUIRED)
    if not requirement_store.kind_allowed(kind):
        return bad_request(CHOOSE_KIND)
    requirement_id = requirement_store.insert_requirement(connection, kind, cleaned, occurred_at)
    return _detail(connection, requirement_id)


def change(
    connection: sqlite3.Connection,
    requirement_id: int,
    statement: str | None,
    kind: str | None,
    occurred_at: str,
):
    row = requirement_store.row_requirement(connection, requirement_id)
    if row is None:
        return missing(REQUIREMENT_NOT_FOUND)
    cleaned = clean(statement)
    if not cleaned:
        return bad_request(STATEMENT_REQUIRED)
    if not requirement_store.kind_allowed(kind):
        return bad_request(CHOOSE_KIND)
    if cleaned == row["statement"] and kind == row["kind"]:
        return _detail(connection, requirement_id)
    requirement_store.update_requirement(connection, requirement_id, kind, cleaned)
    _unverify_linked(connection, requirement_id, occurred_at)
    return _detail(connection, requirement_id)


def link_task(connection: sqlite3.Connection, requirement_id: int, task_id: int | None):
    if requirement_store.row_requirement(connection, requirement_id) is None:
        return missing(REQUIREMENT_NOT_FOUND)
    if task_id is None or task_store.row_task(connection, task_id) is None:
        return missing(TASK_NOT_FOUND)
    if not requirement_store.task_linked(connection, requirement_id, task_id):
        requirement_store.link_task(connection, requirement_id, task_id)
    return _detail(connection, requirement_id)


def link_criterion(
    connection: sqlite3.Connection,
    requirement_id: int,
    task_id: int | None,
    criterion_id: int | None,
):
    if requirement_store.row_requirement(connection, requirement_id) is None:
        return missing(REQUIREMENT_NOT_FOUND)
    if task_id is None or task_store.row_task(connection, task_id) is None:
        return missing(TASK_NOT_FOUND)
    if criterion_id is None:
        return missing(CRITERION_NOT_FOUND)
    criterion = task_store.criterion(connection, task_id, criterion_id)
    if criterion is None:
        anywhere = connection.execute(
            "SELECT id FROM acceptance_criterion WHERE id = ?",
            (criterion_id,),
        ).fetchone()
        if anywhere is None:
            return missing(CRITERION_NOT_FOUND)
        return conflict(CRITERION_ON_TASK)
    if not requirement_store.task_linked(connection, requirement_id, task_id):
        return conflict(CRITERION_ON_TASK)
    if requirement_store.criterion_linked(connection, requirement_id, criterion_id):
        return conflict(CRITERION_ALREADY_LINKED)
    requirement_store.link_criterion(connection, requirement_id, criterion_id)
    return _detail(connection, requirement_id)


def unlink_task(connection: sqlite3.Connection, requirement_id: int, task_id: int):
    if requirement_store.row_requirement(connection, requirement_id) is None:
        return missing(REQUIREMENT_NOT_FOUND)
    if not requirement_store.unlink_task(connection, requirement_id, task_id):
        return missing(TASK_NOT_FOUND)
    return _detail(connection, requirement_id)


def unlink_criterion(connection: sqlite3.Connection, requirement_id: int, criterion_id: int):
    if requirement_store.row_requirement(connection, requirement_id) is None:
        return missing(REQUIREMENT_NOT_FOUND)
    if not requirement_store.unlink_criterion(connection, requirement_id, criterion_id):
        return missing(CRITERION_NOT_FOUND)
    return _detail(connection, requirement_id)


def name_check(connection: sqlite3.Connection, requirement_id: int, name: str | None):
    if requirement_store.row_requirement(connection, requirement_id) is None:
        return missing(REQUIREMENT_NOT_FOUND)
    cleaned = clean(name)
    if not cleaned:
        return bad_request(NAME_CHECK)
    if requirement_store.active_check_by_name(connection, requirement_id, cleaned) is not None:
        return conflict(CHECK_ALREADY_NAMED)
    requirement_store.insert_check(connection, requirement_id, cleaned)
    return _detail(connection, requirement_id)


def remove_check(connection: sqlite3.Connection, requirement_id: int, check_id: int, occurred_at: str):
    if requirement_store.row_requirement(connection, requirement_id) is None:
        return missing(REQUIREMENT_NOT_FOUND)
    check = requirement_store.row_check(connection, check_id)
    if (
        check is None
        or int(check["requirement_id"]) != requirement_id
        or check["removed_at"] is not None
    ):
        return missing(CHECK_NOT_FOUND)
    requirement_store.retire_check(connection, check_id, occurred_at)
    return _detail(connection, requirement_id)


def record_run(
    connection: sqlite3.Connection,
    requirement_id: int,
    check_name: str | None,
    result: str | None,
    run_identifier: str | None,
    occurred_at: str,
):
    if requirement_store.row_requirement(connection, requirement_id) is None:
        return missing(REQUIREMENT_NOT_FOUND)
    cleaned_name = clean(check_name)
    check = (
        requirement_store.active_check_by_name(connection, requirement_id, cleaned_name)
        if cleaned_name
        else None
    )
    if check is None:
        return missing(CHECK_NOT_FOUND)
    cleaned_run = clean(run_identifier)
    if not cleaned_run:
        return bad_request(RUN_IDENTIFIER_REQUIRED)
    stored = _RESULTS.get(result or "")
    if stored is None:
        return bad_request(CHOOSE_RESULT)
    requirement_store.insert_run(
        connection,
        int(check["id"]),
        stored,
        cleaned_run,
        engineer_name(connection),
        occurred_at,
    )
    return _detail(connection, requirement_id)


def criterion_has_unpassed_check(connection: sqlite3.Connection, criterion_id: int) -> bool:
    for requirement_id in requirement_store.requirement_ids_for_criterion(connection, criterion_id):
        for check in requirement_store.active_checks(connection, requirement_id):
            if requirement_store.current_result(connection, int(check["id"])) != "passed":
                return True
    return False


def blocking_identifiers(connection: sqlite3.Connection, task_id: int) -> list[str]:
    codes: list[str] = []
    for row in requirement_store.requirements_for_task(connection, task_id):
        requirement_id = int(row["id"])
        checks = requirement_store.active_checks(connection, requirement_id)
        if not checks:
            continue
        if any(
            requirement_store.current_result(connection, int(check["id"])) != "passed"
            for check in checks
        ):
            codes.append(requirement_store.identifier(requirement_id))
    return codes


def _unverify_linked(connection: sqlite3.Connection, requirement_id: int, occurred_at: str) -> None:
    from task_manager.domain.capture import _leave_completed

    detail = requirement_store.detail(connection, requirement_id)
    assert detail is not None
    completed: list[int] = []
    for criterion in detail["criteria"]:
        if criterion["state"] != "Verified":
            continue
        task_id = int(criterion["task_id"])
        task = task_store.row_task(connection, task_id)
        task_store.clear_verification(connection, int(criterion["id"]))
        if task is not None and task["status"] == "Completed" and task_id not in completed:
            completed.append(task_id)
    for task_id in completed:
        task = task_store.row_task(connection, task_id)
        if task is None or task["status"] != "Completed":
            continue
        _leave_completed(
            connection,
            task,
            occurred_at,
            "requirement_changed",
            str(requirement_id),
        )


def _detail(connection: sqlite3.Connection, requirement_id: int) -> dict[str, object] | Refusal:
    payload = requirement_store.detail(connection, requirement_id)
    if payload is None:
        return missing(REQUIREMENT_NOT_FOUND)
    return payload
