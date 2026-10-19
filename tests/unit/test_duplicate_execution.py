from task_manager.domain import file_read
from task_manager.domain.results import Refusal, bad_request
from task_manager.storage.connection import call_in_transaction


def _in_progress(workspace, title="Add export"):
    created = workspace.create_task(title)
    workspace.set_goal(created["id"], "Take the record")
    workspace.add_criterion(created["id"], "The export contains the goal")
    ready = workspace.transition(created["id"], "mark_ready")
    return workspace.transition(ready["id"], "start")


def test_one_name_reads_and_creates_once(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    note = project / "note.txt"
    note.write_text("hello\n", encoding="utf-8")
    (project / "other.txt").write_text("other\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    first = workspace.record_file_read(task_id, str(project), "note.txt", execution="once")
    assert [item["path"] for item in first["file_reads"]] == ["note.txt"]
    assert first["executions"] == [{"name": "once", "action": "read", "path": "note.txt"}]
    assert first["status"] == "In Progress"
    note.unlink()
    again = workspace.record_file_read(task_id, str(project), "other.txt", execution="once")
    assert [item["path"] for item in again["file_reads"]] == ["note.txt"]
    assert again["executions"] == first["executions"]
    assert not note.exists()
    assert not any(item["path"] == "other.txt" for item in again["file_reads"])
    other = workspace.record_file_read(task_id, str(project), "other.txt", execution="second")
    assert [item["path"] for item in other["file_reads"]] == ["note.txt", "other.txt"]

    folder = project / "notes"
    created = workspace.record_folder(
        task_id,
        str(project),
        "ordinary",
        "Add the notes folder",
        False,
        "notes",
        execution="notes",
    )
    assert created["executions"][-1] == {"name": "notes", "action": "folder", "path": "notes"}
    assert len(created["implementation_changes"]) == 1
    assert folder.is_dir()
    folder.rmdir()
    repeated = workspace.record_folder(
        task_id,
        str(project),
        "ordinary",
        "Add another folder",
        False,
        "other",
        execution="notes",
    )
    assert len(repeated["implementation_changes"]) == 1
    assert not folder.exists()
    assert not (project / "other").exists()

    held = workspace.record_folder(
        task_id,
        str(project),
        "consequential",
        "Hold the archive",
        False,
        "archive",
        execution="hold",
    )
    assert len(held["implementation_changes"]) == 2
    assert not (project / "archive").exists()
    held_again = workspace.record_folder(
        task_id,
        str(project),
        "consequential",
        "Hold it again",
        False,
        "archive",
        execution="hold",
    )
    assert len(held_again["implementation_changes"]) == 2
    assert not (project / "archive").exists()


def test_a_refusal_leaves_the_name_free(workspace, tmp_path):
    project = tmp_path / "demo"
    project.mkdir()
    note = project / "note.txt"
    note.write_text("hello\n", encoding="utf-8")
    task = _in_progress(workspace)
    task_id = task["id"]
    workspace.record_file_read(task_id, str(project), "note.txt", execution="  ")
    again = workspace.record_file_read(task_id, str(project), "note.txt", execution="")
    assert [item["path"] for item in again["file_reads"]] == ["note.txt", "note.txt"]
    assert again["executions"] == []

    missing = workspace.record_file_read(task_id, str(project), "missing.txt", execution="once")
    assert isinstance(missing, Refusal)
    assert missing.message == "The file must already exist."
    assert workspace.get_task(task_id)["executions"] == []
    found = workspace.record_file_read(task_id, str(project), "note.txt", execution="once")
    assert [item["name"] for item in found["executions"]] == ["once"]
    spaced = workspace.record_file_read(task_id, str(project), "note.txt", execution=" once ")
    assert len(spaced["file_reads"]) == len(found["file_reads"])

    other = _in_progress(workspace, "Another task")
    other_read = workspace.record_file_read(other["id"], str(project), "note.txt", execution="once")
    assert other_read["executions"] == [{"name": "once", "action": "read", "path": "note.txt"}]

    draft = workspace.create_task("Draft")
    refused = workspace.record_file_read(draft["id"], str(project), "note.txt", execution="later")
    assert isinstance(refused, Refusal)
    assert refused.message == "The task must be In Progress."
    assert workspace.get_task(draft["id"])["executions"] == []

    def _read_then_refuse(connection):
        file_read.read_file(
            connection,
            task_id,
            str(project),
            "note.txt",
            "2026-10-19T00:00:00Z",
            project,
            "rolled",
        )
        return bad_request("no")

    rolled = call_in_transaction(workspace.connection, _read_then_refuse)
    assert isinstance(rolled, Refusal)
    opened = workspace.get_task(task_id)
    assert [item["name"] for item in opened["executions"]] == ["once"]
    used = workspace.record_file_read(task_id, str(project), "note.txt", execution="rolled")
    assert [item["name"] for item in used["executions"]] == ["once", "rolled"]

    workspace.add_workflow_step(
        task_id, "Read the note", "read", str(project), "note.txt", None, None
    )
    advanced = workspace.advance_workflow(task_id)
    assert [item["name"] for item in advanced["executions"]] == ["once", "rolled"]
    assert advanced["status"] == "In Progress"
