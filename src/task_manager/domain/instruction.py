"""Save the model and start one task from the instruction page."""

import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from task_manager.domain import capture, file_read, model_file, status
from task_manager.domain.file_read import NAME_FILE as NAME_READ
from task_manager.domain.implementation import (
    CHOOSE_CLASS,
    NAME_FILE,
    NAME_PROJECT,
    PROJECT_MUST_EXIST,
    WHAT_CHANGED_REQUIRED,
    _CLASSES,
    _project_dir,
)
from task_manager.domain.model_file import CHOOSE_MODEL
from task_manager.domain.results import Refusal, bad_request
from task_manager.domain.text import clean
from task_manager.storage import model_config_store

NAME_SERVICE = "Name the model service."
TITLE_REQUIRED = "A title is required."
GOAL_REQUIRED = "A goal is required."
CRITERION_REQUIRED = "An acceptance criterion is required."


def save_model(
    connection: sqlite3.Connection,
    name: str | None,
    base_url: str | None,
    api_key: str | None = None,
):
    kept_name = clean(name)
    if not kept_name:
        return bad_request(CHOOSE_MODEL)
    kept_url = _service_address(base_url)
    if kept_url is None:
        return bad_request(NAME_SERVICE)
    kept_key = None if api_key is None or not api_key.strip() else api_key.strip()
    model_config_store.replace_service(connection, kept_name, kept_url, kept_key)
    return {"name": kept_name, "base_url": kept_url, "api_key": kept_key}


def _service_address(value: str | None) -> str | None:
    kept = clean(value)
    if not kept:
        return None
    parsed = urlparse(kept)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return kept


def start_work(
    connection: sqlite3.Connection,
    title: str | None,
    goal: str | None,
    criterion: str | None,
    project: str | None,
    read_path: str | None,
    file_path: str | None,
    change_class: str | None,
    what_changed: str | None,
    occurred_at: str,
    project_root: Path,
    model,
):
    kept_title = clean(title)
    if not kept_title:
        return bad_request(TITLE_REQUIRED)
    kept_goal = clean(goal)
    if not kept_goal:
        return bad_request(GOAL_REQUIRED)
    kept_criterion = clean(criterion)
    if not kept_criterion:
        return bad_request(CRITERION_REQUIRED)
    kept_project = clean(project)
    if not kept_project:
        return bad_request(NAME_PROJECT)
    if not _project_dir(kept_project, project_root).is_dir():
        return bad_request(PROJECT_MUST_EXIST)
    kept_read = clean(read_path)
    if not kept_read:
        return bad_request(NAME_READ)
    kept_file = clean(file_path)
    if not kept_file:
        return bad_request(NAME_FILE)
    kept_class = clean(change_class)
    if kept_class not in _CLASSES:
        return bad_request(CHOOSE_CLASS)
    kept_what = clean(what_changed)
    if not kept_what:
        return bad_request(WHAT_CHANGED_REQUIRED)
    if model is None or not clean(getattr(model, "name", None)):
        return bad_request(CHOOSE_MODEL)
    created = capture.create_task(connection, kept_title, occurred_at)
    if isinstance(created, Refusal):
        return created
    task_id = int(created["id"])
    prepared = (
        capture.set_goal(connection, task_id, kept_goal, occurred_at),
        capture.add_criterion(connection, task_id, kept_criterion),
        status.transition(connection, task_id, "mark_ready", None, occurred_at),
        status.transition(connection, task_id, "start", None, occurred_at),
    )
    for result in prepared:
        if isinstance(result, Refusal):
            return result
    read = file_read.read_file(
        connection, task_id, kept_project, kept_read, occurred_at, project_root
    )
    if isinstance(read, Refusal):
        return read
    read_id = int(read["file_reads"][-1]["id"])
    return model_file.record_model_file(
        connection,
        task_id,
        kept_project,
        kept_class,
        kept_what,
        False,
        kept_file,
        read_id,
        occurred_at,
        project_root,
        model,
    )
