"""Schedule steps, the one step each follows, and one deadline."""

import sqlite3


def step_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, name, length, recorded_at
        FROM path_step
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def insert_step(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    length: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO path_step (task_id, name, length, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, name, length, recorded_at),
    )


def steps(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT s.id, s.name, s.length, l.predecessor_id, p.name AS follows
        FROM path_step s
        LEFT JOIN path_link l ON l.step_id = s.id
        LEFT JOIN path_step p ON p.id = l.predecessor_id
        WHERE s.task_id = ?
        ORDER BY s.id
        """,
        (task_id,),
    ).fetchall()


def link_for_step(connection: sqlite3.Connection, step_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, step_id, predecessor_id
        FROM path_link
        WHERE step_id = ?
        """,
        (step_id,),
    ).fetchone()


def insert_link(
    connection: sqlite3.Connection,
    task_id: int,
    step_id: int,
    predecessor_id: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO path_link (task_id, step_id, predecessor_id, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, step_id, predecessor_id, recorded_at),
    )


def deadline_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, deadline
        FROM path_deadline
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()


def insert_deadline(
    connection: sqlite3.Connection, task_id: int, deadline: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO path_deadline (task_id, deadline, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, deadline, recorded_at),
    )


def update_deadline(
    connection: sqlite3.Connection, task_id: int, deadline: str, recorded_at: str
) -> None:
    connection.execute(
        """
        UPDATE path_deadline
        SET deadline = ?, recorded_at = ?
        WHERE task_id = ?
        """,
        (deadline, recorded_at, task_id),
    )
