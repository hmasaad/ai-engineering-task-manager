"""Workflow steps. One row is one stored action on one task."""

import sqlite3


def steps(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    current = current_version(connection, task_id)
    if current is None:
        return stored_steps(connection, task_id)
    return steps_for_version(connection, int(current["id"]))


def stored_steps(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
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


def steps_for_version(connection: sqlite3.Connection, version_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT workflow_step.id, workflow_step.task_id, workflow_step.position,
               workflow_step.title, workflow_step.action, workflow_step.project,
               workflow_step.path, workflow_step.what_changed, workflow_step.change_class,
               workflow_step.state, workflow_step.detail, workflow_step.change_id
        FROM workflow_step
        JOIN workflow_version_step
          ON workflow_version_step.step_id = workflow_step.id
        WHERE workflow_version_step.version_id = ?
        ORDER BY workflow_version_step.position ASC, workflow_step.id ASC
        """,
        (version_id,),
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
    return any(row["state"] != "Pending" for row in steps(connection, task_id))


def insert_step(
    connection: sqlite3.Connection,
    task_id: int,
    title: str,
    action: str,
    project: str,
    path: str,
    what_changed: str | None,
    change_class: str | None,
) -> int:
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
    return int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])


def delete_step(connection: sqlite3.Connection, step_id: int) -> None:
    connection.execute("DELETE FROM workflow_version_step WHERE step_id = ?", (step_id,))
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


def insert_advance(
    connection: sqlite3.Connection, task_id: int, name: str, step_id: int
) -> bool:
    try:
        connection.execute(
            """
            INSERT INTO workflow_advance (task_id, name, step_id)
            VALUES (?, ?, ?)
            """,
            (task_id, name, step_id),
        )
    except sqlite3.IntegrityError:
        return False
    return True


def row_advance(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT task_id, name, step_id
        FROM workflow_advance
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


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


def current_version(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, number, state
        FROM workflow_version
        WHERE task_id = ? AND state = 'Current'
        """,
        (task_id,),
    ).fetchone()


def draft_version(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, number, state
        FROM workflow_version
        WHERE task_id = ? AND state = 'Draft'
        """,
        (task_id,),
    ).fetchone()


def insert_version(
    connection: sqlite3.Connection, task_id: int, number: int, state: str
) -> int:
    connection.execute(
        """
        INSERT INTO workflow_version (task_id, number, state)
        VALUES (?, ?, ?)
        """,
        (task_id, number, state),
    )
    return int(connection.execute("SELECT last_insert_rowid()").fetchone()[0])


def set_version_state(connection: sqlite3.Connection, version_id: int, state: str) -> None:
    connection.execute(
        "UPDATE workflow_version SET state = ? WHERE id = ?",
        (state, version_id),
    )


def link_step(
    connection: sqlite3.Connection, version_id: int, step_id: int, position: int
) -> None:
    connection.execute(
        """
        INSERT INTO workflow_version_step (version_id, step_id, position)
        VALUES (?, ?, ?)
        """,
        (version_id, step_id, position),
    )


def next_position(connection: sqlite3.Connection, version_id: int) -> int:
    row = connection.execute(
        """
        SELECT COALESCE(MAX(position), 0) + 1
        FROM workflow_version_step
        WHERE version_id = ?
        """,
        (version_id,),
    ).fetchone()
    return int(row[0])


def step_on_version(connection: sqlite3.Connection, version_id: int, step_id: int) -> bool:
    row = connection.execute(
        """
        SELECT 1 FROM workflow_version_step
        WHERE version_id = ? AND step_id = ?
        """,
        (version_id, step_id),
    ).fetchone()
    return row is not None


def delete_version_if_empty(connection: sqlite3.Connection, version_id: int) -> None:
    count = connection.execute(
        "SELECT COUNT(*) FROM workflow_version_step WHERE version_id = ?",
        (version_id,),
    ).fetchone()[0]
    if int(count) == 0:
        connection.execute("DELETE FROM workflow_version WHERE id = ?", (version_id,))


def insert_migration(
    connection: sqlite3.Connection,
    task_id: int,
    from_version_id: int,
    to_version_id: int,
    reason: str,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO workflow_migration (
            task_id, from_version_id, to_version_id, reason, recorded_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, from_version_id, to_version_id, reason, recorded_at),
    )


def migrations(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT from_version.number AS from_version,
               to_version.number AS to_version,
               workflow_migration.reason,
               workflow_migration.recorded_at
        FROM workflow_migration
        JOIN workflow_version AS from_version
          ON from_version.id = workflow_migration.from_version_id
        JOIN workflow_version AS to_version
          ON to_version.id = workflow_migration.to_version_id
        WHERE workflow_migration.task_id = ?
        ORDER BY workflow_migration.id ASC
        """,
        (task_id,),
    ).fetchall()


def insert_outbox(
    connection: sqlite3.Connection,
    task_id: int,
    step_id: int,
    effect: str,
    recorded_at: str,
) -> bool:
    try:
        connection.execute(
            """
            INSERT INTO workflow_outbox (task_id, step_id, effect, state, recorded_at)
            VALUES (?, ?, ?, 'Pending', ?)
            """,
            (task_id, step_id, effect, recorded_at),
        )
    except sqlite3.IntegrityError:
        return False
    return True


def outbox_messages(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT workflow_outbox.id, workflow_step.title, workflow_outbox.effect,
               workflow_outbox.state
        FROM workflow_outbox
        JOIN workflow_step ON workflow_step.id = workflow_outbox.step_id
        WHERE workflow_outbox.task_id = ?
        ORDER BY workflow_outbox.id ASC
        """,
        (task_id,),
    ).fetchall()


def oldest_pending_outbox(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, step_id, effect, state
        FROM workflow_outbox
        WHERE task_id = ? AND state = 'Pending'
        ORDER BY id ASC
        LIMIT 1
        """,
        (task_id,),
    ).fetchone()


def mark_outbox_delivered(connection: sqlite3.Connection, outbox_id: int) -> None:
    connection.execute(
        "UPDATE workflow_outbox SET state = 'Delivered' WHERE id = ?",
        (outbox_id,),
    )


def insert_inbox(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    outbox_id: int,
    recorded_at: str,
) -> bool:
    try:
        connection.execute(
            """
            INSERT INTO workflow_inbox (task_id, name, outbox_id, recorded_at)
            VALUES (?, ?, ?, ?)
            """,
            (task_id, name, outbox_id, recorded_at),
        )
    except sqlite3.IntegrityError:
        return False
    return True


def inbox_entry(connection: sqlite3.Connection, task_id: int, name: str) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT task_id, name, outbox_id, recorded_at
        FROM workflow_inbox
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def inbox_entries(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT name, outbox_id
        FROM workflow_inbox
        WHERE task_id = ?
        ORDER BY recorded_at ASC, name ASC
        """,
        (task_id,),
    ).fetchall()


def compensations(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT
            workflow_compensation.id,
            workflow_compensation.step_id,
            workflow_compensation.reason,
            workflow_compensation.state,
            workflow_compensation.evidence,
            workflow_compensation.decline_reason,
            workflow_step.title,
            workflow_step.action,
            workflow_step.path,
            workflow_step.project
        FROM workflow_compensation
        JOIN workflow_step ON workflow_step.id = workflow_compensation.step_id
        WHERE workflow_compensation.task_id = ?
        ORDER BY workflow_compensation.id ASC
        """,
        (task_id,),
    ).fetchall()


def compensation_on_task(
    connection: sqlite3.Connection, task_id: int, compensation_id: int
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT
            workflow_compensation.id,
            workflow_compensation.step_id,
            workflow_compensation.reason,
            workflow_compensation.state,
            workflow_step.title,
            workflow_step.action,
            workflow_step.path,
            workflow_step.project
        FROM workflow_compensation
        JOIN workflow_step ON workflow_step.id = workflow_compensation.step_id
        WHERE workflow_compensation.task_id = ? AND workflow_compensation.id = ?
        """,
        (task_id, compensation_id),
    ).fetchone()


def insert_compensation(
    connection: sqlite3.Connection,
    task_id: int,
    step_id: int,
    reason: str,
    state: str,
    recorded_at: str,
) -> bool:
    try:
        connection.execute(
            """
            INSERT INTO workflow_compensation (
                task_id, step_id, reason, state, recorded_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (task_id, step_id, reason, state, recorded_at),
        )
    except sqlite3.IntegrityError:
        return False
    return True


def settle_compensation(
    connection: sqlite3.Connection,
    compensation_id: int,
    state: str,
    evidence: str | None,
    decline_reason: str | None,
) -> None:
    connection.execute(
        """
        UPDATE workflow_compensation
        SET state = ?, evidence = ?, decline_reason = ?
        WHERE id = ?
        """,
        (state, evidence, decline_reason, compensation_id),
    )
