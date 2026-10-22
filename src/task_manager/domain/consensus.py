"""Each node suggests from its own reports. The most suggestions win."""

import sqlite3

from task_manager.domain.capture import _detail
from task_manager.domain.results import Refusal, bad_request, conflict, missing
from task_manager.domain.text import clean
from task_manager.storage import consensus_store, task_store

NAME_POINT = "Name this point."
NAME_SETTING = "Name a setting of 1 or 2."
FULL_POINTS = "This task already has 4 points."
NAME_NODE = "Name this node."
FULL_NODES = "This task already has 2 nodes."
NAME_REPORT = "Name this report."
NAME_REPORT_NODE = "Name the node."
NAME_REPORT_POINT = "Name the point."
NAME_SCORE = "Name a score of 1 or 2."
NODE_MISSING = "That node is not on this task."
POINT_MISSING = "That point is not on this task."
ALREADY_REPORTED = "That node already reported this point."
FULL_REPORTS = "This task already has 4 reports."
NAME_POINT_FIRST = "Name a point first."
NAME_NODE_FIRST = "Name a node first."
NAME_REPORT_FIRST = "Record a report first."
NOTHING_LEFT = "No point is left to try."
NOT_IN_PROGRESS = "The task must be In Progress."
_POINT_LIMIT = 4
_NODE_LIMIT = 2
_REPORT_LIMIT = 4


def name_point(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    setting: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_POINT)
    task_key = int(task["id"])
    if consensus_store.point_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    level = _mark(setting)
    if level is None:
        return bad_request(NAME_SETTING)
    if consensus_store.count_points(connection, task_key) >= _POINT_LIMIT:
        return conflict(FULL_POINTS)
    consensus_store.clear_agreement(connection, task_key)
    consensus_store.insert_point(connection, task_key, kept, level, occurred_at)
    return _detail(connection, task_key)


