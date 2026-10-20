from task_manager.domain import learning
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _outcome(name, kind, length):
    return {"name": name, "kind": kind, "length": length}


def _forecast(name, kind, predicted=None, start=None):
    return {"name": name, "kind": kind, "predicted": predicted, "start": start}


def test_an_outcome_keeps_its_kind_and_length(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    recorded = workspace.record_outcome(task_id, " past ", " review ", "2")
    assert recorded["status"] == "In Progress"
    assert recorded["learning"]["outcomes"] == [_outcome("past", "review", 2)]
    assert recorded["learning"]["kinds"] == [{"kind": "review", "predicted": 2}]
    assert recorded["file_reads"] == []
    assert recorded["workflow"]["steps"] == []
    assert recorded["paths"]["steps"] == []
    assert recorded["optimization"]["activities"] == []

    tied = workspace.record_outcome(task_id, "again", "review", "1")
    assert tied["learning"]["kinds"] == [{"kind": "review", "predicted": 1}]
    repeated = workspace.record_outcome(task_id, "past", "export", "1")
    assert repeated["learning"]["outcomes"] == [
        _outcome("past", "review", 2),
        _outcome("again", "review", 1),
    ]
    unchanged = workspace.record_outcome(task_id, "past", " ", "3")
    assert unchanged["learning"]["outcomes"] == repeated["learning"]["outcomes"]

    other = _in_progress(workspace, "Other record")
    other_recorded = workspace.record_outcome(other["id"], "past", "export", "1")
    assert other_recorded["learning"]["outcomes"] == [_outcome("past", "export", 1)]
    assert len(workspace.get_task(task_id)["learning"]["outcomes"]) == 2

    blank = workspace.record_outcome(task_id, " ", "review", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this outcome."

    blank_kind = workspace.record_outcome(task_id, "note", " ", "1")
    assert isinstance(blank_kind, Refusal)
    assert blank_kind.message == "Name this kind."
    assert len(workspace.get_task(task_id)["learning"]["outcomes"]) == 2

    bad_length = workspace.record_outcome(task_id, "note", "review", "3")
    assert isinstance(bad_length, Refusal)
    assert bad_length.message == "Name a length of 1 or 2."
    assert len(workspace.get_task(task_id)["learning"]["outcomes"]) == 2

    full = _in_progress(workspace, "Full record")
    full_id = full["id"]
    for name in ("one", "two", "three", "four"):
        workspace.record_outcome(full_id, name, "review", "1")
    fifth = workspace.record_outcome(full_id, "five", "review", "1")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 outcomes."
    assert len(workspace.get_task(full_id)["learning"]["outcomes"]) == 4

    draft = workspace.create_task("Draft")
    refused = workspace.record_outcome(draft["id"], "past", "review", "1")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["learning"]["outcomes"] == []


def test_a_kind_learns_from_each_new_outcome(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    first = workspace.record_outcome(task_id, "first", "review", "1")
    assert first["learning"]["kinds"] == [{"kind": "review", "predicted": 1}]
    second = workspace.record_outcome(task_id, "second", "review", "2")
    assert second["learning"]["kinds"] == [{"kind": "review", "predicted": 1}]
    third = workspace.record_outcome(task_id, "third", "review", "2")
    assert third["learning"]["kinds"] == [{"kind": "review", "predicted": 2}]
    export = workspace.record_outcome(task_id, "once", "export", "1")
    assert export["learning"]["kinds"] == [
        {"kind": "review", "predicted": 2},
        {"kind": "export", "predicted": 1},
    ]

    named = workspace.name_forecast(task_id, "draft", "review")
    planned = workspace.predict_schedule(task_id)
    assert planned["learning"]["finish"] == 2
    learned = workspace.record_outcome(task_id, "late", "export", "2")
    assert isinstance(learned, Refusal)
    assert learned.message == "This task already has 4 outcomes."
    assert workspace.get_task(task_id)["learning"]["finish"] == 2


def test_a_forecast_uses_the_learned_length(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.record_outcome(task_id, "past", "review", "2")
    workspace.record_outcome(task_id, "again", "review", "2")
    workspace.record_outcome(task_id, "once", "export", "1")

    empty = workspace.predict_schedule(task_id)
    assert isinstance(empty, Refusal)
    assert empty.message == "Name a forecast first."

    draft = workspace.name_forecast(task_id, " draft ", " review ")
    assert draft["learning"]["forecasts"] == [_forecast("draft", "review")]
    assert draft["learning"]["finish"] is None
    ship = workspace.name_forecast(task_id, "ship", " export ")
    assert ship["learning"]["forecasts"] == [
        _forecast("draft", "review"),
        _forecast("ship", "export"),
    ]

    planned = workspace.predict_schedule(task_id)
    assert planned["status"] == "In Progress"
    assert planned["learning"]["finish"] == 3
    assert planned["learning"]["forecasts"] == [
        _forecast("draft", "review", 2, 0),
        _forecast("ship", "export", 1, 2),
    ]
    assert planned["priority"]["waiting"] == []
    repeated = workspace.name_forecast(task_id, "draft", "export")
    assert repeated["learning"]["forecasts"] == planned["learning"]["forecasts"]
    assert repeated["learning"]["finish"] == 3

    unknown = workspace.name_forecast(task_id, "audit-run", "audit")
    assert isinstance(unknown, Refusal)
    assert unknown.message == "Record an outcome for that kind first."

    blank = workspace.name_forecast(task_id, " ", "review")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this forecast."
    blank_kind = workspace.name_forecast(task_id, "note", " ")
    assert isinstance(blank_kind, Refusal)
    assert blank_kind.message == "Name the kind of work."

    updated = workspace.record_outcome(task_id, "extra", "export", "2")
    assert updated["learning"]["finish"] is None
    assert updated["learning"]["kinds"] == [
        {"kind": "review", "predicted": 2},
        {"kind": "export", "predicted": 1},
    ]

    cleared = workspace.name_forecast(task_id, "note", "review")
    assert cleared["learning"]["finish"] is None
    assert cleared["learning"]["forecasts"][0]["start"] is None
    again = workspace.predict_schedule(task_id)
    assert again["learning"]["finish"] == 5
    assert again["learning"]["forecasts"] == [
        _forecast("draft", "review", 2, 0),
        _forecast("ship", "export", 1, 2),
        _forecast("note", "review", 2, 3),
    ]

    full = _in_progress(workspace, "Full forecast")
    full_id = full["id"]
    workspace.record_outcome(full_id, "past", "review", "1")
    for name in ("one", "two", "three", "four"):
        workspace.name_forecast(full_id, name, "review")
    fifth = workspace.name_forecast(full_id, "five", "review")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 forecasts."

    draft_task = workspace.create_task("Draft")
    refused = workspace.name_forecast(draft_task["id"], "draft", "review")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    fresh = _in_progress(workspace, "Rollback")
    fresh_id = fresh["id"]
    workspace.record_outcome(fresh_id, "past", "review", "2")
    workspace.name_forecast(fresh_id, "draft", "review")
    stored = workspace.predict_schedule(fresh_id)
    assert stored["learning"]["finish"] == 2

    def rolled(connection):
        learning.record_outcome(connection, fresh_id, "late", "review", "1", "2026-10-20T00:00:00Z")
        learning.predict_schedule(connection, fresh_id, "2026-10-20T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(fresh_id)
    assert restored["learning"]["outcomes"] == [_outcome("past", "review", 2)]
    assert restored["learning"]["finish"] == 2
    assert restored["learning"]["forecasts"] == [_forecast("draft", "review", 2, 0)]

    other = _in_progress(workspace, "Separate")
    workspace.record_outcome(other["id"], "past", "review", "1")
    assert workspace.get_task(fresh_id)["learning"]["kinds"] == [
        {"kind": "review", "predicted": 2}
    ]
