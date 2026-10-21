"""Arms, contexts, pulls, and one stored draw."""

import sqlite3


def arm_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name
        FROM explore_arm
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_arms(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM explore_arm WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_arm(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO explore_arm (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def arms(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name
        FROM explore_arm
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
        SELECT id, name
        FROM explore_context
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_contexts(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM explore_context WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_context(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO explore_context (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def contexts(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name
        FROM explore_context
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
        FROM explore_pull
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_pulls(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM explore_pull WHERE task_id = ?",
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
        INSERT INTO explore_pull (
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
        FROM explore_pull p
        JOIN explore_context c ON c.id = p.context_id
        JOIN explore_arm a ON a.id = p.arm_id
        WHERE p.task_id = ?
        ORDER BY p.id
        """,
        (task_id,),
    ).fetchall()


def clear_draw(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute("DELETE FROM explore_draw WHERE task_id = ?", (task_id,))


def draw_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT context, arm, sample, step
        FROM explore_draw
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()


def insert_draw(
    connection: sqlite3.Connection,
    task_id: int,
    context: str,
    arm: str,
    sample: str,
    step: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO explore_draw (task_id, context, arm, sample, step, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, context, arm, sample, step, recorded_at),
    )
