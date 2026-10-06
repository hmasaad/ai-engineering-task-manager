"""Parent links. A task is given a parent only while it is being created or attached."""

import sqlite3

from task_manager.storage.task_store import children, row_task, set_parent


def ancestor_ids(connection: sqlite3.Connection, task_id: int) -> list[int]:
    found: list[int] = []
    current = row_task(connection, task_id)
    seen: set[int] = set()
    while current is not None and current["parent_id"] is not None:
        parent_id = int(current["parent_id"])
        if parent_id in seen:
            break
        seen.add(parent_id)
        found.append(parent_id)
        current = row_task(connection, parent_id)
    return found


def descendant_ids(connection: sqlite3.Connection, task_id: int) -> set[int]:
    found: set[int] = set()
    stack = [task_id]
    while stack:
        current = stack.pop()
        for child in children(connection, current):
            child_id = int(child["id"])
            if child_id not in found:
                found.add(child_id)
                stack.append(child_id)
    return found


def link_parent(connection: sqlite3.Connection, child_id: int, parent_id: int) -> None:
    set_parent(connection, child_id, parent_id)
