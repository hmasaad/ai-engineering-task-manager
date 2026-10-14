from pathlib import Path

from task_manager.clock import format_time
from task_manager.domain import workflow
from task_manager.domain.file_read import read_file
from task_manager.domain.folder import record
from task_manager.domain.results import Refusal
from task_manager.storage.connection import call_in_transaction
from task_manager.workspace import Workspace


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _prepare(workspace, task_id):
    occurred_at = format_time(workspace.clock.now())
    return call_in_transaction(
        workspace.connection,
        lambda conn: workflow.prepare(conn, task_id, occurred_at),
    )


def test_the_replay_lists_the_start_and_the_result(workspace, tmp_path, clock):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    assert workspace.workflow_replay(task_id)["events"] == []
    workspace.add_workflow_step(
        task_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    advanced = workspace.advance_workflow(task_id)
    assert [event["state"] for event in advanced["workflow"]["replay"]] == [
        "Running",
        "Completed",
    ]
    assert advanced["workflow"]["replay"][0]["title"] == "Read the note"
    assert advanced["workflow"]["replay"][1]["detail"] is None
    assert len(advanced["file_reads"]) == 1
    opened = workspace.get_task(task_id)
    assert opened["workflow"]["replay"] == advanced["workflow"]["replay"]
    assert len(opened["file_reads"]) == 1

    reopened = Workspace(tmp_path / "workspace.db", clock, "Ada")
    try:
        again = reopened.workflow_replay(task_id)
        assert again["events"] == advanced["workflow"]["replay"]
        assert len(reopened.get_task(task_id)["file_reads"]) == 1
        assert reopened.get_task(task_id)["status"] == "In Progress"
    finally:
        reopened.close()


def test_recover_marks_an_interrupted_step_and_advance_does_not_run_it(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_workflow_step(
        task_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    workspace.add_workflow_step(
        task_id, "Create the folder", "folder", str(project), "notes", "Add notes", "ordinary"
    )
    assert isinstance(_prepare(workspace, task_id), workflow.ReadyToFinish)
    running = workspace.get_task(task_id)
    assert running["workflow"]["steps"][0]["state"] == "Running"
    assert running["workflow"]["stopped"] == (
        "Stopped at Read the note: the step was interrupted."
    )
    refused = workspace.advance_workflow(task_id)
    assert isinstance(refused, Refusal)
    assert refused.message == "Recover the interrupted step first."
    assert workspace.get_task(task_id)["file_reads"] == []
    assert not (project / "notes").exists()

    recovered = workspace.recover_workflow(task_id)
    assert recovered["status"] == "In Progress"
    assert recovered["workflow"]["steps"][0]["state"] == "Failed"
    assert recovered["workflow"]["steps"][1]["state"] == "Pending"
    assert recovered["workflow"]["stopped"] == (
        "Stopped at Read the note: the step was interrupted."
    )
    assert [event["state"] for event in recovered["workflow"]["replay"]] == [
        "Running",
        "Failed",
    ]
    absent = workspace.recover_workflow(task_id)
    assert absent.message == "There is no step to recover."

    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    retried = workspace.advance_workflow(task_id)
    assert [step["state"] for step in retried["workflow"]["steps"]] == ["Completed", "Pending"]
    assert len(retried["file_reads"]) == 1
    assert not (project / "notes").exists()


def test_recover_uses_a_stored_effect_without_repeating_it(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_workflow_step(
        task_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    assert isinstance(_prepare(workspace, task_id), workflow.ReadyToFinish)
    occurred_at = format_time(workspace.clock.now())
    call_in_transaction(
        workspace.connection,
        lambda conn: read_file(
            conn, task_id, str(project), "note.txt", occurred_at, Path(project)
        ),
    )
    recovered = workspace.recover_workflow(task_id)
    assert recovered["workflow"]["steps"][0]["state"] == "Completed"
    assert len(recovered["file_reads"]) == 1
    assert [event["state"] for event in recovered["workflow"]["replay"]] == [
        "Running",
        "Completed",
    ]

    folder_task = _in_progress(workspace, "Hold the folder")
    folder_id = folder_task["id"]
    workspace.add_workflow_step(
        folder_id,
        "Create the folder",
        "folder",
        str(project),
        "notes",
        "Add the notes folder",
        "consequential",
    )
    workspace.add_workflow_step(
        folder_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    assert isinstance(_prepare(workspace, folder_id), workflow.ReadyToFinish)
    recorded_at = format_time(workspace.clock.now())
    call_in_transaction(
        workspace.connection,
        lambda conn: record(
            conn,
            folder_id,
            str(project),
            "consequential",
            "Add the notes folder",
            False,
            "notes",
            recorded_at,
            Path(project),
        ),
    )
    held = workspace.recover_workflow(folder_id)
    assert held["workflow"]["stopped"] == (
        "Stopped at Create the folder: waiting for approval."
    )
    assert held["workflow"]["steps"][0]["state"] == "Waiting"
    assert held["workflow"]["steps"][1]["state"] == "Pending"
    assert len(held["implementation_changes"]) == 1
    assert not (project / "notes").exists()
    change_id = held["workflow"]["steps"][0]["change_id"]
    approved = workspace.approve_change(folder_id, change_id, "The folder path was reviewed.")
    assert approved["workflow"]["steps"][0]["state"] == "Waiting"
    assert workspace.recover_workflow(folder_id).message == "There is no step to recover."
