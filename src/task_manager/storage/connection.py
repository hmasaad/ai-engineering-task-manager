"""Open one SQLite workspace file and wrap each command in a transaction."""

import sqlite3
from pathlib import Path

from task_manager.domain.results import Refusal

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(path: str | Path) -> sqlite3.Connection:
    database = Path(path)
    if database.parent:
        database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.isolation_level = None
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def ensure_engineer(connection: sqlite3.Connection, engineer_name: str) -> str:
    name = engineer_name.strip() or "Engineer"
    row = connection.execute("SELECT engineer_name FROM workspace WHERE id = 1").fetchone()
    if row is None:
        connection.execute(
            "INSERT INTO workspace (id, engineer_name) VALUES (1, ?)",
            (name,),
        )
    else:
        connection.execute(
            "UPDATE workspace SET engineer_name = ? WHERE id = 1",
            (name,),
        )
    connection.commit()
    return name


def engineer_name(connection: sqlite3.Connection) -> str:
    row = connection.execute("SELECT engineer_name FROM workspace WHERE id = 1").fetchone()
    if row is None:
        return "Engineer"
    return str(row["engineer_name"])


def call_in_transaction(connection: sqlite3.Connection, operation):
    """Run one command. A Refusal rolls the transaction back."""
    connection.execute("BEGIN")
    try:
        result = operation(connection)
    except Exception:
        connection.execute("ROLLBACK")
        raise
    if isinstance(result, Refusal):
        connection.execute("ROLLBACK")
        return result
    connection.execute("COMMIT")
    return result
