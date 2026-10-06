"""Status-change rows and verification fields."""

import sqlite3


def append_change(
    connection: sqlite3.Connection,
    task_id: int,
    from_status: str,
    to_status: str,
    occurred_at: str,
    cause_code: str,
    cause_detail: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO status_change (
            task_id, from_status, to_status, occurred_at, cause_code, cause_detail
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, from_status, to_status, occurred_at, cause_code, cause_detail),
    )


def write_verification(
    connection: sqlite3.Connection,
    criterion_id: int,
    observation: str,
    verified_at: str,
    provider_name: str,
) -> None:
    connection.execute(
        """
        UPDATE acceptance_criterion
        SET observation = ?, pass_result = 'pass', verified_at = ?, provider_name = ?
        WHERE id = ?
        """,
        (observation, verified_at, provider_name, criterion_id),
    )
