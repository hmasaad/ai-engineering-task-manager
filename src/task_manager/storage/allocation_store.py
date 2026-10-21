"""Agents, yields, and one stored budget split."""

import sqlite3


def agent_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, name
        FROM allocation_agent
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def count_agents(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM allocation_agent WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_agent(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO allocation_agent (task_id, name, recorded_at)
        VALUES (?, ?, ?)
        """,
        (task_id, name, recorded_at),
    )


def agents(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name
        FROM allocation_agent
        WHERE task_id = ?
        ORDER BY id
        """,
        (task_id,),
    ).fetchall()


def yield_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM allocation_yield
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def yield_for_agent(
    connection: sqlite3.Connection, task_id: int, agent_id: int
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id
        FROM allocation_yield
        WHERE task_id = ? AND agent_id = ?
        """,
        (task_id, agent_id),
    ).fetchone()


def count_yields(connection: sqlite3.Connection, task_id: int) -> int:
    row = connection.execute(
        "SELECT COUNT(*) AS total FROM allocation_yield WHERE task_id = ?",
        (task_id,),
    ).fetchone()
    return int(row["total"])


def insert_yield(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    agent_id: int,
    value: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO allocation_yield (task_id, name, agent_id, value, recorded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, name, agent_id, value, recorded_at),
    )


def yields(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT o.id, o.name, o.agent_id, o.value, a.name AS agent
        FROM allocation_yield o
        JOIN allocation_agent a ON a.id = o.agent_id
        WHERE o.task_id = ?
        ORDER BY o.id
        """,
        (task_id,),
    ).fetchall()


def clear_shares(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute("DELETE FROM allocation_share WHERE task_id = ?", (task_id,))


def insert_share(
    connection: sqlite3.Connection,
    task_id: int,
    agent: str,
    units: int,
    position: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO allocation_share (task_id, agent, units, position, recorded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (task_id, agent, units, position, recorded_at),
    )


def shares_for(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT agent, units
        FROM allocation_share
        WHERE task_id = ?
        ORDER BY position
        """,
        (task_id,),
    ).fetchall()
