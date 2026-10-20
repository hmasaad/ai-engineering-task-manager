from task_manager.domain import priority
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_ranked_work_starts_at_age_zero(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    ranked = workspace.rank_work(task_id, " quiet ", "1")
    assert ranked["status"] == "In Progress"
    assert ranked["priority"]["waiting"] == [{"name": "quiet", "rank": 1, "age": 0}]
    assert ranked["file_reads"] == []
    assert ranked["schedule"]["tenants"] == []
    rush = workspace.rank_work(task_id, "rush", " 3 ")
    assert rush["priority"]["waiting"] == [
        {"name": "quiet", "rank": 1, "age": 0},
        {"name": "rush", "rank": 3, "age": 0},
    ]
    repeated = workspace.rank_work(task_id, "quiet", "3")
    assert repeated["priority"]["waiting"] == rush["priority"]["waiting"]

    other = _in_progress(workspace, "Other rank")
    other_ranked = workspace.rank_work(other["id"], "quiet", "2")
    assert other_ranked["priority"]["waiting"] == [{"name": "quiet", "rank": 2, "age": 0}]
    assert len(workspace.get_task(task_id)["priority"]["waiting"]) == 2

    blank = workspace.rank_work(task_id, " ", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this work."

    bad_rank = workspace.rank_work(task_id, "late", "4")
    assert isinstance(bad_rank, Refusal)
    assert bad_rank.message == "Name a rank from 1 to 3."
    assert len(workspace.get_task(task_id)["priority"]["waiting"]) == 2

    draft = workspace.create_task("Draft")
    refused = workspace.rank_work(draft["id"], "quiet", "1")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["priority"]["waiting"] == []


def test_a_serve_takes_the_highest_score_and_ages_the_rest(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.rank_work(task_id, "quiet", "1")
    workspace.rank_work(task_id, "rush", "3")

    first = workspace.serve_next(task_id, " one ")
    assert first["priority"]["serves"] == [{"name": "one", "work": "rush"}]
    assert first["priority"]["waiting"] == [{"name": "quiet", "rank": 1, "age": 1}]
    assert first["status"] == "In Progress"

    workspace.rank_work(task_id, "again", "3")
    second = workspace.serve_next(task_id, "two")
    assert second["priority"]["serves"][-1] == {"name": "two", "work": "again"}
    assert second["priority"]["waiting"] == [{"name": "quiet", "rank": 1, "age": 2}]

    tied = _in_progress(workspace, "Tied scores")
    workspace.rank_work(tied["id"], "ada", "2")
    workspace.rank_work(tied["id"], "grace", "2")
    chosen = workspace.serve_next(tied["id"], "one")
    assert chosen["priority"]["serves"] == [{"name": "one", "work": "ada"}]
    assert chosen["priority"]["waiting"] == [{"name": "grace", "rank": 2, "age": 1}]

    repeated = workspace.serve_next(task_id, "one")
    assert repeated["priority"]["serves"] == second["priority"]["serves"]
    assert repeated["priority"]["waiting"] == [{"name": "quiet", "rank": 1, "age": 2}]

    empty = _in_progress(workspace, "Empty priority")
    missing = workspace.serve_next(empty["id"], "one")
    assert isinstance(missing, Refusal)
    assert missing.message == "Rank work before serving."

    held = _in_progress(workspace, "Held serve")
    held_id = held["id"]
    workspace.rank_work(held_id, "quiet", "1")

    def _then_refuse(connection):
        priority.serve_next(connection, held_id, "one", "2026-10-20T00:00:00Z")
        return bad_request("no")

    rolled = call_in_transaction(workspace.connection, _then_refuse)
    assert isinstance(rolled, Refusal)
    opened = workspace.get_task(held_id)
    assert opened["priority"]["serves"] == []
    assert opened["priority"]["waiting"] == [{"name": "quiet", "rank": 1, "age": 0}]
    restored = workspace.serve_next(held_id, "one")
    assert restored["priority"]["serves"] == [{"name": "one", "work": "quiet"}]


def test_aged_low_rank_is_served_ahead_of_new_high_rank(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.rank_work(task_id, "quiet", "1")
    workspace.rank_work(task_id, "rush", "3")
    workspace.serve_next(task_id, "one")
    workspace.rank_work(task_id, "again", "3")
    workspace.serve_next(task_id, "two")
    workspace.rank_work(task_id, "late", "3")

    third = workspace.serve_next(task_id, "three")
    assert third["priority"]["serves"][-1] == {"name": "three", "work": "quiet"}
    assert third["priority"]["waiting"] == [{"name": "late", "rank": 3, "age": 1}]
    assert third["status"] == "In Progress"
    assert third["schedule"]["turns"] == []

    blank = workspace.serve_next(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this serve."

    draft = workspace.create_task("Draft serve")
    refused = workspace.serve_next(draft["id"], "one")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    other = _in_progress(workspace, "Other serve")
    workspace.rank_work(other["id"], "quiet", "1")
    other_serve = workspace.serve_next(other["id"], "one")
    assert other_serve["priority"]["serves"] == [{"name": "one", "work": "quiet"}]
    assert len(workspace.get_task(task_id)["priority"]["serves"]) == 3
