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


def _failed_reads(workspace, project):
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the extra", "extra.txt")
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the gap", "missing.txt")
    workspace.advance_workflow(task_id)
    workspace.advance_workflow(task_id)
    failed = workspace.advance_workflow(task_id)
    return failed


def test_compensation_withdraws_the_latest_completed_read_first(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "extra.txt").write_text("extra\n", encoding="utf-8")
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    failed = _failed_reads(workspace, project)
    task_id = failed["id"]
    assert failed["status"] == "In Progress"
    assert failed["workflow"]["saga"] == "Failed"
    reads = [item["path"] for item in failed["file_reads"]]
    replay = len(failed["workflow"]["replay"])

    early = workspace.compensate_workflow(task_id, "Withdraw the note")
    assert isinstance(early, dict)
    assert early["status"] == "In Progress"
    assert [item["title"] for item in early["workflow"]["compensations"]] == ["Read the note"]
    assert early["workflow"]["compensations"][0]["state"] == "Compensated"
    assert early["workflow"]["saga"] == "Failed"
    assert [item["path"] for item in early["file_reads"]] == reads
    assert len(early["workflow"]["replay"]) == replay

    finished = workspace.compensate_workflow(task_id, "Withdraw the extra")
    assert [item["title"] for item in finished["workflow"]["compensations"]] == [
        "Read the note",
        "Read the extra",
    ]
    assert finished["workflow"]["saga"] == "Compensated"
    assert [item["path"] for item in finished["file_reads"]] == reads
    assert [step["state"] for step in finished["workflow"]["steps"]] == [
        "Completed",
        "Completed",
        "Failed",
    ]


def test_compensation_is_refused_until_a_step_fails(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    blank = workspace.compensate_workflow(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name why this step is compensated."
    open_workflow = workspace.compensate_workflow(task_id, "Too soon")
    assert open_workflow.message == "The workflow has not failed."
    assert workspace.get_task(task_id)["workflow"]["compensations"] == []

    _read(workspace, task_id, project, "Read the gap", "missing.txt")
    failed = workspace.advance_workflow(task_id)
    assert failed["workflow"]["saga"] == "Failed"
    none = workspace.compensate_workflow(task_id, "Nothing finished")
    assert none.message == "There is no step to compensate."

    running = _in_progress(workspace, "Read while a step is running")
    running_id = running["id"]
    _read(workspace, running_id, project, "Read the note", "note.txt")
    _read(workspace, running_id, project, "Read the extra", "extra.txt")
    workspace.advance_workflow(running_id)
    occurred_at = format_time(workspace.clock.now())
    call_in_transaction(
        workspace.connection,
        lambda conn: workflow.prepare(conn, running_id, occurred_at),
    )
    interrupted = workspace.compensate_workflow(running_id, "While running")
    assert interrupted.message == "Recover the interrupted step first."


def test_a_rolled_back_compensation_is_not_stored(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the gap", "missing.txt")
    workspace.advance_workflow(task_id)
    workspace.advance_workflow(task_id)

    def _compensate_then_refuse(connection):
        workflow.compensate(connection, task_id, "Withdraw the note", "2026-10-16T00:00:00Z")
        return bad_request("no")

    refused = call_in_transaction(workspace.connection, _compensate_then_refuse)
    assert refused.message == "no"
    opened = workspace.get_task(task_id)
    assert opened["workflow"]["compensations"] == []
    assert opened["workflow"]["saga"] == "Failed"


def test_a_folder_compensation_waits_until_approval(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_workflow_step(
        task_id, "Create the folder", "folder", str(project), "notes", "Add notes", "ordinary"
    )
    _read(workspace, task_id, project, "Read the gap", "missing.txt")
    workspace.advance_workflow(task_id)
    failed = workspace.advance_workflow(task_id)
    assert (project / "notes").is_dir()
    changes = [item["id"] for item in failed["implementation_changes"]]
    waiting = workspace.compensate_workflow(task_id, "Remove the notes folder")
    assert waiting["workflow"]["saga"] == "Waiting"
    assert waiting["workflow"]["compensations"][0]["state"] == "Waiting"
    assert (project / "notes").is_dir()
    compensation_id = waiting["workflow"]["compensations"][0]["id"]

    blank = workspace.approve_compensation(task_id, compensation_id, " ")
    assert blank.message == "An account of the evidence reviewed is required."
    blocked = workspace.compensate_workflow(task_id, "Another step")
    assert blocked.message == "Finish the waiting compensation first."
    assert (project / "notes").is_dir()

    approved = workspace.approve_compensation(task_id, compensation_id, "The folder is empty")
    assert approved["workflow"]["compensations"][0]["state"] == "Compensated"
    assert approved["workflow"]["saga"] == "Compensated"
    assert approved["status"] == "In Progress"
    assert not (project / "notes").exists()
    assert [item["id"] for item in approved["implementation_changes"]] == changes


def test_a_folder_that_contains_a_file_stays(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_workflow_step(
        task_id, "Create the folder", "folder", str(project), "notes", "Add notes", "ordinary"
    )
    _read(workspace, task_id, project, "Read the gap", "missing.txt")
    workspace.advance_workflow(task_id)
    workspace.advance_workflow(task_id)
    waiting = workspace.compensate_workflow(task_id, "Remove the notes folder")
    (project / "notes" / "inside.txt").write_text("keep\n", encoding="utf-8")
    compensation_id = waiting["workflow"]["compensations"][0]["id"]
    refused = workspace.approve_compensation(task_id, compensation_id, "The folder is empty")
    assert refused.message == "The folder must be empty to compensate."
    assert (project / "notes" / "inside.txt").is_file()
    assert workspace.get_task(task_id)["workflow"]["compensations"][0]["state"] == "Waiting"

    unnamed = workspace.decline_compensation(task_id, compensation_id, " ")
    assert unnamed.message == "Name why this compensation will not be carried out."
    declined = workspace.decline_compensation(task_id, compensation_id, "Keep the folder")
    assert declined["workflow"]["compensations"][0]["state"] == "Not carried out"
    assert declined["workflow"]["saga"] == "Compensated"
    assert (project / "notes" / "inside.txt").is_file()
