from task_manager.domain import safety
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _action(name, risk):
    return {"name": name, "risk": risk}


def _probe(name, state, action, reward):
    return {"name": name, "state": state, "action": action, "reward": reward}


def _effect(state, action, instead, effect):
    return {"state": state, "action": action, "instead": instead, "effect": effect}


def test_an_action_keeps_its_risk(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    named = workspace.name_safe_action(task_id, " ada ", "1")
    assert named["status"] == "In Progress"
    assert named["safety"]["actions"] == [_action("ada", 1)]
    assert named["file_reads"] == []
    assert named["workflow"]["steps"] == []
    assert named["evaluation"]["logs"] == []
    repeated = workspace.name_safe_action(task_id, "ada", "2")
    assert repeated["safety"]["actions"] == [_action("ada", 1)]
    second = workspace.name_safe_action(task_id, "grace", "2")
    assert second["safety"]["actions"] == [_action("ada", 1), _action("grace", 2)]

    other = _in_progress(workspace, "Other risk")
    other_named = workspace.name_safe_action(other["id"], "ada", "2")
    assert other_named["safety"]["actions"] == [_action("ada", 2)]
    assert len(workspace.get_task(task_id)["safety"]["actions"]) == 2

    blank = workspace.name_safe_action(task_id, " ", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this action."
    bad_risk = workspace.name_safe_action(task_id, "note", "3")
    assert isinstance(bad_risk, Refusal)
    assert bad_risk.message == "Name a risk of 1 or 2."
    third = workspace.name_safe_action(task_id, "mina", "1")
    assert isinstance(third, Refusal)
    assert third.message == "This task already has 2 actions."
    assert len(workspace.get_task(task_id)["safety"]["actions"]) == 2

    draft = workspace.create_task("Draft")
    refused = workspace.name_safe_action(draft["id"], "ada", "1")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["safety"]["actions"] == []


def test_a_probe_is_allowed_only_for_a_safe_action(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_safe_action(task_id, "ada", "1")
    workspace.name_safe_action(task_id, "grace", "2")
    compared = workspace.compare_actions(task_id, "rush", "grace", "ada")
    assert isinstance(compared, Refusal)
    assert compared.message == "Name a probe first."

    recorded = workspace.record_probe(task_id, " one ", " rush ", " ada ", "1")
    assert recorded["safety"]["probes"] == [_probe("one", "rush", "ada", 1)]
    repeated = workspace.record_probe(task_id, "one", "quiet", "ada", "2")
    assert repeated["safety"]["probes"] == recorded["safety"]["probes"]
    unchanged = workspace.record_probe(task_id, "one", " ", " ", "3")
    assert unchanged["safety"]["probes"] == recorded["safety"]["probes"]

    unsafe = workspace.record_probe(task_id, "two", "rush", "grace", "2")
    assert isinstance(unsafe, Refusal)
    assert unsafe.message == "That action is not safe to explore."
    missing = workspace.record_probe(task_id, "two", "rush", "mina", "1")
    assert isinstance(missing, Refusal)
    assert missing.message == "That action is not on this task."
    blank = workspace.record_probe(task_id, " ", "rush", "ada", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this probe."
    blank_state = workspace.record_probe(task_id, "two", " ", "ada", "1")
    assert isinstance(blank_state, Refusal)
    assert blank_state.message == "Name the state."
    blank_action = workspace.record_probe(task_id, "two", "rush", " ", "1")
    assert isinstance(blank_action, Refusal)
    assert blank_action.message == "Name the action."
    bad_reward = workspace.record_probe(task_id, "two", "rush", "ada", "3")
    assert isinstance(bad_reward, Refusal)
    assert bad_reward.message == "Name a reward of 1 or 2."
    assert len(workspace.get_task(task_id)["safety"]["probes"]) == 1

    full = _in_progress(workspace, "Full probes")
    full_id = full["id"]
    workspace.name_safe_action(full_id, "ada", "1")
    for name in ("one", "two", "three", "four"):
        workspace.record_probe(full_id, name, "rush", "ada", "1")
    fifth = workspace.record_probe(full_id, "five", "rush", "ada", "1")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 probes."
    assert len(workspace.get_task(full_id)["safety"]["probes"]) == 4


def test_the_effect_is_the_reward_difference_in_one_state(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_safe_action(task_id, "ada", "1")
    workspace.name_safe_action(task_id, "grace", "1")
    workspace.record_probe(task_id, "one", "rush", "ada", "1")
    workspace.record_probe(task_id, "early", "rush", "ada", "2")
    workspace.record_probe(task_id, "two", "rush", "grace", "2")

    gained = workspace.compare_actions(task_id, " rush ", " grace ", " ada ")
    assert gained["status"] == "In Progress"
    assert gained["safety"]["effect"] == _effect("rush", "grace", "ada", 1)
    assert gained["bandit"]["actions"] == []
    lost = workspace.compare_actions(task_id, "rush", "ada", "grace")
    assert lost["safety"]["effect"] == _effect("rush", "ada", "grace", -1)

    tied = _in_progress(workspace, "Tie")
    tied_id = tied["id"]
    workspace.name_safe_action(tied_id, "ada", "1")
    workspace.name_safe_action(tied_id, "grace", "1")
    workspace.record_probe(tied_id, "one", "rush", "ada", "2")
    workspace.record_probe(tied_id, "two", "rush", "grace", "2")
    same = workspace.compare_actions(tied_id, "rush", "grace", "ada")
    assert same["safety"]["effect"] == _effect("rush", "grace", "ada", 0)

    itself = workspace.compare_actions(task_id, "rush", "ada", "ada")
    assert isinstance(itself, Refusal)
    assert itself.message == "An action cannot replace itself."
    other_state = workspace.compare_actions(task_id, "quiet", "grace", "ada")
    assert isinstance(other_state, Refusal)
    assert other_state.message == "That comparison needs both actions in this state."
    blank_state = workspace.compare_actions(task_id, " ", "grace", "ada")
    assert isinstance(blank_state, Refusal)
    assert blank_state.message == "Name the state to compare."
    blank_action = workspace.compare_actions(task_id, "rush", " ", "ada")
    assert isinstance(blank_action, Refusal)
    assert blank_action.message == "Name the action."
    blank_instead = workspace.compare_actions(task_id, "rush", "grace", " ")
    assert isinstance(blank_instead, Refusal)
    assert blank_instead.message == "Name the action it replaces."

    cleared = workspace.record_probe(task_id, "three", "quiet", "ada", "1")
    assert cleared["safety"]["effect"] is None

    draft = workspace.create_task("Draft")
    refused = workspace.compare_actions(draft["id"], "rush", "grace", "ada")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    fresh = _in_progress(workspace, "Rollback")
    fresh_id = fresh["id"]
    workspace.name_safe_action(fresh_id, "ada", "1")
    workspace.name_safe_action(fresh_id, "grace", "1")
    workspace.record_probe(fresh_id, "one", "rush", "ada", "1")
    workspace.record_probe(fresh_id, "two", "rush", "grace", "2")
    stored = workspace.compare_actions(fresh_id, "rush", "grace", "ada")
    assert stored["safety"]["effect"] == _effect("rush", "grace", "ada", 1)

    def rolled(connection):
        safety.record_probe(
            connection, fresh_id, "three", "rush", "grace", "1", "2026-10-20T00:00:00Z"
        )
        safety.compare_actions(
            connection, fresh_id, "rush", "grace", "ada", "2026-10-20T00:00:00Z"
        )
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(fresh_id)
    assert len(restored["safety"]["probes"]) == 2
    assert restored["safety"]["effect"] == _effect("rush", "grace", "ada", 1)
