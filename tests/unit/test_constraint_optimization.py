from task_manager.domain import optimization
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _activity(name, length, start=None):
    return {"name": name, "length": length, "start": start}


def test_an_activity_keeps_its_length(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    named = workspace.name_activity(task_id, " design ", "1")
    assert named["status"] == "In Progress"
    assert named["optimization"]["activities"] == [_activity("design", 1)]
    assert named["file_reads"] == []
    assert named["workflow"]["steps"] == []
    assert named["paths"]["steps"] == []

    built = workspace.name_activity(task_id, "build", " 2 ")
    assert built["optimization"]["activities"] == [
        _activity("design", 1),
        _activity("build", 2),
    ]
    repeated = workspace.name_activity(task_id, "design", "2")
    assert repeated["optimization"]["activities"] == built["optimization"]["activities"]

    other = _in_progress(workspace, "Other schedule")
    other_named = workspace.name_activity(other["id"], "design", "2")
    assert other_named["optimization"]["activities"] == [_activity("design", 2)]
    assert len(workspace.get_task(task_id)["optimization"]["activities"]) == 2

    blank = workspace.name_activity(task_id, " ", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this activity."

    bad_length = workspace.name_activity(task_id, "note", "3")
    assert isinstance(bad_length, Refusal)
    assert bad_length.message == "Name a length of 1 or 2."
    assert len(workspace.get_task(task_id)["optimization"]["activities"]) == 2

    full = _in_progress(workspace, "Full schedule")
    full_id = full["id"]
    for name in ("one", "two", "three", "four"):
        workspace.name_activity(full_id, name, "1")
    fifth = workspace.name_activity(full_id, "five", "1")
    assert isinstance(fifth, Refusal)
    assert fifth.message == "This schedule already has 4 activities."
    assert len(workspace.get_task(full_id)["optimization"]["activities"]) == 4

    draft = workspace.create_task("Draft")
    refused = workspace.name_activity(draft["id"], "design", "1")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["optimization"]["activities"] == []


def test_a_constraint_records_one_earlier_activity(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_activity(task_id, "design", "1")
    workspace.name_activity(task_id, "build", "2")
    workspace.name_activity(task_id, "test", "1")
    workspace.set_capacity(task_id, "2")
    planned = workspace.optimize_schedule(task_id)
    assert planned["optimization"]["finish"] == 2

    linked = workspace.add_constraint(task_id, " test ", " build ")
    assert linked["optimization"]["constraints"] == [{"activity": "test", "after": "build"}]
    assert linked["optimization"]["finish"] is None
    assert linked["optimization"]["activities"][0]["start"] is None
    again = workspace.add_constraint(task_id, "test", "build")
    assert again["optimization"]["constraints"] == linked["optimization"]["constraints"]

    self_link = workspace.add_constraint(task_id, "test", "test")
    assert isinstance(self_link, Refusal)
    assert self_link.message == "An activity cannot follow itself."

    missing = workspace.add_constraint(task_id, "test", "missing")
    assert isinstance(missing, Refusal)
    assert missing.message == "That activity is not on this task."

    blank = workspace.add_constraint(task_id, " ", "build")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name the activity."
    blank_earlier = workspace.add_constraint(task_id, "design", " ")
    assert isinstance(blank_earlier, Refusal)
    assert blank_earlier.message == "Name the earlier activity."

    cycle = workspace.add_constraint(task_id, "build", "test")
    assert isinstance(cycle, Refusal)
    assert cycle.message == "Those activities would form a cycle."
    assert workspace.get_task(task_id)["optimization"]["constraints"] == [
        {"activity": "test", "after": "build"}
    ]

    def rolled(connection):
        optimization.add_constraint(
            connection, task_id, "build", "design", "2026-10-20T00:00:00Z"
        )
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    assert workspace.get_task(task_id)["optimization"]["constraints"] == [
        {"activity": "test", "after": "build"}
    ]
    restored = workspace.add_constraint(task_id, "build", "design")
    assert restored["optimization"]["constraints"][-1] == {
        "activity": "build",
        "after": "design",
    }
    assert restored["status"] == "In Progress"

    other = _in_progress(workspace, "Other constraint")
    workspace.name_activity(other["id"], "build", "1")
    workspace.name_activity(other["id"], "test", "1")
    other_link = workspace.add_constraint(other["id"], "test", "build")
    assert other_link["optimization"]["constraints"] == [{"activity": "test", "after": "build"}]
    assert len(workspace.get_task(task_id)["optimization"]["constraints"]) == 2

    draft = workspace.create_task("Draft constraint")
    refused = workspace.add_constraint(draft["id"], "test", "build")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."


def test_optimization_finishes_on_the_earliest_legal_day(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_activity(task_id, "design", "1")
    workspace.name_activity(task_id, "build", "2")
    workspace.name_activity(task_id, "test", "1")
    workspace.add_constraint(task_id, "test", "build")

    missing_capacity = workspace.optimize_schedule(task_id)
    assert isinstance(missing_capacity, Refusal)
    assert missing_capacity.message == "Name a capacity first."

    bounded = workspace.set_capacity(task_id, " 2 ")
    assert bounded["optimization"]["capacity"] == 2
    scheduled = workspace.optimize_schedule(task_id)
    assert scheduled["status"] == "In Progress"
    assert scheduled["optimization"]["finish"] == 3
    assert scheduled["optimization"]["activities"] == [
        _activity("design", 1, 0),
        _activity("build", 2, 0),
        _activity("test", 1, 2),
    ]
    assert scheduled["priority"]["waiting"] == []
    same = workspace.set_capacity(task_id, "2")
    assert same["optimization"]["finish"] == 3

    narrowed = workspace.set_capacity(task_id, "1")
    assert narrowed["optimization"]["capacity"] == 1
    assert narrowed["optimization"]["finish"] is None
    packed = workspace.optimize_schedule(task_id)
    assert packed["optimization"]["activities"] == [
        _activity("design", 1, 0),
        _activity("build", 2, 1),
        _activity("test", 1, 3),
    ]
    assert packed["optimization"]["finish"] == 4

    tie = _in_progress(workspace, "Tie")
    tie_id = tie["id"]
    workspace.name_activity(tie_id, "ada", "1")
    workspace.name_activity(tie_id, "grace", "1")
    workspace.set_capacity(tie_id, "1")
    chosen = workspace.optimize_schedule(tie_id)
    assert chosen["optimization"]["activities"] == [
        _activity("ada", 1, 0),
        _activity("grace", 1, 1),
    ]
    assert chosen["optimization"]["finish"] == 2

    reverse = _in_progress(workspace, "Reverse tie")
    reverse_id = reverse["id"]
    workspace.name_activity(reverse_id, "grace", "1")
    workspace.name_activity(reverse_id, "ada", "1")
    workspace.set_capacity(reverse_id, "1")
    flipped = workspace.optimize_schedule(reverse_id)
    assert flipped["optimization"]["activities"] == [
        _activity("grace", 1, 0),
        _activity("ada", 1, 1),
    ]

    bad_capacity = workspace.set_capacity(task_id, "3")
    assert isinstance(bad_capacity, Refusal)
    assert bad_capacity.message == "Name a capacity of 1 or 2."
    assert workspace.get_task(task_id)["optimization"]["capacity"] == 1

    empty = _in_progress(workspace, "Empty optimization")
    missing_activity = workspace.set_capacity(empty["id"], "1")
    assert isinstance(missing_activity, Refusal)
    assert missing_activity.message == "Name an activity first."
    missing_plan = workspace.optimize_schedule(empty["id"])
    assert isinstance(missing_plan, Refusal)
    assert missing_plan.message == "Name an activity first."

    draft = workspace.create_task("Draft capacity")
    refused = workspace.set_capacity(draft["id"], "1")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    workspace.set_capacity(task_id, "2")
    workspace.optimize_schedule(task_id)
    assert workspace.get_task(task_id)["optimization"]["finish"] == 3

    def rolled(connection):
        optimization.set_capacity(connection, task_id, "1", "2026-10-20T00:00:00Z")
        optimization.optimize_schedule(connection, task_id, "2026-10-20T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    restored = workspace.get_task(task_id)
    assert restored["optimization"]["capacity"] == 2
    assert restored["optimization"]["finish"] == 3
    assert restored["optimization"]["activities"][2]["start"] == 2
