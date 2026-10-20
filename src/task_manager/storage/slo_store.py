"""Objectives and the service that takes the earliest deadline."""

import sqlite3


def objective_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, name, deadline, recorded_at
        FROM slo_objective
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def insert_objective(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    deadline: str,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO slo_objective (task_id, name, deadline, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, name, deadline, recorded_at),
    )


def objectives(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name, deadline
        FROM slo_objective
        WHERE task_id = ?
        ORDER BY id ASC
        """,
        (task_id,),
    ).fetchall()


def waiting(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name, deadline
        FROM slo_objective
        WHERE task_id = ?
          AND NOT EXISTS (
              SELECT 1 FROM slo_service
              WHERE slo_service.objective_id = slo_objective.id
          )
        ORDER BY id ASC
        """,
        (task_id,),
    ).fetchall()


def service_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT id, name FROM slo_service WHERE task_id = ? AND name = ?",
        (task_id, name),
    ).fetchone()


def insert_service(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    objective_id: int,
    result: str,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO slo_service (task_id, name, objective_id, result, recorded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, name, objective_id, result, recorded_at),
    )


def services(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT slo_service.name AS name,
               slo_objective.name AS objective,
               slo_service.result AS result
        FROM slo_service
        JOIN slo_objective ON slo_objective.id = slo_service.objective_id
        WHERE slo_service.task_id = ?
        ORDER BY slo_service.id ASC
        """,
        (task_id,),
    ).fetchall()
