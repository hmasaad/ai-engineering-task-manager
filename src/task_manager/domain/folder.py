"""Create one folder inside a project that already exists."""

import sqlite3
from pathlib import Path

from task_manager.domain.capture import _detail
from task_manager.domain.implementation import (
    CHOOSE_CLASS,
    NAME_PROJECT,
    PROJECT_MUST_EXIST,
    WHAT_CHANGED_REQUIRED,
    _CLASSES,
    _inside,
    _project_dir,
    _record_status,
    _relative_inside,
)
from task_manager.domain.results import bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import implementation_store, task_store
from task_manager.storage.connection import assistant_name, engineer_name

NAME_FOLDER = "Name the folder this change creates."
FOLDER_OUTSIDE = "The folder must stay inside the named project."
PARENT_MUST_EXIST = "The folder that holds this one must already exist."
FOLDER_EXISTS = "The folder already exists."
FILE_IN_THE_WAY = "A file is already at that path."
FOLDER_MISMATCH = "The folder no longer matches the path this change was proposed against."


def record(
    connection: sqlite3.Connection,
    task_id: int,
    project: str | None,
    change_class: str | None,
    what_changed: str | None,
    stopped: bool,
    folder: str | None,
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
    placed = _place(project_dir, folder)
    if not isinstance(placed, tuple):
        return placed
    relative, target = placed
    stored_class = change_class
    stopped_flag = 0
    if change_class == "ordinary" and stopped:
        stored_class = "consequential"
        stopped_flag = 1
    if stored_class == "consequential":
        pass
    else:
        try:
            target.mkdir()
        except FileExistsError:
            stored_class = "consequential"
    change_id = implementation_store.insert_change(
        connection,
        int(task["id"]),
        text,
        stored_class,
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
    implementation_store.insert_created_folder(connection, change_id, relative)
    return _detail(connection, int(task["id"]))


def create_approved(project: str | None, folder_path: str, root: Path):
    if project is None:
        return conflict(FOLDER_OUTSIDE)
    project_dir = _project_dir(project, root)
    if not project_dir.is_dir():
        return conflict(FOLDER_MISMATCH)
    relative = _relative_inside(folder_path)
    if relative is None:
        return conflict(FOLDER_OUTSIDE)
    target = project_dir / relative
    parent = target.parent
    if not parent.is_dir() or not _inside(parent, project_dir.resolve()):
        return conflict(FOLDER_MISMATCH)
    if target.is_symlink() or target.exists():
        return conflict(FOLDER_MISMATCH)
    try:
        target.mkdir()
    except FileExistsError:
        return conflict(FOLDER_MISMATCH)
    return None


def _place(project_dir: Path, folder: str | None):
    named = clean(folder)
    if not named:
        return bad_request(NAME_FOLDER)
    relative = _relative_inside(named)
    if relative is None:
        return conflict(FOLDER_OUTSIDE)
    project_resolved = project_dir.resolve()
    target = project_dir / relative
    parent = target.parent
    if not parent.is_dir():
        return bad_request(PARENT_MUST_EXIST)
    if not _inside(parent, project_resolved):
        return conflict(FOLDER_OUTSIDE)
    if target.is_symlink() or target.exists():
        try:
            resolved = target.resolve(strict=True)
        except OSError:
            return conflict(FOLDER_OUTSIDE)
        if not _inside(resolved, project_resolved):
            return conflict(FOLDER_OUTSIDE)
        if resolved.is_dir():
            return bad_request(FOLDER_EXISTS)
        return bad_request(FILE_IN_THE_WAY)
    return relative, target
