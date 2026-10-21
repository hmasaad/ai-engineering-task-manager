from task_manager.domain import exploration
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _arm(name):
    return {"name": name}


def _pull(name, context, arm, reward):
    return {"name": name, "context": context, "arm": arm, "reward": reward}


def _draw(context, arm, sample):
    return {"context": context, "arm": arm, "sample": sample}


def test_an_arm_and_a_context_keep_their_names(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    named = workspace.name_explore_arm(task_id, " ada ")
    assert named["status"] == "In Progress"
    assert named["exploration"]["arms"] == [_arm("ada")]
    assert named["file_reads"] == []
    assert named["workflow"]["steps"] == []
    assert named["bandit"]["actions"] == []
    assert named["safety"]["actions"] == []
    repeated = workspace.name_explore_arm(task_id, "ada")
    assert repeated["exploration"]["arms"] == [_arm("ada")]
    second = workspace.name_explore_arm(task_id, "grace")
    assert second["exploration"]["arms"] == [_arm("ada"), _arm("grace")]

    other = _in_progress(workspace, "Other arm")
    other_named = workspace.name_explore_arm(other["id"], "ada")
    assert other_named["exploration"]["arms"] == [_arm("ada")]
    assert len(workspace.get_task(task_id)["exploration"]["arms"]) == 2

    blank = workspace.name_explore_arm(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this arm."
    third = workspace.name_explore_arm(task_id, "mina")
    assert isinstance(third, Refusal)
    assert third.message == "This task already has 2 arms."
    assert len(workspace.get_task(task_id)["exploration"]["arms"]) == 2

    rush = workspace.name_explore_context(task_id, " rush ")
    assert rush["exploration"]["contexts"] == [_arm("rush")]
    again = workspace.name_explore_context(task_id, "rush")
    assert again["exploration"]["contexts"] == [_arm("rush")]
    quiet = workspace.name_explore_context(task_id, "quiet")
    assert quiet["exploration"]["contexts"] == [_arm("rush"), _arm("quiet")]
    extra = workspace.name_explore_context(task_id, "night")
    assert isinstance(extra, Refusal)
    assert extra.message == "This task already has 2 contexts."
    blank_context = workspace.name_explore_context(task_id, " ")
    assert isinstance(blank_context, Refusal)
    assert blank_context.message == "Name this context."

    draft = workspace.create_task("Draft")
    refused = workspace.name_explore_arm(draft["id"], "ada")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    refused_context = workspace.name_explore_context(draft["id"], "rush")
    assert isinstance(refused_context, Refusal)
    assert refused_context.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["exploration"]["arms"] == []


def test_a_pull_keeps_its_reward(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_explore_arm(task_id, "ada")
    workspace.name_explore_arm(task_id, "grace")
    workspace.name_explore_context(task_id, "rush")
    recorded = workspace.record_pull(task_id, " one ", " rush ", " ada ", "2")
    assert recorded["exploration"]["pulls"] == [_pull("one", "rush", "ada", 2)]
    repeated = workspace.record_pull(task_id, "one", "quiet", "grace", "1")
    assert repeated["exploration"]["pulls"] == recorded["exploration"]["pulls"]
    unchanged = workspace.record_pull(task_id, "one", " ", " ", "3")
    assert unchanged["exploration"]["pulls"] == recorded["exploration"]["pulls"]

    missing_context = workspace.record_pull(task_id, "two", "quiet", "ada", "2")
    assert isinstance(missing_context, Refusal)
    assert missing_context.message == "That context is not on this task."
    missing_arm = workspace.record_pull(task_id, "two", "rush", "mina", "2")
    assert isinstance(missing_arm, Refusal)
    assert missing_arm.message == "That arm is not on this task."
    blank = workspace.record_pull(task_id, " ", "rush", "ada", "2")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this pull."
    blank_context = workspace.record_pull(task_id, "two", " ", "ada", "2")
    assert isinstance(blank_context, Refusal)
    assert blank_context.message == "Name the context."
    blank_arm = workspace.record_pull(task_id, "two", "rush", " ", "2")
    assert isinstance(blank_arm, Refusal)
    assert blank_arm.message == "Name the arm."
    bad_reward = workspace.record_pull(task_id, "two", "rush", "ada", "3")
    assert isinstance(bad_reward, Refusal)
    assert bad_reward.message == "Name a reward of 1 or 2."
    assert len(workspace.get_task(task_id)["exploration"]["pulls"]) == 1

    full = _in_progress(workspace, "Full pulls")
    full_id = full["id"]
    workspace.name_explore_arm(full_id, "ada")
    workspace.name_explore_context(full_id, "rush")
    for name in ("one", "two", "three", "four"):
        workspace.record_pull(full_id, name, "rush", "ada", "2")
    fifth = workspace.record_pull(full_id, "five", "rush", "ada", "2")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 pulls."
    assert len(workspace.get_task(full_id)["exploration"]["pulls"]) == 4


def test_the_draw_follows_the_middle_high_and_low_samples(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_explore_arm(task_id, "ada")
    workspace.name_explore_arm(task_id, "grace")
    workspace.name_explore_context(task_id, "rush")
    workspace.record_pull(task_id, "one", "rush", "ada", "2")
    workspace.record_pull(task_id, "two", "rush", "ada", "1")

    middle = workspace.draw_arm(task_id, " rush ")
    assert middle["status"] == "In Progress"
    assert middle["exploration"]["draw"] == _draw("rush", "ada", "middle")
    high = workspace.draw_arm(task_id, "rush")
    assert high["exploration"]["draw"] == _draw("rush", "grace", "high")
    low = workspace.draw_arm(task_id, "rush")
    assert low["exploration"]["draw"] == _draw("rush", "ada", "low")

    proven = _in_progress(workspace, "Proven")
    proven_id = proven["id"]
    workspace.name_explore_arm(proven_id, "ada")
    workspace.name_explore_arm(proven_id, "grace")
    workspace.name_explore_context(proven_id, "rush")
    workspace.record_pull(proven_id, "one", "rush", "ada", "2")
    workspace.record_pull(proven_id, "two", "rush", "ada", "2")
    workspace.draw_arm(proven_id, "rush")
    tied = workspace.draw_arm(proven_id, "rush")
    assert tied["exploration"]["draw"] == _draw("rush", "ada", "high")

    split = _in_progress(workspace, "Split")
    split_id = split["id"]
    workspace.name_explore_arm(split_id, "ada")
    workspace.name_explore_arm(split_id, "grace")
    workspace.name_explore_context(split_id, "rush")
    workspace.name_explore_context(split_id, "quiet")
    workspace.record_pull(split_id, "one", "rush", "ada", "2")
    workspace.record_pull(split_id, "two", "rush", "ada", "1")
    workspace.record_pull(split_id, "three", "quiet", "grace", "2")
    isolated = workspace.draw_arm(split_id, "rush")
    assert isolated["exploration"]["draw"] == _draw("rush", "ada", "middle")

    empty = _in_progress(workspace, "Empty draw")
    empty_id = empty["id"]
    missing_arm = workspace.draw_arm(empty_id, "rush")
    assert isinstance(missing_arm, Refusal)
    assert missing_arm.message == "Name an arm first."
    workspace.name_explore_arm(empty_id, "ada")
    blank = workspace.draw_arm(empty_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name the context to draw."
    missing_context = workspace.draw_arm(empty_id, "rush")
    assert isinstance(missing_context, Refusal)
    assert missing_context.message == "Name a context first."
    workspace.name_explore_context(empty_id, "rush")
    unknown = workspace.draw_arm(empty_id, "quiet")
    assert isinstance(unknown, Refusal)
    assert unknown.message == "That context is not on this task."

    restarted = workspace.name_explore_context(task_id, "quiet")
    assert restarted["exploration"]["draw"] is None
    again = workspace.draw_arm(task_id, "rush")
    assert again["exploration"]["draw"] == _draw("rush", "ada", "middle")

    draft = workspace.create_task("Draft")
    refused = workspace.draw_arm(draft["id"], "rush")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    fresh = _in_progress(workspace, "Rollback")
    fresh_id = fresh["id"]
    workspace.name_explore_arm(fresh_id, "ada")
    workspace.name_explore_arm(fresh_id, "grace")
    workspace.name_explore_context(fresh_id, "rush")
    workspace.record_pull(fresh_id, "one", "rush", "ada", "2")
    workspace.record_pull(fresh_id, "two", "rush", "ada", "1")
    stored = workspace.draw_arm(fresh_id, "rush")
    assert stored["exploration"]["draw"] == _draw("rush", "ada", "middle")

    def rolled(connection):
        exploration.record_pull(
            connection, fresh_id, "three", "rush", "ada", "2", "2026-10-21T00:00:00Z"
        )
        exploration.draw_arm(connection, fresh_id, "rush", "2026-10-21T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(fresh_id)
    assert len(restored["exploration"]["pulls"]) == 2
    assert restored["exploration"]["draw"] == _draw("rush", "ada", "middle")
