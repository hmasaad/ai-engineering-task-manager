from task_manager.domain import asha
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _name(name):
    return {"name": name}


def _rung(name, trial, rung, score):
    return {"name": name, "trial": trial, "rung": rung, "score": score}


def _assignment(trial, runner):
    return {"trial": trial, "runner": runner}


def test_a_trial_and_a_runner_are_named_once(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    named = workspace.name_hyperband_trial(task_id, " red ")
    assert named["status"] == "In Progress"
    assert named["hyperband"]["trials"] == [_name("red")]
    assert named["file_reads"] == []
    assert named["workflow"]["steps"] == []
    assert named["allocation"]["agents"] == []
    repeated = workspace.name_hyperband_trial(task_id, "red")
    assert repeated["hyperband"]["trials"] == [_name("red")]
    runner = workspace.name_hyperband_runner(task_id, " ada ")
    assert runner["hyperband"]["runners"] == [_name("ada")]
    again = workspace.name_hyperband_runner(task_id, "ada")
    assert again["hyperband"]["runners"] == [_name("ada")]
    for name in ("blue", "gold", "teal"):
        workspace.name_hyperband_trial(task_id, name)
    assert [item["name"] for item in workspace.get_task(task_id)["hyperband"]["trials"]] == [
        "red",
        "blue",
        "gold",
        "teal",
    ]
    workspace.name_hyperband_runner(task_id, "grace")

    other = _in_progress(workspace, "Other trial")
    other_named = workspace.name_hyperband_trial(other["id"], "red")
    assert other_named["hyperband"]["trials"] == [_name("red")]

    blank = workspace.name_hyperband_trial(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this trial."
    blank_runner = workspace.name_hyperband_runner(task_id, " ")
    assert isinstance(blank_runner, Refusal)
    assert blank_runner.message == "Name this runner."
    fifth = workspace.name_hyperband_trial(task_id, "lime")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 trials."
    third = workspace.name_hyperband_runner(task_id, "mina")
    assert isinstance(third, Refusal)
    assert third.message == "This task already has 2 runners."
    assert len(workspace.get_task(task_id)["hyperband"]["trials"]) == 4
    assert len(workspace.get_task(task_id)["hyperband"]["runners"]) == 2

    draft = workspace.create_task("Draft")
    refused = workspace.name_hyperband_trial(draft["id"], "red")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["hyperband"]["trials"] == []


def test_a_rung_score_keeps_its_score(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_hyperband_trial(task_id, "red")
    recorded = workspace.record_rung(task_id, " one ", " red ", "1", "1")
    assert recorded["hyperband"]["rungs"] == [_rung("one", "red", 1, 1)]
    repeated = workspace.record_rung(task_id, "one", "red", "1", "2")
    assert repeated["hyperband"]["rungs"] == recorded["hyperband"]["rungs"]
    unchanged = workspace.record_rung(task_id, "one", " ", "3", " ")
    assert unchanged["hyperband"]["rungs"] == recorded["hyperband"]["rungs"]

    missing = workspace.record_rung(task_id, "two", "blue", "1", "2")
    assert isinstance(missing, Refusal)
    assert missing.message == "That trial is not on this task."
    again = workspace.record_rung(task_id, "two", "red", "1", "2")
    assert isinstance(again, Refusal)
    assert again.message == "That trial already has this rung."
    early = workspace.record_rung(task_id, "two", "red", "2", "1")
    assert isinstance(early, Refusal)
    assert early.message == "Record two rung scores first."
    blank = workspace.record_rung(task_id, " ", "red", "1", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this rung score."
    blank_trial = workspace.record_rung(task_id, "two", " ", "1", "1")
    assert isinstance(blank_trial, Refusal)
    assert blank_trial.message == "Name the trial."
    bad_rung = workspace.record_rung(task_id, "two", "red", "3", "1")
    assert isinstance(bad_rung, Refusal)
    assert bad_rung.message == "Name a rung of 1 or 2."
    bad_score = workspace.record_rung(task_id, "two", "red", "1", " ")
    assert isinstance(bad_score, Refusal)
    assert bad_score.message == "Name a score of 1 or 2."
    assert len(workspace.get_task(task_id)["hyperband"]["rungs"]) == 1

    full = _in_progress(workspace, "Full rungs")
    full_id = full["id"]
    for name in ("red", "blue", "gold", "teal"):
        workspace.name_hyperband_trial(full_id, name)
    workspace.record_rung(full_id, "one", "red", "1", "1")
    workspace.record_rung(full_id, "two", "blue", "1", "2")
    workspace.record_rung(full_id, "three", "gold", "1", "2")
    workspace.record_rung(full_id, "four", "teal", "1", "1")
    workspace.record_rung(full_id, "five", "blue", "2", "1")
    workspace.record_rung(full_id, "six", "gold", "2", "2")
    seventh = workspace.record_rung(full_id, "seven", "red", "1", "2")
    assert isinstance(seventh, Refusal)
    assert seventh.message == "This task already has 6 rung scores."
    assert len(workspace.get_task(full_id)["hyperband"]["rungs"]) == 6


def test_the_next_trial_goes_to_the_least_loaded_runner(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    for name in ("red", "blue", "gold", "teal"):
        workspace.name_hyperband_trial(task_id, name)
    workspace.name_hyperband_runner(task_id, "ada")
    workspace.name_hyperband_runner(task_id, "grace")
    workspace.record_rung(task_id, "one", "red", "1", "1")
    workspace.record_rung(task_id, "two", "blue", "1", "2")

    early = workspace.schedule_hyperband(task_id)
    assert early["status"] == "In Progress"
    assert early["hyperband"]["promoted"] == [_name("blue")]
    assert early["hyperband"]["assignments"] == [_assignment("blue", "ada")]
    assert early["hyperband"]["winner"] is None
    assert early["fidelity"]["candidates"] == []
    repeated = workspace.schedule_hyperband(task_id)
    assert repeated["hyperband"]["assignments"] == [_assignment("blue", "ada")]

    left_out = workspace.record_rung(task_id, "five", "red", "2", "2")
    assert isinstance(left_out, Refusal)
    assert left_out.message == "That trial is not promoted."
    assert workspace.get_task(task_id)["hyperband"]["assignments"] == [
        _assignment("blue", "ada")
    ]

    workspace.record_rung(task_id, "three", "gold", "1", "2")
    assert workspace.get_task(task_id)["hyperband"]["assignments"] == []
    workspace.schedule_hyperband(task_id)
    workspace.record_rung(task_id, "four", "teal", "1", "1")
    assert workspace.get_task(task_id)["hyperband"]["assignments"] == []
    first = workspace.schedule_hyperband(task_id)
    assert first["hyperband"]["promoted"] == [_name("blue"), _name("gold")]
    assert first["hyperband"]["assignments"] == [_assignment("blue", "ada")]
    second = workspace.schedule_hyperband(task_id)
    assert second["hyperband"]["assignments"] == [
        _assignment("blue", "ada"),
        _assignment("gold", "grace"),
    ]

    workspace.record_rung(task_id, "five", "blue", "2", "1")
    assert workspace.get_task(task_id)["hyperband"]["assignments"] == [
        _assignment("blue", "ada"),
        _assignment("gold", "grace"),
    ]
    workspace.record_rung(task_id, "six", "gold", "2", "2")
    chosen = workspace.schedule_hyperband(task_id)
    assert chosen["hyperband"]["winner"] == "gold"
    assert chosen["hyperband"]["assignments"] == [
        _assignment("blue", "ada"),
        _assignment("gold", "grace"),
    ]

    blocked = workspace.record_rung(task_id, "seven", "red", "2", "2")
    assert isinstance(blocked, Refusal)
    assert blocked.message == "This task already has 6 rung scores."
    assert workspace.get_task(task_id)["hyperband"]["winner"] == "gold"

    tied = _in_progress(workspace, "Tied winner")
    tied_id = tied["id"]
    for name in ("red", "blue", "gold", "teal"):
        workspace.name_hyperband_trial(tied_id, name)
    workspace.name_hyperband_runner(tied_id, "ada")
    workspace.record_rung(tied_id, "one", "red", "1", "1")
    workspace.record_rung(tied_id, "two", "blue", "1", "2")
    workspace.record_rung(tied_id, "three", "gold", "1", "2")
    workspace.record_rung(tied_id, "four", "teal", "1", "1")
    workspace.record_rung(tied_id, "five", "blue", "2", "2")
    workspace.record_rung(tied_id, "six", "gold", "2", "2")
    assert workspace.schedule_hyperband(tied_id)["hyperband"]["winner"] == "blue"

    early_tie = _in_progress(workspace, "Early tie")
    early_id = early_tie["id"]
    for name in ("red", "blue", "gold"):
        workspace.name_hyperband_trial(early_id, name)
    workspace.name_hyperband_runner(early_id, "ada")
    workspace.record_rung(early_id, "one", "red", "1", "1")
    workspace.record_rung(early_id, "two", "blue", "1", "1")
    assert workspace.schedule_hyperband(early_id)["hyperband"]["promoted"] == [_name("red")]
    workspace.record_rung(early_id, "three", "gold", "1", "2")
    overtaken = workspace.schedule_hyperband(early_id)
    assert overtaken["hyperband"]["promoted"] == [_name("gold")]
    assert overtaken["hyperband"]["assignments"] == [_assignment("gold", "ada")]

    empty = _in_progress(workspace, "Empty hyperband")
    empty_id = empty["id"]
    missing = workspace.schedule_hyperband(empty_id)
    assert isinstance(missing, Refusal)
    assert missing.message == "Name a trial first."
    workspace.name_hyperband_trial(empty_id, "red")
    workspace.name_hyperband_trial(empty_id, "blue")
    no_runner = workspace.schedule_hyperband(empty_id)
    assert isinstance(no_runner, Refusal)
    assert no_runner.message == "Name a runner first."
    workspace.name_hyperband_runner(empty_id, "ada")
    workspace.record_rung(empty_id, "one", "red", "1", "1")
    waiting = workspace.schedule_hyperband(empty_id)
    assert isinstance(waiting, Refusal)
    assert waiting.message == "Record two rung scores first."

    draft = workspace.create_task("Draft")
    draft_refused = workspace.schedule_hyperband(draft["id"])
    assert isinstance(draft_refused, Refusal)
    assert draft_refused.message == "The task must be In Progress."

    fresh = _in_progress(workspace, "Rollback")
    fresh_id = fresh["id"]
    for name in ("red", "blue", "gold"):
        workspace.name_hyperband_trial(fresh_id, name)
    workspace.name_hyperband_runner(fresh_id, "ada")
    workspace.record_rung(fresh_id, "one", "red", "1", "1")
    workspace.record_rung(fresh_id, "two", "blue", "1", "2")
    stored = workspace.schedule_hyperband(fresh_id)
    assert stored["hyperband"]["assignments"] == [_assignment("blue", "ada")]

    def rolled(connection):
        asha.record_rung(connection, fresh_id, "three", "gold", "1", "2", "2026-10-21T00:00:00Z")
        asha.schedule(connection, fresh_id, "2026-10-21T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(fresh_id)
    assert len(restored["hyperband"]["rungs"]) == 2
    assert restored["hyperband"]["assignments"] == [_assignment("blue", "ada")]
    assert restored["hyperband"]["promoted"] == [_name("blue")]
