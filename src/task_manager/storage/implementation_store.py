"""Insert-only implementation changes and their one resolution."""

import sqlite3


_CHANGE_SQL = """
SELECT
    c.id,
    c.task_id,
    c.what_changed,
    c.class,
    c.engineer_name,
    c.recorded_at,
    r.kind,
    r.evidence,
    r.reason,
    r.engineer_name AS resolution_engineer,
    r.resolved_at,
    a.project AS assistant_project,
    a.assistant_name AS assistant_actor,
    a.stopped AS assistant_stopped,
    f.file_path AS applied_path,
    f.was_new AS applied_was_new,
    f.previous_text AS applied_previous,
    f.file_text AS applied_text
FROM implementation_change AS c
LEFT JOIN implementation_resolution AS r ON r.change_id = c.id
LEFT JOIN assistant_change AS a ON a.change_id = c.id
LEFT JOIN applied_file AS f ON f.change_id = c.id
"""


def insert_change(
    connection: sqlite3.Connection,
    task_id: int,
    what_changed: str,
    change_class: str,
    engineer_name: str,
    recorded_at: str,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO implementation_change (
            task_id, what_changed, class, engineer_name, recorded_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, what_changed, change_class, engineer_name, recorded_at),
    )
    return int(cursor.lastrowid)


def insert_resolution(
    connection: sqlite3.Connection,
    change_id: int,
    kind: str,
    evidence: str | None,
    reason: str | None,
    engineer_name: str,
    resolved_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO implementation_resolution (
            change_id, kind, evidence, reason, engineer_name, resolved_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (change_id, kind, evidence, reason, engineer_name, resolved_at),
    )


def insert_assistant_change(
    connection: sqlite3.Connection,
    change_id: int,
    project: str,
    assistant_name: str,
    stopped: int,
) -> None:
    connection.execute(
        """
        INSERT INTO assistant_change (change_id, project, assistant_name, stopped)
        VALUES (?, ?, ?, ?)
        """,
        (change_id, project, assistant_name, stopped),
    )


def insert_applied_file(
    connection: sqlite3.Connection,
    change_id: int,
    file_path: str,
    was_new: int,
    previous_text: str | None,
    file_text: str,
) -> None:
    connection.execute(
        """
        INSERT INTO applied_file (
            change_id, file_path, was_new, previous_text, file_text
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (change_id, file_path, was_new, previous_text, file_text),
    )


def row_applied_file(connection: sqlite3.Connection, change_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT file_path, was_new, previous_text, file_text
        FROM applied_file
        WHERE change_id = ?
        """,
        (change_id,),
    ).fetchone()


def row_change(connection: sqlite3.Connection, change_id: int) -> sqlite3.Row | None:
    return connection.execute(
        _CHANGE_SQL + " WHERE c.id = ?",
        (change_id,),
    ).fetchone()


def changes_for(connection: sqlite3.Connection, task_id: int) -> list[dict[str, object]]:
    rows = connection.execute(
        _CHANGE_SQL + " WHERE c.task_id = ? ORDER BY c.recorded_at ASC, c.id ASC",
        (task_id,),
    ).fetchall()
    return [change_payload(row) for row in rows]


def change_payload(row: sqlite3.Row) -> dict[str, object]:
    kind = row["kind"]
    change_class = row["class"]
    approval = None
    not_carried_out = None
    if change_class == "ordinary":
        outcome = "Carried out"
    elif kind == "approved":
        outcome = "Carried out"
        approval = {
            "evidence": row["evidence"],
            "engineer_name": row["resolution_engineer"],
            "approved_at": row["resolved_at"],
        }
    elif kind == "not_carried_out":
        outcome = "Not carried out"
        not_carried_out = {
            "reason": row["reason"],
            "engineer_name": row["resolution_engineer"],
            "declined_at": row["resolved_at"],
        }
    else:
        outcome = "Awaiting approval"
    return {
        "id": row["id"],
        "what_changed": row["what_changed"],
        "class": change_class,
        "outcome": outcome,
        "engineer_name": row["engineer_name"],
        "recorded_at": row["recorded_at"],
        "approval": approval,
        "not_carried_out": not_carried_out,
        "project": row["assistant_project"],
        "assistant_name": row["assistant_actor"],
        "recorded_by": "assistant" if row["assistant_actor"] is not None else "engineer",
        "stopped": row["assistant_stopped"] == 1,
        "file": _file_payload(row),
    }


def _file_payload(row: sqlite3.Row) -> dict[str, object] | None:
    if row["applied_path"] is None:
        return None
    was_new = row["applied_was_new"] == 1
    return {
        "path": row["applied_path"],
        "was_new": was_new,
        "previous_text": None if was_new else row["applied_previous"],
        "text": row["applied_text"],
    }
