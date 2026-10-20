"""A probe is allowed only for a safe action. The effect compares two actions in one state."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import safety_store, task_store

NAME_ACTION = "Name this action."
NAME_RISK = "Name a risk of 1 or 2."
FULL_ACTIONS = "This task already has 2 actions."
NAME_PROBE = "Name this probe."
NAME_STATE = "Name the state."
NAME_PROBE_ACTION = "Name the action."
NAME_REWARD = "Name a reward of 1 or 2."
NOT_ON_TASK = "That action is not on this task."
NOT_SAFE = "That action is not safe to explore."
FULL_PROBES = "This task already has 4 probes."
NAME_PROBE_FIRST = "Name a probe first."
NAME_COMPARE_STATE = "Name the state to compare."
NAME_COMPARE_ACTION = "Name the action."
NAME_INSTEAD = "Name the action it replaces."
SELF_COMPARE = "An action cannot replace itself."
NEED_BOTH = "That comparison needs both actions in this state."
NOT_IN_PROGRESS = "The task must be In Progress."
_ACTION_LIMIT = 2
_PROBE_LIMIT = 4


def name_action(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    risk: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_ACTION)
    task_key = int(task["id"])
    if safety_store.action_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    level = _choice(risk)
    if level is None:
        return bad_request(NAME_RISK)
    if safety_store.count_actions(connection, task_key) >= _ACTION_LIMIT:
        return conflict(FULL_ACTIONS)
    safety_store.clear_effect(connection, task_key)
    safety_store.insert_action(connection, task_key, kept, level, occurred_at)
    return _detail(connection, task_key)


def record_probe(
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
        return bad_request(NAME_PROBE)
    task_key = int(task["id"])
    if safety_store.probe_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    state_name = clean(state)
    if not state_name:
        return bad_request(NAME_STATE)
    action_name = clean(action)
    if not action_name:
        return bad_request(NAME_PROBE_ACTION)
    points = _choice(reward)
    if points is None:
        return bad_request(NAME_REWARD)
    action_row = safety_store.action_by_name(connection, task_key, action_name)
    if action_row is None:
        return conflict(NOT_ON_TASK)
    if int(action_row["risk"]) != 1:
        return conflict(NOT_SAFE)
    if safety_store.count_probes(connection, task_key) >= _PROBE_LIMIT:
        return conflict(FULL_PROBES)
    safety_store.clear_effect(connection, task_key)
    safety_store.insert_probe(
        connection,
        task_key,
        kept,
        state_name,
        int(action_row["id"]),
        points,
        occurred_at,
    )
    return _detail(connection, task_key)


def compare_actions(
    connection: sqlite3.Connection,
    task_id: int,
    state: str | None,
    action: str | None,
    instead: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    recorded = safety_store.probes(connection, task_key)
    if not recorded:
        return conflict(NAME_PROBE_FIRST)
    state_name = clean(state)
    if not state_name:
        return bad_request(NAME_COMPARE_STATE)
    action_name = clean(action)
    if not action_name:
        return bad_request(NAME_COMPARE_ACTION)
    instead_name = clean(instead)
    if not instead_name:
        return bad_request(NAME_INSTEAD)
    if action_name == instead_name:
        return conflict(SELF_COMPARE)
    action_reward = _earliest(recorded, state_name, action_name)
    instead_reward = _earliest(recorded, state_name, instead_name)
    if action_reward is None or instead_reward is None:
        return conflict(NEED_BOTH)
    safety_store.clear_effect(connection, task_key)
    safety_store.insert_effect(
        connection,
        task_key,
        state_name,
        action_name,
        instead_name,
        action_reward - instead_reward,
        occurred_at,
    )
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = safety_store.actions(connection, task_id)
    recorded = safety_store.probes(connection, task_id)
    stored = safety_store.effect_for(connection, task_id)
    safe = any(int(row["risk"]) == 1 for row in roster)
    return {
        "actions": [{"name": row["name"], "risk": int(row["risk"])} for row in roster],
        "probes": [
            {
                "name": row["name"],
                "state": row["state"],
                "action": row["action"],
                "reward": int(row["reward"]),
            }
            for row in recorded
        ],
        "effect": None
        if stored is None
        else {
            "state": stored["state"],
            "action": stored["action"],
            "instead": stored["instead"],
            "effect": int(stored["effect"]),
        },
        "can_name": in_progress,
        "can_probe": in_progress and safe,
        "can_compare": in_progress and len(recorded) >= 2,
    }


def _open(connection: sqlite3.Connection, task_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] != "In Progress":
        return conflict(NOT_IN_PROGRESS)
    return task


def _choice(value: str | None) -> int | None:
    if value is None:
        return None
    kept = value.strip()
    if kept == "1":
        return 1
    if kept == "2":
        return 2
    return None


def _earliest(rows: list[sqlite3.Row], state: str, action: str) -> int | None:
    for row in rows:
        if str(row["state"]) == state and str(row["action"]) == action:
            return int(row["reward"])
    return None
