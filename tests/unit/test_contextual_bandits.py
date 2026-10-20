from task_manager.domain import bandit
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _trial(name, context, action, reward):
    return {"name": name, "context": context, "action": action, "reward": reward}


def _value(context, action, total, count):
    return {"context": context, "action": action, "total": total, "count": count}


def test_an_action_and_a_context_keep_their_names(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    named = workspace.name_bandit_action(task_id, " ada ")
    assert named["status"] == "In Progress"
    assert named["bandit"]["actions"] == [{"name": "ada"}]
    assert named["file_reads"] == []
    assert named["workflow"]["steps"] == []
    assert named["learning"]["outcomes"] == []
    repeated = workspace.name_bandit_action(task_id, "ada")
    assert repeated["bandit"]["actions"] == [{"name": "ada"}]
    second = workspace.name_bandit_action(task_id, "grace")
    assert second["bandit"]["actions"] == [{"name": "ada"}, {"name": "grace"}]

    context = workspace.name_bandit_context(task_id, " rush ")
    assert context["bandit"]["contexts"] == [{"name": "rush"}]
    again = workspace.name_bandit_context(task_id, "rush")
    assert again["bandit"]["contexts"] == [{"name": "rush"}]

    other = _in_progress(workspace, "Other choice")
    other_named = workspace.name_bandit_action(other["id"], "ada")
    assert other_named["bandit"]["actions"] == [{"name": "ada"}]
    assert len(workspace.get_task(task_id)["bandit"]["actions"]) == 2

    blank = workspace.name_bandit_action(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this action."
    blank_context = workspace.name_bandit_context(task_id, " ")
    assert isinstance(blank_context, Refusal)
    assert blank_context.message == "Name this context."

    third = workspace.name_bandit_action(task_id, "mina")
    assert isinstance(third, Refusal)
    assert third.message == "This task already has 2 actions."
    assert len(workspace.get_task(task_id)["bandit"]["actions"]) == 2

    full = _in_progress(workspace, "Full contexts")
    full_id = full["id"]
    for name in ("one", "two", "three", "four"):
        workspace.name_bandit_context(full_id, name)
    fifth = workspace.name_bandit_context(full_id, "five")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 contexts."

    draft = workspace.create_task("Draft")
    refused = workspace.name_bandit_action(draft["id"], "ada")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    refused_context = workspace.name_bandit_context(draft["id"], "rush")
    assert isinstance(refused_context, Refusal)
    assert refused_context.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["bandit"]["actions"] == []


def test_a_trial_keeps_its_reward(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_bandit_action(task_id, "ada")
    workspace.name_bandit_action(task_id, "grace")
    workspace.name_bandit_context(task_id, "rush")
    chosen = workspace.choose_bandit_action(task_id, "rush")
    assert chosen["bandit"]["choice"] == {"context": "rush", "action": "ada"}

    recorded = workspace.record_bandit_trial(task_id, " one ", " rush ", " ada ", "1")
    assert recorded["bandit"]["trials"] == [_trial("one", "rush", "ada", 1)]
    assert recorded["bandit"]["values"] == [_value("rush", "ada", 1, 1)]
    assert recorded["bandit"]["choice"] is None
    repeated = workspace.record_bandit_trial(task_id, "one", "rush", "grace", "2")
    assert repeated["bandit"]["trials"] == recorded["bandit"]["trials"]
    unchanged = workspace.record_bandit_trial(task_id, "one", " ", " ", "3")
    assert unchanged["bandit"]["trials"] == recorded["bandit"]["trials"]

    bad_reward = workspace.record_bandit_trial(task_id, "note", "rush", "ada", "3")
    assert isinstance(bad_reward, Refusal)
    assert bad_reward.message == "Name a reward of 1 or 2."
    missing_context = workspace.record_bandit_trial(task_id, "note", "quiet", "ada", "1")
    assert isinstance(missing_context, Refusal)
    assert missing_context.message == "That context is not on this task."
    missing_action = workspace.record_bandit_trial(task_id, "note", "rush", "mina", "1")
    assert isinstance(missing_action, Refusal)
    assert missing_action.message == "That action is not on this task."
    blank = workspace.record_bandit_trial(task_id, " ", "rush", "ada", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this trial."
    blank_context = workspace.record_bandit_trial(task_id, "note", " ", "ada", "1")
    assert isinstance(blank_context, Refusal)
    assert blank_context.message == "Name the context."
    blank_action = workspace.record_bandit_trial(task_id, "note", "rush", " ", "1")
    assert isinstance(blank_action, Refusal)
    assert blank_action.message == "Name the action."
    assert len(workspace.get_task(task_id)["bandit"]["trials"]) == 1

    full = _in_progress(workspace, "Full trials")
    full_id = full["id"]
    workspace.name_bandit_action(full_id, "ada")
    workspace.name_bandit_context(full_id, "rush")
    for name in ("one", "two", "three", "four"):
        workspace.record_bandit_trial(full_id, name, "rush", "ada", "1")
    fifth = workspace.record_bandit_trial(full_id, "five", "rush", "ada", "1")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 trials."
    assert len(workspace.get_task(full_id)["bandit"]["trials"]) == 4


def test_a_choice_follows_the_learned_reward(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    empty = workspace.choose_bandit_action(task_id, "rush")
    assert isinstance(empty, Refusal)
    assert empty.message == "Name an action first."

    workspace.name_bandit_action(task_id, "ada")
    workspace.name_bandit_action(task_id, "grace")
    missing = workspace.choose_bandit_action(task_id, "rush")
    assert isinstance(missing, Refusal)
    assert missing.message == "Name a context first."
    blank = workspace.choose_bandit_action(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name the context to choose."

    workspace.name_bandit_context(task_id, "rush")
    unknown = workspace.choose_bandit_action(task_id, "quiet")
    assert isinstance(unknown, Refusal)
    assert unknown.message == "That context is not on this task."

    first = workspace.choose_bandit_action(task_id, " rush ")
    assert first["status"] == "In Progress"
    assert first["bandit"]["choice"] == {"context": "rush", "action": "ada"}
    assert first["optimization"]["activities"] == []
    kept = workspace.name_bandit_action(task_id, "ada")
    assert kept["bandit"]["choice"] == {"context": "rush", "action": "ada"}

    workspace.record_bandit_trial(task_id, "one", "rush", "ada", "1")
    second = workspace.choose_bandit_action(task_id, "rush")
    assert second["bandit"]["choice"] == {"context": "rush", "action": "grace"}

    workspace.record_bandit_trial(task_id, "two", "rush", "grace", "1")
    tied = workspace.choose_bandit_action(task_id, "rush")
    assert tied["bandit"]["choice"] == {"context": "rush", "action": "ada"}
    assert tied["bandit"]["values"] == [
        _value("rush", "ada", 1, 1),
        _value("rush", "grace", 1, 1),
    ]

    workspace.record_bandit_trial(task_id, "three", "rush", "grace", "2")
    learned = workspace.choose_bandit_action(task_id, "rush")
    assert learned["bandit"]["values"] == [
        _value("rush", "ada", 1, 1),
        _value("rush", "grace", 3, 2),
    ]
    assert learned["bandit"]["choice"] == {"context": "rush", "action": "grace"}

    workspace.name_bandit_context(task_id, "quiet")
    separate = workspace.choose_bandit_action(task_id, "quiet")
    assert separate["bandit"]["choice"] == {"context": "quiet", "action": "ada"}

    draft = workspace.create_task("Draft")
    refused = workspace.choose_bandit_action(draft["id"], "rush")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    fresh = _in_progress(workspace, "Rollback")
    fresh_id = fresh["id"]
    workspace.name_bandit_action(fresh_id, "ada")
    workspace.name_bandit_action(fresh_id, "grace")
    workspace.name_bandit_context(fresh_id, "rush")
    workspace.record_bandit_trial(fresh_id, "one", "rush", "ada", "1")
    workspace.record_bandit_trial(fresh_id, "two", "rush", "grace", "1")
    stored = workspace.choose_bandit_action(fresh_id, "rush")
    assert stored["bandit"]["choice"] == {"context": "rush", "action": "ada"}

    def rolled(connection):
        bandit.record_trial(
            connection, fresh_id, "three", "rush", "grace", "2", "2026-10-20T00:00:00Z"
        )
        bandit.choose_action(connection, fresh_id, "rush", "2026-10-20T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(fresh_id)
    assert restored["bandit"]["trials"] == [
        _trial("one", "rush", "ada", 1),
        _trial("two", "rush", "grace", 1),
    ]
    assert restored["bandit"]["choice"] == {"context": "rush", "action": "ada"}
