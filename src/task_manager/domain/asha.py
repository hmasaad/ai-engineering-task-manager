"""Early scores promote half the trials. The next one goes to the least-loaded runner."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import asha_store, task_store

NAME_TRIAL = "Name this trial."
FULL_TRIALS = "This task already has 4 trials."
NAME_RUNNER = "Name this runner."
FULL_RUNNERS = "This task already has 2 runners."
NAME_RUNG = "Name this rung score."
NAME_RUNG_TRIAL = "Name the trial."
NAME_LEVEL = "Name a rung of 1 or 2."
NAME_SCORE = "Name a score of 1 or 2."
TRIAL_MISSING = "That trial is not on this task."
ALREADY_SCORED = "That trial already has this rung."
FULL_RUNGS = "This task already has 6 rung scores."
NAME_TWO = "Record two rung scores first."
NOT_PROMOTED = "That trial is not promoted."
NAME_TRIAL_FIRST = "Name a trial first."
NAME_RUNNER_FIRST = "Name a runner first."
NOT_IN_PROGRESS = "The task must be In Progress."
_TRIAL_LIMIT = 4
_RUNNER_LIMIT = 2
_RUNG_LIMIT = 6


def name_trial(
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
        return bad_request(NAME_TRIAL)
    task_key = int(task["id"])
    if asha_store.trial_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    if asha_store.count_trials(connection, task_key) >= _TRIAL_LIMIT:
        return conflict(FULL_TRIALS)
    asha_store.clear_schedule(connection, task_key)
    asha_store.insert_trial(connection, task_key, kept, occurred_at)
    return _detail(connection, task_key)


def name_runner(
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
        return bad_request(NAME_RUNNER)
    task_key = int(task["id"])
    if asha_store.runner_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    if asha_store.count_runners(connection, task_key) >= _RUNNER_LIMIT:
        return conflict(FULL_RUNNERS)
    asha_store.clear_schedule(connection, task_key)
    asha_store.insert_runner(connection, task_key, kept, occurred_at)
    return _detail(connection, task_key)


def record_rung(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    trial: str | None,
    rung: str | None,
    score: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_RUNG)
    task_key = int(task["id"])
    if asha_store.rung_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    trial_name = clean(trial)
    if not trial_name:
        return bad_request(NAME_RUNG_TRIAL)
    level = _level(rung)
    if level is None:
        return bad_request(NAME_LEVEL)
    points = _level(score)
    if points is None:
        return bad_request(NAME_SCORE)
    trial_row = asha_store.trial_by_name(connection, task_key, trial_name)
    if trial_row is None:
        return conflict(TRIAL_MISSING)
    if asha_store.count_rungs(connection, task_key) >= _RUNG_LIMIT:
        return conflict(FULL_RUNGS)
    trial_key = int(trial_row["id"])
    if asha_store.rung_for_trial(connection, task_key, trial_key, level) is not None:
        return conflict(ALREADY_SCORED)
    if level == 2:
        promoted = _promoted(
            asha_store.trials(connection, task_key),
            _scores(asha_store.rungs(connection, task_key), 1),
        )
        if not promoted:
            return conflict(NAME_TWO)
        if trial_key not in {int(row["id"]) for row in promoted}:
            return conflict(NOT_PROMOTED)
        asha_store.clear_winner(connection, task_key)
    else:
        asha_store.clear_schedule(connection, task_key)
    asha_store.insert_rung(
        connection, task_key, kept, trial_key, level, points, occurred_at
    )
    return _detail(connection, task_key)


def schedule(connection: sqlite3.Connection, task_id: int, occurred_at: str):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    roster = asha_store.trials(connection, task_key)
    if not roster:
        return conflict(NAME_TRIAL_FIRST)
    runners = asha_store.runners(connection, task_key)
    if not runners:
        return conflict(NAME_RUNNER_FIRST)
    recorded = asha_store.rungs(connection, task_key)
    early = _scores(recorded, 1)
    if len(early) < 2:
        return conflict(NAME_TWO)
    promoted = _promoted(roster, early)
    later = _scores(recorded, 2)
    asha_store.clear_promoted(connection, task_key)
    for position, row in enumerate(promoted, start=1):
        asha_store.insert_promoted(
            connection, task_key, str(row["name"]), position, occurred_at
        )
    assigned = {
        str(row["trial"]) for row in asha_store.assignments_for(connection, task_key)
    }
    waiting = [
        row
        for row in promoted
        if int(row["id"]) not in later and str(row["name"]) not in assigned
    ]
    if waiting:
        runner = _runner(runners, asha_store.assignments_for(connection, task_key))
        asha_store.insert_assignment(
            connection,
            task_key,
            str(waiting[0]["name"]),
            str(runner["name"]),
            len(assigned) + 1,
            occurred_at,
        )
        asha_store.clear_winner(connection, task_key)
        return _detail(connection, task_key)
    if all(int(row["id"]) in later for row in promoted):
        asha_store.clear_winner(connection, task_key)
        asha_store.insert_winner(
            connection, task_key, _winner(promoted, later), occurred_at
        )
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = asha_store.trials(connection, task_id)
    runners = asha_store.runners(connection, task_id)
    recorded = asha_store.rungs(connection, task_id)
    stored = asha_store.winner_for(connection, task_id)
    early = sum(1 for row in recorded if int(row["rung"]) == 1)
    return {
        "trials": [{"name": row["name"]} for row in roster],
        "runners": [{"name": row["name"]} for row in runners],
        "rungs": [
            {
                "name": row["name"],
                "trial": row["trial"],
                "rung": int(row["rung"]),
                "score": int(row["score"]),
            }
            for row in recorded
        ],
        "promoted": [
            {"name": row["trial"]} for row in asha_store.promoted_for(connection, task_id)
        ],
        "assignments": [
            {"trial": row["trial"], "runner": row["runner"]}
            for row in asha_store.assignments_for(connection, task_id)
        ],
        "winner": None if stored is None else stored["winner"],
        "can_name": in_progress,
        "can_runner": in_progress,
        "can_record": in_progress and len(roster) >= 1,
        "can_schedule": in_progress and len(runners) >= 1 and early >= 2,
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


def _scores(recorded: list[sqlite3.Row], level: int) -> dict[int, int]:
    return {
        int(row["trial_id"]): int(row["score"])
        for row in recorded
        if int(row["rung"]) == level
    }


def _promoted(roster: list[sqlite3.Row], early: dict[int, int]) -> list[sqlite3.Row]:
    scored = [row for row in roster if int(row["id"]) in early]
    scored.sort(key=lambda row: (-early[int(row["id"])], int(row["id"])))
    return scored[: len(scored) // 2]


def _runner(runners: list[sqlite3.Row], assignments: list[sqlite3.Row]) -> sqlite3.Row:
    counts = {str(row["name"]): 0 for row in runners}
    for row in assignments:
        counts[str(row["runner"])] = counts.get(str(row["runner"]), 0) + 1
    chosen = runners[0]
    for runner in runners[1:]:
        if counts[str(runner["name"])] < counts[str(chosen["name"])]:
            chosen = runner
    return chosen


def _winner(promoted: list[sqlite3.Row], later: dict[int, int]) -> str:
    chosen = promoted[0]
    for row in promoted[1:]:
        score = later[int(row["id"])]
        best = later[int(chosen["id"])]
        if score > best or (score == best and int(row["id"]) < int(chosen["id"])):
            chosen = row
    return str(chosen["name"])
