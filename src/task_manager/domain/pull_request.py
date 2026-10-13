"""Open one pull request after the engineer approves."""

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

NAME_BRANCH = "Name the branch this change proposes."
BRANCH_MUST_EXIST = "The branch must already exist."
NOT_A_REPOSITORY = "The project must already be a repository."
REMOTE_REQUIRED = "The project must already have a remote."
BASE_REQUIRED = "The repository must already have a base branch."
OTHER_BRANCH = "Choose a branch other than the base branch."
PULL_MISMATCH = "The pull request no longer matches the branch this change was proposed against."
PULL_REFUSED = "The pull request was refused."
PULL_COULD_NOT = "The pull request could not be opened."

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
    base = _ready(project_dir)
    if not isinstance(base, str):
        return base
    text = clean(what_changed)
    if not text:
        return bad_request(WHAT_CHANGED_REQUIRED)
    if change_class not in _CLASSES:
        return bad_request(CHOOSE_CLASS)
    named_branch = _branch_name(branch)
    if not isinstance(named_branch, str):
        return named_branch
    exists = _local_branch(project_dir, named_branch)
    if exists is not True:
        return exists
    if named_branch == base:
        return bad_request(OTHER_BRANCH)
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
    implementation_store.insert_pull_request(connection, change_id, named_branch, base)
    return _detail(connection, int(task["id"]))


def open_approved(project: str | None, branch: str, base: str, title: str, root: Path):
    if project is None or not clean(title):
        return conflict(PULL_MISMATCH)
    project_dir = _project_dir(project, root)
    if not project_dir.is_dir():
        return conflict(PULL_MISMATCH)
    current_base = _ready(project_dir)
    if not isinstance(current_base, str):
        if getattr(current_base, "message", None) == PULL_COULD_NOT:
            return conflict(PULL_COULD_NOT)
        return conflict(PULL_MISMATCH)
    named_branch = _branch_name(branch)
    if not isinstance(named_branch, str):
        return conflict(PULL_MISMATCH)
    exists = _local_branch(project_dir, named_branch)
    if exists is not True:
        if getattr(exists, "message", None) == PULL_COULD_NOT:
            return conflict(PULL_COULD_NOT)
        return conflict(PULL_MISMATCH)
    if named_branch != branch or current_base != base or named_branch == current_base:
        return conflict(PULL_MISMATCH)
    published = _git(
        project_dir,
        ["push", "origin", f"refs/heads/{named_branch}:refs/heads/{named_branch}"],
    )
    if not isinstance(published, subprocess.CompletedProcess):
        return conflict(PULL_COULD_NOT)
    if published.returncode != 0:
        return conflict(PULL_REFUSED)
    opened = _gh(
        project_dir,
        [
            "pr",
            "create",
            "--base",
            current_base,
            "--head",
            named_branch,
            "--title",
            title,
            "--body",
            title,
        ],
    )
    if not isinstance(opened, subprocess.CompletedProcess):
        return conflict(PULL_COULD_NOT)
    if opened.returncode != 0:
        return conflict(PULL_REFUSED)
    url = opened.stdout.strip()
    if not url.startswith("https://") or any(character.isspace() for character in url):
        return conflict(PULL_REFUSED)
    return url


def _ready(project_dir: Path):
    repository = _repository(project_dir)
    if repository is not None:
        return repository
    remote = _git(project_dir, ["remote", "get-url", "origin"])
    if not isinstance(remote, subprocess.CompletedProcess):
        return remote
    if remote.returncode != 0 or not remote.stdout.strip():
        return bad_request(REMOTE_REQUIRED)
    return _base(project_dir)


def _branch_name(branch: str | None):
    named = clean(branch)
    if not named or ".." in named or "//" in named or named.endswith("/") or not _BRANCH.fullmatch(named):
        return bad_request(NAME_BRANCH)
    return named


def _repository(project_dir: Path):
    completed = _git(project_dir, ["rev-parse", "--is-inside-work-tree"])
    if not isinstance(completed, subprocess.CompletedProcess):
        return completed
    if completed.returncode != 0 or completed.stdout.strip() != "true":
        return bad_request(NOT_A_REPOSITORY)
    return None


def _base(project_dir: Path):
    completed = _git(project_dir, ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"])
    if not isinstance(completed, subprocess.CompletedProcess):
        return completed
    if completed.returncode != 0:
        return bad_request(BASE_REQUIRED)
    short = completed.stdout.strip()
    prefix = "origin/"
    if not short.startswith(prefix):
        return bad_request(BASE_REQUIRED)
    name = short[len(prefix) :]
    if not name or not _BRANCH.fullmatch(name):
        return bad_request(BASE_REQUIRED)
    return name


def _local_branch(project_dir: Path, branch: str):
    completed = _git(project_dir, ["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"])
    if not isinstance(completed, subprocess.CompletedProcess):
        return completed
    if completed.returncode == 0:
        return True
    if completed.returncode == 1:
        return bad_request(BRANCH_MUST_EXIST)
    return bad_request(PULL_COULD_NOT)


def _git(project_dir: Path, args: list[str]):
    return _command(project_dir, ["git", *args])


def _gh(project_dir: Path, args: list[str]):
    return _command(project_dir, ["gh", *args])


def _command(project_dir: Path, argv: list[str]):
    try:
        return subprocess.run(
            argv,
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
        return bad_request(PULL_COULD_NOT)
    except OSError:
        return bad_request(PULL_COULD_NOT)


def _environment() -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in _STRIPPED and not key.startswith(_CONFIG_PREFIX)
    }
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_EDITOR"] = "true"
    env["GIT_SEQUENCE_EDITOR"] = "true"
    env["GH_PROMPT_DISABLED"] = "1"
    return env
