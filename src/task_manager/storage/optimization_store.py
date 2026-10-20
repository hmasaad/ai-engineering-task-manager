"""Activities, precedence constraints, capacity, and one optimized plan."""

import sqlite3


def activity_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, name, length, recorded_at
        FROM opt_activity
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_activities(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM opt_activity WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_activity(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    length: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO opt_activity (task_id, name, length, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, name, length, recorded_at),
    )


def activities(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT a.id, a.name, a.length, pl.start
        FROM opt_activity a
        LEFT JOIN opt_plan p ON p.task_id = a.task_id
        LEFT JOIN opt_placement pl ON pl.plan_id = p.id AND pl.activity_id = a.id
        WHERE a.task_id = ?
        ORDER BY a.id
        """,
        (task_id,),
    ).fetchall()


def constraint_pair(
    connection: sqlite3.Connection, activity_id: int, after_id: int
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM opt_constraint
        WHERE activity_id = ? AND after_id = ?
        """,
        (activity_id, after_id),
    ).fetchone()


def constraints(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT c.id, c.activity_id, c.after_id, later.name AS activity, earlier.name AS after
        FROM opt_constraint c
        JOIN opt_activity later ON later.id = c.activity_id
        JOIN opt_activity earlier ON earlier.id = c.after_id
        WHERE c.task_id = ?
        ORDER BY c.id
        """,
        (task_id,),
    ).fetchall()


def insert_constraint(
    connection: sqlite3.Connection,
    task_id: int,
    activity_id: int,
    after_id: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO opt_constraint (task_id, activity_id, after_id, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, activity_id, after_id, recorded_at),
    )


def capacity_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, capacity
        FROM opt_capacity
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()


def insert_capacity(
    connection: sqlite3.Connection, task_id: int, capacity: int, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO opt_capacity (task_id, capacity, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, capacity, recorded_at),
    )


def update_capacity(
    connection: sqlite3.Connection, task_id: int, capacity: int, recorded_at: str
) -> None:
    connection.execute(
        """
        UPDATE opt_capacity
        SET capacity = ?, recorded_at = ?
        WHERE task_id = ?
        """,
        (capacity, recorded_at, task_id),
    )


def clear_plan(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute(
        """
        DELETE FROM opt_placement
        WHERE plan_id IN (SELECT id FROM opt_plan WHERE task_id = ?)
        """,
        (task_id,),
    )
    connection.execute("DELETE FROM opt_plan WHERE task_id = ?", (task_id,))


def insert_plan(
    connection: sqlite3.Connection, task_id: int, finish: int, recorded_at: str
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO opt_plan (task_id, finish, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, finish, recorded_at),
    )
    return int(cursor.lastrowid)


def insert_placement(
    connection: sqlite3.Connection, plan_id: int, activity_id: int, start: int
) -> None:
    connection.execute(
        """
        INSERT INTO opt_placement (plan_id, activity_id, start)
        VALUES (?, ?, ?)
        """,
        (plan_id, activity_id, start),
    )


def plan_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, finish
        FROM opt_plan
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()
