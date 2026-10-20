"""Ranked work and the serve that takes the highest score."""

import sqlite3


def work_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, name, rank, age, recorded_at
        FROM priority_work
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def insert_work(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    rank: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO priority_work (task_id, name, rank, age, recorded_at)
        VALUES (?, ?, ?, 0, ?)
        """,
        (task_id, name, rank, recorded_at),
    )


def waiting(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name, rank, age
        FROM priority_work
        WHERE task_id = ?
          AND NOT EXISTS (
              SELECT 1 FROM priority_serve
              WHERE priority_serve.work_id = priority_work.id
          )
        ORDER BY id ASC
        """,
        (task_id,),
    ).fetchall()


def serve_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT id, name FROM priority_serve WHERE task_id = ? AND name = ?",
        (task_id, name),
    ).fetchone()


def insert_serve(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    work_id: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO priority_serve (task_id, name, work_id, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, name, work_id, recorded_at),
    )
    connection.execute(
        """
        UPDATE priority_work
        SET age = age + 1
        WHERE task_id = ?
          AND NOT EXISTS (
              SELECT 1 FROM priority_serve
              WHERE priority_serve.work_id = priority_work.id
          )
        """,
        (task_id,),
    )


def serves(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT priority_serve.name AS name, priority_work.name AS work
        FROM priority_serve
        JOIN priority_work ON priority_work.id = priority_serve.work_id
        WHERE priority_serve.task_id = ?
        ORDER BY priority_serve.id ASC
        """,
        (task_id,),
    ).fetchall()
