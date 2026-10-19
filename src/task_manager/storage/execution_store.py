"""Named executions of one read or one folder command."""

import sqlite3


def row_execution(
    connection: sqlite3.Connection, task_id: int, name: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT name, action, path
        FROM command_execution
        WHERE task_id = ? AND name = ?
        """,
        (task_id, name),
    ).fetchone()


def insert_execution(
    connection: sqlite3.Connection,
    task_id: int,
    name: str,
    action: str,
    path: str,
    recorded_at: str,
) -> bool:
    try:
        connection.execute(
            """
            INSERT INTO command_execution (task_id, name, action, path, recorded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (task_id, name, action, path, recorded_at),
        )
    except sqlite3.IntegrityError:
        return False
    return True


def executions_for(connection: sqlite3.Connection, task_id: int) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT name, action, path
        FROM command_execution
        WHERE task_id = ?
        ORDER BY id ASC
        """,
        (task_id,),
    ).fetchall()
    return [
        {"name": row["name"], "action": row["action"], "path": row["path"]} for row in rows
    ]