def name_node(
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
        return bad_request(NAME_NODE)
    task_key = int(task["id"])
    if consensus_store.node_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    if consensus_store.count_nodes(connection, task_key) >= _NODE_LIMIT:
        return conflict(FULL_NODES)
    consensus_store.clear_agreement(connection, task_key)
    consensus_store.insert_node(connection, task_key, kept, occurred_at)
    return _detail(connection, task_key)


def record_report(
    connection: sqlite3.Connection,
    task_id: int,
    name: str | None,
    node: str | None,
    point: str | None,
    score: str | None,
    occurred_at: str,
):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    kept = clean(name)
    if not kept:
        return bad_request(NAME_REPORT)
    task_key = int(task["id"])
    if consensus_store.report_by_name(connection, task_key, kept) is not None:
        return _detail(connection, task_key)
    node_name = clean(node)
    if not node_name:
        return bad_request(NAME_REPORT_NODE)
    point_name = clean(point)
    if not point_name:
        return bad_request(NAME_REPORT_POINT)
    level = _mark(score)
    if level is None:
        return bad_request(NAME_SCORE)
    stored_node = consensus_store.node_by_name(connection, task_key, node_name)
    if stored_node is None:
        return conflict(NODE_MISSING)
    stored_point = consensus_store.point_by_name(connection, task_key, point_name)
    if stored_point is None:
        return conflict(POINT_MISSING)
    if consensus_store.count_reports(connection, task_key) >= _REPORT_LIMIT:
        return conflict(FULL_REPORTS)
    if (
        consensus_store.report_for_pair(
            connection, task_key, int(stored_node["id"]), int(stored_point["id"])
        )
        is not None
    ):
        return conflict(ALREADY_REPORTED)
    consensus_store.clear_agreement(connection, task_key)
    consensus_store.insert_report(
        connection,
        task_key,
        kept,
        int(stored_node["id"]),
        int(stored_point["id"]),
        level,
        occurred_at,
    )
    return _detail(connection, task_key)


def agree(connection: sqlite3.Connection, task_id: int, occurred_at: str):
    task = _open(connection, task_id)
    if isinstance(task, Refusal):
        return task
    task_key = int(task["id"])
    roster = consensus_store.points(connection, task_key)
    if not roster:
        return conflict(NAME_POINT_FIRST)
    peers = consensus_store.nodes(connection, task_key)
    if not peers:
        return conflict(NAME_NODE_FIRST)
    recorded = consensus_store.reports(connection, task_key)
    if not recorded:
        return conflict(NAME_REPORT_FIRST)
    proposals = []
    for node in peers:
        suggested = _suggest(node, roster, recorded)
        if suggested is not None:
            proposals.append((node, suggested))
    if not proposals:
        return conflict(NOTHING_LEFT)
    counts = {int(point["id"]): 0 for point in roster}
    for _node, suggested in proposals:
        counts[int(suggested["id"])] += 1
    chosen = roster[0]
    for point in roster[1:]:
        if counts[int(point["id"])] > counts[int(chosen["id"])]:
            chosen = point
    named = next(
        node for node, suggested in proposals if int(suggested["id"]) == int(chosen["id"])
    )
    consensus_store.clear_agreement(connection, task_key)
    for position, (node, suggested) in enumerate(proposals, start=1):
        consensus_store.insert_proposal(
            connection,
            task_key,
            str(node["name"]),
            str(suggested["name"]),
            position,
            occurred_at,
        )
    consensus_store.insert_choice(
        connection,
        task_key,
        str(chosen["name"]),
        str(named["name"]),
        counts[int(chosen["id"])],
        occurred_at,
    )
    return _detail(connection, task_key)


def payload(connection: sqlite3.Connection, task_id: int) -> dict[str, object]:
    task = task_store.row_task(connection, task_id)
    in_progress = task is not None and task["status"] == "In Progress"
    roster = consensus_store.points(connection, task_id)
    peers = consensus_store.nodes(connection, task_id)
    recorded = consensus_store.reports(connection, task_id)
    stored = consensus_store.choice_for(connection, task_id)
    choice = None
    if stored is not None:
        choice = {
            "point": stored["point"],
            "node": stored["node"],
            "suggestions": int(stored["suggestions"]),
        }
    return {
        "points": [
            {"name": row["name"], "setting": int(row["setting"])} for row in roster
        ],
        "nodes": [{"name": row["name"]} for row in peers],
        "reports": [
            {
                "name": row["name"],
                "node": row["node"],
                "point": row["point"],
                "score": int(row["score"]),
            }
            for row in recorded
        ],
        "proposals": [
            {"node": row["node"], "point": row["point"]}
            for row in consensus_store.proposals(connection, task_id)
        ],
        "choice": choice,
        "can_name": in_progress,
        "can_node": in_progress,
        "can_report": in_progress and len(roster) >= 1 and len(peers) >= 1,
        "can_agree": in_progress and len(recorded) >= 1,
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
    if kept == "1":
        return 1
    if kept == "2":
        return 2
    return None


def _suggest(
    node: sqlite3.Row, roster: list[sqlite3.Row], recorded: list[sqlite3.Row]
) -> sqlite3.Row | None:
    own = [row for row in recorded if int(row["node_id"]) == int(node["id"])]
    reported = {int(row["point_id"]) for row in own}
    open_points = [point for point in roster if int(point["id"]) not in reported]
    if not open_points:
        return None
    if not own:
        return open_points[0]
    best = own[0]
    for report in own[1:]:
        if int(report["score"]) > int(best["score"]):
            best = report
    best_point = next(
        point for point in roster if int(point["id"]) == int(best["point_id"])
    )
    best_setting = int(best_point["setting"])
    best_score = int(best["score"])
    chosen = open_points[0]
    chosen_value = best_score - (0 if int(chosen["setting"]) == best_setting else 1)
    for point in open_points[1:]:
        value = best_score - (0 if int(point["setting"]) == best_setting else 1)
        if value > chosen_value:
            chosen = point
            chosen_value = value
    return chosen
