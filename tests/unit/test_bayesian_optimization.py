from task_manager.domain import bayes
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _design(name, first, second):
    return {"name": name, "first": first, "second": second}


def _observation(name, design, first, second, constraint):
    return {
        "name": name,
        "design": design,
        "first": first,
        "second": second,
        "constraint": constraint,
    }


def _front(design, first, second):
    return {"design": design, "first": first, "second": second}


def test_a_design_keeps_its_settings(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    named = workspace.name_search_design(task_id, " ada ", "1", "1")
    assert named["status"] == "In Progress"
    assert named["search"]["designs"] == [_design("ada", 1, 1)]
    assert named["file_reads"] == []
    assert named["workflow"]["steps"] == []
    assert named["optimization"]["activities"] == []
    assert named["models"]["arms"] == []
    repeated = workspace.name_search_design(task_id, "ada", "2", "2")
    assert repeated["search"]["designs"] == [_design("ada", 1, 1)]
    ignored = workspace.name_search_design(task_id, "ada", " ", "3")
    assert ignored["search"]["designs"] == [_design("ada", 1, 1)]
    for name, first, second in (("grace", "2", "2"), ("mina", "1", "2"), ("nora", "2", "1")):
        workspace.name_search_design(task_id, name, first, second)
    assert [item["name"] for item in workspace.get_task(task_id)["search"]["designs"]] == [
        "ada",
        "grace",
        "mina",
        "nora",
    ]

    other = _in_progress(workspace, "Other design")
    other_named = workspace.name_search_design(other["id"], "ada", "2", "2")
    assert other_named["search"]["designs"] == [_design("ada", 2, 2)]

    blank = workspace.name_search_design(task_id, " ", "1", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this design."
    bad_setting = workspace.name_search_design(task_id, "note", "3", "1")
    assert isinstance(bad_setting, Refusal)
    assert bad_setting.message == "Name a setting of 1 or 2."
    bad_second = workspace.name_search_design(task_id, "note", "1", " ")
    assert isinstance(bad_second, Refusal)
    assert bad_second.message == "Name a setting of 1 or 2."
    fifth = workspace.name_search_design(task_id, "otis", "1", "1")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 designs."
    assert len(workspace.get_task(task_id)["search"]["designs"]) == 4

    draft = workspace.create_task("Draft")
    refused = workspace.name_search_design(draft["id"], "ada", "1", "1")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["search"]["designs"] == []


def test_an_observation_keeps_its_constraint(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_search_design(task_id, "ada", "1", "1")
    recorded = workspace.record_observation(task_id, " one ", " ada ", "2", "1", "1")
    assert recorded["search"]["observations"] == [_observation("one", "ada", 2, 1, 1)]
    repeated = workspace.record_observation(task_id, "one", "ada", "1", "2", "2")
    assert repeated["search"]["observations"] == recorded["search"]["observations"]
    unchanged = workspace.record_observation(task_id, "one", " ", "3", " ", "4")
    assert unchanged["search"]["observations"] == recorded["search"]["observations"]

    missing = workspace.record_observation(task_id, "two", "grace", "2", "2", "1")
    assert isinstance(missing, Refusal)
    assert missing.message == "That design is not on this task."
    again = workspace.record_observation(task_id, "two", "ada", "1", "1", "1")
    assert isinstance(again, Refusal)
    assert again.message == "That design already has an observation."
    blank = workspace.record_observation(task_id, " ", "ada", "1", "1", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this observation."
    blank_design = workspace.record_observation(task_id, "two", " ", "1", "1", "1")
    assert isinstance(blank_design, Refusal)
    assert blank_design.message == "Name the design."
    bad_objective = workspace.record_observation(task_id, "two", "ada", "3", "1", "1")
    assert isinstance(bad_objective, Refusal)
    assert bad_objective.message == "Name an objective of 1 or 2."
    bad_second = workspace.record_observation(task_id, "two", "ada", "1", " ", "1")
    assert isinstance(bad_second, Refusal)
    assert bad_second.message == "Name an objective of 1 or 2."
    bad_constraint = workspace.record_observation(task_id, "two", "ada", "1", "1", "3")
    assert isinstance(bad_constraint, Refusal)
    assert bad_constraint.message == "Name a constraint of 1 or 2."
    assert len(workspace.get_task(task_id)["search"]["observations"]) == 1

    full = _in_progress(workspace, "Full observations")
    full_id = full["id"]
    for name in ("ada", "grace", "mina", "nora"):
        workspace.name_search_design(full_id, name, "1", "1")
        workspace.record_observation(full_id, name, name, "1", "1", "1")
    fifth = workspace.record_observation(full_id, "five", "ada", "1", "1", "1")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 observations."
    assert len(workspace.get_task(full_id)["search"]["observations"]) == 4


def test_the_next_design_is_the_nearest_feasible_neighbor(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_search_design(task_id, "ada", "1", "1")
    workspace.name_search_design(task_id, "grace", "2", "2")
    workspace.name_search_design(task_id, "mina", "1", "2")
    workspace.name_search_design(task_id, "nora", "2", "1")
    workspace.record_observation(task_id, "one", "ada", "2", "1", "1")
    workspace.record_observation(task_id, "two", "grace", "2", "2", "2")

    recommended = workspace.recommend_design(task_id)
    assert recommended["status"] == "In Progress"
    assert recommended["search"]["front"] == [_front("ada", 2, 1)]
    assert recommended["search"]["next"] == "mina"
    assert recommended["bandit"]["actions"] == []

    dominated = _in_progress(workspace, "Dominated")
    dominated_id = dominated["id"]
    workspace.name_search_design(dominated_id, "ada", "1", "1")
    workspace.name_search_design(dominated_id, "grace", "2", "2")
    workspace.name_search_design(dominated_id, "mina", "1", "2")
    workspace.record_observation(dominated_id, "one", "ada", "1", "1", "1")
    workspace.record_observation(dominated_id, "two", "grace", "2", "2", "1")
    covered = workspace.recommend_design(dominated_id)
    assert covered["search"]["front"] == [_front("grace", 2, 2)]
    assert covered["search"]["next"] == "mina"

    trade = _in_progress(workspace, "Tradeoff")
    trade_id = trade["id"]
    workspace.name_search_design(trade_id, "ada", "1", "1")
    workspace.name_search_design(trade_id, "grace", "2", "2")
    workspace.name_search_design(trade_id, "mina", "1", "2")
    workspace.record_observation(trade_id, "one", "ada", "2", "1", "1")
    workspace.record_observation(trade_id, "two", "grace", "1", "2", "1")
    both = workspace.recommend_design(trade_id)
    assert both["search"]["front"] == [_front("ada", 2, 1), _front("grace", 1, 2)]
    assert both["search"]["next"] == "mina"

    empty = _in_progress(workspace, "Empty search")
    empty_id = empty["id"]
    missing = workspace.recommend_design(empty_id)
    assert isinstance(missing, Refusal)
    assert missing.message == "Name a design first."
    workspace.name_search_design(empty_id, "ada", "1", "1")
    workspace.name_search_design(empty_id, "mina", "1", "2")
    blocked = workspace.record_observation(empty_id, "one", "ada", "2", "2", "2")
    assert blocked["search"]["next"] is None
    refused = workspace.recommend_design(empty_id)
    assert isinstance(refused, Refusal)
    assert refused.message == "Record a feasible observation first."

    packed = _in_progress(workspace, "Packed")
    packed_id = packed["id"]
    workspace.name_search_design(packed_id, "ada", "1", "1")
    workspace.record_observation(packed_id, "one", "ada", "2", "1", "1")
    full = workspace.recommend_design(packed_id)
    assert isinstance(full, Refusal)
    assert full.message == "No design is left to try."

    cleared = workspace.name_search_design(task_id, "otis", "1", "1")
    assert isinstance(cleared, Refusal)
    kept = workspace.record_observation(dominated_id, "three", "mina", "1", "1", "1")
    assert kept["search"]["next"] is None

    draft = workspace.create_task("Draft")
    draft_refused = workspace.recommend_design(draft["id"])
    assert isinstance(draft_refused, Refusal)
    assert draft_refused.message == "The task must be In Progress."

    fresh = _in_progress(workspace, "Rollback")
    fresh_id = fresh["id"]
    workspace.name_search_design(fresh_id, "ada", "1", "1")
    workspace.name_search_design(fresh_id, "mina", "1", "2")
    workspace.record_observation(fresh_id, "one", "ada", "2", "1", "1")
    stored = workspace.recommend_design(fresh_id)
    assert stored["search"]["next"] == "mina"

    def rolled(connection):
        bayes.record_observation(
            connection, fresh_id, "two", "mina", "1", "1", "1", "2026-10-21T00:00:00Z"
        )
        bayes.recommend(connection, fresh_id, "2026-10-21T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(fresh_id)
    assert len(restored["search"]["observations"]) == 1
    assert restored["search"]["next"] == "mina"
    assert restored["search"]["front"] == [_front("ada", 2, 1)]
