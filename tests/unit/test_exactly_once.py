from pathlib import Path

from task_manager.clock import format_time
from task_manager.domain import workflow
from task_manager.domain.file_read import read_file
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


def test_finish_uses_a_stored_read_without_reading_again(workspace, tmp_path):
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
    finished = call_in_transaction(
        workspace.connection,
        lambda conn: workflow.finish(conn, task_id, occurred_at, Path(project)),
    )
    assert finished["workflow"]["steps"][0]["state"] == "Completed"
    assert len(finished["file_reads"]) == 1
    assert [event["state"] for event in finished["workflow"]["replay"]] == [
        "Running",
        "Completed",
    ]


def test_a_declined_folder_is_not_recorded_again(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_workflow_step(
        task_id,
        "Create the folder",
        "folder",
        str(project),
        "notes",
        "Add notes",
        "consequential",
    )
    workspace.add_workflow_step(
        task_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    held = workspace.advance_workflow(task_id)
    workspace.mark_change_not_carried_out(
        task_id, held["workflow"]["steps"][0]["change_id"], "Not this folder"
    )
    failed = workspace.advance_workflow(task_id)
    assert failed["workflow"]["stopped"] == "Stopped at Create the folder: Not this folder"
    replay = failed["workflow"]["replay"]
    again = workspace.advance_workflow(task_id)
    assert len(again["implementation_changes"]) == 1
    assert again["workflow"]["steps"][0]["state"] == "Failed"
    assert again["workflow"]["steps"][1]["state"] == "Pending"
    assert again["workflow"]["stopped"] == "Stopped at Create the folder: Not this folder"
    assert again["workflow"]["replay"] == replay
    assert again["file_reads"] == []
    assert not (project / "notes").exists()


def test_a_missing_file_can_still_be_retried(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_workflow_step(
        task_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    failed = workspace.advance_workflow(task_id)
    assert failed["workflow"]["steps"][0]["state"] == "Failed"
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    retried = workspace.advance_workflow(task_id)
    assert retried["workflow"]["steps"][0]["state"] == "Completed"
    assert len(retried["file_reads"]) == 1


def test_the_same_advance_name_performs_one_step(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_workflow_step(
        task_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    workspace.add_workflow_step(
        task_id, "Create the folder", "folder", str(project), "notes", "Add notes", "ordinary"
    )
    once = workspace.advance_workflow(task_id, "once")
    assert [step["state"] for step in once["workflow"]["steps"]] == ["Completed", "Pending"]
    assert len(once["file_reads"]) == 1
    replay = once["workflow"]["replay"]
    again = workspace.advance_workflow(task_id, "  once  ")
    assert again["workflow"]["steps"][1]["state"] == "Pending"
    assert len(again["file_reads"]) == 1
    assert again["workflow"]["replay"] == replay
    assert not (project / "notes").exists()
    opened = Workspace(tmp_path / "workspace.db", workspace.clock, "Ada")
    try:
        repeated = opened.advance_workflow(task_id, "once")
        assert repeated["workflow"]["replay"] == replay
        assert not (project / "notes").exists()
    finally:
        opened.close()
    followed = workspace.advance_workflow(task_id, "next")
    assert followed["workflow"]["steps"][1]["state"] == "Completed"
    assert (project / "notes").is_dir()
    assert len(followed["file_reads"]) == 1


def test_a_blank_name_can_perform_the_next_step(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_workflow_step(
        task_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    workspace.add_workflow_step(
        task_id, "Create the folder", "folder", str(project), "notes", "Add notes", "ordinary"
    )
    first = workspace.advance_workflow(task_id, "   ")
    assert [step["state"] for step in first["workflow"]["steps"]] == ["Completed", "Pending"]
    second = workspace.advance_workflow(task_id, None)
    assert second["workflow"]["steps"][1]["state"] == "Completed"
    assert (project / "notes").is_dir()


def test_the_same_name_on_another_task_still_runs(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    first = _in_progress(workspace, "First note")
    second = _in_progress(workspace, "Second note")
    for task_id in (first["id"], second["id"]):
        workspace.add_workflow_step(
            task_id, "Read the note", "read", str(project), "note.txt", None, None
        )
    workspace.advance_workflow(first["id"], "once")
    other = workspace.advance_workflow(second["id"], "once")
    assert other["workflow"]["steps"][0]["state"] == "Completed"
    assert len(other["file_reads"]) == 1


def test_a_refused_advance_does_not_save_the_name(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    created = workspace.create_task("Still a draft")
    refused = workspace.advance_workflow(created["id"], "once")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    started = workspace.transition(ready["id"], "start")
    workspace.add_workflow_step(
        started["id"], "Read the note", "read", str(project), "note.txt", None, None
    )
    advanced = workspace.advance_workflow(started["id"], "once")
    assert advanced["workflow"]["steps"][0]["state"] == "Completed"
    assert len(advanced["file_reads"]) == 1


def test_a_running_name_must_be_recovered_before_it_is_saved(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_workflow_step(
        task_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    assert isinstance(_prepare(workspace, task_id), workflow.ReadyToFinish)
    refused = workspace.advance_workflow(task_id, "once")
    assert isinstance(refused, Refusal)
    assert refused.message == "Recover the interrupted step first."
    recovered = workspace.recover_workflow(task_id)
    assert recovered["workflow"]["steps"][0]["state"] == "Failed"
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    retried = workspace.advance_workflow(task_id, "once")
    assert retried["workflow"]["steps"][0]["state"] == "Completed"
    assert len(retried["file_reads"]) == 1
