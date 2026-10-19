from task_manager.domain import workflow
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def _read(workspace, task_id, project, title, path, present=True):
    if present:
        (project / path).write_text(path + "\n", encoding="utf-8")
    return workspace.add_workflow_step(task_id, title, "read", str(project), path, None, None)


def test_a_run_reads_only_the_next_file(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the extra", "extra.txt")

    ran = workspace.run_file_read(task_id, "once")
    assert ran["status"] == "In Progress"
    assert [step["state"] for step in ran["workflow"]["steps"]] == ["Completed", "Pending"]
    assert [item["path"] for item in ran["file_reads"]] == ["note.txt"]
    assert ran["workflow"]["runs"] == [{"name": "once", "title": "Read the note"}]
    assert ran["executions"] == []

    repeated = workspace.run_file_read(task_id, " once ")
    assert [item["path"] for item in repeated["file_reads"]] == ["note.txt"]
    assert [step["state"] for step in repeated["workflow"]["steps"]] == ["Completed", "Pending"]

    followed = workspace.run_file_read(task_id, "next")
    assert [item["path"] for item in followed["file_reads"]] == ["note.txt", "extra.txt"]
    assert [step["state"] for step in followed["workflow"]["steps"]] == ["Completed", "Completed"]
    assert followed["workflow"]["runs"] == [
        {"name": "once", "title": "Read the note"},
        {"name": "next", "title": "Read the extra"},
    ]
    assert followed["workflow"]["inbox"] == []

    other = _in_progress(workspace, "Read the other")
    _read(workspace, other["id"], project, "Read the other note", "other.txt")
    other_run = workspace.run_file_read(other["id"], "once")
    assert [item["path"] for item in other_run["file_reads"]] == ["other.txt"]
    assert [item["path"] for item in workspace.get_task(task_id)["file_reads"]] == [
        "note.txt",
        "extra.txt",
    ]


def test_a_run_leaves_a_folder_and_a_rollback_pending(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.add_workflow_step(
        task_id, "Create the folder", "folder", str(project), "notes", "Add notes", "ordinary"
    )
    _read(workspace, task_id, project, "Read the note", "note.txt")

    blocked = workspace.run_file_read(task_id, "once")
    assert isinstance(blocked, Refusal)
    assert blocked.message == "The next step is not a file read."
    assert not (project / "notes").exists()
    assert workspace.get_task(task_id)["workflow"]["runs"] == []
    assert workspace.get_task(task_id)["file_reads"] == []

    blank = workspace.run_file_read(task_id, "  ")
    assert isinstance(blank, Refusal)
    assert blank.message == "Name this run."
    empty = _in_progress(workspace, "Empty")
    missing = workspace.run_file_read(empty["id"], "later")
    assert isinstance(missing, Refusal)
    assert missing.message == "There is no file to read."

    readable = _in_progress(workspace, "Readable")
    readable_id = readable["id"]
    _read(workspace, readable_id, project, "Read the note", "kept.txt")

    def _then_refuse(connection):
        workflow.run_file_read(
            connection,
            readable_id,
            "once",
            "2026-10-19T00:00:00Z",
            workspace.project_root,
        )
        return bad_request("no")

    rolled = call_in_transaction(workspace.connection, _then_refuse)
    assert isinstance(rolled, Refusal)
    opened = workspace.get_task(readable_id)
    assert opened["workflow"]["steps"][0]["state"] == "Pending"
    assert opened["workflow"]["runs"] == []
    assert opened["file_reads"] == []

    restored = workspace.run_file_read(readable_id, "once")
    assert restored["workflow"]["steps"][0]["state"] == "Completed"
    assert [item["path"] for item in restored["file_reads"]] == ["kept.txt"]

    absent = _in_progress(workspace, "Absent")
    absent_id = absent["id"]
    _read(workspace, absent_id, project, "Read the gap", "missing.txt", present=False)
    _read(workspace, absent_id, project, "Read the note", "note.txt")
    failed = workspace.run_file_read(absent_id, "once")
    assert failed["workflow"]["steps"][0]["state"] == "Failed"
    assert failed["workflow"]["stopped"] == "Stopped at Read the gap: The file must already exist."
    assert failed["workflow"]["steps"][1]["state"] == "Pending"
    assert failed["file_reads"] == []
    assert failed["workflow"]["runs"] == [{"name": "once", "title": "Read the gap"}]
    repeated = workspace.run_file_read(absent_id, "once")
    assert repeated["workflow"]["steps"][1]["state"] == "Pending"
    (project / "missing.txt").write_text("back\n", encoding="utf-8")
    retried = workspace.run_file_read(absent_id, "next")
    assert retried["workflow"]["steps"][0]["state"] == "Completed"
    assert retried["workflow"]["steps"][1]["state"] == "Pending"
    assert [item["path"] for item in retried["file_reads"]] == ["missing.txt"]

    held = _in_progress(workspace, "Held")
    held_id = held["id"]
    _read(workspace, held_id, project, "Read the note", "held.txt")
    call_in_transaction(
        workspace.connection,
        lambda connection: workflow.prepare(connection, held_id, "2026-10-19T00:00:00Z"),
    )
    interrupted = workspace.run_file_read(held_id, "once")
    assert isinstance(interrupted, Refusal)
    assert interrupted.message == "Recover the interrupted step first."
    assert workspace.get_task(held_id)["workflow"]["runs"] == []

    draft = workspace.create_task("Draft")
    refused = workspace.run_file_read(draft["id"], "later")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
