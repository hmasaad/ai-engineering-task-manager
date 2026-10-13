"""Requirement, link, named-check, and verification-run rows."""

import sqlite3

_KINDS = {"functional", "non-functional"}
_RESULTS = {"passed": "Passed", "failed": "Failed"}


def identifier(requirement_id: int) -> str:
    return f"REQ-{requirement_id}"


def row_requirement(connection: sqlite3.Connection, requirement_id: int) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM requirement WHERE id = ?",
        (requirement_id,),
    ).fetchone()


def insert_requirement(
    connection: sqlite3.Connection,
    kind: str,
    statement: str,
    created_at: str,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO requirement (kind, statement, created_at)
        VALUES (?, ?, ?)
        """,
        (kind, statement, created_at),
    )
    return int(cursor.lastrowid)


def update_requirement(
    connection: sqlite3.Connection,
    requirement_id: int,
    kind: str,
    statement: str,
) -> None:
    connection.execute(
        "UPDATE requirement SET kind = ?, statement = ? WHERE id = ?",
        (kind, statement, requirement_id),
    )


def task_linked(connection: sqlite3.Connection, requirement_id: int, task_id: int) -> bool:
    row = connection.execute(
        """
        SELECT 1 FROM requirement_task
        WHERE requirement_id = ? AND task_id = ?
        """,
        (requirement_id, task_id),
    ).fetchone()
    return row is not None


def link_task(connection: sqlite3.Connection, requirement_id: int, task_id: int) -> None:
    connection.execute(
        "INSERT INTO requirement_task (requirement_id, task_id) VALUES (?, ?)",
        (requirement_id, task_id),
    )


def unlink_task(connection: sqlite3.Connection, requirement_id: int, task_id: int) -> bool:
    cursor = connection.execute(
        "DELETE FROM requirement_task WHERE requirement_id = ? AND task_id = ?",
        (requirement_id, task_id),
    )
    return cursor.rowcount > 0


def criterion_linked(connection: sqlite3.Connection, requirement_id: int, criterion_id: int) -> bool:
    row = connection.execute(
        """
        SELECT 1 FROM requirement_criterion
        WHERE requirement_id = ? AND criterion_id = ?
        """,
        (requirement_id, criterion_id),
    ).fetchone()
    return row is not None


def link_criterion(connection: sqlite3.Connection, requirement_id: int, criterion_id: int) -> None:
    connection.execute(
        "INSERT INTO requirement_criterion (requirement_id, criterion_id) VALUES (?, ?)",
        (requirement_id, criterion_id),
    )


def unlink_criterion(connection: sqlite3.Connection, requirement_id: int, criterion_id: int) -> bool:
    cursor = connection.execute(
        """
        DELETE FROM requirement_criterion
        WHERE requirement_id = ? AND criterion_id = ?
        """,
        (requirement_id, criterion_id),
    )
    return cursor.rowcount > 0


def requirement_ids_for_criterion(connection: sqlite3.Connection, criterion_id: int) -> list[int]:
    rows = connection.execute(
        """
        SELECT requirement_id FROM requirement_criterion
        WHERE criterion_id = ?
        ORDER BY requirement_id ASC
        """,
        (criterion_id,),
    ).fetchall()
    return [int(row["requirement_id"]) for row in rows]


def requirements_for_task(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT requirement.*
        FROM requirement
        JOIN requirement_task ON requirement_task.requirement_id = requirement.id
        WHERE requirement_task.task_id = ?
        ORDER BY requirement.id ASC
        """,
        (task_id,),
    ).fetchall()


def summaries_for_task(connection: sqlite3.Connection, task_id: int) -> list[dict[str, object]]:
    return [_summary(row) for row in requirements_for_task(connection, task_id)]


