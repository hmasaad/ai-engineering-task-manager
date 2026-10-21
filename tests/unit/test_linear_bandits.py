from task_manager.domain import linear_bandit
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


def _context(name, first, second):
    return {"name": name, "first": first, "second": second}


def _pull(name, context, arm, reward):
    return {"name": name, "context": context, "arm": arm, "reward": reward}


def _choice(context, model, arm):
    return {"context": context, "model": model, "arm": arm}


def test_an_arm_and_a_context_keep_their_marks(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    named = workspace.name_model_arm(task_id, " ada ")
    assert named["status"] == "In Progress"
    assert named["models"]["arms"] == [_arm("ada")]
    assert named["file_reads"] == []
    assert named["workflow"]["steps"] == []
    assert named["bandit"]["actions"] == []
    assert named["exploration"]["arms"] == []
    repeated = workspace.name_model_arm(task_id, "ada")
    assert repeated["models"]["arms"] == [_arm("ada")]
    second = workspace.name_model_arm(task_id, "grace")
    assert second["models"]["arms"] == [_arm("ada"), _arm("grace")]

    other = _in_progress(workspace, "Other arm")
    other_named = workspace.name_model_arm(other["id"], "ada")
    assert other_named["models"]["arms"] == [_arm("ada")]
    assert len(workspace.get_task(task_id)["models"]["arms"]) == 2

    blank = workspace.name_model_arm(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this arm."
    third = workspace.name_model_arm(task_id, "mina")
    assert isinstance(third, Refusal)
    assert third.message == "This task already has 2 arms."

    rush = workspace.name_model_context(task_id, " rush ", "1", "1")
    assert rush["models"]["contexts"] == [_context("rush", 1, 1)]
    again = workspace.name_model_context(task_id, "rush", "0", "0")
    assert again["models"]["contexts"] == [_context("rush", 1, 1)]
    ignored = workspace.name_model_context(task_id, "rush", " ", "3")
    assert ignored["models"]["contexts"] == [_context("rush", 1, 1)]
    quiet = workspace.name_model_context(task_id, "quiet", "1", "0")
    assert quiet["models"]["contexts"] == [
        _context("rush", 1, 1),
        _context("quiet", 1, 0),
    ]
    extra = workspace.name_model_context(task_id, "night", "0", "1")
    assert isinstance(extra, Refusal)
    assert extra.message == "This task already has 2 contexts."
    blank_context = workspace.name_model_context(task_id, " ", "1", "1")
    assert isinstance(blank_context, Refusal)
    assert blank_context.message == "Name this context."
    bad_mark = workspace.name_model_context(task_id, "night", "2", "1")
    assert isinstance(bad_mark, Refusal)
    assert bad_mark.message == "Name a mark of 0 or 1."
    bad_second = workspace.name_model_context(task_id, "night", "0", " ")
    assert isinstance(bad_second, Refusal)
    assert bad_second.message == "Name a mark of 0 or 1."
    assert len(workspace.get_task(task_id)["models"]["contexts"]) == 2

    draft = workspace.create_task("Draft")
    refused = workspace.name_model_arm(draft["id"], "ada")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    refused_context = workspace.name_model_context(draft["id"], "rush", "1", "1")
    assert isinstance(refused_context, Refusal)
    assert refused_context.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["models"]["arms"] == []


def test_a_pull_adds_its_reward_only_where_the_mark_is_on(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_model_arm(task_id, "ada")
    workspace.name_model_arm(task_id, "grace")
    workspace.name_model_context(task_id, "quiet", "1", "0")
    recorded = workspace.record_model_pull(task_id, " one ", " quiet ", " ada ", "2")
    assert recorded["models"]["pulls"] == [_pull("one", "quiet", "ada", 2)]
    repeated = workspace.record_model_pull(task_id, "one", "rush", "grace", "1")
    assert repeated["models"]["pulls"] == recorded["models"]["pulls"]
    unchanged = workspace.record_model_pull(task_id, "one", " ", " ", "3")
    assert unchanged["models"]["pulls"] == recorded["models"]["pulls"]

    missing_context = workspace.record_model_pull(task_id, "two", "rush", "ada", "2")
    assert isinstance(missing_context, Refusal)
    assert missing_context.message == "That context is not on this task."
    missing_arm = workspace.record_model_pull(task_id, "two", "quiet", "mina", "2")
    assert isinstance(missing_arm, Refusal)
    assert missing_arm.message == "That arm is not on this task."
    blank = workspace.record_model_pull(task_id, " ", "quiet", "ada", "2")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this pull."
    blank_context = workspace.record_model_pull(task_id, "two", " ", "ada", "2")
    assert isinstance(blank_context, Refusal)
    assert blank_context.message == "Name the context."
    blank_arm = workspace.record_model_pull(task_id, "two", "quiet", " ", "2")
    assert isinstance(blank_arm, Refusal)
    assert blank_arm.message == "Name the arm."
    bad_reward = workspace.record_model_pull(task_id, "two", "quiet", "ada", "3")
    assert isinstance(bad_reward, Refusal)
    assert bad_reward.message == "Name a reward of 1 or 2."
    assert len(workspace.get_task(task_id)["models"]["pulls"]) == 1

    full = _in_progress(workspace, "Full pulls")
    full_id = full["id"]
    workspace.name_model_arm(full_id, "ada")
    workspace.name_model_context(full_id, "quiet", "1", "0")
    for name in ("one", "two", "three", "four"):
        workspace.record_model_pull(full_id, name, "quiet", "ada", "2")
    fifth = workspace.record_model_pull(full_id, "five", "quiet", "ada", "2")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This task already has 4 pulls."
    assert len(workspace.get_task(full_id)["models"]["pulls"]) == 4


def test_the_neural_score_adds_the_pair_when_both_marks_are_on(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_model_arm(task_id, "ada")
    workspace.name_model_arm(task_id, "grace")
    workspace.name_model_context(task_id, "quiet", "1", "0")
    workspace.name_model_context(task_id, "rush", "1", "1")
    workspace.record_model_pull(task_id, "one", "quiet", "ada", "2")
    workspace.record_model_pull(task_id, "two", "quiet", "ada", "2")
    workspace.record_model_pull(task_id, "three", "rush", "grace", "2")

    linear = workspace.choose_model_arm(task_id, " rush ", " linear ")
    assert linear["status"] == "In Progress"
    assert linear["models"]["choice"] == _choice("rush", "linear", "ada")
    neural = workspace.choose_model_arm(task_id, "rush", "neural")
    assert neural["models"]["choice"] == _choice("rush", "neural", "grace")
    quiet = workspace.choose_model_arm(task_id, "quiet", "neural")
    assert quiet["models"]["choice"] == _choice("quiet", "neural", "ada")

    fresh = _in_progress(workspace, "No pulls")
    fresh_id = fresh["id"]
    workspace.name_model_arm(fresh_id, "ada")
    workspace.name_model_arm(fresh_id, "grace")
    workspace.name_model_context(fresh_id, "rush", "1", "1")
    zero = workspace.choose_model_arm(fresh_id, "rush", "linear")
    assert zero["models"]["choice"] == _choice("rush", "linear", "ada")

    empty = _in_progress(workspace, "Empty choice")
    empty_id = empty["id"]
    missing_arm = workspace.choose_model_arm(empty_id, "rush", "linear")
    assert isinstance(missing_arm, Refusal)
    assert missing_arm.message == "Name an arm first."
    workspace.name_model_arm(empty_id, "ada")
    blank = workspace.choose_model_arm(empty_id, " ", "linear")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name the context to choose."
    missing_context = workspace.choose_model_arm(empty_id, "rush", "linear")
    assert isinstance(missing_context, Refusal)
    assert missing_context.message == "Name a context first."
    workspace.name_model_context(empty_id, "rush", "1", "1")
    unknown = workspace.choose_model_arm(empty_id, "quiet", "linear")
    assert isinstance(unknown, Refusal)
    assert unknown.message == "That context is not on this task."
    blank_model = workspace.choose_model_arm(empty_id, "rush", " ")
    assert isinstance(blank_model, Refusal)
    assert blank_model.message == "Name the model."
    bad_model = workspace.choose_model_arm(empty_id, "rush", "tree")
    assert isinstance(bad_model, Refusal)
    assert bad_model.message == "Name a linear or neural model."

    cleared = workspace.record_model_pull(task_id, "four", "rush", "ada", "1")
    assert cleared["models"]["choice"] is None

    draft = workspace.create_task("Draft")
    refused = workspace.choose_model_arm(draft["id"], "rush", "linear")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    stored = workspace.choose_model_arm(fresh_id, "rush", "linear")
    assert stored["models"]["choice"] == _choice("rush", "linear", "ada")

    def rolled(connection):
        linear_bandit.record_pull(
            connection, fresh_id, "one", "rush", "ada", "2", "2026-10-21T00:00:00Z"
        )
        linear_bandit.choose(
            connection, fresh_id, "rush", "neural", "2026-10-21T00:00:00Z"
        )
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(fresh_id)
    assert restored["models"]["pulls"] == []
    assert restored["models"]["choice"] == _choice("rush", "linear", "ada")
