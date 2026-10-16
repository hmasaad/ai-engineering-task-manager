from task_manager.clock import format_time
from task_manager.domain import workflow
from task_manager.domain.results import Refusal
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _read(workspace, task_id, project, title, path):
    return workspace.add_workflow_step(task_id, title, "read", str(project), path, None, None)


def _prepare(workspace, task_id):
    occurred_at = format_time(workspace.clock.now())
    return call_in_transaction(
        workspace.connection,
        lambda conn: workflow.prepare(conn, task_id, occurred_at),
    )


def test_a_finished_workflow_replays_the_same_report(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    (project / "extra.txt").write_text("extra\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    assert workspace.replay_workflow_execution(task_id).message == "There is no step to replay."
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the extra", "extra.txt")
    workspace.advance_workflow(task_id)
    finished = workspace.advance_workflow(task_id)
    events = list(finished["workflow"]["replay"])
    clock_index = workspace.clock._index
    report = workspace.replay_workflow_execution(task_id)
    again = workspace.replay_workflow_execution(task_id)
    assert again == report
    assert report == {
        "version": 1,
        "matched": [
            {
                "title": "Read the note",
                "action": "read",
                "state": "Completed",
                "effect": "note.txt",
            },
            {
                "title": "Read the extra",
                "action": "read",
                "state": "Completed",
                "effect": "extra.txt",
            },
        ],
        "stopped": None,
    }
    opened = workspace.get_task(task_id)
    assert opened["status"] == "In Progress"
    assert opened["workflow"]["execution"] == report
    assert opened["workflow"]["replay"] == events
    assert [item["path"] for item in opened["file_reads"]] == ["note.txt", "extra.txt"]
    assert workspace.clock._index == clock_index


def test_a_missing_effect_stops_without_reading_again(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    workspace.advance_workflow(task_id)
    call_in_transaction(
        workspace.connection,
        lambda conn: conn.execute("DELETE FROM file_read"),
    )
    report = workspace.replay_workflow_execution(task_id)
    assert report["matched"] == []
    assert report["stopped"] == "Stopped at Read the note: the stored effect is missing."
    assert workspace.get_task(task_id)["file_reads"] == []


def test_replay_stops_at_the_first_unfinished_step(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    (project / "other.txt").write_text("other\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the other", "other.txt")
    workspace.advance_workflow(task_id)
    report = workspace.replay_workflow_execution(task_id)
    assert report["matched"] == [
        {
            "title": "Read the note",
            "action": "read",
            "state": "Completed",
            "effect": "note.txt",
        }
    ]
    assert report["stopped"] == "Stopped at Read the other: the step has not run."
    assert workspace.replay_workflow_execution(task_id) == report
    assert [item["path"] for item in workspace.get_task(task_id)["file_reads"]] == ["note.txt"]

    waiting = _in_progress(workspace, "Make the folder")
    waiting_id = waiting["id"]
    workspace.add_workflow_step(
        waiting_id,
        "Create the folder",
        "folder",
        str(project),
        "notes",
        "Create the notes folder",
        "consequential",
    )
    held = workspace.advance_workflow(waiting_id)
    assert held["workflow"]["steps"][0]["state"] == "Waiting"
    held_report = workspace.replay_workflow_execution(waiting_id)
    assert held_report["matched"] == []
    assert held_report["stopped"] == "Stopped at Create the folder: waiting for approval."
    assert len(workspace.get_task(waiting_id)["implementation_changes"]) == 1
    assert held["workflow"]["steps"][0]["state"] == "Waiting"

    missing = _in_progress(workspace, "Read a missing file")
    missing_id = missing["id"]
    _read(workspace, missing_id, project, "Read the gap", "missing.txt")
    failed = workspace.advance_workflow(missing_id)
    failed_report = workspace.replay_workflow_execution(missing_id)
    assert failed_report["stopped"] == (
        "Stopped at Read the gap: The file must already exist."
    )
    assert failed["workflow"]["steps"][0]["state"] == "Failed"
    assert workspace.get_task(missing_id)["file_reads"] == []


def test_a_running_step_is_not_replayed(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    assert isinstance(_prepare(workspace, task_id), workflow.ReadyToFinish)
    refused = workspace.replay_workflow_execution(task_id)
    assert isinstance(refused, Refusal)
    assert refused.message == "Recover the interrupted step first."
    opened = workspace.get_task(task_id)
    assert opened["workflow"]["steps"][0]["state"] == "Running"
    assert opened["workflow"]["execution"] is None
    assert opened["file_reads"] == []
