"""Prerequisite links. One row names one task and one prerequisite."""

import sqlite3


def prerequisites(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT task.id, task.title, task.status
        FROM task_dependency
        JOIN task ON task.id = task_dependency.prerequisite_id
        WHERE task_dependency.task_id = ?
        ORDER BY task.id ASC
        """,
        (task_id,),
    ).fetchall()


def has_link(connection: sqlite3.Connection, task_id: int, prerequisite_id: int) -> bool:
    row = connection.execute(
        """
        SELECT 1 FROM task_dependency
        WHERE task_id = ? AND prerequisite_id = ?
        """,
        (task_id, prerequisite_id),
    ).fetchone()
    return row is not None


def insert_link(connection: sqlite3.Connection, task_id: int, prerequisite_id: int) -> None:
    connection.execute(
        """
        INSERT INTO task_dependency (task_id, prerequisite_id)
        VALUES (?, ?)
        """,
        (task_id, prerequisite_id),
    )


def delete_link(connection: sqlite3.Connection, task_id: int, prerequisite_id: int) -> None:
    connection.execute(
        """
        DELETE FROM task_dependency
        WHERE task_id = ? AND prerequisite_id = ?
        """,
        (task_id, prerequisite_id),
    )


def all_tasks(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return connection.execute(
        "SELECT id, title, status FROM task ORDER BY id ASC"
    ).fetchall()


def all_edges(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return connection.execute(
        "SELECT task_id, prerequisite_id FROM task_dependency ORDER BY task_id ASC, prerequisite_id ASC"
    ).fetchall()
