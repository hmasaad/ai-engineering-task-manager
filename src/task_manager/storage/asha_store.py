"""Trials, runners, rung scores, and one stored schedule."""

import sqlite3


def trial_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name
        FROM asha_trial
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_trials(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM asha_trial WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_trial(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO asha_trial (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def trials(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name
        FROM asha_trial
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def runner_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name
        FROM asha_runner
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_runners(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM asha_runner WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_runner(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO asha_runner (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def runners(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name
        FROM asha_runner
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def rung_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM asha_rung
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def rung_for_trial(
    connection: sqlite3.Connection, task_id: int, trial_id: int, rung: int
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM asha_rung
        WHERE task_id = ? AND trial_id = ? AND rung = ?
        """,
        (task_id, trial_id, rung),
    ).fetchone()


def count_rungs(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM asha_rung WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_rung(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    trial_id: int,
    rung: int,
    score: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO asha_rung (task_id, name, trial_id, rung, score, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, name, trial_id, rung, score, recorded_at),
    )


def rungs(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT o.id, o.name, o.trial_id, o.rung, o.score, t.name AS trial
        FROM asha_rung o
        JOIN asha_trial t ON t.id = o.trial_id
        WHERE o.task_id = ?
        ORDER BY o.id
        """,
        (task_id,),
    ).fetchall()


def clear_schedule(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute("DELETE FROM asha_promoted WHERE task_id = ?", (task_id,))
    connection.execute("DELETE FROM asha_assignment WHERE task_id = ?", (task_id,))
    connection.execute("DELETE FROM asha_winner WHERE task_id = ?", (task_id,))


def clear_promoted(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute("DELETE FROM asha_promoted WHERE task_id = ?", (task_id,))


def clear_winner(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute("DELETE FROM asha_winner WHERE task_id = ?", (task_id,))


def insert_promoted(
    connection: sqlite3.Connection,
    task_id: int,
    trial: str,
    position: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO asha_promoted (task_id, trial, position, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, trial, position, recorded_at),
    )


def insert_assignment(
    connection: sqlite3.Connection,
    task_id: int,
    trial: str,
    runner: str,
    position: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO asha_assignment (task_id, trial, runner, position, recorded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, trial, runner, position, recorded_at),
    )


def insert_winner(
    connection: sqlite3.Connection, task_id: int, winner: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO asha_winner (task_id, winner, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, winner, recorded_at),
    )


def promoted_for(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT trial
        FROM asha_promoted
        WHERE task_id = ?
        ORDER BY position
        """,
        (task_id,),
    ).fetchall()


def assignments_for(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT trial, runner
        FROM asha_assignment
        WHERE task_id = ?
        ORDER BY position
        """,
        (task_id,),
    ).fetchall()


def winner_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT winner
        FROM asha_winner
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()
