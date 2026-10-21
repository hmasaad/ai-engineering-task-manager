"""Candidates, measurements, and one stored halving."""

import sqlite3


def candidate_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name
        FROM fidelity_candidate
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_candidates(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM fidelity_candidate WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_candidate(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO fidelity_candidate (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def candidates(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name
        FROM fidelity_candidate
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def measurement_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM fidelity_measurement
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def measurement_for_candidate(
    connection: sqlite3.Connection, task_id: int, candidate_id: int, fidelity: int
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM fidelity_measurement
        WHERE task_id = ? AND candidate_id = ? AND fidelity = ?
        """,
        (task_id, candidate_id, fidelity),
    ).fetchone()


def count_measurements(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM fidelity_measurement WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_measurement(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    candidate_id: int,
    fidelity: int,
    score: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO fidelity_measurement (
            task_id, name, candidate_id, fidelity, score, recorded_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, name, candidate_id, fidelity, score, recorded_at),
    )


def measurements(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT
            o.id,
            o.name,
            o.candidate_id,
            o.fidelity,
            o.score,
            c.name AS candidate
        FROM fidelity_measurement o
        JOIN fidelity_candidate c ON c.id = o.candidate_id
        WHERE o.task_id = ?
        ORDER BY o.id
        """,
        (task_id,),
    ).fetchall()


def clear_round(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute("DELETE FROM fidelity_kept WHERE task_id = ?", (task_id,))
    connection.execute("DELETE FROM fidelity_round WHERE task_id = ?", (task_id,))


def clear_winner(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute(
        "UPDATE fidelity_round SET winner = '' WHERE task_id = ?",
        (task_id,),
    )


def insert_round(
    connection: sqlite3.Connection, task_id: int, winner: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO fidelity_round (task_id, winner, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, winner, recorded_at),
    )


def insert_kept(
    connection: sqlite3.Connection,
    task_id: int,
    candidate: str,
    position: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO fidelity_kept (task_id, candidate, position, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, candidate, position, recorded_at),
    )


def round_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT winner
        FROM fidelity_round
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()


def kept_for(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT candidate
        FROM fidelity_kept
        WHERE task_id = ?
        ORDER BY position
        """,
        (task_id,),
    ).fetchall()
