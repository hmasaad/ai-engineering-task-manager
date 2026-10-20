"""Tenants and the turns granted to them."""

import sqlite3

QUOTA = 2


def tenant_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, task_id, name, quota, recorded_at
        FROM schedule_tenant
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def insert_tenant(
    connection: sqlite3.Connection, task_id: int, name: str, recorded_at: str
) -> None:
    connection.execute(
        """
        INSERT INTO schedule_tenant (task_id, name, quota, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, name, QUOTA, recorded_at),
    )


def tenants(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT id, name, quota
        FROM schedule_tenant
        WHERE task_id = ?
        ORDER BY id ASC
        """,
        (task_id,),
    ).fetchall()


def turn_by_name(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT id, name FROM schedule_turn WHERE task_id = ? AND name = ?",
        (task_id, name),
    ).fetchone()


def insert_turn(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    tenant_id: int,
    recorded_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO schedule_turn (task_id, name, tenant_id, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, name, tenant_id, recorded_at),
    )


def turns(connection: sqlite3.Connection, task_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT schedule_turn.name AS name, schedule_tenant.name AS tenant
        FROM schedule_turn
        JOIN schedule_tenant ON schedule_tenant.id = schedule_turn.tenant_id
        WHERE schedule_turn.task_id = ?
        ORDER BY schedule_turn.id ASC
        """,
        (task_id,),
    ).fetchall()


def used_counts(connection: sqlite3.Connection, task_id: int) -> dict[int, int]:
    rows = connection.execute(
        """
        SELECT tenant_id, COUNT(*) AS used
        FROM schedule_turn
        WHERE task_id = ?
        GROUP BY tenant_id
        """,
        (task_id,),
    ).fetchall()
    return {int(row["tenant_id"]): int(row["used"]) for row in rows}
