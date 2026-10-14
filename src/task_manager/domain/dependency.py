"""Prerequisite links, the execution order, and the start hold."""

import sqlite3

from task_manager.domain.capture import CANCELLED, _detail
from task_manager.domain.results import bad_request, conflict, missing
from task_manager.storage import dependency_store, task_store

SELF = "A task cannot depend on itself."
PREREQUISITE_NOT_FOUND = "Prerequisite not found."
CYCLE = "That dependency would form a cycle."
NOT_LINKED = "That prerequisite is not linked."
NAME_PREREQUISITE = "Name the prerequisite task."


def add(
    connection: sqlite3.Connection,
    task_id: int,
    prerequisite_id: int | None,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict(CANCELLED)
    if prerequisite_id is None:
        return bad_request(NAME_PREREQUISITE)
    prerequisite = task_store.row_task(connection, prerequisite_id)
    if prerequisite is None:
        return missing(PREREQUISITE_NOT_FOUND)
    if prerequisite_id == task_id:
        return conflict(SELF)
    if _reaches(connection, prerequisite_id, task_id):
        return conflict(CYCLE)
    if not dependency_store.has_link(connection, task_id, prerequisite_id):
        dependency_store.insert_link(connection, task_id, prerequisite_id)
    return _detail(connection, task_id)


def remove(
    connection: sqlite3.Connection,
    task_id: int,
    prerequisite_id: int,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] == "Cancelled":
        return conflict(CANCELLED)
    if task_store.row_task(connection, prerequisite_id) is None:
        return missing(PREREQUISITE_NOT_FOUND)
    if not dependency_store.has_link(connection, task_id, prerequisite_id):
        return conflict(NOT_LINKED)
    dependency_store.delete_link(connection, task_id, prerequisite_id)
    return _detail(connection, task_id)


def blocked_sentence(connection: sqlite3.Connection, task_id: int) -> str | None:
    parts: list[str] = []
    for prerequisite in dependency_store.prerequisites(connection, task_id):
        if prerequisite["status"] == "Completed":
            continue
        unmet = [
            row["text"]
            for row in task_store.criteria_for(connection, int(prerequisite["id"]))
            if not task_store.is_verified(row)
        ]
        if unmet:
            parts.append(
                f"Blocked by {prerequisite['title']} ({prerequisite['status']}): unverified {', '.join(unmet)}"
            )
        else:
            parts.append(
                f"Blocked by {prerequisite['title']} ({prerequisite['status']}): incomplete"
            )
    if not parts:
        return None
    return ". ".join(parts) + "."


def execution_order(connection: sqlite3.Connection) -> list[dict[str, object]]:
    tasks = dependency_store.all_tasks(connection)
    by_id = {int(row["id"]): row for row in tasks}
    indegree = {task_id: 0 for task_id in by_id}
    successors: dict[int, list[int]] = {task_id: [] for task_id in by_id}
    for edge in dependency_store.all_edges(connection):
        task_id = int(edge["task_id"])
        prerequisite_id = int(edge["prerequisite_id"])
        indegree[task_id] += 1
        successors[prerequisite_id].append(task_id)
    ready = sorted(task_id for task_id, count in indegree.items() if count == 0)
    order: list[dict[str, object]] = []
    while ready:
        current = ready.pop(0)
        row = by_id[current]
        order.append({"id": int(row["id"]), "title": row["title"], "status": row["status"]})
        released: list[int] = []
        for successor in successors[current]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                released.append(successor)
        ready.extend(released)
        ready.sort()
    return order


def _reaches(connection: sqlite3.Connection, start_id: int, target_id: int) -> bool:
    seen: set[int] = set()
    stack = [start_id]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        for row in dependency_store.prerequisites(connection, current):
            prerequisite_id = int(row["id"])
            if prerequisite_id == target_id:
                return True
            stack.append(prerequisite_id)
    return False
