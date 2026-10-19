"""One named command performs once. The same name does not perform again."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.text import clean
from task_manager.storage import execution_store


def earlier(connection: sqlite3.Connection, task_id: int, name: str | None):
    kept = clean(name)
    if not kept:
        return None
    row = execution_store.row_execution(connection, task_id, kept)
    if row is None:
        return None
    return _detail(connection, task_id)


def remember(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    action: str,
    path: str,
    occurred_at: str,
) -> None:
    kept = clean(name)
    if not kept:
        return
    execution_store.insert_execution(connection, task_id, kept, action, path, occurred_at)
