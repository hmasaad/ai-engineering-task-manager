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
    f.file_text AS applied_text,
    d.folder_path AS created_folder_path,
    tr.test_path AS test_path,
    ts.result AS test_result,
    ts.output AS test_output,
    df.file_path AS deleted_file_path,
    df.previous_text AS deleted_previous_text,
    m.model_name AS model_name,
    m.model_input AS model_input,
    m.model_output AS model_output,
    m.file_read_id AS model_file_read_id
FROM implementation_change AS c
LEFT JOIN implementation_resolution AS r ON r.change_id = c.id
LEFT JOIN assistant_change AS a ON a.change_id = c.id
LEFT JOIN applied_file AS f ON f.change_id = c.id
LEFT JOIN created_folder AS d ON d.change_id = c.id
LEFT JOIN test_run AS tr ON tr.change_id = c.id
LEFT JOIN test_run_result AS ts ON ts.change_id = c.id
LEFT JOIN deleted_file AS df ON df.change_id = c.id
LEFT JOIN model_call AS m ON m.change_id = c.id
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


def insert_created_folder(connection: sqlite3.Connection, change_id: int, folder_path: str) -> None:
    connection.execute(
        """
        INSERT INTO created_folder (change_id, folder_path)
        VALUES (?, ?)
        """,
        (change_id, folder_path),
    )


def row_created_folder(connection: sqlite3.Connection, change_id: int) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT folder_path FROM created_folder WHERE change_id = ?",
        (change_id,),
    ).fetchone()


def insert_test_run(connection: sqlite3.Connection, change_id: int, test_path: str) -> None:
    connection.execute(
        """
        INSERT INTO test_run (change_id, test_path)
        VALUES (?, ?)
        """,
        (change_id, test_path),
    )


def insert_test_run_result(
    connection: sqlite3.Connection,
    change_id: int,
    result: str,
    output: str,
) -> None:
    connection.execute(
        """
        INSERT INTO test_run_result (change_id, result, output)
        VALUES (?, ?, ?)
        """,
        (change_id, result, output),
    )


def insert_deleted_file(
    connection: sqlite3.Connection,
    change_id: int,
    file_path: str,
    previous_text: str,
) -> None:
    connection.execute(
        """
        INSERT INTO deleted_file (change_id, file_path, previous_text)
        VALUES (?, ?, ?)
        """,
        (change_id, file_path, previous_text),
    )


def row_deleted_file(connection: sqlite3.Connection, change_id: int) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT file_path, previous_text FROM deleted_file WHERE change_id = ?",
        (change_id,),
    ).fetchone()


def row_test_run(connection: sqlite3.Connection, change_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT tr.test_path AS test_path, ts.result AS result
        FROM test_run AS tr
        LEFT JOIN test_run_result AS ts ON ts.change_id = tr.change_id
        WHERE tr.change_id = ?
        """,
        (change_id,),
    ).fetchone()


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
        "folder": None if row["created_folder_path"] is None else {"path": row["created_folder_path"]},
        "test": _test_payload(row),
        "deleted_file": _deleted_payload(row),
        "model": _model_payload(row),
    }


def _deleted_payload(row: sqlite3.Row) -> dict[str, object] | None:
    if row["deleted_file_path"] is None:
        return None
    return {"path": row["deleted_file_path"], "text": row["deleted_previous_text"]}


def _test_payload(row: sqlite3.Row) -> dict[str, object] | None:
    if row["test_path"] is None:
        return None
    result = row["test_result"]
    shown = None
    if result == "passed":
        shown = "Passed"
    elif result == "failed":
        shown = "Failed"
    output = row["test_output"]
    return {
        "path": row["test_path"],
        "result": shown,
        "output": "" if output is None else output,
    }


def _model_payload(row: sqlite3.Row) -> dict[str, object] | None:
    if row["model_name"] is None:
        return None
    return {
        "name": row["model_name"],
        "input": row["model_input"],
        "output": row["model_output"],
        "file_read_id": row["model_file_read_id"],
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
