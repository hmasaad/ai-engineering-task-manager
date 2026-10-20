"""Outcomes teach a predicted length. Forecasts then run one at a time."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import learning_store, task_store

NAME_OUTCOME = "Name this outcome."
NAME_KIND = "Name this kind."
NAME_LENGTH = "Name a length of 1 or 2."
FULL_OUTCOMES = "This task already has 4 outcomes."
NAME_FORECAST = "Name this forecast."
NAME_KIND_OF_WORK = "Name the kind of work."
NAME_OUTCOME_FIRST = "Record an outcome for that kind first."
FULL_FORECASTS = "This task already has 4 forecasts."
NAME_FORECAST_FIRST = "Name a forecast first."
NOT_IN_PROGRESS = "The task must be In Progress."
_LIMIT = 4


def record_outcome(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    kind: str | None,
    length: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_OUTCOME)
    task_key = int(task["id"])
    if learning_store.outcome_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    kind_name = clean(kind)
    if not kind_name:
        return bad_request(NAME_KIND)
    days = _choice(length)
    if days is None:
        return bad_request(NAME_LENGTH)
    if learning_store.count_outcomes(connection, task_key) >= _LIMIT:
        return conflict(FULL_OUTCOMES)
    learning_store.clear_plan(connection, task_key)
    learning_store.insert_outcome(connection, task_key, kept, kind_name, days, occurred_at)
    return _detail(connection, task_key)


def name_forecast(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    kind: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_FORECAST)
    task_key = int(task["id"])
    if learning_store.forecast_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    kind_name = clean(kind)
    if not kind_name:
        return bad_request(NAME_KIND_OF_WORK)
    if not learning_store.kind_exists(connection, task_key, kind_name):
        return conflict(NAME_OUTCOME_FIRST)
    if learning_store.count_forecasts(connection, task_key) >= _LIMIT:
        return conflict(FULL_FORECASTS)
    learning_store.clear_plan(connection, task_key)
    learning_store.insert_forecast(connection, task_key, kept, kind_name, occurred_at)
    return _detail(connection, task_key)


def predict_schedule(connection: sqlite3.Connection, task_id: int, occurred_at: str):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    roster = learning_store.forecasts(connection, task_key)
    if not roster:
        return conflict(NAME_FORECAST_FIRST)
    placed, finish = _place(learning_store.outcomes(connection, task_key), roster)
    learning_store.clear_plan(connection, task_key)
    plan_id = learning_store.insert_plan(connection, task_key, finish, occurred_at)
    for forecast_id, predicted, start in placed:
        learning_store.insert_placement(connection, plan_id, forecast_id, predicted, start)
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    recorded = learning_store.outcomes(connection, task_id)
    upcoming = learning_store.forecasts(connection, task_id)
    stored = learning_store.plan_for(connection, task_id)
    return {
        "outcomes": [
            {"name": row["name"], "kind": row["kind"], "length": int(row["length"])}
            for row in recorded
        ],
        "kinds": _kinds(recorded),
        "forecasts": [
            {
                "name": row["name"],
                "kind": row["kind"],
                "predicted": None if row["predicted"] is None else int(row["predicted"]),
                "start": None if row["start"] is None else int(row["start"]),
            }
            for row in upcoming
        ],
        "finish": None if stored is None else int(stored["finish"]),
        "can_record": in_progress,
        "can_forecast": in_progress and len(recorded) >= 1,
        "can_predict": in_progress and len(upcoming) >= 1,
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


def _kinds(rows: list[sqlite3.Row]) -> list[dict[str, object]]:
    ones: dict[str, int] = {}
    twos: dict[str, int] = {}
    order: list[str] = []
    for row in rows:
        kind = str(row["kind"])
        if kind not in ones:
            order.append(kind)
            ones[kind] = 0
            twos[kind] = 0
        if int(row["length"]) == 2:
            twos[kind] += 1
        else:
            ones[kind] += 1
    return [
        {"kind": kind, "predicted": 2 if twos[kind] > ones[kind] else 1} for kind in order
    ]


def _place(
    recorded: list[sqlite3.Row], upcoming: list[sqlite3.Row]
) -> tuple[list[tuple[int, int, int]], int]:
    predicted = {str(item["kind"]): int(item["predicted"]) for item in _kinds(recorded)}
    start = 0
    placed: list[tuple[int, int, int]] = []
    for row in upcoming:
        days = predicted[str(row["kind"])]
        placed.append((int(row["id"]), days, start))
        start += days
    return placed, start
