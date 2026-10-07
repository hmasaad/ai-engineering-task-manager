"""Task and acceptance-criterion rows."""

import sqlite3

from task_manager.clock import format_time
from task_manager.storage.implementation_store import changes_for
from task_manager.storage.decision_store import check_for_link, check_id_for_decision
from task_manager.storage.verification_store import checks_for, passing_check
from task_manager.domain.text import clean


def row_task(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute("SELECT * FROM task WHERE id = ?", (task_id,)).fetchone()


def insert_task(
    connection: sqlite3.Connection,
    title: str,
    created_at: str,
    parent_id: int | None,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO task (title, goal, status, parent_id, created_at, cancel_reason)
        VALUES (?, NULL, 'Draft', ?, ?, NULL)
        """,
        (title, parent_id, created_at),
    )
    return int(cursor.lastrowid)


def list_top_level(connection: sqlite3.Connection) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT id, title, status, created_at
        FROM task
        WHERE parent_id IS NULL
        ORDER BY created_at ASC, id ASC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def criteria_for(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT * FROM acceptance_criterion
        WHERE task_id = ?
        ORDER BY position ASC, id ASC
        """,
        (task_id,),
    ).fetchall()


def criterion(connection: sqlite3.Connection, task_id: int, criterion_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT * FROM acceptance_criterion
        WHERE id = ? AND task_id = ?
        """,
        (criterion_id, task_id),
    ).fetchone()


def insert_criterion(connection: sqlite3.Connection, task_id: int, text: str) -> int:
    position = connection.execute(
        "SELECT COALESCE(MAX(position), 0) + 1 AS next_pos FROM acceptance_criterion WHERE task_id = ?",
        (task_id,),
    ).fetchone()["next_pos"]
    cursor = connection.execute(
        """
        INSERT INTO acceptance_criterion (
            task_id, text, position, observation, pass_result, verified_at, provider_name
        ) VALUES (?, ?, ?, NULL, NULL, NULL, NULL)
        """,
        (task_id, text, position),
    )
    return int(cursor.lastrowid)


def update_criterion_text(connection: sqlite3.Connection, criterion_id: int, text: str) -> None:
    connection.execute(
        "UPDATE acceptance_criterion SET text = ? WHERE id = ?",
        (text, criterion_id),
    )


def clear_verification(connection: sqlite3.Connection, criterion_id: int) -> None:
    connection.execute(
        """
        UPDATE acceptance_criterion
        SET observation = NULL, pass_result = NULL, verified_at = NULL, provider_name = NULL
        WHERE id = ?
        """,
        (criterion_id,),
    )


def delete_criterion(connection: sqlite3.Connection, criterion_id: int) -> None:
    connection.execute("DELETE FROM acceptance_criterion WHERE id = ?", (criterion_id,))


def set_goal(connection: sqlite3.Connection, task_id: int, goal: str | None) -> None:
    connection.execute("UPDATE task SET goal = ? WHERE id = ?", (goal, task_id))


def set_status(
    connection: sqlite3.Connection,
    task_id: int,
    status: str,
    cancel_reason: str | None,
) -> None:
    connection.execute(
        "UPDATE task SET status = ?, cancel_reason = ? WHERE id = ?",
        (status, cancel_reason, task_id),
    )


def children(connection: sqlite3.Connection, parent_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, title, status, created_at
        FROM task
        WHERE parent_id = ?
        ORDER BY created_at ASC, id ASC
        """,
        (parent_id,),
    ).fetchall()


def set_parent(connection: sqlite3.Connection, child_id: int, parent_id: int) -> None:
    connection.execute("UPDATE task SET parent_id = ? WHERE id = ?", (parent_id, child_id))


def is_verified(row: sqlite3.Row) -> bool:
    return row["pass_result"] == "pass" and bool(clean(row["observation"])) and row["verified_at"] and row["provider_name"]


def criterion_payload(row: sqlite3.Row) -> dict[str, object]:
    verified = is_verified(row)
    return {
        "id": row["id"],
        "text": row["text"],
        "state": "Verified" if verified else "Unverified",
        "observation": row["observation"] if verified else None,
        "pass_result": row["pass_result"] if verified else None,
        "verified_at": row["verified_at"] if verified else None,
        "provider_name": row["provider_name"] if verified else None,
    }


def history(connection: sqlite3.Connection, task_id: int) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT id, from_status, to_status, occurred_at, cause_code, cause_detail
        FROM status_change
        WHERE task_id = ?
        ORDER BY occurred_at ASC, id ASC
        """,
        (task_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def decisions(connection: sqlite3.Connection, task_id: int) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT id, statement, rationale, recorded_at
        FROM implementation_decision
        WHERE task_id = ?
        ORDER BY recorded_at ASC, id ASC
        """,
        (task_id,),
    ).fetchall()
    payloads = []
    for row in rows:
        links = connection.execute(
            """
            SELECT earlier_decision_id
            FROM decision_supersedes
            WHERE decision_id = ?
            ORDER BY earlier_decision_id ASC
            """,
            (row["id"],),
        ).fetchall()
        payloads.append(
            {
                "id": row["id"],
                "statement": row["statement"],
                "rationale": row["rationale"],
                "recorded_at": row["recorded_at"],
                "supersedes": [link["earlier_decision_id"] for link in links],
                "check": _decision_check(connection, int(row["id"])),
            }
        )
    return payloads


def _decision_check(connection: sqlite3.Connection, decision_id: int) -> dict[str, object] | None:
    check_id = check_id_for_decision(connection, decision_id)
    if check_id is None:
        return None
    row = check_for_link(connection, check_id)
    if row is None:
        return None
    return {
        "id": row["id"],
        "change_id": row["change_id"],
        "what_changed": row["what_changed"],
        "criterion_id": row["criterion_id"],
        "criterion_text": row["criterion_text"],
        "evidence": row["evidence"],
        "result": "Passed" if row["result"] == "passed" else "Failed",
        "engineer_name": row["engineer_name"],
        "checked_at": row["checked_at"],
    }


def task_detail(connection: sqlite3.Connection, task_id: int) -> dict[str, object] | None:
    task = row_task(connection, task_id)
    if task is None:
        return None
    return {
        "id": task["id"],
        "title": task["title"],
        "goal": task["goal"],
        "status": task["status"],
        "parent_id": task["parent_id"],
        "created_at": task["created_at"],
        "cancel_reason": task["cancel_reason"],
        "criteria": [criterion_payload(row) for row in criteria_for(connection, task_id)],
        "subtasks": [dict(row) for row in children(connection, task_id)],
        "decisions": decisions(connection, task_id),
        "history": history(connection, task_id),
        "implementation_changes": _with_checks(connection, task_id),
    }


def _with_checks(connection: sqlite3.Connection, task_id: int) -> list[dict[str, object]]:
    live = {int(row["id"]) for row in criteria_for(connection, task_id)}
    changes = changes_for(connection, task_id)
    for change in changes:
        checks = checks_for(connection, int(change["id"]))
        change["checks"] = checks
        change["passing_check"] = passing_check(str(change["outcome"]), checks, live)
    return changes


def stamp(moment) -> str:
    return format_time(moment)
