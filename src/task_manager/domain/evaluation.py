"""A fixed log scores one action for each state. The score counts only the matches."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import evaluation_store, task_store

NAME_STEP = "Name this step."
NAME_STATE = "Name the state."
NAME_ACTION = "Name the action."
NAME_REWARD = "Name a reward of 1 or 2."
FULL_LOGS = "This task already has 4 logged steps."
NAME_RULE_STATE = "Name the state for this rule."
NAME_RULE_ACTION = "Name the action for this rule."
NAME_LOG_FIRST = "Name a logged step first."
NOT_IN_LOG = "That state is not in the log."
NAME_RULE_FIRST = "Name a policy rule first."
NO_MATCH = "No logged step matches this policy."
NOT_IN_PROGRESS = "The task must be In Progress."
_LIMIT = 4


def record_log(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    state: str | None,
    action: str | None,
    reward: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_STEP)
    task_key = int(task["id"])
    if evaluation_store.log_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    state_name = clean(state)
    if not state_name:
        return bad_request(NAME_STATE)
    action_name = clean(action)
    if not action_name:
        return bad_request(NAME_ACTION)
    points = _reward(reward)
    if points is None:
        return bad_request(NAME_REWARD)
    if evaluation_store.count_logs(connection, task_key) >= _LIMIT:
        return conflict(FULL_LOGS)
    evaluation_store.clear_score(connection, task_key)
    evaluation_store.insert_log(
        connection, task_key, kept, state_name, action_name, points, occurred_at
    )
    return _detail(connection, task_key)


def name_rule(
    connection: sqlite3.Connection,
    task_id: int,
    state: str | None,
    action: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    state_name = clean(state)
    if not state_name:
        return bad_request(NAME_RULE_STATE)
    action_name = clean(action)
    if not action_name:
        return bad_request(NAME_RULE_ACTION)
    task_key = int(task["id"])
    if evaluation_store.count_logs(connection, task_key) == 0:
        return conflict(NAME_LOG_FIRST)
    if not evaluation_store.state_in_log(connection, task_key, state_name):
        return conflict(NOT_IN_LOG)
    current = evaluation_store.rule_for_state(connection, task_key, state_name)
    if current is not None and str(current["action"]) == action_name:
        return _detail(connection, task_key)
    evaluation_store.clear_score(connection, task_key)
    if current is None:
        evaluation_store.insert_rule(connection, task_key, state_name, action_name, occurred_at)
    else:
        evaluation_store.update_rule(connection, task_key, state_name, action_name, occurred_at)
    return _detail(connection, task_key)


def evaluate(connection: sqlite3.Connection, task_id: int, occurred_at: str):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    recorded = evaluation_store.logs(connection, task_key)
    if not recorded:
        return conflict(NAME_LOG_FIRST)
    stated = evaluation_store.rules(connection, task_key)
    if not stated:
        return conflict(NAME_RULE_FIRST)
    total, count = _score(recorded, stated)
    if count == 0:
        return conflict(NO_MATCH)
    evaluation_store.clear_score(connection, task_key)
    evaluation_store.insert_score(connection, task_key, total, count, occurred_at)
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    recorded = evaluation_store.logs(connection, task_id)
    stated = evaluation_store.rules(connection, task_id)
    stored = evaluation_store.score_for(connection, task_id)
    return {
        "logs": [
            {
                "name": row["name"],
                "state": row["state"],
                "action": row["action"],
                "reward": int(row["reward"]),
            }
            for row in recorded
        ],
        "rules": [{"state": row["state"], "action": row["action"]} for row in stated],
        "score": None
        if stored is None
        else {"total": int(stored["total"]), "count": int(stored["count"])},
        "can_log": in_progress,
        "can_rule": in_progress and len(recorded) >= 1,
        "can_evaluate": in_progress and len(stated) >= 1,
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


def _score(logs: list[sqlite3.Row], rules: list[sqlite3.Row]) -> tuple[int, int]:
    chosen = {str(row["state"]): str(row["action"]) for row in rules}
    total = 0
    count = 0
    for row in logs:
        action = chosen.get(str(row["state"]))
        if action is None or action != str(row["action"]):
            continue
        total += int(row["reward"])
        count += 1
    return total, count
