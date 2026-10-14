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


def insert_attempt(connection: sqlite3.Connection, step_id: int, effect_before: int) -> None:
    connection.execute(
        """
        INSERT INTO workflow_attempt (step_id, effect_before)
        VALUES (?, ?)
        """,
        (step_id, effect_before),
    )


def row_attempt(connection: sqlite3.Connection, step_id: int) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT step_id, effect_before FROM workflow_attempt WHERE step_id = ?",
        (step_id,),
    ).fetchone()


def delete_attempt(connection: sqlite3.Connection, step_id: int) -> None:
    connection.execute("DELETE FROM workflow_attempt WHERE step_id = ?", (step_id,))


def insert_event(
    connection: sqlite3.Connection,
    task_id: int,
    step_id: int,
    state: str,
    detail: str | None,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO workflow_event (task_id, step_id, state, detail, recorded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, step_id, state, detail, recorded_at),
    )


def events(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT workflow_event.id, workflow_event.step_id, workflow_step.title,
               workflow_event.state, workflow_event.detail, workflow_event.recorded_at
        FROM workflow_event
        JOIN workflow_step ON workflow_step.id = workflow_event.step_id
        WHERE workflow_event.task_id = ?
        ORDER BY workflow_event.id ASC
        """,
        (task_id,),
    ).fetchall()


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
