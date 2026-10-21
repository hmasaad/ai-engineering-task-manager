"""Task and acceptance-criterion rows."""

import sqlite3

from task_manager.clock import format_time
from task_manager.storage import execution_store, file_read_store, requirement_store
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
        SELECT acceptance_criterion.*,
               criterion_evidence.method AS method,
               criterion_evidence.run_identifier AS run_identifier
        FROM acceptance_criterion
        LEFT JOIN criterion_evidence
          ON criterion_evidence.criterion_id = acceptance_criterion.id
        WHERE acceptance_criterion.task_id = ?
        ORDER BY acceptance_criterion.position ASC, acceptance_criterion.id ASC
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
    connection.execute(
        "DELETE FROM criterion_evidence WHERE criterion_id = ?",
        (criterion_id,),
    )


def write_criterion_evidence(
    connection: sqlite3.Connection,
    criterion_id: int,
    method: str,
    run_identifier: str,
) -> None:
    connection.execute(
        """
        INSERT INTO criterion_evidence (criterion_id, method, run_identifier)
        VALUES (?, ?, ?)
        ON CONFLICT(criterion_id) DO UPDATE SET
            method = excluded.method,
            run_identifier = excluded.run_identifier
        """,
        (criterion_id, method, run_identifier),
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
        "method": row["method"] if verified else None,
        "run_identifier": row["run_identifier"] if verified else None,
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
        "assistant_name": row["assistant_name"],
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
        "file_reads": file_read_store.file_reads_for(connection, task_id),
        "executions": _executions(connection, task_id),
        "requirements": requirement_store.summaries_for_task(connection, task_id),
        "prerequisites": _prerequisites(connection, task_id),
        "blocked_by": _blocked_by(connection, task_id),
        "workflow": _workflow(connection, task_id),
        "work": _work(connection, task_id),
        "schedule": _schedule(connection, task_id),
        "priority": _priority(connection, task_id),
        "slo": _slo(connection, task_id),
        "paths": _paths(connection, task_id),
        "optimization": _optimization(connection, task_id),
        "learning": _learning(connection, task_id),
        "bandit": _bandit(connection, task_id),
        "evaluation": _evaluation(connection, task_id),
        "safety": _safety(connection, task_id),
        "exploration": _exploration(connection, task_id),
        "models": _models(connection, task_id),
        "search": _search(connection, task_id),
        "fidelity": _fidelity(connection, task_id),
        "allocation": _allocation(connection, task_id),
        "hyperband": _hyperband(connection, task_id),
    }


def _executions(connection: sqlite3.Connection, task_id: int) -> list[dict[str, object]]:
    return execution_store.executions_for(connection, task_id)


def _prerequisites(connection: sqlite3.Connection, task_id: int) -> list[dict[str, object]]:
    from task_manager.storage import dependency_store

    return [
        {"id": int(row["id"]), "title": row["title"], "status": row["status"]}
        for row in dependency_store.prerequisites(connection, task_id)
    ]


def _blocked_by(connection: sqlite3.Connection, task_id: int) -> str | None:
    from task_manager.domain.dependency import blocked_sentence

    return blocked_sentence(connection, task_id)


def _workflow(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.workflow import payload

    return payload(connection, task_id)


def _work(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.workers import payload

    return payload(connection, task_id)


def _schedule(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.schedule import payload

    return payload(connection, task_id)


def _priority(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.priority import payload

    return payload(connection, task_id)


def _slo(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.slo import payload

    return payload(connection, task_id)


def _paths(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.paths import payload

    return payload(connection, task_id)


def _optimization(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.optimization import payload

    return payload(connection, task_id)


def _learning(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.learning import payload

    return payload(connection, task_id)


def _bandit(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.bandit import payload

    return payload(connection, task_id)


def _evaluation(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.evaluation import payload

    return payload(connection, task_id)


def _safety(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.safety import payload

    return payload(connection, task_id)


def _exploration(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.exploration import payload

    return payload(connection, task_id)


def _models(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.linear_bandit import payload

    return payload(connection, task_id)


def _search(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.bayes import payload

    return payload(connection, task_id)


def _fidelity(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.fidelity import payload

    return payload(connection, task_id)


def _allocation(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.allocation import payload

    return payload(connection, task_id)


def _hyperband(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    from task_manager.domain.asha import payload

    return payload(connection, task_id)


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
