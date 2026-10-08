"""Read one existing text file and store that text."""

import sqlite3
from pathlib import Path

from task_manager.domain.capture import _detail
from task_manager.domain.implementation import (
    FILE_NOT_TEXT,
    FILE_OUTSIDE,
    NAME_PROJECT,
    PROJECT_MUST_EXIST,
    _inside,
    _is_text,
    _project_dir,
    _record_status,
    _relative_inside,
)
from task_manager.domain.results import bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import file_read_store, task_store
from task_manager.storage.connection import assistant_name

NAME_FILE = "Name the file this change reads."
FILE_MUST_EXIST = "The file must already exist."


def read_file(
    connection: sqlite3.Connection,
    task_id: int,
    project: str | None,
    file_path: str | None,
    occurred_at: str,
    project_root: Path | None = None,
):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    status_refusal = _record_status(task["status"])
    if status_refusal is not None:
        return status_refusal
    named_project = clean(project)
    if not named_project:
        return bad_request(NAME_PROJECT)
    root = project_root or Path.cwd()
    project_dir = _project_dir(named_project, root)
    if not project_dir.is_dir():
        return bad_request(PROJECT_MUST_EXIST)
    named = clean(file_path)
    if not named:
        return bad_request(NAME_FILE)
    relative = _relative_inside(named)
    if relative is None:
        return conflict(FILE_OUTSIDE)
    project_resolved = project_dir.resolve()
    target = project_dir / relative
    parent = target.parent
    if not parent.exists() and not parent.is_symlink():
        return bad_request(FILE_MUST_EXIST)
    if not _inside(parent, project_resolved):
        return conflict(FILE_OUTSIDE)
    if not target.exists() and not target.is_symlink():
        return bad_request(FILE_MUST_EXIST)
    try:
        resolved = target.resolve(strict=True)
    except OSError:
        return bad_request(FILE_MUST_EXIST)
    if not _inside(resolved, project_resolved):
        return conflict(FILE_OUTSIDE)
    if not target.is_file():
        return bad_request(FILE_NOT_TEXT)
    data = target.read_bytes()
    if not _is_text(data):
        return bad_request(FILE_NOT_TEXT)
    file_read_store.insert_file_read(
        connection,
        int(task["id"]),
        named_project,
        relative,
        data.decode("utf-8"),
        assistant_name(connection),
        occurred_at,
    )
    return _detail(connection, int(task["id"]))