def all_requirements(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return connection.execute("SELECT * FROM requirement ORDER BY id ASC").fetchall()


def trace_payloads(connection: sqlite3.Connection) -> dict[str, object]:
    tasks = connection.execute(
        """
        SELECT task.id, task.title, task.status
        FROM task
        WHERE NOT EXISTS (
            SELECT 1 FROM requirement_task WHERE requirement_task.task_id = task.id
        )
        ORDER BY task.id ASC
        """
    ).fetchall()
    criteria = connection.execute(
        """
        SELECT acceptance_criterion.id,
               acceptance_criterion.task_id,
               acceptance_criterion.text,
               task.title AS task_title
        FROM acceptance_criterion
        JOIN task ON task.id = acceptance_criterion.task_id
        WHERE NOT (
            acceptance_criterion.pass_result = 'pass'
            AND acceptance_criterion.observation IS NOT NULL
            AND length(trim(acceptance_criterion.observation)) > 0
            AND acceptance_criterion.verified_at IS NOT NULL
            AND acceptance_criterion.provider_name IS NOT NULL
            AND length(trim(acceptance_criterion.provider_name)) > 0
        )
        ORDER BY acceptance_criterion.id ASC
        """
    ).fetchall()
    return {
        "tasks_without_requirement": [
            {"id": int(row["id"]), "title": row["title"], "status": row["status"]}
            for row in tasks
        ],
        "criteria_without_verification": [
            {
                "id": int(row["id"]),
                "task_id": int(row["task_id"]),
                "task_title": row["task_title"],
                "text": row["text"],
            }
            for row in criteria
        ],
    }


def list_payloads(connection: sqlite3.Connection) -> list[dict[str, object]]:
    payloads = []
    for row in all_requirements(connection):
        item = _summary(row)
        item["missing"] = missing_phrases(connection, int(row["id"]))
        payloads.append(item)
    return payloads


def active_check_by_name(
    connection: sqlite3.Connection,
    requirement_id: int,
    name: str,
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT * FROM requirement_check
        WHERE requirement_id = ? AND name = ? AND removed_at IS NULL
        """,
        (requirement_id, name),
    ).fetchone()


def row_check(connection: sqlite3.Connection, check_id: int) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM requirement_check WHERE id = ?",
        (check_id,),
    ).fetchone()


def active_checks(connection: sqlite3.Connection, requirement_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT * FROM requirement_check
        WHERE requirement_id = ? AND removed_at IS NULL
        ORDER BY id ASC
        """,
        (requirement_id,),
    ).fetchall()


def removed_checks(connection: sqlite3.Connection, requirement_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT * FROM requirement_check
        WHERE requirement_id = ? AND removed_at IS NOT NULL
        ORDER BY id ASC
        """,
        (requirement_id,),
    ).fetchall()


def insert_check(connection: sqlite3.Connection, requirement_id: int, name: str) -> int:
    cursor = connection.execute(
        """
        INSERT INTO requirement_check (requirement_id, name, removed_at)
        VALUES (?, ?, NULL)
        """,
        (requirement_id, name),
    )
    return int(cursor.lastrowid)


def retire_check(connection: sqlite3.Connection, check_id: int, removed_at: str) -> None:
    connection.execute(
        "UPDATE requirement_check SET removed_at = ? WHERE id = ?",
        (removed_at, check_id),
    )


def insert_run(
    connection: sqlite3.Connection,
    check_id: int,
    result: str,
    run_identifier: str,
    engineer: str,
    recorded_at: str,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO verification_run (
            check_id, result, run_identifier, engineer_name, recorded_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (check_id, result, run_identifier, engineer, recorded_at),
    )
    return int(cursor.lastrowid)


def current_result(connection: sqlite3.Connection, check_id: int) -> str | None:
    row = connection.execute(
        """
        SELECT result FROM verification_run
        WHERE check_id = ?
        ORDER BY recorded_at DESC, id DESC
        LIMIT 1
        """,
        (check_id,),
    ).fetchone()
    if row is None:
        return None
    return str(row["result"])


def runs_for(connection: sqlite3.Connection, check_id: int) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT * FROM verification_run
        WHERE check_id = ?
        ORDER BY recorded_at ASC, id ASC
        """,
        (check_id,),
    ).fetchall()
    return [_run_payload(row) for row in rows]


def missing_phrases(connection: sqlite3.Connection, requirement_id: int) -> list[str]:
    phrases: list[str] = []
    if not _linked_tasks(connection, requirement_id):
        phrases.append("Missing a task")
    if not _linked_criteria(connection, requirement_id):
        phrases.append("Missing an acceptance criterion")
    checks = active_checks(connection, requirement_id)
    if not checks:
        phrases.append("Missing a check")
    for check in checks:
        if current_result(connection, int(check["id"])) != "passed":
            phrases.append(f"Missing a passing result for {check['name']}")
    return phrases


def detail(connection: sqlite3.Connection, requirement_id: int) -> dict[str, object] | None:
    row = row_requirement(connection, requirement_id)
    if row is None:
        return None
    payload = _summary(row)
    payload["tasks"] = _task_payloads(connection, requirement_id)
    payload["criteria"] = _criterion_payloads(connection, requirement_id)
    payload["checks"] = [_check_payload(connection, check) for check in active_checks(connection, requirement_id)]
    payload["removed_checks"] = [
        _check_payload(connection, check) for check in removed_checks(connection, requirement_id)
    ]
    return payload


def _summary(row: sqlite3.Row) -> dict[str, object]:
    requirement_id = int(row["id"])
    return {
        "id": requirement_id,
        "identifier": identifier(requirement_id),
        "kind": row["kind"],
        "statement": row["statement"],
    }


def _linked_tasks(connection: sqlite3.Connection, requirement_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT task.id, task.title, task.status
        FROM requirement_task
        JOIN task ON task.id = requirement_task.task_id
        WHERE requirement_task.requirement_id = ?
        ORDER BY task.id ASC
        """,
        (requirement_id,),
    ).fetchall()


def _task_payloads(connection: sqlite3.Connection, requirement_id: int) -> list[dict[str, object]]:
    return [
        {"id": row["id"], "title": row["title"], "status": row["status"]}
        for row in _linked_tasks(connection, requirement_id)
    ]


def _linked_criteria(connection: sqlite3.Connection, requirement_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT acceptance_criterion.*
        FROM requirement_criterion
        JOIN acceptance_criterion
          ON acceptance_criterion.id = requirement_criterion.criterion_id
        WHERE requirement_criterion.requirement_id = ?
        ORDER BY acceptance_criterion.id ASC
        """,
        (requirement_id,),
    ).fetchall()


def _criterion_payloads(connection: sqlite3.Connection, requirement_id: int) -> list[dict[str, object]]:
    payloads = []
    for row in _linked_criteria(connection, requirement_id):
        verified = (
            row["pass_result"] == "pass"
            and row["observation"] is not None
            and str(row["observation"]).strip() != ""
            and row["verified_at"] is not None
            and row["provider_name"] is not None
            and str(row["provider_name"]).strip() != ""
        )
        payloads.append(
            {
                "id": row["id"],
                "task_id": row["task_id"],
                "text": row["text"],
                "state": "Verified" if verified else "Unverified",
            }
        )
    return payloads


def _check_payload(connection: sqlite3.Connection, check: sqlite3.Row) -> dict[str, object]:
    stored = current_result(connection, int(check["id"]))
    return {
        "id": check["id"],
        "name": check["name"],
        "current_result": _RESULTS.get(stored) if stored else None,
        "runs": runs_for(connection, int(check["id"])),
    }


def _run_payload(row: sqlite3.Row) -> dict[str, object]:
    return {
        "id": row["id"],
        "result": _RESULTS[str(row["result"])],
        "run_identifier": row["run_identifier"],
        "engineer_name": row["engineer_name"],
        "recorded_at": row["recorded_at"],
    }


def kind_allowed(kind: str | None) -> bool:
    return kind in _KINDS
