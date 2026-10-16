from task_manager.clock import format_time
from task_manager.domain import workflow
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _read(workspace, task_id, project, title, path):
    return workspace.add_workflow_step(task_id, title, "read", str(project), path, None, None)


def test_two_steps_share_one_trace(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    (project / "extra.txt").write_text("extra\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    assert task["workflow"]["trace"] is None
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the extra", "extra.txt")
    first = workspace.advance_workflow(task_id)
    second = workspace.advance_workflow(task_id)
    trace = second["workflow"]["trace"]
    assert trace["id"] == first["workflow"]["trace"]["id"]
    assert [span["name"] for span in trace["spans"]] == ["Read the note", "Read the extra"]
    assert [span["state"] for span in trace["spans"]] == ["Completed", "Completed"]
    assert trace["spans"][0]["parent_id"] is None
    assert trace["spans"][1]["parent_id"] == trace["spans"][0]["id"]
    assert trace["spans"][0]["started_at"]
    assert trace["spans"][0]["ended_at"]
    assert second["status"] == "In Progress"
    assert [item["path"] for item in second["file_reads"]] == ["note.txt", "extra.txt"]


def test_a_failed_step_closes_its_span(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the gap", "missing.txt")
    failed = workspace.advance_workflow(task_id)
    span = failed["workflow"]["trace"]["spans"][0]
    assert span["state"] == "Failed"
    assert span["detail"] == "The file must already exist."
    assert span["ended_at"]


def test_a_running_step_has_no_end(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    occurred_at = format_time(workspace.clock.now())
    call_in_transaction(
        workspace.connection,
        lambda conn: workflow.prepare(conn, task_id, occurred_at),
    )
    running = workspace.get_task(task_id)
    span = running["workflow"]["trace"]["spans"][0]
    assert span["state"] == "Running"
    assert span["ended_at"] is None
    recovered = workspace.recover_workflow(task_id)
    closed = recovered["workflow"]["trace"]["spans"][0]
    assert closed["state"] == "Failed"
    assert closed["ended_at"]


def test_a_rolled_back_start_leaves_no_trace(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    occurred_at = format_time(workspace.clock.now())

    def _start_then_refuse(connection):
        workflow.prepare(connection, task_id, occurred_at)
        return bad_request("no")

    refused = call_in_transaction(workspace.connection, _start_then_refuse)
    assert isinstance(refused, Refusal)
    assert refused.message == "no"
    opened = workspace.get_task(task_id)
    assert opened["workflow"]["steps"][0]["state"] == "Pending"
    assert opened["workflow"]["trace"] is None


def test_reading_the_trace_does_not_run_the_workflow(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    assert workspace.workflow_trace(task_id) == {"id": None, "spans": []}
    missing = workspace.workflow_trace(9999)
    assert isinstance(missing, Refusal)
    assert missing.message == "Task not found."
    _read(workspace, task_id, project, "Read the note", "note.txt")
    workspace.advance_workflow(task_id)
    clock_index = workspace.clock._index
    first = workspace.workflow_trace(task_id)
    second = workspace.workflow_trace(task_id)
    assert second == first
    assert first["spans"][0]["state"] == "Completed"
    assert workspace.clock._index == clock_index
    opened = workspace.get_task(task_id)
    assert opened["status"] == "In Progress"
    assert [item["path"] for item in opened["file_reads"]] == ["note.txt"]
