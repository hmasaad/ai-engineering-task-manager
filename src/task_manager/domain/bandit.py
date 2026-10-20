"""Two actions learn a reward in each context. The stored choice follows that reward."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import bandit_store, task_store

NAME_ACTION = "Name this action."
FULL_ACTIONS = "This task already has 2 actions."
NAME_CONTEXT = "Name this context."
FULL_CONTEXTS = "This task already has 4 contexts."
NAME_TRIAL = "Name this trial."
NAME_TRIAL_CONTEXT = "Name the context."
NAME_TRIAL_ACTION = "Name the action."
NAME_REWARD = "Name a reward of 1 or 2."
NOT_CONTEXT = "That context is not on this task."
NOT_ACTION = "That action is not on this task."
FULL_TRIALS = "This task already has 4 trials."
NAME_ACTION_FIRST = "Name an action first."
NAME_CONTEXT_FIRST = "Name a context first."
NAME_CHOICE_CONTEXT = "Name the context to choose."
NOT_IN_PROGRESS = "The task must be In Progress."
_ACTION_LIMIT = 2
_LIMIT = 4


def name_action(
    connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_ACTION)
    task_key = int(task["id"])
    if bandit_store.action_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    if bandit_store.count_actions(connection, task_key) >= _ACTION_LIMIT:
        return conflict(FULL_ACTIONS)
    bandit_store.clear_choice(connection, task_key)
    bandit_store.insert_action(connection, task_key, kept, occurred_at)
    return _detail(connection, task_key)


def name_context(
    connection: sqlite3.Connection, task_id: int, name: str | None, occurred_at: str
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_CONTEXT)
    task_key = int(task["id"])
    if bandit_store.context_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    if bandit_store.count_contexts(connection, task_key) >= _LIMIT:
        return conflict(FULL_CONTEXTS)
    bandit_store.clear_choice(connection, task_key)
    bandit_store.insert_context(connection, task_key, kept, occurred_at)
    return _detail(connection, task_key)


def record_trial(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    context: str | None,
    action: str | None,
    reward: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_TRIAL)
    task_key = int(task["id"])
    if bandit_store.trial_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    context_name = clean(context)
    if not context_name:
        return bad_request(NAME_TRIAL_CONTEXT)
    action_name = clean(action)
    if not action_name:
        return bad_request(NAME_TRIAL_ACTION)
    points = _reward(reward)
    if points is None:
        return bad_request(NAME_REWARD)
    context_row = bandit_store.context_by_name(connection, task_key, context_name)
    if context_row is None:
        return conflict(NOT_CONTEXT)
    action_row = bandit_store.action_by_name(connection, task_key, action_name)
    if action_row is None:
        return conflict(NOT_ACTION)
    if bandit_store.count_trials(connection, task_key) >= _LIMIT:
        return conflict(FULL_TRIALS)
    bandit_store.clear_choice(connection, task_key)
    bandit_store.insert_trial(
        connection,
        task_key,
        kept,
        int(context_row["id"]),
        int(action_row["id"]),
        points,
        occurred_at,
    )
    return _detail(connection, task_key)


def choose_action(
    connection: sqlite3.Connection,
    task_id: int,
    context: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    roster = bandit_store.actions(connection, task_key)
    if not roster:
        return conflict(NAME_ACTION_FIRST)
    context_name = clean(context)
    if not context_name:
        return bad_request(NAME_CHOICE_CONTEXT)
    if bandit_store.count_contexts(connection, task_key) == 0:
        return conflict(NAME_CONTEXT_FIRST)
    context_row = bandit_store.context_by_name(connection, task_key, context_name)
    if context_row is None:
        return conflict(NOT_CONTEXT)
    context_id = int(context_row["id"])
    relevant = [
        row
        for row in bandit_store.trials(connection, task_key)
        if int(row["context_id"]) == context_id
    ]
    selected = _select(roster, relevant)
    bandit_store.clear_choice(connection, task_key)
    bandit_store.insert_choice(
        connection, task_key, context_id, int(selected["id"]), occurred_at
    )
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = bandit_store.actions(connection, task_id)
    situations = bandit_store.contexts(connection, task_id)
    recorded = bandit_store.trials(connection, task_id)
    stored = bandit_store.choice_for(connection, task_id)
    ready = in_progress and len(roster) >= 1 and len(situations) >= 1
    return {
        "actions": [{"name": row["name"]} for row in roster],
        "contexts": [{"name": row["name"]} for row in situations],
        "trials": [
            {
                "name": row["name"],
                "context": row["context"],
                "action": row["action"],
                "reward": int(row["reward"]),
            }
            for row in recorded
        ],
        "values": _values(recorded),
        "choice": None
        if stored is None
        else {"context": stored["context"], "action": stored["action"]},
        "can_name_action": in_progress,
        "can_name_context": in_progress,
        "can_try": ready,
        "can_choose": ready,
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


def _values(rows: list[sqlite3.Row]) -> list[dict[str, object]]:
    totals: dict[tuple[str, str], int] = {}
    counts: dict[tuple[str, str], int] = {}
    order: list[tuple[str, str]] = []
    for row in rows:
        key = (str(row["context"]), str(row["action"]))
        if key not in totals:
            order.append(key)
            totals[key] = 0
            counts[key] = 0
        totals[key] += int(row["reward"])
        counts[key] += 1
    return [
        {"context": context, "action": action, "total": totals[key], "count": counts[key]}
        for key in order
        for context, action in [key]
    ]


def _select(actions: list[sqlite3.Row], trials: list[sqlite3.Row]) -> sqlite3.Row:
    totals = {int(row["id"]): 0 for row in actions}
    counts = {int(row["id"]): 0 for row in actions}
    for row in trials:
        action_id = int(row["action_id"])
        totals[action_id] += int(row["reward"])
        counts[action_id] += 1
    untried = [row for row in actions if counts[int(row["id"])] == 0]
    if untried:
        return untried[0]
    best = actions[0]
    best_id = int(best["id"])
    for row in actions[1:]:
        candidate_id = int(row["id"])
        if totals[candidate_id] * counts[best_id] > totals[best_id] * counts[candidate_id]:
            best = row
            best_id = candidate_id
    return best
