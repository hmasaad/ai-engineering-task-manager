"""A draw chooses the arm with the higher middle, high, or low score in one context."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import exploration_store, task_store

NAME_ARM = "Name this arm."
FULL_ARMS = "This task already has 2 arms."
NAME_CONTEXT = "Name this context."
FULL_CONTEXTS = "This task already has 2 contexts."
NAME_PULL = "Name this pull."
NAME_PULL_CONTEXT = "Name the context."
NAME_PULL_ARM = "Name the arm."
NAME_REWARD = "Name a reward of 1 or 2."
CONTEXT_MISSING = "That context is not on this task."
ARM_MISSING = "That arm is not on this task."
FULL_PULLS = "This task already has 4 pulls."
NAME_ARM_FIRST = "Name an arm first."
NAME_DRAW_CONTEXT = "Name the context to draw."
NAME_CONTEXT_FIRST = "Name a context first."
NOT_IN_PROGRESS = "The task must be In Progress."
_ARM_LIMIT = 2
_CONTEXT_LIMIT = 2
_PULL_LIMIT = 4


def name_arm(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_ARM)
    task_key = int(task["id"])
    if exploration_store.arm_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    if exploration_store.count_arms(connection, task_key) >= _ARM_LIMIT:
        return conflict(FULL_ARMS)
    exploration_store.clear_draw(connection, task_key)
    exploration_store.insert_arm(connection, task_key, kept, occurred_at)
    return _detail(connection, task_key)


def name_context(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_CONTEXT)
    task_key = int(task["id"])
    if exploration_store.context_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    if exploration_store.count_contexts(connection, task_key) >= _CONTEXT_LIMIT:
        return conflict(FULL_CONTEXTS)
    exploration_store.clear_draw(connection, task_key)
    exploration_store.insert_context(connection, task_key, kept, occurred_at)
    return _detail(connection, task_key)


def record_pull(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    context: str | None,
    arm: str | None,
    reward: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_PULL)
    task_key = int(task["id"])
    if exploration_store.pull_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    context_name = clean(context)
    if not context_name:
        return bad_request(NAME_PULL_CONTEXT)
    arm_name = clean(arm)
    if not arm_name:
        return bad_request(NAME_PULL_ARM)
    points = _reward(reward)
    if points is None:
        return bad_request(NAME_REWARD)
    context_row = exploration_store.context_by_name(connection, task_key, context_name)
    if context_row is None:
        return conflict(CONTEXT_MISSING)
    arm_row = exploration_store.arm_by_name(connection, task_key, arm_name)
    if arm_row is None:
        return conflict(ARM_MISSING)
    if exploration_store.count_pulls(connection, task_key) >= _PULL_LIMIT:
        return conflict(FULL_PULLS)
    exploration_store.clear_draw(connection, task_key)
    exploration_store.insert_pull(
        connection,
        task_key,
        kept,
        int(context_row["id"]),
        int(arm_row["id"]),
        points,
        occurred_at,
    )
    return _detail(connection, task_key)


def draw_arm(
    connection: sqlite3.Connection,
    task_id: int,
    context: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    roster = exploration_store.arms(connection, task_key)
    if not roster:
        return conflict(NAME_ARM_FIRST)
    context_name = clean(context)
    if not context_name:
        return bad_request(NAME_DRAW_CONTEXT)
    if exploration_store.count_contexts(connection, task_key) == 0:
        return conflict(NAME_CONTEXT_FIRST)
    if exploration_store.context_by_name(connection, task_key, context_name) is None:
        return conflict(CONTEXT_MISSING)
    stored = exploration_store.draw_for(connection, task_key)
    step = 1 if stored is None else int(stored["step"]) + 1
    sample = _sample(step)
    recorded = exploration_store.pulls(connection, task_key)
    chosen = _choose(roster, recorded, context_name, sample)
    exploration_store.clear_draw(connection, task_key)
    exploration_store.insert_draw(
        connection, task_key, context_name, chosen, sample, step, occurred_at
    )
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = exploration_store.arms(connection, task_id)
    situations = exploration_store.contexts(connection, task_id)
    recorded = exploration_store.pulls(connection, task_id)
    stored = exploration_store.draw_for(connection, task_id)
    ready = in_progress and len(roster) >= 1 and len(situations) >= 1
    return {
        "arms": [{"name": row["name"]} for row in roster],
        "contexts": [{"name": row["name"]} for row in situations],
        "pulls": [
            {
                "name": row["name"],
                "context": row["context"],
                "arm": row["arm"],
                "reward": int(row["reward"]),
            }
            for row in recorded
        ],
        "draw": None
        if stored is None
        else {
            "context": stored["context"],
            "arm": stored["arm"],
            "sample": stored["sample"],
        },
        "can_name": in_progress,
        "can_context": in_progress,
        "can_pull": ready,
        "can_draw": ready,
    }


def _open(connection: sqlite3.Connection, task_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] != "In Progress":
        return conflict(NOT_IN_PROGRESS)
    return task


def _reward(value: str | None) -> int | None:
    if value is None:
        return None
    kept = value.strip()
    if kept == "1":
        return 1
    if kept == "2":
        return 2
    return None


def _sample(step: int) -> str:
    kind = step % 3
    if kind == 1:
        return "middle"
    if kind == 2:
        return "high"
    return "low"


def _choose(
    roster: list[sqlite3.Row],
    recorded: list[sqlite3.Row],
    context: str,
    sample: str,
) -> str:
    chosen = ""
    best = 0
    for row in roster:
        score = _score(recorded, context, str(row["name"]), sample)
        if chosen == "" or score > best:
            chosen = str(row["name"])
            best = score
    return chosen


def _score(
    recorded: list[sqlite3.Row], context: str, arm: str, sample: str
) -> int:
    wins = 0
    losses = 0
    for row in recorded:
        if str(row["context"]) != context or str(row["arm"]) != arm:
            continue
        if int(row["reward"]) == 2:
            wins += 1
        else:
            losses += 1
    middle = (wins + 1) * 2 - (losses + 1)
    if sample == "middle":
        return middle
    if sample == "low":
        return middle - 1
    pulls = wins + losses
    if pulls == 0:
        extra = 4
    elif pulls == 1:
        extra = 1
    else:
        extra = 0
    return middle + extra
