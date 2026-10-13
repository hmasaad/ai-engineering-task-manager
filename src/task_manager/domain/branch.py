"""Create one local branch after the engineer approves."""

import os
import re
import sqlite3
import subprocess
from pathlib import Path

from task_manager.domain.capture import _detail
from task_manager.domain.implementation import (
    CHOOSE_CLASS,
    NAME_PROJECT,
    PROJECT_MUST_EXIST,
    WHAT_CHANGED_REQUIRED,
    _CLASSES,
    _project_dir,
    _record_status,
)
from task_manager.domain.results import bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import implementation_store, task_store
from task_manager.storage.connection import assistant_name, engineer_name

NAME_BRANCH = "Name the branch this change creates."
BRANCH_EXISTS = "The branch already exists."
NOT_A_REPOSITORY = "The project must already be a repository."
COMMIT_REQUIRED = "The repository must already have a commit."
BRANCH_MISMATCH = "The branch no longer matches the commit this change was proposed against."
BRANCH_REFUSED = "The branch was refused."
BRANCH_COULD_NOT = "The branch could not be created."

_BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
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
    branch: str | None,
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
    start = _head(project_dir)
    if not isinstance(start, str):
        return start
    text = clean(what_changed)
    if not text:
        return bad_request(WHAT_CHANGED_REQUIRED)
    if change_class not in _CLASSES:
        return bad_request(CHOOSE_CLASS)
    named_branch = _branch_name(branch)
    if not isinstance(named_branch, str):
        return named_branch
    exists = _branch_exists(project_dir, named_branch)
    if exists is not False:
        if exists is True:
            return bad_request(BRANCH_EXISTS)
        return exists
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
    implementation_store.insert_created_branch(connection, change_id, named_branch, start)
    return _detail(connection, int(task["id"]))


def checkout_approved(project: str | None, branch: str, start_commit: str, root: Path):
    if project is None or not clean(start_commit):
        return conflict(BRANCH_MISMATCH)
    project_dir = _project_dir(project, root)
    if not project_dir.is_dir():
        return conflict(BRANCH_MISMATCH)
    repository = _repository(project_dir)
    if repository is not None:
        if getattr(repository, "message", None) == BRANCH_COULD_NOT:
            return conflict(BRANCH_COULD_NOT)
        return conflict(BRANCH_MISMATCH)
    start = _head(project_dir)
    if not isinstance(start, str):
        if getattr(start, "message", None) == BRANCH_COULD_NOT:
            return conflict(BRANCH_COULD_NOT)
        return conflict(BRANCH_MISMATCH)
    named_branch = _branch_name(branch)
    if not isinstance(named_branch, str) or named_branch != branch or start != start_commit:
        return conflict(BRANCH_MISMATCH)
    exists = _branch_exists(project_dir, named_branch)
    if exists is not False:
        if getattr(exists, "message", None) == BRANCH_COULD_NOT:
            return conflict(BRANCH_COULD_NOT)
        return conflict(BRANCH_MISMATCH)
    switched = _git(project_dir, ["switch", "-c", named_branch])
    if not isinstance(switched, subprocess.CompletedProcess):
        return conflict(BRANCH_COULD_NOT)
    if switched.returncode != 0:
        return conflict(BRANCH_REFUSED)
    current = _current(project_dir)
    after = _head(project_dir)
    if current != named_branch or after != start_commit:
        _git(project_dir, ["switch", "-"])
        _git(project_dir, ["branch", "-d", named_branch])
        return conflict(BRANCH_REFUSED)
    return None


def _repository(project_dir: Path):
    completed = _git(project_dir, ["rev-parse", "--is-inside-work-tree"])
    if not isinstance(completed, subprocess.CompletedProcess):
        return completed
    if completed.returncode != 0 or completed.stdout.strip() != "true":
        return bad_request(NOT_A_REPOSITORY)
    return None


def _head(project_dir: Path):
    completed = _git(project_dir, ["rev-parse", "HEAD"])
    if not isinstance(completed, subprocess.CompletedProcess):
        return completed
    if completed.returncode != 0 or not completed.stdout.strip():
        return bad_request(COMMIT_REQUIRED)
    return completed.stdout.strip()


def _current(project_dir: Path) -> str:
    completed = _git(project_dir, ["branch", "--show-current"])
    if not isinstance(completed, subprocess.CompletedProcess) or completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _branch_name(branch: str | None):
    named = clean(branch)
    if not named or ".." in named or "//" in named or named.endswith("/") or not _BRANCH.fullmatch(named):
        return bad_request(NAME_BRANCH)
    return named


def _branch_exists(project_dir: Path, branch: str):
    completed = _git(project_dir, ["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"])
    if not isinstance(completed, subprocess.CompletedProcess):
        return completed
    if completed.returncode == 0:
        return True
    if completed.returncode == 1:
        return False
    return bad_request(BRANCH_COULD_NOT)


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
        return bad_request(BRANCH_COULD_NOT)
    except OSError:
        return bad_request(BRANCH_COULD_NOT)


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
