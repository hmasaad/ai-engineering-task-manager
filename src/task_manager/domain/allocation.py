"""The workflow budget of 4 units follows each agent's yield."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import allocation_store, task_store

NAME_AGENT = "Name this agent."
FULL_AGENTS = "This task already has 4 agents."
NAME_YIELD = "Name this yield."
NAME_YIELD_AGENT = "Name the agent."
NAME_VALUE = "Name a yield of 1 or 2."
AGENT_MISSING = "That agent is not on this task."
ALREADY_YIELDED = "That agent already has a yield."
FULL_YIELDS = "This task already has 4 yields."
NAME_AGENT_FIRST = "Name an agent first."
NAME_EVERY_YIELD = "Record a yield for every agent first."
NOT_IN_PROGRESS = "The task must be In Progress."
_AGENT_LIMIT = 4
_YIELD_LIMIT = 4
_POOL = 4


def name_agent(
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
        return bad_request(NAME_AGENT)
    task_key = int(task["id"])
    if allocation_store.agent_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    if allocation_store.count_agents(connection, task_key) >= _AGENT_LIMIT:
        return conflict(FULL_AGENTS)
    allocation_store.clear_shares(connection, task_key)
    allocation_store.insert_agent(connection, task_key, kept, occurred_at)
    return _detail(connection, task_key)


def record_yield(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    agent: str | None,
    amount: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_YIELD)
    task_key = int(task["id"])
    if allocation_store.yield_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    agent_name = clean(agent)
    if not agent_name:
        return bad_request(NAME_YIELD_AGENT)
    value = _level(amount)
    if value is None:
        return bad_request(NAME_VALUE)
    agent_row = allocation_store.agent_by_name(connection, task_key, agent_name)
    if agent_row is None:
        return conflict(AGENT_MISSING)
    if allocation_store.count_yields(connection, task_key) >= _YIELD_LIMIT:
        return conflict(FULL_YIELDS)
    agent_key = int(agent_row["id"])
    if allocation_store.yield_for_agent(connection, task_key, agent_key) is not None:
        return conflict(ALREADY_YIELDED)
    allocation_store.clear_shares(connection, task_key)
    allocation_store.insert_yield(
        connection, task_key, kept, agent_key, value, occurred_at
    )
    return _detail(connection, task_key)


def allocate(connection: sqlite3.Connection, task_id: int, occurred_at: str):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    roster = allocation_store.agents(connection, task_key)
    if not roster:
        return conflict(NAME_AGENT_FIRST)
    recorded = allocation_store.yields(connection, task_key)
    amounts = {int(row["agent_id"]): int(row["value"]) for row in recorded}
    if any(int(row["id"]) not in amounts for row in roster):
        return conflict(NAME_EVERY_YIELD)
    shares = _shares(roster, amounts)
    allocation_store.clear_shares(connection, task_key)
    for position, (agent_name, units) in enumerate(shares, start=1):
        allocation_store.insert_share(
            connection, task_key, agent_name, units, position, occurred_at
        )
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = allocation_store.agents(connection, task_id)
    recorded = allocation_store.yields(connection, task_id)
    shares = allocation_store.shares_for(connection, task_id)
    return {
        "agents": [{"name": row["name"]} for row in roster],
        "yields": [
            {"name": row["name"], "agent": row["agent"], "value": int(row["value"])}
            for row in recorded
        ],
        "shares": [
            {"agent": row["agent"], "units": int(row["units"])} for row in shares
        ],
        "can_name": in_progress,
        "can_record": in_progress and len(roster) >= 1,
        "can_allocate": in_progress and len(recorded) >= 1,
    }


def _open(connection: sqlite3.Connection, task_id: int):
    task = task_store.row_task(connection, task_id)
    if task is None:
        return missing("Task not found.")
    if task["status"] != "In Progress":
        return conflict(NOT_IN_PROGRESS)
    return task


def _level(value: str | None) -> int | None:
    if value is None:
        return None
    kept = value.strip()
    if kept == "1":
        return 1
    if kept == "2":
        return 2
    return None


def _shares(
    roster: list[sqlite3.Row], amounts: dict[int, int]
) -> list[tuple[str, int]]:
    assigned = {int(row["id"]): 0 for row in roster}
    order = [int(row["id"]) for row in roster]
    names = {int(row["id"]): str(row["name"]) for row in roster}
    for _ in range(_POOL):
        chosen = order[0]
        for candidate in order[1:]:
            if _beats(candidate, chosen, amounts, assigned):
                chosen = candidate
        assigned[chosen] += 1
    return [(names[agent_id], assigned[agent_id]) for agent_id in order]


def _beats(
    candidate: int, current: int, amounts: dict[int, int], assigned: dict[int, int]
) -> bool:
    left = amounts[candidate] * (assigned[current] + 1)
    right = amounts[current] * (assigned[candidate] + 1)
    if left != right:
        return left > right
    return candidate < current
