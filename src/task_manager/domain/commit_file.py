"""Commit one text file after the engineer approves."""

import os
import sqlite3
import subprocess
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

NAME_FILE = "Name the file this change commits."
FILE_MUST_EXIST = "The file must already exist."
NOT_A_REPOSITORY = "The project must already be a repository."
PATH_IS_FOLDER = "The path is a folder."
LINK_CANNOT = "A link cannot be committed by this change."
NO_CHANGE = "That file has no change to commit."
COMMIT_COULD_NOT = "The commit could not be made."
COMMIT_REFUSED = "The commit was refused."

_TIMEOUT_SECONDS = 30
_CONFIG_PREFIX = "GIT_CONFIG"
_STRIPPED = {
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_PREFIX",
    "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
}


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
    repository = _repository(project_dir)
    if repository is not None:
        return repository
    text = clean(what_changed)
    if not text:
        return bad_request(WHAT_CHANGED_REQUIRED)
    if change_class not in _CLASSES:
        return bad_request(CHOOSE_CLASS)
    placed = _inspect(project_dir, file_path)
    if not isinstance(placed, tuple):
        return placed
    relative, file_text = placed
    changed = _status(project_dir, relative)
    if not isinstance(changed, str):
        return changed
    if changed == "":
        return bad_request(NO_CHANGE)
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
    implementation_store.insert_committed_file(connection, change_id, relative, file_text)
    return _detail(connection, int(task["id"]))


def commit_approved(
    project: str | None,
    file_path: str,
    file_text: str,
    message: str,
    root: Path,
):
    if project is None or not clean(message):
        return conflict(FILE_MISMATCH)
    project_dir = _project_dir(project, root)
    if not project_dir.is_dir():
        return conflict(FILE_MISMATCH)
    repository = _repository(project_dir)
    if repository is not None:
        if repository.message == COMMIT_COULD_NOT:
            return conflict(COMMIT_COULD_NOT)
        return conflict(FILE_MISMATCH)
    placed = _inspect(project_dir, file_path)
    if not isinstance(placed, tuple):
        return conflict(FILE_MISMATCH)
    relative, current = placed
    if current != file_text:
        return conflict(FILE_MISMATCH)
    changed = _status(project_dir, relative)
    if not isinstance(changed, str):
        return conflict(COMMIT_COULD_NOT)
    if changed == "":
        return conflict(NO_CHANGE)
    digest = _commit(project_dir, relative, message, changed.startswith("?? "))
    return digest


def _inspect(project_dir: Path, file_path: str | None):
    named = clean(file_path)
    if not named:
        return bad_request(NAME_FILE)
    relative = _relative_inside(named)
    if relative is None or ".git" in Path(relative).parts:
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
    return relative, data.decode("utf-8")


def _repository(project_dir: Path):
    completed = _git(project_dir, ["rev-parse", "--is-inside-work-tree"])
    if not isinstance(completed, subprocess.CompletedProcess):
        return completed
    if completed.returncode != 0 or completed.stdout.strip() != "true":
        return bad_request(NOT_A_REPOSITORY)
    return None


def _status(project_dir: Path, relative: str):
    completed = _git(project_dir, ["status", "--porcelain=v1", "-z", "--", relative])
    if not isinstance(completed, subprocess.CompletedProcess):
        return completed
    if completed.returncode != 0:
        return bad_request(COMMIT_COULD_NOT)
    return completed.stdout


def _commit(project_dir: Path, relative: str, message: str, untracked: bool):
    if untracked:
        added = _git(project_dir, ["add", "--", relative])
        if not isinstance(added, subprocess.CompletedProcess) or added.returncode != 0:
            return conflict(COMMIT_REFUSED) if isinstance(added, subprocess.CompletedProcess) else added
    before = _head(project_dir)
    committed = _git(project_dir, ["commit", "-m", message, "--", relative])
    if not isinstance(committed, subprocess.CompletedProcess) or committed.returncode != 0:
        if untracked:
            _git(project_dir, ["restore", "--staged", "--", relative])
        if not isinstance(committed, subprocess.CompletedProcess):
            return committed
        return conflict(COMMIT_REFUSED)
    after = _head(project_dir)
    if not after or after == before:
        return conflict(COMMIT_REFUSED)
    return after


def _head(project_dir: Path) -> str:
    completed = _git(project_dir, ["rev-parse", "HEAD"])
    if not isinstance(completed, subprocess.CompletedProcess) or completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _git(project_dir: Path, args: list[str]):
    try:
        return subprocess.run(
            ["git", *args],
            cwd=project_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            timeout=_TIMEOUT_SECONDS,
            check=False,
            env=_environment(),
        )
    except subprocess.TimeoutExpired:
        return bad_request(COMMIT_COULD_NOT)
    except OSError:
        return bad_request(COMMIT_COULD_NOT)


def _environment() -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in _STRIPPED and not key.startswith(_CONFIG_PREFIX)
    }
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_EDITOR"] = "true"
    env["GIT_SEQUENCE_EDITOR"] = "true"
    return env
