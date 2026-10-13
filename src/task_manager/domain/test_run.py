"""Run one named test inside a project that already exists."""

import os
import re
import sqlite3
import subprocess
import sys
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

NAME_TEST = "Name the test this change runs."
ONE_TEST = "Name one test in a file."
TEST_OUTSIDE = "The test must stay inside the named project."
TEST_MUST_EXIST = "The test must already exist."
TEST_COULD_NOT_RUN = "The test could not be run."
TEST_MISMATCH = "The test no longer matches the path this change was proposed against."
TEST_DID_NOT_FINISH = "The test did not finish."

_NODE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)*(?:\[[A-Za-z0-9_.:\-]+\])?$"
)
_TIMEOUT_SECONDS = 30
_OUTPUT_LIMIT = 64_000


def record(
    connection: sqlite3.Connection,
    task_id: int,
    project: str | None,
    change_class: str | None,
    what_changed: str | None,
    stopped: bool,
    test: str | None,
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
    placed = _place(project_dir, test)
    if not isinstance(placed, str):
        return placed
    stored_class = change_class
    stopped_flag = 0
    if change_class == "ordinary" and stopped:
        stored_class = "consequential"
        stopped_flag = 1
    ran = None
    if stored_class == "ordinary":
        ran = _execute(project_dir, placed)
        if not isinstance(ran, tuple):
            return ran
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
    implementation_store.insert_test_run(connection, change_id, placed)
    if ran is not None:
        result, output = ran
        implementation_store.insert_test_run_result(connection, change_id, result, output)
    return _detail(connection, int(task["id"]))


def run_approved(project: str | None, test_path: str, root: Path):
    if project is None:
        return conflict(TEST_MISMATCH)
    project_dir = _project_dir(project, root)
    if not project_dir.is_dir():
        return conflict(TEST_MISMATCH)
    placed = _place(project_dir, test_path)
    if not isinstance(placed, str):
        return conflict(TEST_MISMATCH)
    return _execute(project_dir, placed)


def _place(project_dir: Path, test: str | None):
    named = clean(test)
    if not named:
        return bad_request(NAME_TEST)
    if "::" not in named:
        return bad_request(ONE_TEST)
    file_part, node = named.split("::", 1)
    if not _NODE.fullmatch(node):
        return bad_request(ONE_TEST)
    relative = _relative_inside(file_part)
    if relative is None:
        return conflict(TEST_OUTSIDE)
    if not relative.endswith(".py"):
        return bad_request(ONE_TEST)
    project_resolved = project_dir.resolve()
    target = project_dir / relative
    if not (target.is_symlink() or target.exists()):
        return bad_request(TEST_MUST_EXIST)
    try:
        resolved = target.resolve(strict=True)
    except OSError:
        return conflict(TEST_OUTSIDE)
    if not _inside(resolved, project_resolved) or not resolved.is_file():
        if not _inside(resolved, project_resolved):
            return conflict(TEST_OUTSIDE)
        return bad_request(TEST_MUST_EXIST)
    return f"{relative}::{node}"


def _execute(project_dir: Path, node: str):
    try:
        root = str(project_dir.resolve())
        completed = subprocess.run(
            [
                _interpreter(project_dir),
                "-m",
                "pytest",
                node,
                "-q",
                "--tb=line",
                "-p",
                "no:cacheprovider",
                "-o",
                "addopts=",
                "--confcutdir",
                root,
                "--rootdir",
                root,
            ],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            timeout=_TIMEOUT_SECONDS,
            check=False,
            env=_environment(),
        )
    except subprocess.TimeoutExpired as exc:
        output = _clip(_join(_text(exc.stdout), _text(exc.stderr)))
        if output and not output.endswith("\n"):
            output += "\n"
        return "failed", output + TEST_DID_NOT_FINISH
    except OSError:
        return bad_request(TEST_COULD_NOT_RUN)
    output = _clip(_join(completed.stdout or "", completed.stderr or ""))
    result = "passed" if completed.returncode == 0 else "failed"
    return result, output


def _interpreter(project_dir: Path) -> str:
    candidate = project_dir / ".venv" / "bin" / "python"
    if candidate.is_file():
        return str(candidate)
    return sys.executable


def _environment() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if not key.startswith("PYTEST_")}


def _join(stdout: str, stderr: str) -> str:
    if stdout and stderr:
        if not stdout.endswith("\n"):
            stdout += "\n"
        return stdout + stderr
    return stdout or stderr


def _text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _clip(text: str) -> str:
    if len(text) <= _OUTPUT_LIMIT:
        return text
    return text[:_OUTPUT_LIMIT] + "\nThe rest of the output was left out."
