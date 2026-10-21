from task_manager.domain import fidelity
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _candidate(name):
    return {"name": name}


def _measurement(name, candidate, level, score):
    return {"name": name, "candidate": candidate, "fidelity": level, "score": score}


def test_a_candidate_is_named_once(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    named = workspace.name_fidelity_candidate(task_id, " ada ")
    assert named["status"] == "In Progress"
    assert named["fidelity"]["candidates"] == [_candidate("ada")]
    assert named["file_reads"] == []
    assert named["workflow"]["steps"] == []
    assert named["search"]["designs"] == []
    repeated = workspace.name_fidelity_candidate(task_id, "ada")
    assert repeated["fidelity"]["candidates"] == [_candidate("ada")]
    for name in ("grace", "mina", "nora"):
        workspace.name_fidelity_candidate(task_id, name)
    assert [item["name"] for item in workspace.get_task(task_id)["fidelity"]["candidates"]] == [
        "ada",
        "grace",
        "mina",
        "nora",
    ]

    other = _in_progress(workspace, "Other candidate")
    other_named = workspace.name_fidelity_candidate(other["id"], "ada")
    assert other_named["fidelity"]["candidates"] == [_candidate("ada")]

    blank = workspace.name_fidelity_candidate(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this candidate."
    fifth = workspace.name_fidelity_candidate(task_id, "otis")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 candidates."
    assert len(workspace.get_task(task_id)["fidelity"]["candidates"]) == 4

    draft = workspace.create_task("Draft")
    refused = workspace.name_fidelity_candidate(draft["id"], "ada")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["fidelity"]["candidates"] == []


def test_a_measurement_keeps_its_score(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_fidelity_candidate(task_id, "ada")
    recorded = workspace.record_fidelity(task_id, " one ", " ada ", "1", "2")
    assert recorded["fidelity"]["measurements"] == [_measurement("one", "ada", 1, 2)]
    repeated = workspace.record_fidelity(task_id, "one", "ada", "1", "1")
    assert repeated["fidelity"]["measurements"] == recorded["fidelity"]["measurements"]
    unchanged = workspace.record_fidelity(task_id, "one", " ", "3", " ")
    assert unchanged["fidelity"]["measurements"] == recorded["fidelity"]["measurements"]

    missing = workspace.record_fidelity(task_id, "two", "grace", "1", "1")
    assert isinstance(missing, Refusal)
    assert missing.message == "That candidate is not on this task."
    again = workspace.record_fidelity(task_id, "two", "ada", "1", "1")
    assert isinstance(again, Refusal)
    assert again.message == "That candidate already has this fidelity."
    early = workspace.record_fidelity(task_id, "two", "ada", "2", "1")
    assert isinstance(early, Refusal)
    assert early.message == "Halve the field before an expensive measurement."
    blank = workspace.record_fidelity(task_id, " ", "ada", "1", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this measurement."
    blank_candidate = workspace.record_fidelity(task_id, "two", " ", "1", "1")
    assert isinstance(blank_candidate, Refusal)
    assert blank_candidate.message == "Name the candidate."
    bad_fidelity = workspace.record_fidelity(task_id, "two", "ada", "3", "1")
    assert isinstance(bad_fidelity, Refusal)
    assert bad_fidelity.message == "Name a fidelity of 1 or 2."
    bad_score = workspace.record_fidelity(task_id, "two", "ada", "1", " ")
    assert isinstance(bad_score, Refusal)
    assert bad_score.message == "Name a score of 1 or 2."
    assert len(workspace.get_task(task_id)["fidelity"]["measurements"]) == 1

    full = _in_progress(workspace, "Full measurements")
    full_id = full["id"]
    for name in ("ada", "grace", "mina", "nora"):
        workspace.name_fidelity_candidate(full_id, name)
    workspace.record_fidelity(full_id, "one", "ada", "1", "1")
    workspace.record_fidelity(full_id, "two", "grace", "1", "2")
    workspace.record_fidelity(full_id, "three", "mina", "1", "2")
    workspace.record_fidelity(full_id, "four", "nora", "1", "1")
    workspace.halve_candidates(full_id)
    workspace.record_fidelity(full_id, "five", "grace", "2", "1")
    workspace.record_fidelity(full_id, "six", "mina", "2", "2")
    seventh = workspace.record_fidelity(full_id, "seven", "ada", "1", "1")
    assert isinstance(seventh, Refusal)
    assert seventh.message == "This task already has 6 measurements."
    assert len(workspace.get_task(full_id)["fidelity"]["measurements"]) == 6


def test_the_winner_is_the_best_expensive_score(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    for name in ("ada", "grace", "mina", "nora"):
        workspace.name_fidelity_candidate(task_id, name)
    workspace.record_fidelity(task_id, "one", "ada", "1", "1")
    workspace.record_fidelity(task_id, "two", "grace", "1", "2")
    workspace.record_fidelity(task_id, "three", "mina", "1", "2")
    workspace.record_fidelity(task_id, "four", "nora", "1", "1")

    halved = workspace.halve_candidates(task_id)
    assert halved["status"] == "In Progress"
    assert halved["fidelity"]["kept"] == [_candidate("grace"), _candidate("mina")]
    assert halved["fidelity"]["winner"] is None
    assert halved["bandit"]["actions"] == []

    left_out = workspace.record_fidelity(task_id, "five", "ada", "2", "2")
    assert isinstance(left_out, Refusal)
    assert left_out.message == "That candidate was not kept."
    assert workspace.get_task(task_id)["fidelity"]["kept"] == [
        _candidate("grace"),
        _candidate("mina"),
    ]

    workspace.record_fidelity(task_id, "five", "grace", "2", "1")
    workspace.record_fidelity(task_id, "six", "mina", "2", "2")
    chosen = workspace.halve_candidates(task_id)
    assert chosen["fidelity"]["kept"] == [_candidate("grace"), _candidate("mina")]
    assert chosen["fidelity"]["winner"] == "mina"

    tied = _in_progress(workspace, "Tied winner")
    tied_id = tied["id"]
    for name in ("ada", "grace", "mina", "nora"):
        workspace.name_fidelity_candidate(tied_id, name)
    workspace.record_fidelity(tied_id, "one", "ada", "1", "1")
    workspace.record_fidelity(tied_id, "two", "grace", "1", "2")
    workspace.record_fidelity(tied_id, "three", "mina", "1", "2")
    workspace.record_fidelity(tied_id, "four", "nora", "1", "1")
    workspace.halve_candidates(tied_id)
    workspace.record_fidelity(tied_id, "five", "grace", "2", "2")
    workspace.record_fidelity(tied_id, "six", "mina", "2", "2")
    tie = workspace.halve_candidates(tied_id)
    assert tie["fidelity"]["winner"] == "grace"

    pair = _in_progress(workspace, "Two candidates")
    pair_id = pair["id"]
    workspace.name_fidelity_candidate(pair_id, "ada")
    workspace.name_fidelity_candidate(pair_id, "grace")
    workspace.record_fidelity(pair_id, "one", "ada", "1", "2")
    workspace.record_fidelity(pair_id, "two", "grace", "1", "1")
    kept_one = workspace.halve_candidates(pair_id)
    assert kept_one["fidelity"]["kept"] == [_candidate("ada")]
    assert kept_one["fidelity"]["winner"] is None

    trio = _in_progress(workspace, "Three candidates")
    trio_id = trio["id"]
    for name, score in (("ada", "2"), ("grace", "1"), ("mina", "2")):
        workspace.name_fidelity_candidate(trio_id, name)
        workspace.record_fidelity(trio_id, name, name, "1", score)
    assert workspace.halve_candidates(trio_id)["fidelity"]["kept"] == [_candidate("ada")]

    empty = _in_progress(workspace, "Empty fidelity")
    empty_id = empty["id"]
    missing = workspace.halve_candidates(empty_id)
    assert isinstance(missing, Refusal)
    assert missing.message == "Name a candidate first."
    workspace.name_fidelity_candidate(empty_id, "ada")
    alone = workspace.halve_candidates(empty_id)
    assert isinstance(alone, Refusal)
    assert alone.message == "Name another candidate first."
    workspace.name_fidelity_candidate(empty_id, "grace")
    workspace.record_fidelity(empty_id, "one", "ada", "1", "2")
    waiting = workspace.halve_candidates(empty_id)
    assert isinstance(waiting, Refusal)
    assert waiting.message == "Record a cheap measurement for every candidate first."

    cleared = workspace.name_fidelity_candidate(pair_id, "mina")
    assert cleared["fidelity"]["kept"] == []
    assert cleared["fidelity"]["winner"] is None

    draft = workspace.create_task("Draft")
    draft_refused = workspace.halve_candidates(draft["id"])
    assert isinstance(draft_refused, Refusal)
    assert draft_refused.message == "The task must be In Progress."

    fresh = _in_progress(workspace, "Rollback")
    fresh_id = fresh["id"]
    workspace.name_fidelity_candidate(fresh_id, "ada")
    workspace.name_fidelity_candidate(fresh_id, "grace")
    workspace.record_fidelity(fresh_id, "one", "ada", "1", "2")
    workspace.record_fidelity(fresh_id, "two", "grace", "1", "1")
    stored = workspace.halve_candidates(fresh_id)
    assert stored["fidelity"]["kept"] == [_candidate("ada")]
    assert stored["fidelity"]["winner"] is None

    def rolled(connection):
        fidelity.record_fidelity(
            connection, fresh_id, "three", "ada", "2", "2", "2026-10-21T00:00:00Z"
        )
        fidelity.halve(connection, fresh_id, "2026-10-21T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(fresh_id)
    assert len(restored["fidelity"]["measurements"]) == 2
    assert restored["fidelity"]["kept"] == [_candidate("ada")]
    assert restored["fidelity"]["winner"] is None
