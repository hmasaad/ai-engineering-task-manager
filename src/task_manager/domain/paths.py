"""A schedule step follows one earlier step. The longest chain is the critical path."""

import sqlite3
from datetime import datetime, timedelta

from task_manager.clock import format_time
from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import path_store, task_store

NAME_STEP = "Name this step."
NAME_LENGTH = "Name a length of 1 or 2."
NAME_FOLLOWS = "Name the step that follows."
NAME_PREDECESSOR = "Name the step it follows."
NOT_ON_TASK = "That step is not on this task."
SELF_LINK = "A step cannot follow itself."
ALREADY_FOLLOWS = "That step already follows another step."
CYCLE = "Those steps would form a cycle."
NAME_DEADLINE = "Name a deadline."
NAME_FIRST = "Name a step first."
NOT_IN_PROGRESS = "The task must be In Progress."
_DEADLINE = "%Y-%m-%dT%H:%M:%SZ"


def name_step(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    length: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_STEP)
    if path_store.step_by_name(connection, int(task["id"]), kept) is not None:
        return _detail(connection, int(task["id"]))
    days = _length(length)
    if days is None:
        return bad_request(NAME_LENGTH)
    path_store.insert_step(connection, int(task["id"]), kept, days, occurred_at)
    return _detail(connection, int(task["id"]))


def add_dependency(
    connection: sqlite3.Connection,
    task_id: int,
    step: str | None,
    follows: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    follower = clean(step)
    if not follower:
        return bad_request(NAME_FOLLOWS)
    earlier = clean(follows)
    if not earlier:
        return bad_request(NAME_PREDECESSOR)
    task_key = int(task["id"])
    step_row = path_store.step_by_name(connection, task_key, follower)
    predecessor = path_store.step_by_name(connection, task_key, earlier)
    if step_row is None or predecessor is None:
        return conflict(NOT_ON_TASK)
    step_id = int(step_row["id"])
    predecessor_id = int(predecessor["id"])
    if step_id == predecessor_id:
        return conflict(SELF_LINK)
    existing = path_store.link_for_step(connection, step_id)
    if existing is not None:
        if int(existing["predecessor_id"]) == predecessor_id:
            return _detail(connection, task_key)
        return conflict(ALREADY_FOLLOWS)
    rows = path_store.steps(connection, task_key)
    if _would_cycle(rows, step_id, predecessor_id):
        return conflict(CYCLE)
    path_store.insert_link(connection, task_key, step_id, predecessor_id, occurred_at)
    return _detail(connection, task_key)


def set_deadline(
    connection: sqlite3.Connection,
    task_id: int,
    deadline: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    stored = _deadline(deadline)
    if stored is None:
        return bad_request(NAME_DEADLINE)
    task_key = int(task["id"])
    if not path_store.steps(connection, task_key):
        return conflict(NAME_FIRST)
    current = path_store.deadline_for(connection, task_key)
    if current is not None and current["deadline"] == stored:
        return _detail(connection, task_key)
    if current is None:
        path_store.insert_deadline(connection, task_key, stored, occurred_at)
    else:
        path_store.update_deadline(connection, task_key, stored, occurred_at)
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    rows = path_store.steps(connection, task_id)
    chains = _chains(rows)
    stored = path_store.deadline_for(connection, task_id)
    deadline = None if stored is None else stored["deadline"]
    latest = {} if deadline is None else _latests(chains, deadline)
    return {
        "steps": [
            {
                "name": row["name"],
                "length": int(row["length"]),
                "follows": row["follows"],
                "latest": latest.get(int(row["id"])),
            }
            for row in rows
        ],
        "critical": _critical(chains),
        "deadline": deadline,
        "can_name": in_progress,
        "can_link": in_progress and len(rows) >= 2,
        "can_deadline": in_progress and len(rows) >= 1,
    }


def _open(connection: sqlite3.Connection, task_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] != "In Progress":
        return conflict(NOT_IN_PROGRESS)
    return task


def _length(value: str | None) -> int | None:
    if value is None:
        return None
    kept = value.strip()
    if kept == "1":
        return 1
    if kept == "2":
        return 2
    return None


def _deadline(value: str | None) -> str | None:
    if value is None:
        return None
    kept = value.strip()
    try:
        datetime.strptime(kept, _DEADLINE)
    except ValueError:
        return None
    return kept


def _chains(rows: list[sqlite3.Row]) -> list[list[sqlite3.Row]]:
    by_id = {int(row["id"]): row for row in rows}
    predecessor: dict[int, int] = {}
    for row in rows:
        if row["predecessor_id"] is not None:
            predecessor[int(row["id"])] = int(row["predecessor_id"])
    followed = set(predecessor.values())
    chains = []
    for row in rows:
        if int(row["id"]) in followed:
            continue
        chain = []
        current: int | None = int(row["id"])
        seen: set[int] = set()
        while current is not None and current not in seen and current in by_id:
            seen.add(current)
            chain.append(by_id[current])
            current = predecessor.get(current)
        chain.reverse()
        chains.append(chain)
    return chains


def _critical(chains: list[list[sqlite3.Row]]) -> list[str]:
    chosen: list[sqlite3.Row] | None = None
    best_length = -1
    best_start = 0
    for chain in chains:
        total = sum(int(step["length"]) for step in chain)
        start = int(chain[0]["id"])
        if chosen is None or total > best_length or (total == best_length and start < best_start):
            chosen = chain
            best_length = total
            best_start = start
    if chosen is None:
        return []
    return [step["name"] for step in chosen]


def _latests(chains: list[list[sqlite3.Row]], deadline: str) -> dict[int, str]:
    moment = datetime.strptime(deadline, _DEADLINE)
    found: dict[int, str] = {}
    for chain in chains:
        after = 0
        for step in reversed(chain):
            found[int(step["id"])] = format_time(moment - timedelta(days=after))
            after += int(step["length"])
    return found


def _would_cycle(rows: list[sqlite3.Row], step_id: int, predecessor_id: int) -> bool:
    predecessor: dict[int, int] = {}
    for row in rows:
        if row["predecessor_id"] is not None:
            predecessor[int(row["id"])] = int(row["predecessor_id"])
    current: int | None = predecessor_id
    seen: set[int] = set()
    while current is not None and current not in seen:
        if current == step_id:
            return True
        seen.add(current)
        current = predecessor.get(current)
    return False
