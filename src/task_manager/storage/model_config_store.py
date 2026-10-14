"""The one model service saved for this workspace."""

import sqlite3

from task_manager.model import HttpModel


def replace_service(
    connection: sqlite3.Connection,
    name: str,
    base_url: str,
    api_key: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO model_service (id, model_name, base_url, api_key)
        VALUES (1, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            model_name = excluded.model_name,
            base_url = excluded.base_url,
            api_key = excluded.api_key
        """,
        (name, base_url, api_key),
    )


def load_model(connection: sqlite3.Connection) -> HttpModel | None:
    row = connection.execute(
        "SELECT model_name, base_url, api_key FROM model_service WHERE id = 1"
    ).fetchone()
    if row is None:
        return None
    return HttpModel(row["model_name"], row["base_url"], row["api_key"])
