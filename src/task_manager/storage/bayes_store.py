"""Designs, observations, and one stored recommendation."""

import sqlite3


def design_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name, first_setting, second_setting
        FROM bayes_design
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_designs(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM bayes_design WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_design(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    first_setting: int,
    second_setting: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO bayes_design (
            task_id, name, first_setting, second_setting, recorded_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, name, first_setting, second_setting, recorded_at),
    )


def designs(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name, first_setting, second_setting
        FROM bayes_design
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def observation_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM bayes_observation
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def observation_for_design(
    connection: sqlite3.Connection, task_id: int, design_id: int
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM bayes_observation
        WHERE task_id = ? AND design_id = ?
        """,
        (task_id, design_id),
    ).fetchone()


def count_observations(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM bayes_observation WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_observation(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    design_id: int,
    first_objective: int,
    second_objective: int,
    constraint_mark: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO bayes_observation (
            task_id, name, design_id, first_objective, second_objective,
            constraint_mark, recorded_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_id,
            name,
            design_id,
            first_objective,
            second_objective,
            constraint_mark,
            recorded_at,
        ),
    )


def observations(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT
            o.id,
            o.name,
            o.first_objective,
            o.second_objective,
            o.constraint_mark,
            d.name AS design,
            d.first_setting,
            d.second_setting
        FROM bayes_observation o
        JOIN bayes_design d ON d.id = o.design_id
        WHERE o.task_id = ?
        ORDER BY o.id
        """,
        (task_id,),
    ).fetchall()


def clear_recommendation(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute("DELETE FROM bayes_front WHERE task_id = ?", (task_id,))
    connection.execute("DELETE FROM bayes_pick WHERE task_id = ?", (task_id,))


def insert_pick(
    connection: sqlite3.Connection,
    task_id: int,
    next_design: str,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO bayes_pick (task_id, next_design, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, next_design, recorded_at),
    )


def insert_front(
    connection: sqlite3.Connection,
    task_id: int,
    design: str,
    first_objective: int,
    second_objective: int,
    position: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO bayes_front (
            task_id, design, first_objective, second_objective, position, recorded_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, design, first_objective, second_objective, position, recorded_at),
    )


def pick_for(connection: sqlite3.Connection, task_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT next_design
        FROM bayes_pick
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchone()


def front_for(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT design, first_objective, second_objective
        FROM bayes_front
        WHERE task_id = ?
        ORDER BY position
        """,
        (task_id,),
    ).fetchall()
