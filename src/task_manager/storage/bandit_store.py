"""Actions, contexts, trials, and one stored choice."""

import sqlite3


def action_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, name, recorded_at
        FROM bandit_action
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_actions(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM bandit_action WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_action(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO bandit_action (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def actions(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name
        FROM bandit_action
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def context_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, name, recorded_at
        FROM bandit_context
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_contexts(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM bandit_context WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_context(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO bandit_context (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def contexts(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name
        FROM bandit_context
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def trial_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM bandit_trial
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_trials(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM bandit_trial WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_trial(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    context_id: int,
    action_id: int,
    reward: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO bandit_trial (
            task_id, name, context_id, action_id, reward, recorded_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, name, context_id, action_id, reward, recorded_at),
    )


def trials(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT t.id, t.name, t.reward, t.context_id, t.action_id,
               c.name AS context, a.name AS action
        FROM bandit_trial t
        JOIN bandit_context c ON c.id = t.context_id
        JOIN bandit_action a ON a.id = t.action_id
        WHERE t.task_id = ?
        ORDER BY t.id
        """,
        (task_id,),
    ).fetchall()


def clear_choice(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute("DELETE FROM bandit_choice WHERE task_id = ?", (task_id,))


def insert_choice(
    connection: sqlite3.Connection,
    task_id: int,
    context_id: int,
    action_id: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO bandit_choice (task_id, context_id, action_id, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, context_id, action_id, recorded_at),
    )


def choice_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT ch.id, c.name AS context, a.name AS action
        FROM bandit_choice ch
        JOIN bandit_context c ON c.id = ch.context_id
        JOIN bandit_action a ON a.id = ch.action_id
        WHERE ch.task_id = ?
        """,
        (task_id,),
    ).fetchone()
