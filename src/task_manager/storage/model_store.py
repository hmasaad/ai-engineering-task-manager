"""Insert-only model calls."""

import sqlite3


def insert_model_call(
    connection: sqlite3.Connection,
    change_id: int,
    file_read_id: int,
    model_name: str,
    model_input: str,
    model_output: str,
) -> None:
    connection.execute(
        """
        INSERT INTO model_call (
            change_id, file_read_id, model_name, model_input, model_output
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (change_id, file_read_id, model_name, model_input, model_output),
    )


def row_file_read(connection: sqlite3.Connection, file_read_id: int) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT id, task_id, project, file_path, file_text FROM file_read WHERE id = ?",
        (file_read_id,),
    ).fetchone()
