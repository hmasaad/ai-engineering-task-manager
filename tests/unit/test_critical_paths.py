from task_manager.domain import paths
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_a_step_keeps_its_length(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    named = workspace.name_step(task_id, " design ", "1")
    assert named["status"] == "In Progress"
    assert named["paths"]["steps"] == [
        {"name": "design", "length": 1, "follows": None, "latest": None}
    ]
    assert named["paths"]["critical"] == ["design"]
    assert named["file_reads"] == []
    assert named["workflow"]["steps"] == []
    assert named["slo"]["waiting"] == []

    built = workspace.name_step(task_id, "build", " 2 ")
    assert built["paths"]["steps"] == [
        {"name": "design", "length": 1, "follows": None, "latest": None},
        {"name": "build", "length": 2, "follows": None, "latest": None},
    ]
    repeated = workspace.name_step(task_id, "design", "2")
    assert repeated["paths"]["steps"] == built["paths"]["steps"]

    other = _in_progress(workspace, "Other schedule")
    other_named = workspace.name_step(other["id"], "design", "2")
    assert other_named["paths"]["steps"] == [
        {"name": "design", "length": 2, "follows": None, "latest": None}
    ]
    assert len(workspace.get_task(task_id)["paths"]["steps"]) == 2

    blank = workspace.name_step(task_id, " ", "1")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this step."

    bad_length = workspace.name_step(task_id, "note", "3")
    assert isinstance(bad_length, Refusal)
    assert bad_length.message == "Name a length of 1 or 2."
    assert len(workspace.get_task(task_id)["paths"]["steps"]) == 2

    draft = workspace.create_task("Draft")
    refused = workspace.name_step(draft["id"], "design", "1")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["paths"]["steps"] == []


def test_a_step_follows_one_earlier_step(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_step(task_id, "design", "1")
    workspace.name_step(task_id, "build", "2")
    workspace.name_step(task_id, "review", "1")
    workspace.name_step(task_id, "note", "1")

    linked = workspace.add_dependency(task_id, " build ", " design ")
    assert linked["paths"]["steps"][1]["follows"] == "design"
    assert linked["paths"]["critical"] == ["design", "build"]
    again = workspace.add_dependency(task_id, "build", "design")
    assert again["paths"]["steps"] == linked["paths"]["steps"]

    second = workspace.add_dependency(task_id, "build", "note")
    assert isinstance(second, Refusal)
    assert second.message == "That step already follows another step."

    self_link = workspace.add_dependency(task_id, "review", "review")
    assert isinstance(self_link, Refusal)
    assert self_link.message == "A step cannot follow itself."

    missing = workspace.add_dependency(task_id, "review", "missing")
    assert isinstance(missing, Refusal)
    assert missing.message == "That step is not on this task."

    blank = workspace.add_dependency(task_id, " ", "design")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name the step that follows."
    blank_predecessor = workspace.add_dependency(task_id, "review", " ")
    assert isinstance(blank_predecessor, Refusal)
    assert blank_predecessor.message == "Name the step it follows."

    workspace.add_dependency(task_id, "review", "build")
    cycle = workspace.add_dependency(task_id, "design", "review")
    assert isinstance(cycle, Refusal)
    assert cycle.message == "Those steps would form a cycle."
    assert workspace.get_task(task_id)["paths"]["steps"][0]["follows"] is None

    def rolled(connection):
        paths.add_dependency(connection, task_id, "note", "design", "2026-10-20T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    note = next(
        step
        for step in workspace.get_task(task_id)["paths"]["steps"]
        if step["name"] == "note"
    )
    assert note["follows"] is None
    restored = workspace.add_dependency(task_id, "note", "design")
    assert restored["paths"]["steps"][-1]["follows"] == "design"
    assert restored["paths"]["critical"] == ["design", "build", "review"]
    assert restored["status"] == "In Progress"

    other = _in_progress(workspace, "Other link")
    workspace.name_step(other["id"], "design", "1")
    workspace.name_step(other["id"], "build", "1")
    other_link = workspace.add_dependency(other["id"], "build", "design")
    assert other_link["paths"]["steps"][1]["follows"] == "design"
    assert workspace.get_task(task_id)["paths"]["steps"][1]["follows"] == "design"

    draft = workspace.create_task("Draft link")
    refused = workspace.add_dependency(draft["id"], "build", "design")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."


def test_the_critical_path_propagates_the_deadline(workspace):
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.name_step(task_id, "design", "1")
    workspace.name_step(task_id, "build", "2")
    workspace.add_dependency(task_id, "build", "design")

    scheduled = workspace.set_schedule_deadline(task_id, " 2026-12-03T00:00:00Z ")
    assert scheduled["status"] == "In Progress"
    assert scheduled["paths"]["deadline"] == "2026-12-03T00:00:00Z"
    assert scheduled["paths"]["critical"] == ["design", "build"]
    assert scheduled["paths"]["steps"] == [
        {
            "name": "design",
            "length": 1,
            "follows": None,
            "latest": "2026-12-01T00:00:00Z",
        },
        {
            "name": "build",
            "length": 2,
            "follows": "design",
            "latest": "2026-12-03T00:00:00Z",
        },
    ]
    same = workspace.set_schedule_deadline(task_id, "2026-12-03T00:00:00Z")
    assert same["paths"]["deadline"] == "2026-12-03T00:00:00Z"
    later = workspace.set_schedule_deadline(task_id, "2026-12-04T00:00:00Z")
    assert later["paths"]["steps"][0]["latest"] == "2026-12-02T00:00:00Z"
    assert later["paths"]["steps"][1]["latest"] == "2026-12-04T00:00:00Z"

    tie = _in_progress(workspace, "Tie")
    tie_id = tie["id"]
    workspace.name_step(tie_id, "note", "2")
    workspace.name_step(tie_id, "design", "1")
    workspace.name_step(tie_id, "build", "1")
    workspace.add_dependency(tie_id, "build", "design")
    assert workspace.get_task(tie_id)["paths"]["critical"] == ["note"]

    earlier = _in_progress(workspace, "Earlier chain")
    earlier_id = earlier["id"]
    workspace.name_step(earlier_id, "design", "1")
    workspace.name_step(earlier_id, "build", "1")
    workspace.name_step(earlier_id, "note", "2")
    workspace.add_dependency(earlier_id, "build", "design")
    assert workspace.get_task(earlier_id)["paths"]["critical"] == ["design", "build"]

    bad_deadline = workspace.set_schedule_deadline(task_id, "tomorrow")
    assert isinstance(bad_deadline, Refusal)
    assert bad_deadline.message == "Name a deadline."
    assert workspace.get_task(task_id)["paths"]["deadline"] == "2026-12-04T00:00:00Z"

    empty = _in_progress(workspace, "Empty schedule")
    missing_step = workspace.set_schedule_deadline(empty["id"], "2026-12-03T00:00:00Z")
    assert isinstance(missing_step, Refusal)
    assert missing_step.message == "Name a step first."

    draft = workspace.create_task("Draft deadline")
    refused = workspace.set_schedule_deadline(draft["id"], "2026-12-03T00:00:00Z")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."

    def rolled(connection):
        paths.set_deadline(connection, task_id, "2026-12-10T00:00:00Z", "2026-10-20T00:00:00Z")
        return bad_request("stop")

    assert isinstance(call_in_transaction(workspace.connection, rolled), Refusal)
    assert workspace.get_task(task_id)["paths"]["deadline"] == "2026-12-04T00:00:00Z"
    assert workspace.get_task(task_id)["priority"]["waiting"] == []
