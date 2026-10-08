"""Insert-only reads of one project file."""

import sqlite3


def insert_file_read(
    connection: sqlite3.Connection,
    task_id: int,
    project: str,
    file_path: str,
    file_text: str,
    assistant_name: str,
    read_at: str,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO file_read (
            task_id, project, file_path, file_text, assistant_name, read_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, project.strip(), file_path.strip(), file_text, assistant_name, read_at),
    )
    return int(cursor.lastrowid)


def file_reads_for(connection: sqlite3.Connection, task_id: int) -> list[dict[str, object]]:
    rows = connection.execute(
        """
        SELECT id, project, file_path, file_text, assistant_name, read_at
        FROM file_read
        WHERE task_id = ?
        ORDER BY read_at, id
        """,
        (task_id,),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "project": row["project"],
            "path": row["file_path"],
            "text": row["file_text"],
            "assistant_name": row["assistant_name"],
            "read_at": row["read_at"],
        }
        for row in rows
    ]
