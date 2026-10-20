"""Outcomes, forecasts, and one predicted schedule."""

import sqlite3


def outcome_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, name, kind, length, recorded_at
        FROM learn_outcome
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_outcomes(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM learn_outcome WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_outcome(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    kind: str,
    length: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO learn_outcome (task_id, name, kind, length, recorded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, name, kind, length, recorded_at),
    )


def outcomes(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name, kind, length
        FROM learn_outcome
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def kind_exists(connection: sqlite3.Connection, task_id: int, kind: str) -> bool:
    row = connection.execute(
        """
        SELECT id
        FROM learn_outcome
        WHERE task_id = ? AND kind = ?
        """,
        (task_id, kind),
    ).fetchone()
    return row is not None


def forecast_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, name, kind, recorded_at
        FROM learn_forecast
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_forecasts(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM learn_forecast WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_forecast(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    kind: str,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO learn_forecast (task_id, name, kind, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, name, kind, recorded_at),
    )


def forecasts(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT f.id, f.name, f.kind, pl.predicted, pl.start
        FROM learn_forecast f
        LEFT JOIN learn_plan p ON p.task_id = f.task_id
        LEFT JOIN learn_placement pl ON pl.plan_id = p.id AND pl.forecast_id = f.id
        WHERE f.task_id = ?
        ORDER BY f.id
        """,
        (task_id,),
    ).fetchall()


def clear_plan(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute(
        """
        DELETE FROM learn_placement
        WHERE plan_id IN (SELECT id FROM learn_plan WHERE task_id = ?)
        """,
        (task_id,),
    )
    connection.execute("DELETE FROM learn_plan WHERE task_id = ?", (task_id,))


def insert_plan(
    connection: sqlite3.Connection, task_id: int, finish: int, recorded_at: str
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO learn_plan (task_id, finish, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, finish, recorded_at),
    )
    return int(cursor.lastrowid)


def insert_placement(
    connection: sqlite3.Connection,
    plan_id: int,
    forecast_id: int,
    predicted: int,
    start: int,
) -> None:
    connection.execute(
        """
        INSERT INTO learn_placement (plan_id, forecast_id, predicted, start)
        VALUES (?, ?, ?, ?)
        """,
        (plan_id, forecast_id, predicted, start),
    )


def plan_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, finish
        FROM learn_plan
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()
