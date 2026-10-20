"""Logged steps, policy rules, and one stored score."""

import sqlite3


def log_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM eval_log
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_logs(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM eval_log WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def state_in_log(connection: sqlite3.Connection, task_id: int, state: str) -> bool:
    row = connection.execute(
        """
        SELECT id
        FROM eval_log
        WHERE task_id = ? AND state = ?
        """,
        (task_id, state),
    ).fetchone()
    return row is not None


def insert_log(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    state: str,
    action: str,
    reward: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO eval_log (task_id, name, state, action, reward, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, name, state, action, reward, recorded_at),
    )


def logs(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name, state, action, reward
        FROM eval_log
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def rule_for_state(
    connection: sqlite3.Connection, task_id: int, state: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, action
        FROM eval_rule
        WHERE task_id = ? AND state = ?
        """,
        (task_id, state),
    ).fetchone()


def count_rules(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM eval_rule WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_rule(
    connection: sqlite3.Connection,
    task_id: int,
    state: str,
    action: str,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO eval_rule (task_id, state, action, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, state, action, recorded_at),
    )


def update_rule(
    connection: sqlite3.Connection,
    task_id: int,
    state: str,
    action: str,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        UPDATE eval_rule
        SET action = ?, recorded_at = ?
        WHERE task_id = ? AND state = ?
        """,
        (action, recorded_at, task_id, state),
    )


def rules(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, state, action
        FROM eval_rule
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def clear_score(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute("DELETE FROM eval_score WHERE task_id = ?", (task_id,))


def insert_score(
    connection: sqlite3.Connection,
    task_id: int,
    total: int,
    count: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO eval_score (task_id, total, count, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, total, count, recorded_at),
    )


def score_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, total, count
        FROM eval_score
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()
