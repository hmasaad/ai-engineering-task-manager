"""Arms, marked contexts, pulls, and one stored model choice."""

import sqlite3


def arm_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name
        FROM model_arm
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_arms(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM model_arm WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_arm(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO model_arm (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def arms(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name
        FROM model_arm
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
        SELECT id, name, first_mark, second_mark
        FROM model_context
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_contexts(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM model_context WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_context(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    first_mark: int,
    second_mark: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO model_context (
            task_id, name, first_mark, second_mark, recorded_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, name, first_mark, second_mark, recorded_at),
    )


def contexts(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name, first_mark, second_mark
        FROM model_context
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def pull_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM model_pull
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_pulls(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM model_pull WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_pull(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    context_id: int,
    arm_id: int,
    reward: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO model_pull (
            task_id, name, context_id, arm_id, reward, recorded_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, name, context_id, arm_id, reward, recorded_at),
    )


def pulls(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT p.id, p.name, p.reward, c.name AS context, a.name AS arm
        FROM model_pull p
        JOIN model_context c ON c.id = p.context_id
        JOIN model_arm a ON a.id = p.arm_id
        WHERE p.task_id = ?
        ORDER BY p.id
        """,
        (task_id,),
    ).fetchall()


def clear_choice(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute("DELETE FROM model_choice WHERE task_id = ?", (task_id,))


def choice_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT context, model, arm
        FROM model_choice
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()


def insert_choice(
    connection: sqlite3.Connection,
    task_id: int,
    context: str,
    model: str,
    arm: str,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO model_choice (task_id, context, model, arm, recorded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, context, model, arm, recorded_at),
    )
