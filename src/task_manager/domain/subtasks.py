"""Subtask links and the rule that a parent cannot finish before its children."""

import sqlite3

from task_manager.domain.capture import CANCELLED, _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import task_store
from task_manager.storage.subtask_store import ancestor_ids, descendant_ids, link_parent


def add_subtask(
    connection: sqlite3.Connection,
    parent_id: int,
    title: str,
    occurred_at: str,
):
    parent = task_store.row_task(connection, parent_id)
    if parent is None:
        return missing("Task not found.")
    if parent["status"] == "Cancelled":
        return conflict(CANCELLED)
    if parent["status"] == "Completed":
        return conflict("Reopen the parent before adding a subtask.")
    cleaned = clean(title)
    if not cleaned:
        return bad_request("A title is required.")
    child_id = task_store.insert_task(connection, cleaned, occurred_at, parent_id)
    return _detail(connection, child_id)


def attach(connection: sqlite3.Connection, child_id: int, parent_id: int):
    """Attach an existing task under a parent. Refuses a second parent or a cycle.

    The HTTP API does not expose this. New subtasks are created with add_subtask.
    """
    child = task_store.row_task(connection, child_id)
    parent = task_store.row_task(connection, parent_id)
    if child is None or parent is None:
        return missing("Task not found.")
    if child_id == parent_id or child_id in ancestor_ids(connection, parent_id):
        return conflict("A task cannot contain its own ancestor.")
    if parent_id in descendant_ids(connection, child_id):
        return conflict("A task cannot contain its own ancestor.")
    if child["parent_id"] is not None:
        return conflict("A task cannot have more than one parent.")
    if parent["status"] == "Cancelled":
        return conflict(CANCELLED)
    if parent["status"] == "Completed":
        return conflict("Reopen the parent before adding a subtask.")
    link_parent(connection, child_id, parent_id)
    return _detail(connection, child_id)
