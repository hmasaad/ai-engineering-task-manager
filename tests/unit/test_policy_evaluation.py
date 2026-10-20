from task_manager.domain import evaluation
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _log(name, state, action, reward):
    return {"name": name, "state": state, "action": action, "reward": reward}


def test_a_logged_step_keeps_its_reward(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    recorded = workspace.record_logged_step(task_id, " one ", " rush ", " ada ", "1")
    assert recorded["status"] == "In Progress"
    assert recorded["evaluation"]["logs"] == [_log("one", "rush", "ada", 1)]
    assert recorded["file_reads"] == []
    assert recorded["workflow"]["steps"] == []
    assert recorded["bandit"]["actions"] == []
    repeated = workspace.record_logged_step(task_id, "one", "quiet", "grace", "2")
    assert repeated["evaluation"]["logs"] == [_log("one", "rush", "ada", 1)]
    unchanged = workspace.record_logged_step(task_id, "one", " ", " ", "3")
    assert unchanged["evaluation"]["logs"] == repeated["evaluation"]["logs"]

    other = _in_progress(workspace, "Other log")
    other_recorded = workspace.record_logged_step(other["id"], "one", "quiet", "grace", "2")
    assert other_recorded["evaluation"]["logs"] == [_log("one", "quiet", "grace", 2)]
    assert len(workspace.get_task(task_id)["evaluation"]["logs"]) == 1

    blank = workspace.record_logged_step(task_id, " ", "rush", "ada", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this step."
    blank_state = workspace.record_logged_step(task_id, "note", " ", "ada", "1")
    assert isinstance(blank_state, Refusal)
    assert blank_state.message == "Name the state."
    blank_action = workspace.record_logged_step(task_id, "note", "rush", " ", "1")
    assert isinstance(blank_action, Refusal)
    assert blank_action.message == "Name the action."
    bad_reward = workspace.record_logged_step(task_id, "note", "rush", "ada", "3")
    assert isinstance(bad_reward, Refusal)
    assert bad_reward.message == "Name a reward of 1 or 2."
    assert len(workspace.get_task(task_id)["evaluation"]["logs"]) == 1

    full = _in_progress(workspace, "Full log")
    full_id = full["id"]
    for name in ("one", "two", "three", "four"):
        workspace.record_logged_step(full_id, name, "rush", "ada", "1")
    fifth = workspace.record_logged_step(full_id, "five", "rush", "ada", "1")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 logged steps."
    assert len(workspace.get_task(full_id)["evaluation"]["logs"]) == 4

    draft = workspace.create_task("Draft")
    refused = workspace.record_logged_step(draft["id"], "one", "rush", "ada", "1")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["evaluation"]["logs"] == []


def test_a_rule_names_one_action_for_a_state(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    missing = workspace.name_policy_rule(task_id, "rush", "ada")
    assert isinstance(missing, Refusal)
    assert missing.message == "Name a logged step first."
    empty = workspace.evaluate_policy(task_id)
    assert isinstance(empty, Refusal)
    assert empty.message == "Name a logged step first."

    workspace.record_logged_step(task_id, "one", "rush", "ada", "1")
    no_rule = workspace.evaluate_policy(task_id)
    assert isinstance(no_rule, Refusal)
    assert no_rule.message == "Name a policy rule first."

    named = workspace.name_policy_rule(task_id, " rush ", " ada ")
    assert named["evaluation"]["rules"] == [{"state": "rush", "action": "ada"}]
    again = workspace.name_policy_rule(task_id, "rush", "ada")
    assert again["evaluation"]["rules"] == named["evaluation"]["rules"]
    scored = workspace.evaluate_policy(task_id)
    assert scored["evaluation"]["score"] == {"total": 1, "count": 1}
    kept = workspace.name_policy_rule(task_id, "rush", "ada")
    assert kept["evaluation"]["score"] == {"total": 1, "count": 1}

    changed = workspace.name_policy_rule(task_id, "rush", "grace")
    assert changed["evaluation"]["rules"] == [{"state": "rush", "action": "grace"}]
    assert changed["evaluation"]["score"] is None
    unknown = workspace.name_policy_rule(task_id, "quiet", "ada")
    assert isinstance(unknown, Refusal)
    assert unknown.message == "That state is not in the log."
    blank_state = workspace.name_policy_rule(task_id, " ", "ada")
    assert isinstance(blank_state, Refusal)
    assert blank_state.message == "Name the state for this rule."
    blank_action = workspace.name_policy_rule(task_id, "rush", " ")
    assert isinstance(blank_action, Refusal)
    assert blank_action.message == "Name the action for this rule."

    unmatched = workspace.evaluate_policy(task_id)
    assert isinstance(unmatched, Refusal)
    assert unmatched.message == "No logged step matches this policy."
    assert workspace.get_task(task_id)["evaluation"]["score"] is None


def test_evaluation_counts_only_matching_steps(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.record_logged_step(task_id, "one", "rush", "ada", "1")
    workspace.record_logged_step(task_id, "two", "rush", "grace", "2")
    workspace.record_logged_step(task_id, "three", "quiet", "ada", "2")
    workspace.name_policy_rule(task_id, "rush", "grace")
    workspace.name_policy_rule(task_id, "quiet", "ada")
    scored = workspace.evaluate_policy(task_id)
    assert scored["status"] == "In Progress"
    assert scored["evaluation"]["score"] == {"total": 4, "count": 2}
    assert scored["learning"]["outcomes"] == []

    added = workspace.record_logged_step(task_id, "four", "quiet", "ada", "1")
    assert added["evaluation"]["score"] is None
    again = workspace.evaluate_policy(task_id)
    assert again["evaluation"]["score"] == {"total": 5, "count": 3}

    draft = workspace.create_task("Draft")
    refused = workspace.evaluate_policy(draft["id"])
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    fresh = _in_progress(workspace, "Rollback")
    fresh_id = fresh["id"]
    workspace.record_logged_step(fresh_id, "one", "rush", "ada", "1")
    workspace.record_logged_step(fresh_id, "two", "rush", "grace", "2")
    workspace.record_logged_step(fresh_id, "three", "quiet", "ada", "2")
    workspace.name_policy_rule(fresh_id, "rush", "grace")
    workspace.name_policy_rule(fresh_id, "quiet", "ada")
    stored = workspace.evaluate_policy(fresh_id)
    assert stored["evaluation"]["score"] == {"total": 4, "count": 2}

    def rolled(connection):
        evaluation.record_log(
            connection, fresh_id, "four", "quiet", "ada", "1", "2026-10-20T00:00:00Z"
        )
        evaluation.evaluate(connection, fresh_id, "2026-10-20T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(fresh_id)
    assert len(restored["evaluation"]["logs"]) == 3
    assert restored["evaluation"]["score"] == {"total": 4, "count": 2}

    other = _in_progress(workspace, "Separate")
    workspace.record_logged_step(other["id"], "one", "rush", "ada", "2")
    assert workspace.get_task(fresh_id)["evaluation"]["score"] == {"total": 4, "count": 2}
