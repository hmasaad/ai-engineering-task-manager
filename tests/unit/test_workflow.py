from task_manager.domain.results import Refusal
from task_manager.workspace import Workspace


def _task(workspace, title):
    return workspace.create_task(title)


def _in_progress(workspace, title="Add export"):
    created = _task(workspace, title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_steps_are_stored_in_order_and_a_bad_step_is_refused(workspace):
    draft = _task(workspace, "Still a draft")
    refused = workspace.add_workflow_step(
        draft["id"], "Read the note", "read", "/tmp/demo", "note.txt", None, None
    )
    assert refused.message == "The task must be In Progress."

    ready = _task(workspace, "Not started")
    workspace.set_goal(ready["id"], "Take the record")
    workspace.add_criterion(ready["id"], "The export contains the goal")
    ready = workspace.transition(ready["id"], "mark_ready")
    assert (
        workspace.add_workflow_step(
            ready["id"], "Read the note", "read", "/tmp/demo", "note.txt", None, None
        ).message
        == "Start the task first."
    )

    task = _in_progress(workspace)
    task_id = task["id"]
    assert workspace.add_workflow_step(
        task_id, "  ", "read", "/tmp/demo", "note.txt", None, None
    ).message == "Name the step."
    assert workspace.add_workflow_step(
        task_id, "Commit the note", "commit", "/tmp/demo", "note.txt", None, None
    ).message == "Choose a step action."
    assert workspace.add_workflow_step(
        task_id, "Read the note", "read", "  ", "note.txt", None, None
    ).message == "Name the project this change is for."
    assert workspace.add_workflow_step(
        task_id, "Read the note", "read", "/tmp/demo", "  ", None, None
    ).message == "Name the file this change reads."
    assert workspace.add_workflow_step(
        task_id, "Create the folder", "folder", "/tmp/demo", "notes", "  ", "ordinary"
    ).message == "An account of what changed is required."
    assert workspace.add_workflow_step(
        task_id, "Create the folder", "folder", "/tmp/demo", "notes", "Add notes", "later"
    ).message == "Choose ordinary or consequential."
    assert workspace.add_workflow_step(
        task_id, "Create the folder", "folder", "/tmp/demo", "  ", "Add notes", "ordinary"
    ).message == "Name the folder this change creates."
    assert workspace.get_task(task_id)["workflow"]["steps"] == []

    first = workspace.add_workflow_step(
        task_id, "Read the note", "read", "/tmp/demo", "note.txt", "ignored", "ordinary"
    )
    assert first["status"] == "In Progress"
    second = workspace.add_workflow_step(
        task_id,
        "Create the folder",
        "folder",
        "/tmp/demo",
        "notes",
        "Add notes",
        "ordinary",
    )
    assert [step["title"] for step in second["workflow"]["steps"]] == [
        "Read the note",
        "Create the folder",
    ]
    assert [step["state"] for step in second["workflow"]["steps"]] == ["Pending", "Pending"]
    assert second["workflow"]["steps"][0]["action"] == "read"
    assert second["workflow"]["started"] is False
    opened = workspace.get_task(task_id)
    assert opened["workflow"]["steps"] == second["workflow"]["steps"]

    removed = workspace.remove_workflow_step(task_id, second["workflow"]["steps"][0]["id"])
    assert [step["title"] for step in removed["workflow"]["steps"]] == ["Create the folder"]
    absent = workspace.remove_workflow_step(task_id, 999)
    assert absent.message == "That step is not on this task."

    completed = _in_progress(workspace, "Already done")
    criterion_id = completed["criteria"][0]["id"]
    workspace.verify_criterion(
        completed["id"], criterion_id, "The export contains the goal", "pass", "inspection", "local-1"
    )
    completed = workspace.transition(completed["id"], "complete")
    assert (
        workspace.add_workflow_step(
            completed["id"], "Read the note", "read", "/tmp/demo", "note.txt", None, None
        ).message
        == "Reopen the task first."
    )
    dropped = _task(workspace, "Dropped")
    cancelled = workspace.transition(dropped["id"], "cancel", "Not needed")
    assert (
        workspace.add_workflow_step(
            cancelled["id"], "Read the note", "read", "/tmp/demo", "note.txt", None, None
        ).message
        == "A cancelled task cannot be changed. Continued work is a new task."
    )


def test_one_advance_runs_one_step_and_reopening_resumes(workspace, tmp_path, clock):
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
    advanced = workspace.advance_workflow(task_id)
    assert advanced["status"] == "In Progress"
    assert [step["state"] for step in advanced["workflow"]["steps"]] == ["Completed", "Pending"]
    assert advanced["workflow"]["stopped"] is None
    assert len(advanced["file_reads"]) == 1
    assert not (project / "notes").exists()
    assert (
        workspace.add_workflow_step(
            task_id, "Read it again", "read", str(project), "note.txt", None, None
        ).message
        == "A step can be added only before the workflow runs."
    )
    assert (
        workspace.remove_workflow_step(task_id, advanced["workflow"]["steps"][1]["id"]).message
        == "A step cannot be removed after the workflow runs."
    )

    reopened = Workspace(tmp_path / "workspace.db", clock, "Ada")
    try:
        stored = reopened.get_task(task_id)
        assert [step["state"] for step in stored["workflow"]["steps"]] == ["Completed", "Pending"]
        assert len(stored["file_reads"]) == 1
        resumed = reopened.advance_workflow(task_id)
        assert [step["state"] for step in resumed["workflow"]["steps"]] == [
            "Completed",
            "Completed",
        ]
        assert resumed["workflow"]["finished"] is True
        assert (project / "notes").is_dir()
        assert len(resumed["file_reads"]) == 1
        again = reopened.advance_workflow(task_id)
        assert isinstance(again, Refusal)
        assert again.message == "There is no step to run."
        assert reopened.get_task(task_id)["status"] == "In Progress"
    finally:
        reopened.close()


def test_a_refusal_stops_the_workflow_and_names_the_step(workspace, tmp_path):
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
    stopped = workspace.advance_workflow(task_id)
    assert stopped["workflow"]["steps"][0]["state"] == "Failed"
    assert stopped["workflow"]["steps"][1]["state"] == "Pending"
    assert stopped["workflow"]["stopped"] == (
        "Stopped at Read the note: The file must already exist."
    )
    assert stopped["file_reads"] == []
    assert not (project / "notes").exists()
    assert stopped["status"] == "In Progress"

    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    retried = workspace.advance_workflow(task_id)
    assert [step["state"] for step in retried["workflow"]["steps"]] == ["Completed", "Pending"]
    assert retried["workflow"]["stopped"] is None
    assert len(retried["file_reads"]) == 1
    assert not (project / "notes").exists()


def test_a_waiting_step_is_settled_without_running_it_again(workspace, tmp_path):
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
        "Add the notes folder",
        "consequential",
    )
    workspace.add_workflow_step(
        task_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    waiting = workspace.advance_workflow(task_id)
    assert waiting["workflow"]["stopped"] == (
        "Stopped at Create the folder: waiting for approval."
    )
    assert waiting["workflow"]["steps"][0]["state"] == "Waiting"
    assert waiting["workflow"]["steps"][1]["state"] == "Pending"
    assert not (project / "notes").exists()
    assert len(waiting["implementation_changes"]) == 1
    change_id = waiting["workflow"]["steps"][0]["change_id"]
    again = workspace.advance_workflow(task_id)
    assert again["workflow"]["steps"][0]["state"] == "Waiting"
    assert len(again["implementation_changes"]) == 1

    approved = workspace.approve_change(task_id, change_id, "The folder path was reviewed.")
    assert approved["workflow"]["steps"][0]["state"] == "Waiting"
    assert (project / "notes").is_dir()
    settled = workspace.advance_workflow(task_id)
    assert settled["workflow"]["steps"][0]["state"] == "Completed"
    assert settled["workflow"]["steps"][1]["state"] == "Pending"
    assert settled["workflow"]["stopped"] is None
    assert len(settled["implementation_changes"]) == 1
    assert settled["file_reads"] == []

    declined_task = _in_progress(workspace, "Hold the folder")
    declined_id = declined_task["id"]
    workspace.add_workflow_step(
        declined_id,
        "Create the folder",
        "folder",
        str(project),
        "other",
        "Add the other folder",
        "consequential",
    )
    workspace.add_workflow_step(
        declined_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    held = workspace.advance_workflow(declined_id)
    workspace.mark_change_not_carried_out(
        declined_id, held["workflow"]["steps"][0]["change_id"], "Not this folder"
    )
    failed = workspace.advance_workflow(declined_id)
    assert failed["workflow"]["stopped"] == "Stopped at Create the folder: Not this folder"
    assert failed["workflow"]["steps"][0]["state"] == "Failed"
    assert failed["workflow"]["steps"][1]["state"] == "Pending"
    assert not (project / "other").exists()
