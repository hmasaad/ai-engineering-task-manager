"""Actions with a risk, safe probes, and one stored effect."""

import sqlite3


def action_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name, risk
        FROM safe_action
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_actions(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM safe_action WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_action(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    risk: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO safe_action (task_id, name, risk, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, name, risk, recorded_at),
    )


def actions(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name, risk
        FROM safe_action
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def probe_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM safe_probe
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_probes(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM safe_probe WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_probe(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    state: str,
    action_id: int,
    reward: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO safe_probe (task_id, name, state, action_id, reward, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, name, state, action_id, reward, recorded_at),
    )


def probes(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT p.id, p.name, p.state, p.reward, a.name AS action
        FROM safe_probe p
        JOIN safe_action a ON a.id = p.action_id
        WHERE p.task_id = ?
        ORDER BY p.id
        """,
        (task_id,),
    ).fetchall()


def clear_effect(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute("DELETE FROM safe_effect WHERE task_id = ?", (task_id,))


def insert_effect(
    connection: sqlite3.Connection,
    task_id: int,
    state: str,
    action: str,
    instead: str,
    effect: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO safe_effect (task_id, state, action, instead, effect, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, state, action, instead, effect, recorded_at),
    )


def effect_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT state, action, instead, effect
        FROM safe_effect
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()
