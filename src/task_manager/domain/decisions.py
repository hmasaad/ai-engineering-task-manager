"""Record decisions. Rows are inserted once and never updated or deleted."""

import sqlite3

from task_manager.domain.capture import CANCELLED, _detail
from task_manager.domain.results import bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import task_store
from task_manager.storage.decision_store import (
    check_for_link,
    decision_row,
    insert_decision,
    insert_decision_check,
    link_supersedes,
)


def add_decision(
    connection: sqlite3.Connection,
    task_id: int,
    statement: str,
    rationale: str,
    supersedes: list[int] | None,
    occurred_at: str,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict("Decisions cannot be added to a cancelled task.")
    cleaned_statement = clean(statement)
    cleaned_rationale = clean(rationale)
    if not cleaned_statement or not cleaned_rationale:
        return bad_request("Both a statement and a rationale are required.")
    decision_id = insert_decision(
        connection, task_id, cleaned_statement, cleaned_rationale, occurred_at
    )
    for earlier_id in _unique(supersedes or []):
        if earlier_id == decision_id:
            return conflict("A decision cannot supersede itself or a decision that comes after it.")
        earlier = decision_row(connection, earlier_id)
        if earlier is None:
            return missing("Decision not found.")
        if int(earlier["task_id"]) != task_id:
            return conflict("A decision can only supersede earlier decisions on the same task.")
        if _comes_after(earlier["recorded_at"], int(earlier["id"]), occurred_at, decision_id):
            return conflict("A decision cannot supersede itself or a decision that comes after it.")
        link_supersedes(connection, decision_id, earlier_id)
    return _detail(connection, task_id)


def add_linked_decision(
    connection: sqlite3.Connection,
    task_id: int,
    statement: str,
    rationale: str,
    check_id: int | None,
    supersedes: list[int] | None,
    occurred_at: str,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict("Decisions cannot be added to a cancelled task.")
    cleaned_statement = clean(statement)
    cleaned_rationale = clean(rationale)
    if not cleaned_statement or not cleaned_rationale:
        return bad_request("Both a statement and a rationale are required.")
    if check_id is None:
        return bad_request("Choose the check this decision rests on.")
    check = check_for_link(connection, check_id)
    if check is None:
        return missing("Check not found.")
    if int(check["task_id"]) != task_id:
        return conflict("The decision must name a check on that task.")
    decision_id = insert_decision(
        connection, task_id, cleaned_statement, cleaned_rationale, occurred_at
    )
    insert_decision_check(connection, decision_id, int(check["id"]))
    for earlier_id in _unique(supersedes or []):
        if earlier_id == decision_id:
            return conflict("A decision cannot supersede itself or a decision that comes after it.")
        earlier = decision_row(connection, earlier_id)
        if earlier is None:
            return missing("Decision not found.")
        if int(earlier["task_id"]) != task_id:
            return conflict("A decision can only supersede earlier decisions on the same task.")
        if _comes_after(earlier["recorded_at"], int(earlier["id"]), occurred_at, decision_id):
            return conflict("A decision cannot supersede itself or a decision that comes after it.")
        link_supersedes(connection, decision_id, earlier_id)
    return _detail(connection, task_id)


def _unique(values: list[int]) -> list[int]:
    seen: list[int] = []
    for value in values:
        if value not in seen:
            seen.append(value)
    return seen


def _comes_after(existing_at: str, existing_id: int, new_at: str, new_id: int) -> bool:
    if existing_at > new_at:
        return True
    if existing_at == new_at and existing_id > new_id:
        return True
    return False
