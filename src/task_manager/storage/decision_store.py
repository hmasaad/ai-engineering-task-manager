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


def insert_decision_check(
    connection: sqlite3.Connection,
    decision_id: int,
    check_id: int,
) -> None:
    connection.execute(
        """
        INSERT INTO decision_check (decision_id, check_id)
        VALUES (?, ?)
        """,
        (decision_id, check_id),
    )


def check_id_for_decision(connection: sqlite3.Connection, decision_id: int) -> int | None:
    row = connection.execute(
        "SELECT check_id FROM decision_check WHERE decision_id = ?",
        (decision_id,),
    ).fetchone()
    if row is None:
        return None
    return int(row["check_id"])


def check_for_link(connection: sqlite3.Connection, check_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT
            implementation_check.id,
            implementation_check.change_id,
            implementation_change.what_changed,
            implementation_change.task_id,
            implementation_check.criterion_id,
            implementation_check.criterion_text,
            implementation_check.evidence,
            implementation_check.result,
            implementation_check.engineer_name,
            implementation_check.checked_at
        FROM implementation_check
        JOIN implementation_change ON implementation_change.id = implementation_check.change_id
        WHERE implementation_check.id = ?
        """,
        (check_id,),
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
