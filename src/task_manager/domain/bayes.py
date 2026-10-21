"""The front keeps feasible designs. The next design follows the nearest feasible neighbor."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import bayes_store, task_store

NAME_DESIGN = "Name this design."
NAME_SETTING = "Name a setting of 1 or 2."
FULL_DESIGNS = "This task already has 4 designs."
NAME_OBSERVATION = "Name this observation."
NAME_OBSERVED_DESIGN = "Name the design."
NAME_OBJECTIVE = "Name an objective of 1 or 2."
NAME_CONSTRAINT = "Name a constraint of 1 or 2."
DESIGN_MISSING = "That design is not on this task."
ALREADY_OBSERVED = "That design already has an observation."
FULL_OBSERVATIONS = "This task already has 4 observations."
NAME_DESIGN_FIRST = "Name a design first."
NAME_FEASIBLE = "Record a feasible observation first."
NONE_LEFT = "No design is left to try."
NOT_IN_PROGRESS = "The task must be In Progress."
_DESIGN_LIMIT = 4
_OBSERVATION_LIMIT = 4


def name_design(
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
        return bad_request(NAME_DESIGN)
    task_key = int(task["id"])
    if bayes_store.design_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    first_setting = _level(first)
    if first_setting is None:
        return bad_request(NAME_SETTING)
    second_setting = _level(second)
    if second_setting is None:
        return bad_request(NAME_SETTING)
    if bayes_store.count_designs(connection, task_key) >= _DESIGN_LIMIT:
        return conflict(FULL_DESIGNS)
    bayes_store.clear_recommendation(connection, task_key)
    bayes_store.insert_design(
        connection, task_key, kept, first_setting, second_setting, occurred_at
    )
    return _detail(connection, task_key)


def record_observation(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    design: str | None,
    first: str | None,
    second: str | None,
    constraint: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_OBSERVATION)
    task_key = int(task["id"])
    if bayes_store.observation_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    design_name = clean(design)
    if not design_name:
        return bad_request(NAME_OBSERVED_DESIGN)
    first_objective = _level(first)
    if first_objective is None:
        return bad_request(NAME_OBJECTIVE)
    second_objective = _level(second)
    if second_objective is None:
        return bad_request(NAME_OBJECTIVE)
    constraint_mark = _level(constraint)
    if constraint_mark is None:
        return bad_request(NAME_CONSTRAINT)
    design_row = bayes_store.design_by_name(connection, task_key, design_name)
    if design_row is None:
        return conflict(DESIGN_MISSING)
    if bayes_store.count_observations(connection, task_key) >= _OBSERVATION_LIMIT:
        return conflict(FULL_OBSERVATIONS)
    if (
        bayes_store.observation_for_design(connection, task_key, int(design_row["id"]))
        is not None
    ):
        return conflict(ALREADY_OBSERVED)
    bayes_store.clear_recommendation(connection, task_key)
    bayes_store.insert_observation(
        connection,
        task_key,
        kept,
        int(design_row["id"]),
        first_objective,
        second_objective,
        constraint_mark,
        occurred_at,
    )
    return _detail(connection, task_key)


def recommend(connection: sqlite3.Connection, task_id: int, occurred_at: str):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    roster = bayes_store.designs(connection, task_key)
    if not roster:
        return conflict(NAME_DESIGN_FIRST)
    recorded = bayes_store.observations(connection, task_key)
    feasible = [row for row in recorded if int(row["constraint_mark"]) == 1]
    if not feasible:
        return conflict(NAME_FEASIBLE)
    observed = {str(row["design"]) for row in recorded}
    if all(str(row["name"]) in observed for row in roster):
        return conflict(NONE_LEFT)
    front = _front(feasible)
    chosen = _next(roster, observed, feasible)
    bayes_store.clear_recommendation(connection, task_key)
    bayes_store.insert_pick(connection, task_key, chosen, occurred_at)
    for position, row in enumerate(front, start=1):
        bayes_store.insert_front(
            connection,
            task_key,
            str(row["design"]),
            int(row["first_objective"]),
            int(row["second_objective"]),
            position,
            occurred_at,
        )
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = bayes_store.designs(connection, task_id)
    recorded = bayes_store.observations(connection, task_id)
    stored = bayes_store.pick_for(connection, task_id)
    front = bayes_store.front_for(connection, task_id)
    return {
        "designs": [
            {
                "name": row["name"],
                "first": int(row["first_setting"]),
                "second": int(row["second_setting"]),
            }
            for row in roster
        ],
        "observations": [
            {
                "name": row["name"],
                "design": row["design"],
                "first": int(row["first_objective"]),
                "second": int(row["second_objective"]),
                "constraint": int(row["constraint_mark"]),
            }
            for row in recorded
        ],
        "front": [
            {
                "design": row["design"],
                "first": int(row["first_objective"]),
                "second": int(row["second_objective"]),
            }
            for row in front
        ],
        "next": None if stored is None else stored["next_design"],
        "can_name": in_progress,
        "can_observe": in_progress and len(roster) >= 1,
        "can_recommend": in_progress and len(recorded) >= 1,
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


def _front(feasible: list[sqlite3.Row]) -> list[sqlite3.Row]:
    kept: list[sqlite3.Row] = []
    for item in feasible:
        dominated = False
        for other in feasible:
            if int(other["id"]) == int(item["id"]):
                continue
            first_better = int(other["first_objective"]) >= int(item["first_objective"])
            second_better = int(other["second_objective"]) >= int(
                item["second_objective"]
            )
            strict = int(other["first_objective"]) > int(item["first_objective"]) or int(
                other["second_objective"]
            ) > int(item["second_objective"])
            if first_better and second_better and strict:
                dominated = True
                break
        if not dominated:
            kept.append(item)
    return kept


def _next(
    roster: list[sqlite3.Row],
    observed: set[str],
    feasible: list[sqlite3.Row],
) -> str:
    chosen = ""
    best = 0
    for design in roster:
        if str(design["name"]) in observed:
            continue
        distance, total = _neighbor(design, feasible)
        score = total - distance
        if chosen == "" or score > best:
            chosen = str(design["name"])
            best = score
    return chosen


def _neighbor(design: sqlite3.Row, feasible: list[sqlite3.Row]) -> tuple[int, int]:
    distance = 0
    total = 0
    found = False
    for item in feasible:
        gap = int(int(design["first_setting"]) != int(item["first_setting"])) + int(
            int(design["second_setting"]) != int(item["second_setting"])
        )
        points = int(item["first_objective"]) + int(item["second_objective"])
        if not found or gap < distance or (gap == distance and points > total):
            distance = gap
            total = points
            found = True
    return distance, total
