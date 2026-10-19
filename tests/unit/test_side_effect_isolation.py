from task_manager.domain import workflow
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage import workflow_store
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _read(workspace, task_id, project, title, path):
    return workspace.add_workflow_step(task_id, title, "read", str(project), path, None, None)


def test_a_completed_step_seals_one_effect(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    completed = workspace.advance_workflow(task_id)
    assert completed["workflow"]["isolated"]["matched"] == [
        {"title": "Read the note", "effect": "note.txt"}
    ]
    assert completed["workflow"]["isolated"]["stopped"] is None
    step_id = completed["workflow"]["steps"][0]["id"]

    def _complete_again(connection):
        step = workflow_store.row_step(connection, step_id)
        workflow._set_outcome(connection, step, "Completed", None, None, "2026-10-19T00:00:01Z")

    call_in_transaction(workspace.connection, _complete_again)
    again = workspace.replay_isolated_effects(task_id)
    assert again["matched"] == completed["workflow"]["isolated"]["matched"]

    missing = _in_progress(workspace, "Read a missing file")
    missing_id = missing["id"]
    _read(workspace, missing_id, project, "Read the gap", "missing.txt")
    failed = workspace.advance_workflow(missing_id)
    assert failed["workflow"]["steps"][0]["state"] == "Failed"
    assert failed["workflow"]["isolated"]["matched"] == []
    assert failed["workflow"]["isolated"]["stopped"] == (
        "Stopped at Read the gap: The file must already exist."
    )


def test_a_rolled_back_completion_seals_nothing(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    added = _read(workspace, task_id, project, "Read the note", "note.txt")
    step_id = added["workflow"]["steps"][0]["id"]
    step = workflow_store.row_step(workspace.connection, step_id)

    def _complete_then_refuse(connection):
        workflow._set_outcome(connection, step, "Completed", None, None, "2026-10-19T00:00:00Z")
        return bad_request("no")

    refused = call_in_transaction(workspace.connection, _complete_then_refuse)
    assert isinstance(refused, Refusal)
    assert refused.message == "no"
    opened = workspace.get_task(task_id)
    assert opened["workflow"]["steps"][0]["state"] == "Pending"
    assert opened["workflow"]["isolated"]["matched"] == []
    assert opened["file_reads"] == []


def test_replay_leaves_a_removed_file_removed(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    note = project / "note.txt"
    note.write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the extra", "extra.txt")
    workspace.advance_workflow(task_id)
    note.unlink()
    clock_index = workspace.clock._index
    first = workspace.replay_isolated_effects(task_id)
    second = workspace.replay_isolated_effects(task_id)
    assert second == first
    assert first["matched"] == [{"title": "Read the note", "effect": "note.txt"}]
    assert first["stopped"] == "Stopped at Read the extra: the step has not run."
    assert workspace.clock._index == clock_index
    assert not note.exists()
    opened = workspace.get_task(task_id)
    assert opened["status"] == "In Progress"
    assert [item["path"] for item in opened["file_reads"]] == ["note.txt"]
    missing = workspace.replay_isolated_effects(9999)
    assert missing.message == "Task not found."
    empty = _in_progress(workspace, "No steps")
    none = workspace.replay_isolated_effects(empty["id"])
    assert none.message == "There is no isolated effect to replay."


def test_replay_leaves_a_removed_folder_removed(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_workflow_step(
        task_id, "Create the folder", "folder", str(project), "notes", "Add notes", "ordinary"
    )
    created = workspace.advance_workflow(task_id)
    assert created["workflow"]["isolated"]["matched"] == [
        {"title": "Create the folder", "effect": "notes"}
    ]
    folder = project / "notes"
    folder.rmdir()
    report = workspace.replay_isolated_effects(task_id)
    assert report["matched"] == [{"title": "Create the folder", "effect": "notes"}]
    assert report["stopped"] is None
    assert not folder.exists()
