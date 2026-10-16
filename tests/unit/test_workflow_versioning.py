from task_manager.clock import format_time
from task_manager.domain import workflow
from task_manager.domain.results import Refusal
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


def _prepare(workspace, task_id):
    occurred_at = format_time(workspace.clock.now())
    return call_in_transaction(
        workspace.connection,
        lambda conn: workflow.prepare(conn, task_id, occurred_at),
    )


def test_a_new_workflow_is_version_1(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    (project / "other.txt").write_text("other\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    opened = _read(workspace, task_id, project, "Read the other", "other.txt")
    assert opened["workflow"]["version"] == 1
    assert opened["workflow"]["draft"] is None
    assert opened["status"] == "In Progress"
    advanced = workspace.advance_workflow(task_id)
    assert advanced["workflow"]["version"] == 1
    assert [step["state"] for step in advanced["workflow"]["steps"]] == [
        "Completed",
        "Pending",
    ]
    assert len(advanced["file_reads"]) == 1
    again = workspace.get_task(task_id)
    assert again["workflow"]["version"] == 1
    refused = workspace.add_workflow_step(
        task_id, "Read again", "read", str(project), "note.txt", None, None
    )
    assert refused.message == "A step can be added only before the workflow runs."


def test_an_existing_workflow_reports_version_1_without_writing(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]

    def _insert(conn):
        workflow_store.insert_step(
            conn, task_id, "Read the note", "read", str(project), "note.txt", None, None
        )

    call_in_transaction(workspace.connection, _insert)
    opened = workspace.get_task(task_id)
    assert opened["workflow"]["version"] == 1
    assert opened["workflow"]["steps"][0]["title"] == "Read the note"
    stored = workspace.connection.execute("SELECT COUNT(*) FROM workflow_version").fetchone()[0]
    assert stored == 0


def test_revise_keeps_the_steps_that_already_ran(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    (project / "other.txt").write_text("other\n", encoding="utf-8")
    (project / "extra.txt").write_text("extra\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    early = workspace.revise_workflow(task_id)
    assert early.message == "There is no workflow to revise."
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the other", "other.txt")
    assert workspace.revise_workflow(task_id).message == "The workflow has not run yet."
    advanced = workspace.advance_workflow(task_id)
    replay = list(advanced["workflow"]["replay"])
    revised = workspace.revise_workflow(task_id)
    assert revised["status"] == "In Progress"
    assert revised["workflow"]["version"] == 1
    assert [step["title"] for step in revised["workflow"]["steps"]] == [
        "Read the note",
        "Read the other",
    ]
    assert revised["workflow"]["draft"]["number"] == 2
    assert [step["title"] for step in revised["workflow"]["draft"]["steps"]] == [
        "Read the note"
    ]
    assert revised["workflow"]["replay"] == replay
    again = workspace.revise_workflow(task_id)
    assert again.message == "A draft version already exists."
    added = _read(workspace, task_id, project, "Read the extra", "extra.txt")
    assert [step["title"] for step in added["workflow"]["steps"]] == [
        "Read the note",
        "Read the other",
    ]
    assert [step["title"] for step in added["workflow"]["draft"]["steps"]] == [
        "Read the note",
        "Read the extra",
    ]
    kept = added["workflow"]["draft"]["steps"][0]
    refused = workspace.remove_workflow_step(task_id, kept["id"])
    assert refused.message == "A step that already ran must stay in the new version."
    extra = added["workflow"]["draft"]["steps"][1]
    removed = workspace.remove_workflow_step(task_id, extra["id"])
    assert [step["title"] for step in removed["workflow"]["draft"]["steps"]] == [
        "Read the note"
    ]


def test_an_interrupted_step_is_recovered_before_revise(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _prepare(workspace, task_id)
    refused = workspace.revise_workflow(task_id)
    assert isinstance(refused, Refusal)
    assert refused.message == "Recover the interrupted step first."
    assert workspace.get_task(task_id)["workflow"]["draft"] is None


def test_migration_switches_to_the_draft_and_skips_the_old_pending_step(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    (project / "note.txt").write_text("hello\n", encoding="utf-8")
    (project / "other.txt").write_text("other\n", encoding="utf-8")
    (project / "extra.txt").write_text("extra\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    assert workspace.migrate_workflow(task_id, "Replace the remaining step").message == (
        "There is no draft version to migrate."
    )
    _read(workspace, task_id, project, "Read the note", "note.txt")
    _read(workspace, task_id, project, "Read the other", "other.txt")
    workspace.advance_workflow(task_id)
    workspace.revise_workflow(task_id)
    _read(workspace, task_id, project, "Read the extra", "extra.txt")
    blank = workspace.migrate_workflow(task_id, " ")
    assert blank.message == "Name why this workflow is migrating."
    assert workspace.get_task(task_id)["workflow"]["version"] == 1
    migrated = workspace.migrate_workflow(task_id, "Replace the remaining step")
    assert migrated["status"] == "In Progress"
    assert migrated["workflow"]["version"] == 2
    assert migrated["workflow"]["draft"] is None
    assert [step["title"] for step in migrated["workflow"]["steps"]] == [
        "Read the note",
        "Read the extra",
    ]
    assert migrated["workflow"]["steps"][0]["state"] == "Completed"
    assert migrated["workflow"]["migrations"] == [
        {
            "from_version": 1,
            "to_version": 2,
            "reason": "Replace the remaining step",
            "recorded_at": migrated["workflow"]["migrations"][0]["recorded_at"],
        }
    ]
    assert len(migrated["workflow"]["replay"]) == 2
    assert len(migrated["file_reads"]) == 1
    followed = workspace.advance_workflow(task_id)
    assert [step["state"] for step in followed["workflow"]["steps"]] == [
        "Completed",
        "Completed",
    ]
    assert [read["path"] for read in followed["file_reads"]] == ["note.txt", "extra.txt"]
    assert not any(read["path"] == "other.txt" for read in followed["file_reads"])
    assert workspace.get_task(task_id)["workflow"]["migrations"][0]["reason"] == (
        "Replace the remaining step"
    )
