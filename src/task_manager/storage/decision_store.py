"""Append-only implementation decisions."""

import sqlite3


def insert_decision(
    connection: sqlite3.Connection,
    task_id: int,
    statement: str,
    rationale: str,
    recorded_at: str,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO implementation_decision (task_id, statement, rationale, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, statement, rationale, recorded_at),
    )
    return int(cursor.lastrowid)


def decision_row(connection: sqlite3.Connection, decision_id: int) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM implementation_decision WHERE id = ?",
        (decision_id,),
    ).fetchone()


def link_supersedes(
    connection: sqlite3.Connection,
    decision_id: int,
    earlier_decision_id: int,
) -> None:
    connection.execute(
        """
        INSERT INTO decision_supersedes (decision_id, earlier_decision_id)
        VALUES (?, ?)
        """,
        (decision_id, earlier_decision_id),
    )
