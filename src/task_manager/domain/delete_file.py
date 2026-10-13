"""Delete one text file after the engineer approves."""

import sqlite3
from pathlib import Path

from task_manager.domain.capture import _detail
from task_manager.domain.implementation import (
    CHOOSE_CLASS,
    FILE_MISMATCH,
    FILE_NOT_TEXT,
    FILE_OUTSIDE,
    NAME_PROJECT,
    PROJECT_MUST_EXIST,
    WHAT_CHANGED_REQUIRED,
    _CLASSES,
    _inside,
    _is_text,
    _project_dir,
    _record_status,
    _relative_inside,
)
from task_manager.domain.results import bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import implementation_store, task_store
from task_manager.storage.connection import assistant_name, engineer_name

NAME_FILE = "Name the file this change deletes."
FILE_MUST_EXIST = "The file must already exist."
PATH_IS_FOLDER = "The path is a folder."
LINK_CANNOT = "A link cannot be deleted by this change."


def record(
    connection: sqlite3.Connection,
    task_id: int,
    project: str | None,
    change_class: str | None,
    what_changed: str | None,
    stopped: bool,
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
    text = clean(what_changed)
    if not text:
        return bad_request(WHAT_CHANGED_REQUIRED)
    if change_class not in _CLASSES:
        return bad_request(CHOOSE_CLASS)
    placed = _inspect(project_dir, file_path)
    if not isinstance(placed, tuple):
        return placed
    relative, previous, _resolved = placed
    stopped_flag = 1 if change_class == "ordinary" and stopped else 0
    change_id = implementation_store.insert_change(
        connection,
        int(task["id"]),
        text,
        "consequential",
        engineer_name(connection),
        occurred_at,
    )
    implementation_store.insert_assistant_change(
        connection,
        change_id,
        named_project,
        assistant_name(connection),
        stopped_flag,
    )
    implementation_store.insert_deleted_file(connection, change_id, relative, previous)
    return _detail(connection, int(task["id"]))


def delete_approved(project: str | None, file_path: str, previous_text: str, root: Path):
    if project is None:
        return conflict(FILE_MISMATCH)
    project_dir = _project_dir(project, root)
    if not project_dir.is_dir():
        return conflict(FILE_MISMATCH)
    placed = _inspect(project_dir, file_path)
    if not isinstance(placed, tuple):
        return conflict(FILE_MISMATCH)
    _relative, current_text, resolved = placed
    if current_text != previous_text or resolved.is_symlink() or not resolved.is_file():
        return conflict(FILE_MISMATCH)
    try:
        again = resolved.read_bytes()
    except OSError:
        return conflict(FILE_MISMATCH)
    if not _is_text(again) or again.decode("utf-8") != previous_text:
        return conflict(FILE_MISMATCH)
    try:
        resolved.unlink()
    except OSError:
        return conflict(FILE_MISMATCH)
    return None


def _inspect(project_dir: Path, file_path: str | None):
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
    if target.is_symlink():
        try:
            resolved = target.resolve(strict=True)
        except OSError:
            return conflict(FILE_OUTSIDE)
        if not _inside(resolved, project_resolved):
            return conflict(FILE_OUTSIDE)
        return bad_request(LINK_CANNOT)
    try:
        resolved = target.resolve(strict=True)
    except OSError:
        return bad_request(FILE_MUST_EXIST)
    if not _inside(resolved, project_resolved):
        return conflict(FILE_OUTSIDE)
    if resolved.is_dir():
        return bad_request(PATH_IS_FOLDER)
    if not resolved.is_file():
        return bad_request(FILE_NOT_TEXT)
    try:
        data = resolved.read_bytes()
    except OSError:
        return bad_request(FILE_MUST_EXIST)
    if not _is_text(data):
        return bad_request(FILE_NOT_TEXT)
    return relative, data.decode("utf-8"), resolved
