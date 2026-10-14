"""Ask the configured model once for the text of one file."""

import sqlite3
from pathlib import Path

from task_manager.domain.capture import _detail
from task_manager.domain import implementation
from task_manager.domain.implementation import (
    CHOOSE_CLASS,
    NAME_FILE,
    NAME_PROJECT,
    PROJECT_MUST_EXIST,
    WHAT_CHANGED_REQUIRED,
    _CLASSES,
    _inspect_new_file,
    _project_dir,
    _record_status,
)
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.model import ModelUnavailable
from task_manager.storage import model_store, task_store

CHOOSE_READ = "Choose the file read this change uses."
READ_NOT_FOUND = "File read not found."
READ_ON_TASK = "The change must name a file read on that task."
CHOOSE_MODEL = "Choose the model this change uses."
MODEL_NO_TEXT = "The model did not return file text."
MODEL_UNREACHABLE = "The model service could not be reached."


def record_model_file(
    connection: sqlite3.Connection,
    task_id: int,
    project: str | None,
    change_class: str | None,
    what_changed: str | None,
    stopped: bool,
    file_path: str | None,
    file_read_id: int | None,
    occurred_at: str,
    project_root: Path | None = None,
    model=None,
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
    account = clean(what_changed)
    if not account:
        return bad_request(WHAT_CHANGED_REQUIRED)
    if change_class not in _CLASSES:
        return bad_request(CHOOSE_CLASS)
    named_file = clean(file_path)
    if not named_file:
        return bad_request(NAME_FILE)
    if file_read_id is None:
        return bad_request(CHOOSE_READ)
    stored_read = model_store.row_file_read(connection, file_read_id)
    if stored_read is None:
        return missing(READ_NOT_FOUND)
    if int(stored_read["task_id"]) != int(task["id"]):
        return conflict(READ_ON_TASK)
    placed = _inspect_new_file(project_dir, named_file, "")
    if isinstance(placed, Refusal):
        return placed
    if model is None or not clean(getattr(model, "name", None)):
        return bad_request(CHOOSE_MODEL)
    detail = task_store.task_detail(connection, int(task["id"]))
    prompt = _prompt(detail, stored_read, named_project, placed.relative, account)
    try:
        output = model.complete(prompt)
    except ModelUnavailable:
        return bad_request(MODEL_UNREACHABLE)
    except Exception:
        return bad_request(MODEL_NO_TEXT)
    if not isinstance(output, str) or not output.strip():
        return bad_request(MODEL_NO_TEXT)
    recorded = implementation.record_assistant(
        connection,
        int(task["id"]),
        named_project,
        change_class,
        account,
        stopped,
        occurred_at,
        placed.relative,
        output,
        root,
    )
    if isinstance(recorded, Refusal):
        return recorded
    change_id = int(recorded["implementation_changes"][-1]["id"])
    model_store.insert_model_call(
        connection,
        change_id,
        int(stored_read["id"]),
        clean(model.name),
        prompt,
        output,
    )
    return _detail(connection, int(task["id"]))


def _prompt(
    task: dict,
    stored_read: sqlite3.Row,
    project: str,
    file_path: str,
    what_changed: str,
) -> str:
    goal = task["goal"] or ""
    criteria = [f"- {item['text']}" for item in task["criteria"]] or ["-"]
    return (
        f"Task: {task['title']}\n"
        f"Goal: {goal}\n"
        f"Criteria:\n"
        + "\n".join(criteria)
        + "\n"
        f"What changed: {what_changed}\n"
        f"File read: {stored_read['file_path']}\n"
        f"{stored_read['file_text']}\n"
        f"Project: {project}\n"
        f"File: {file_path}\n"
        "Return only the full text of the file.\n"
    )
