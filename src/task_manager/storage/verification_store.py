"""Insert-only checks of a carried-out implementation change."""

import sqlite3


def insert_check(
    connection: sqlite3.Connection,
    change_id: int,
    criterion_id: int,
    criterion_text: str,
    evidence: str,
    result: str,
    engineer_name: str,
    checked_at: str,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO implementation_check (
            change_id, criterion_id, criterion_text, evidence, result, engineer_name, checked_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (change_id, criterion_id, criterion_text, evidence, result, engineer_name, checked_at),
    )
    return int(cursor.lastrowid)


def insert_assistant_check(
    connection: sqlite3.Connection,
    check_id: int,
    assistant_name: str,
) -> None:
    connection.execute(
        """
        INSERT INTO assistant_check (check_id, assistant_name)
        VALUES (?, ?)
        """,
        (check_id, assistant_name),
    )


def checks_for(connection: sqlite3.Connection, change_id: int) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT
            implementation_check.id,
            implementation_check.criterion_id,
            implementation_check.criterion_text,
            implementation_check.evidence,
            implementation_check.result,
            implementation_check.engineer_name,
            implementation_check.checked_at,
            assistant_check.assistant_name
        FROM implementation_check
        LEFT JOIN assistant_check ON assistant_check.check_id = implementation_check.id
        WHERE implementation_check.change_id = ?
        ORDER BY implementation_check.checked_at ASC, implementation_check.id ASC
        """,
        (change_id,),
    ).fetchall()
    return [check_payload(row) for row in rows]


def check_payload(row: sqlite3.Row) -> dict[str, object]:
    return {
        "id": row["id"],
        "criterion_id": row["criterion_id"],
        "criterion_text": row["criterion_text"],
        "evidence": row["evidence"],
        "result": "Passed" if row["result"] == "passed" else "Failed",
        "engineer_name": row["engineer_name"],
        "assistant_name": row["assistant_name"],
        "checked_at": row["checked_at"],
    }


def passing_check(outcome: str, checks: list[dict[str, object]], live_ids: set[int]) -> bool:
    if outcome != "Carried out":
        return False
    current: dict[int, str] = {}
    for check in checks:
        criterion_id = int(check["criterion_id"])
        if criterion_id in live_ids:
            current[criterion_id] = str(check["result"])
    if not current:
        return False
    return all(result == "Passed" for result in current.values())
