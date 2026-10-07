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


def checks_for(connection: sqlite3.Connection, change_id: int) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT id, criterion_id, criterion_text, evidence, result, engineer_name, checked_at
        FROM implementation_check
        WHERE change_id = ?
        ORDER BY checked_at ASC, id ASC
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
