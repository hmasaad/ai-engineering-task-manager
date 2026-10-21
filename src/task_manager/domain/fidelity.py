"""Cheap scores keep half the field. The expensive score names the winner."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import fidelity_store, task_store

NAME_CANDIDATE = "Name this candidate."
FULL_CANDIDATES = "This task already has 4 candidates."
NAME_MEASUREMENT = "Name this measurement."
NAME_MEASURED = "Name the candidate."
NAME_FIDELITY = "Name a fidelity of 1 or 2."
NAME_SCORE = "Name a score of 1 or 2."
CANDIDATE_MISSING = "That candidate is not on this task."
ALREADY_MEASURED = "That candidate already has this fidelity."
FULL_MEASUREMENTS = "This task already has 6 measurements."
HALVE_FIRST = "Halve the field before an expensive measurement."
NOT_KEPT = "That candidate was not kept."
NAME_CANDIDATE_FIRST = "Name a candidate first."
NAME_ANOTHER = "Name another candidate first."
NAME_CHEAP = "Record a cheap measurement for every candidate first."
NOT_IN_PROGRESS = "The task must be In Progress."
_CANDIDATE_LIMIT = 4
_MEASUREMENT_LIMIT = 6


def name_candidate(
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
        return bad_request(NAME_CANDIDATE)
    task_key = int(task["id"])
    if fidelity_store.candidate_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    if fidelity_store.count_candidates(connection, task_key) >= _CANDIDATE_LIMIT:
        return conflict(FULL_CANDIDATES)
    fidelity_store.clear_round(connection, task_key)
    fidelity_store.insert_candidate(connection, task_key, kept, occurred_at)
    return _detail(connection, task_key)


def record_fidelity(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    candidate: str | None,
    fidelity: str | None,
    score: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_MEASUREMENT)
    task_key = int(task["id"])
    if fidelity_store.measurement_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    candidate_name = clean(candidate)
    if not candidate_name:
        return bad_request(NAME_MEASURED)
    level = _level(fidelity)
    if level is None:
        return bad_request(NAME_FIDELITY)
    points = _level(score)
    if points is None:
        return bad_request(NAME_SCORE)
    candidate_row = fidelity_store.candidate_by_name(connection, task_key, candidate_name)
    if candidate_row is None:
        return conflict(CANDIDATE_MISSING)
    if fidelity_store.count_measurements(connection, task_key) >= _MEASUREMENT_LIMIT:
        return conflict(FULL_MEASUREMENTS)
    candidate_key = int(candidate_row["id"])
    if (
        fidelity_store.measurement_for_candidate(
            connection, task_key, candidate_key, level
        )
        is not None
    ):
        return conflict(ALREADY_MEASURED)
    if level == 2:
        stored = fidelity_store.round_for(connection, task_key)
        if stored is None:
            return conflict(HALVE_FIRST)
        names = {str(row["candidate"]) for row in fidelity_store.kept_for(connection, task_key)}
        if candidate_name not in names:
            return conflict(NOT_KEPT)
        fidelity_store.clear_winner(connection, task_key)
    else:
        fidelity_store.clear_round(connection, task_key)
    fidelity_store.insert_measurement(
        connection, task_key, kept, candidate_key, level, points, occurred_at
    )
    return _detail(connection, task_key)


def halve(connection: sqlite3.Connection, task_id: int, occurred_at: str):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    roster = fidelity_store.candidates(connection, task_key)
    if not roster:
        return conflict(NAME_CANDIDATE_FIRST)
    if len(roster) < 2:
        return conflict(NAME_ANOTHER)
    recorded = fidelity_store.measurements(connection, task_key)
    cheap = {
        int(row["candidate_id"]): int(row["score"])
        for row in recorded
        if int(row["fidelity"]) == 1
    }
    if any(int(row["id"]) not in cheap for row in roster):
        return conflict(NAME_CHEAP)
    expensive = {
        int(row["candidate_id"]): int(row["score"])
        for row in recorded
        if int(row["fidelity"]) == 2
    }
    ranked = sorted(roster, key=lambda row: (-cheap[int(row["id"])], int(row["id"])))
    chosen = ranked[: len(roster) // 2]
    winner = ""
    if all(int(row["id"]) in expensive for row in chosen):
        ordered = sorted(
            chosen, key=lambda row: (-expensive[int(row["id"])], int(row["id"]))
        )
        winner = str(ordered[0]["name"])
    fidelity_store.clear_round(connection, task_key)
    fidelity_store.insert_round(connection, task_key, winner, occurred_at)
    for position, row in enumerate(chosen, start=1):
        fidelity_store.insert_kept(
            connection, task_key, str(row["name"]), position, occurred_at
        )
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = fidelity_store.candidates(connection, task_id)
    recorded = fidelity_store.measurements(connection, task_id)
    stored = fidelity_store.round_for(connection, task_id)
    kept = fidelity_store.kept_for(connection, task_id)
    cheap = sum(1 for row in recorded if int(row["fidelity"]) == 1)
    winner = None
    if stored is not None and stored["winner"]:
        winner = stored["winner"]
    return {
        "candidates": [{"name": row["name"]} for row in roster],
        "measurements": [
            {
                "name": row["name"],
                "candidate": row["candidate"],
                "fidelity": int(row["fidelity"]),
                "score": int(row["score"]),
            }
            for row in recorded
        ],
        "kept": [{"name": row["candidate"]} for row in kept],
        "winner": winner,
        "can_name": in_progress,
        "can_measure": in_progress and len(roster) >= 1,
        "can_halve": in_progress and cheap >= 2,
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
