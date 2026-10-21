"""A linear score uses each mark. A neural score also adds the pair when both marks are on."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import linear_bandit_store, task_store

NAME_ARM = "Name this arm."
FULL_ARMS = "This task already has 2 arms."
NAME_CONTEXT = "Name this context."
NAME_MARK = "Name a mark of 0 or 1."
FULL_CONTEXTS = "This task already has 2 contexts."
NAME_PULL = "Name this pull."
NAME_PULL_CONTEXT = "Name the context."
NAME_PULL_ARM = "Name the arm."
NAME_REWARD = "Name a reward of 1 or 2."
CONTEXT_MISSING = "That context is not on this task."
ARM_MISSING = "That arm is not on this task."
FULL_PULLS = "This task already has 4 pulls."
NAME_ARM_FIRST = "Name an arm first."
NAME_CHOOSE_CONTEXT = "Name the context to choose."
NAME_CONTEXT_FIRST = "Name a context first."
NAME_MODEL = "Name the model."
NAME_MODEL_KIND = "Name a linear or neural model."
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
    if linear_bandit_store.arm_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    if linear_bandit_store.count_arms(connection, task_key) >= _ARM_LIMIT:
        return conflict(FULL_ARMS)
    linear_bandit_store.clear_choice(connection, task_key)
    linear_bandit_store.insert_arm(connection, task_key, kept, occurred_at)
    return _detail(connection, task_key)


def name_context(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    first: str | None,
    second: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_CONTEXT)
    task_key = int(task["id"])
    if linear_bandit_store.context_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    first_mark = _mark(first)
    if first_mark is None:
        return bad_request(NAME_MARK)
    second_mark = _mark(second)
    if second_mark is None:
        return bad_request(NAME_MARK)
    if linear_bandit_store.count_contexts(connection, task_key) >= _CONTEXT_LIMIT:
        return conflict(FULL_CONTEXTS)
    linear_bandit_store.clear_choice(connection, task_key)
    linear_bandit_store.insert_context(
        connection, task_key, kept, first_mark, second_mark, occurred_at
    )
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
    if linear_bandit_store.pull_by_name(connection, task_key, kept) is not None:
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
    context_row = linear_bandit_store.context_by_name(connection, task_key, context_name)
    if context_row is None:
        return conflict(CONTEXT_MISSING)
    arm_row = linear_bandit_store.arm_by_name(connection, task_key, arm_name)
    if arm_row is None:
        return conflict(ARM_MISSING)
    if linear_bandit_store.count_pulls(connection, task_key) >= _PULL_LIMIT:
        return conflict(FULL_PULLS)
    linear_bandit_store.clear_choice(connection, task_key)
    linear_bandit_store.insert_pull(
        connection,
        task_key,
        kept,
        int(context_row["id"]),
        int(arm_row["id"]),
        points,
        occurred_at,
    )
    return _detail(connection, task_key)


def choose(
    connection: sqlite3.Connection,
    task_id: int,
    context: str | None,
    model: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    roster = linear_bandit_store.arms(connection, task_key)
    if not roster:
        return conflict(NAME_ARM_FIRST)
    context_name = clean(context)
    if not context_name:
        return bad_request(NAME_CHOOSE_CONTEXT)
    situations = linear_bandit_store.contexts(connection, task_key)
    if not situations:
        return conflict(NAME_CONTEXT_FIRST)
    marks = {
        str(row["name"]): (int(row["first_mark"]), int(row["second_mark"]))
        for row in situations
    }
    if context_name not in marks:
        return conflict(CONTEXT_MISSING)
    kind = _model(model)
    if kind is None:
        if model is None or not model.strip():
            return bad_request(NAME_MODEL)
        return bad_request(NAME_MODEL_KIND)
    recorded = linear_bandit_store.pulls(connection, task_key)
    chosen = _choose(roster, recorded, marks, context_name, kind)
    linear_bandit_store.clear_choice(connection, task_key)
    linear_bandit_store.insert_choice(
        connection, task_key, context_name, kind, chosen, occurred_at
    )
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = linear_bandit_store.arms(connection, task_id)
    situations = linear_bandit_store.contexts(connection, task_id)
    recorded = linear_bandit_store.pulls(connection, task_id)
    stored = linear_bandit_store.choice_for(connection, task_id)
    ready = in_progress and len(roster) >= 1 and len(situations) >= 1
    return {
        "arms": [{"name": row["name"]} for row in roster],
        "contexts": [
            {
                "name": row["name"],
                "first": int(row["first_mark"]),
                "second": int(row["second_mark"]),
            }
            for row in situations
        ],
        "pulls": [
            {
                "name": row["name"],
                "context": row["context"],
                "arm": row["arm"],
                "reward": int(row["reward"]),
            }
            for row in recorded
        ],
        "choice": None
        if stored is None
        else {
            "context": stored["context"],
            "model": stored["model"],
            "arm": stored["arm"],
        },
        "can_name": in_progress,
        "can_context": in_progress,
        "can_pull": ready,
        "can_choose": ready,
    }


def _open(connection: sqlite3.Connection, task_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] != "In Progress":
        return conflict(NOT_IN_PROGRESS)
    return task


def _mark(value: str | None) -> int | None:
    if value is None:
        return None
    kept = value.strip()
    if kept == "0":
        return 0
    if kept == "1":
        return 1
    return None


def _reward(value: str | None) -> int | None:
    if value is None:
        return None
    kept = value.strip()
    if kept == "1":
        return 1
    if kept == "2":
        return 2
    return None


def _model(value: str | None) -> str | None:
    if value is None:
        return None
    kept = value.strip()
    if kept in {"linear", "neural"}:
        return kept
    return None


def _choose(
    roster: list[sqlite3.Row],
    recorded: list[sqlite3.Row],
    marks: dict[str, tuple[int, int]],
    context: str,
    model: str,
) -> str:
    chosen = ""
    best = 0
    context_marks = marks[context]
    for row in roster:
        score = _score(recorded, marks, str(row["name"]), context_marks, model)
        if chosen == "" or score > best:
            chosen = str(row["name"])
            best = score
    return chosen


def _score(
    recorded: list[sqlite3.Row],
    marks: dict[str, tuple[int, int]],
    arm: str,
    context_marks: tuple[int, int],
    model: str,
) -> int:
    first = 0
    second = 0
    pair = 0
    for row in recorded:
        if str(row["arm"]) != arm:
            continue
        pull_marks = marks[str(row["context"])]
        reward = int(row["reward"])
        if pull_marks[0] == 1:
            first += reward
        if pull_marks[1] == 1:
            second += reward
        if pull_marks[0] == 1 and pull_marks[1] == 1:
            pair += reward
    linear = first * context_marks[0] + second * context_marks[1]
    if model == "neural" and context_marks[0] == 1 and context_marks[1] == 1:
        return linear + pair
    return linear
