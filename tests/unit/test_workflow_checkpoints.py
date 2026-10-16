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


def test_a_checkpoint_keeps_the_original_step_states(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    (project / "extra.txt").write_text("extra\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    assert task["workflow"]["checkpoints"] == []
    blank = workspace.take_checkpoint(task_id, " ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this checkpoint."
    empty = _in_progress(workspace, "No steps yet")
    missing_workflow = workspace.take_checkpoint(empty["id"], "before the read")
    assert missing_workflow.message == "There is no workflow to checkpoint."

    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the extra", "extra.txt")
    saved = workspace.take_checkpoint(task_id, "before the read")
    assert saved["status"] == "In Progress"
    assert saved["workflow"]["checkpoints"] == [
        {
            "id": saved["workflow"]["checkpoints"][0]["id"],
            "name": "before the read",
            "steps": [
                {"title": "Read the note", "state": "Pending"},
                {"title": "Read the extra", "state": "Pending"},
            ],
        }
    ]
    workspace.advance_workflow(task_id)
    repeated = workspace.take_checkpoint(task_id, "before the read")
    assert repeated["workflow"]["checkpoints"] == saved["workflow"]["checkpoints"]
    assert [item["path"] for item in repeated["file_reads"]] == ["note.txt"]

    other = _in_progress(workspace, "Another export")
    other_id = other["id"]
    _read(workspace, other_id, project, "Read the note", "note.txt")
    other_saved = workspace.take_checkpoint(other_id, "before the read")
    assert other_saved["workflow"]["checkpoints"][0]["name"] == "before the read"
    assert len(workspace.get_task(task_id)["workflow"]["checkpoints"]) == 1


def test_a_running_step_cannot_be_checkpointed(workspace, tmp_path):
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
    refused = workspace.take_checkpoint(task_id, "while running")
    assert refused.message == "Recover the interrupted step first."
    assert workspace.get_task(task_id)["workflow"]["checkpoints"] == []


def test_a_rolled_back_checkpoint_is_not_stored(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")

    def _save_then_refuse(connection):
        workflow.take_checkpoint(connection, task_id, "before the read", "2026-10-16T00:00:00Z")
        return bad_request("no")

    refused = call_in_transaction(workspace.connection, _save_then_refuse)
    assert refused.message == "no"
    assert workspace.get_task(task_id)["workflow"]["checkpoints"] == []


def test_restore_returns_a_failed_step_to_pending(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the gap", "missing.txt")
    workspace.advance_workflow(task_id)
    saved = workspace.take_checkpoint(task_id, "after the note")
    checkpoint_id = saved["workflow"]["checkpoints"][0]["id"]
    failed = workspace.advance_workflow(task_id)
    assert failed["workflow"]["steps"][1]["state"] == "Failed"
    restored = workspace.restore_checkpoint(task_id, checkpoint_id)
    assert restored["status"] == "In Progress"
    assert [step["state"] for step in restored["workflow"]["steps"]] == ["Completed", "Pending"]
    assert [item["path"] for item in restored["file_reads"]] == ["note.txt"]
    assert restored["workflow"]["checkpoints"][0]["steps"][1]["state"] == "Pending"
    missing = workspace.restore_checkpoint(task_id, 9999)
    assert missing.message == "That checkpoint is not on this task."


def test_a_stored_effect_cannot_be_restored_over(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
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
    saved = workspace.take_checkpoint(task_id, "before the folder")
    checkpoint_id = saved["workflow"]["checkpoints"][0]["id"]
    held = workspace.advance_workflow(task_id)
    workspace.mark_change_not_carried_out(
        task_id, held["workflow"]["steps"][0]["change_id"], "Not this folder"
    )
    failed = workspace.advance_workflow(task_id)
    assert failed["workflow"]["steps"][0]["state"] == "Failed"
    refused = workspace.restore_checkpoint(task_id, checkpoint_id)
    assert refused.message == "A stored effect cannot be restored over."
    assert workspace.get_task(task_id)["workflow"]["steps"][0]["state"] == "Failed"
    assert not (project / "notes").exists()


def test_a_changed_workflow_cannot_be_restored(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    saved = workspace.take_checkpoint(task_id, "one step")
    checkpoint_id = saved["workflow"]["checkpoints"][0]["id"]
    _read(workspace, task_id, project, "Read the extra", "note.txt")
    refused = workspace.restore_checkpoint(task_id, checkpoint_id)
    assert refused.message == "The workflow has changed since this checkpoint."
    assert [step["state"] for step in workspace.get_task(task_id)["workflow"]["steps"]] == [
        "Pending",
        "Pending",
    ]


def test_reading_checkpoints_does_not_move_the_clock(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    workspace.take_checkpoint(task_id, "before the read")
    clock_index = workspace.clock._index
    first = workspace.workflow_checkpoints(task_id)
    second = workspace.workflow_checkpoints(task_id)
    assert second == first
    assert first["checkpoints"][0]["name"] == "before the read"
    assert workspace.clock._index == clock_index
    missing = workspace.workflow_checkpoints(9999)
    assert missing.message == "Task not found."
