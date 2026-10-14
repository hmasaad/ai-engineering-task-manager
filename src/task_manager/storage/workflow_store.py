"""Workflow steps. One row is one stored action on one task."""

import sqlite3


def steps(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, task_id, position, title, action, project, path,
               what_changed, change_class, state, detail, change_id
        FROM workflow_step
        WHERE task_id = ?
        ORDER BY position ASC, id ASC
        """,
        (task_id,),
    ).fetchall()


def row_step(connection: sqlite3.Connection, step_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, position, title, action, project, path,
               what_changed, change_class, state, detail, change_id
        FROM workflow_step
        WHERE id = ?
        """,
        (step_id,),
    ).fetchone()


def any_started(connection: sqlite3.Connection, task_id: int) -> bool:
    row = connection.execute(
        """
        SELECT 1 FROM workflow_step
        WHERE task_id = ? AND state != 'Pending'
        LIMIT 1
        """,
        (task_id,),
    ).fetchone()
    return row is not None


def insert_step(
    connection: sqlite3.Connection,
    task_id: int,
    title: str,
    action: str,
    project: str,
    path: str,
    what_changed: str | None,
    change_class: str | None,
) -> None:
    position = connection.execute(
        """
        SELECT COALESCE(MAX(position), 0) + 1
        FROM workflow_step
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()[0]
    connection.execute(
        """
        INSERT INTO workflow_step (
            task_id, position, title, action, project, path,
            what_changed, change_class, state
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
        """,
        (task_id, position, title, action, project, path, what_changed, change_class),
    )


def delete_step(connection: sqlite3.Connection, step_id: int) -> None:
    connection.execute("DELETE FROM workflow_step WHERE id = ?", (step_id,))


def update_step(
    connection: sqlite3.Connection,
    step_id: int,
    state: str,
    detail: str | None,
    change_id: int | None,
) -> None:
    connection.execute(
        """
        UPDATE workflow_step
        SET state = ?, detail = ?, change_id = ?
        WHERE id = ?
        """,
        (state, detail, change_id, step_id),
    )
