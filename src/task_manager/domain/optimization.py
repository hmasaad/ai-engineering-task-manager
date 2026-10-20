"""Activities obey precedence and a capacity. The stored plan finishes as early as possible."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import optimization_store, task_store

NAME_ACTIVITY = "Name this activity."
NAME_LENGTH = "Name a length of 1 or 2."
FULL = "This schedule already has 4 activities."
NAME_LATER = "Name the activity."
NAME_EARLIER = "Name the earlier activity."
NOT_ON_TASK = "That activity is not on this task."
SELF_LINK = "An activity cannot follow itself."
CYCLE = "Those activities would form a cycle."
NAME_CAPACITY = "Name a capacity of 1 or 2."
NAME_FIRST = "Name an activity first."
NAME_CAPACITY_FIRST = "Name a capacity first."
NOT_IN_PROGRESS = "The task must be In Progress."
_LIMIT = 4


def name_activity(
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
        return bad_request(NAME_ACTIVITY)
    task_key = int(task["id"])
    if optimization_store.activity_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    days = _choice(length)
    if days is None:
        return bad_request(NAME_LENGTH)
    if optimization_store.count_activities(connection, task_key) >= _LIMIT:
        return conflict(FULL)
    optimization_store.clear_plan(connection, task_key)
    optimization_store.insert_activity(connection, task_key, kept, days, occurred_at)
    return _detail(connection, task_key)


def add_constraint(
    connection: sqlite3.Connection,
    task_id: int,
    activity: str | None,
    after: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    later = clean(activity)
    if not later:
        return bad_request(NAME_LATER)
    earlier = clean(after)
    if not earlier:
        return bad_request(NAME_EARLIER)
    task_key = int(task["id"])
    activity_row = optimization_store.activity_by_name(connection, task_key, later)
    after_row = optimization_store.activity_by_name(connection, task_key, earlier)
    if activity_row is None or after_row is None:
        return conflict(NOT_ON_TASK)
    activity_id = int(activity_row["id"])
    after_id = int(after_row["id"])
    if activity_id == after_id:
        return conflict(SELF_LINK)
    if optimization_store.constraint_pair(connection, activity_id, after_id) is not None:
        return _detail(connection, task_key)
    rows = optimization_store.constraints(connection, task_key)
    if _would_cycle(rows, activity_id, after_id):
        return conflict(CYCLE)
    optimization_store.clear_plan(connection, task_key)
    optimization_store.insert_constraint(
        connection, task_key, activity_id, after_id, occurred_at
    )
    return _detail(connection, task_key)


def set_capacity(
    connection: sqlite3.Connection,
    task_id: int,
    capacity: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = _choice(capacity)
    if kept is None:
        return bad_request(NAME_CAPACITY)
    task_key = int(task["id"])
    if optimization_store.count_activities(connection, task_key) == 0:
        return conflict(NAME_FIRST)
    current = optimization_store.capacity_for(connection, task_key)
    if current is not None and int(current["capacity"]) == kept:
        return _detail(connection, task_key)
    if current is None:
        optimization_store.insert_capacity(connection, task_key, kept, occurred_at)
    else:
        optimization_store.update_capacity(connection, task_key, kept, occurred_at)
        optimization_store.clear_plan(connection, task_key)
    return _detail(connection, task_key)


def optimize_schedule(connection: sqlite3.Connection, task_id: int, occurred_at: str):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    roster = optimization_store.activities(connection, task_key)
    if not roster:
        return conflict(NAME_FIRST)
    current = optimization_store.capacity_for(connection, task_key)
    if current is None:
        return conflict(NAME_CAPACITY_FIRST)
    starts, finish = _schedule(
        roster, optimization_store.constraints(connection, task_key), int(current["capacity"])
    )
    optimization_store.clear_plan(connection, task_key)
    plan_id = optimization_store.insert_plan(connection, task_key, finish, occurred_at)
    for activity_id, start in starts.items():
        optimization_store.insert_placement(connection, plan_id, activity_id, start)
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = optimization_store.activities(connection, task_id)
    current = optimization_store.capacity_for(connection, task_id)
    stored = optimization_store.plan_for(connection, task_id)
    return {
        "activities": [
            {
                "name": row["name"],
                "length": int(row["length"]),
                "start": None if row["start"] is None else int(row["start"]),
            }
            for row in roster
        ],
        "constraints": [
            {"activity": row["activity"], "after": row["after"]}
            for row in optimization_store.constraints(connection, task_id)
        ],
        "capacity": None if current is None else int(current["capacity"]),
        "finish": None if stored is None else int(stored["finish"]),
        "can_name": in_progress,
        "can_constrain": in_progress and len(roster) >= 2,
        "can_bound": in_progress and len(roster) >= 1,
        "can_optimize": in_progress and len(roster) >= 1 and current is not None,
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


def _would_cycle(rows: list[sqlite3.Row], activity_id: int, after_id: int) -> bool:
    successors: dict[int, list[int]] = {}
    for row in rows:
        successors.setdefault(int(row["after_id"]), []).append(int(row["activity_id"]))
    seen: set[int] = set()
    pending = [activity_id]
    while pending:
        current = pending.pop()
        if current == after_id:
            return True
        if current in seen:
            continue
        seen.add(current)
        pending.extend(successors.get(current, []))
    return False


def _schedule(
    activities: list[sqlite3.Row], constraints: list[sqlite3.Row], capacity: int
) -> tuple[dict[int, int], int]:
    order = [int(row["id"]) for row in activities]
    lengths = {int(row["id"]): int(row["length"]) for row in activities}
    predecessors: dict[int, list[int]] = {}
    for row in constraints:
        predecessors.setdefault(int(row["activity_id"]), []).append(int(row["after_id"]))
    upper = sum(lengths.values())
    best_finish: int | None = None
    best_starts: tuple[int, ...] | None = None

    def feasible(assignment: dict[int, int]) -> bool:
        for activity_id, earlier_ids in predecessors.items():
            if activity_id not in assignment:
                continue
            for earlier_id in earlier_ids:
                if earlier_id not in assignment:
                    continue
                if assignment[activity_id] < assignment[earlier_id] + lengths[earlier_id]:
                    return False
        finish = max(assignment[key] + lengths[key] for key in assignment)
        for day in range(finish):
            running = 0
            for activity_id, start in assignment.items():
                if start <= day < start + lengths[activity_id]:
                    running += 1
            if running > capacity:
                return False
        return True

    def search(index: int, assignment: dict[int, int]) -> None:
        nonlocal best_finish, best_starts
        if index == len(order):
            finish = max(assignment[activity_id] + lengths[activity_id] for activity_id in order)
            vector = tuple(assignment[activity_id] for activity_id in order)
            if (
                best_starts is None
                or finish < best_finish
                or (finish == best_finish and vector < best_starts)
            ):
                best_finish = finish
                best_starts = vector
            return
        activity_id = order[index]
        earliest = 0
        for earlier_id in predecessors.get(activity_id, []):
            if earlier_id in assignment:
                earliest = max(earliest, assignment[earlier_id] + lengths[earlier_id])
        for start in range(earliest, upper - lengths[activity_id] + 1):
            assignment[activity_id] = start
            if feasible(assignment):
                partial = max(assignment[key] + lengths[key] for key in assignment)
                if best_finish is None or partial <= best_finish:
                    search(index + 1, assignment)
            del assignment[activity_id]

    search(0, {})
    assert best_starts is not None and best_finish is not None
    return {activity_id: best_starts[index] for index, activity_id in enumerate(order)}, best_finish
